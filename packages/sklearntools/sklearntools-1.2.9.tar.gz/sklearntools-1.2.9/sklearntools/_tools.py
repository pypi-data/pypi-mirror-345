import os
import time
import warnings
from typing import Union
import numpy as np
from collections import Counter
from concurrent.futures import as_completed, ProcessPoolExecutor
from sklearn.model_selection import ParameterGrid
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, mean_squared_error, mean_absolute_error, r2_score, \
	precision_score, f1_score, recall_score, roc_auc_score, classification_report
from logging import basicConfig, INFO, getLogger, Formatter, StreamHandler, DEBUG

warnings.filterwarnings("ignore")

# 设置日志记录器
logger = getLogger(__name__)
formatter = Formatter('[%(asctime)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

handler = StreamHandler()
handler.setLevel(DEBUG)
handler.setFormatter(formatter)

logger.addHandler(handler)
logger.setLevel(INFO)


def _log(score, describe, evaluate_fn, is_classifier, cost_time):
	"""内部函数：用于记录模型评估结果的日志
	
	Args:
		score: 评分结果
		describe: 评分描述
		evaluate_fn: 评估函数
		is_classifier: 是否为分类模型
		cost_time: 耗时
	"""
	if is_classifier:
		if cost_time:
			logger.info(f'{describe}: {score:.1%} \t 耗时: {cost_time:.2f} seconds.')
		else:
			logger.info(f'{describe}: {score:.1%}')
	else:
		if '准确率' == describe:
			if evaluate_fn == mean_squared_error:
				describe = 'MSE'
			# elif evaluate_fn == root_mean_squared_error:
			# 	describe = 'RMSE'
			else:
				describe = 'R2_SCORE'
		if cost_time:
			logger.info(f'{describe}: {score:.2f} \t 耗时: {cost_time:.2f} seconds.')
		else:
			logger.info(f'{describe}: {score:.2f}')
		

def train_evaluate(model, X_train, y_train, X_test, y_test, describe='准确率', verbose=True, return_predict=False,
                   evaluate_fn=None, show_time=False) -> Union[float, tuple[float, list]]:
	"""训练并评估模型
	
	分类器默认使用accuracy_score评分
	回归器默认使用r2_score评分
	
	Args:
		model: 机器学习模型实例
		X_train: 训练数据特征
		y_train: 训练数据标签
		X_test: 测试数据特征
		y_test: 测试数据标签
		describe: 评分描述文字
		verbose: 是否打印评估结果
		return_predict: 是否返回预测结果
		evaluate_fn: 自定义评估函数
		show_time: 是否显示训练耗时
		
	Returns:
		如果return_predict为False，返回评分
		如果return_predict为True，返回(评分, 预测结果)的元组
	
    Examples
    --------
    >>> import numpy as np
    >>> from sklearn.ensemble import RandomForestClassifier
    >>> from sklearn.model_selection import train_test_split
    >>> from sklearntools import train_evaluate
    >>> X, y = np.arange(20).reshape((10, 2)), range(10)
    >>> X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3)
    >>> model = RandomForestClassifier(n_estimators=837, bootstrap=False)
    >>> train_evaluate(model, X_train, y_train, X_test, y_test)
    0.88
	"""
	if show_time:
		start_time = time.perf_counter()
		model.fit(X_train, y_train)
		cost_time = time.perf_counter() - start_time
	else:
		cost_time = None
		model.fit(X_train, y_train)

	is_classifier = 'classifier' == model._estimator_type
	if return_predict or evaluate_fn is not None:
		prediction = model.predict(X_test)
		if is_classifier:
			evaluate_fn = evaluate_fn or accuracy_score
		else:
			evaluate_fn = evaluate_fn or r2_score
		if isinstance(evaluate_fn, str):
			fn_dict = {
				"accuracy_score": accuracy_score,
				"acc": accuracy_score,
				"accuracy": accuracy_score,
				"mean_squared_error": mean_squared_error,
				"mse": mean_squared_error,
				"root_mean_squared_error": lambda y_true, y_pred: np.sqrt(mean_squared_error(y_true, y_pred)),
				"rmse": lambda y_true, y_pred: np.sqrt(mean_squared_error(y_true, y_pred)),
				"mean_absolute_error": mean_absolute_error,
				"mae": mean_absolute_error,
				"r2_score": r2_score,
				"r2": r2_score,
			}
			evaluate_fn = evaluate_fn.lower()
			assert evaluate_fn in fn_dict
			evaluate_fn = fn_dict[evaluate_fn]
			
		score = evaluate_fn(y_test, prediction)
		if verbose:
			_log(score, describe, evaluate_fn, is_classifier, cost_time)
		return score, prediction
	else:
		score = model.score(X_test, y_test)
		if verbose:
			_log(score, describe, None, is_classifier, cost_time)
		return score
	

def train_evaluate_split(model, X, y, test_size=0.2, describe='准确率', verbose=True, return_predict=False,
                         random_state=42, evaluate_fn=None, show_time=False) -> Union[float, tuple[float, list]]:
	"""训练并评估模型（包含数据集切分）
	
	这是train_evaluate的封装版本，增加了数据集切分功能
	
	Args:
		model: 机器学习模型实例
		X: 完整数据特征
		y: 完整数据标签
		test_size: 测试集比例
		describe: 评分描述文字
		verbose: 是否打印评估结果
		return_predict: 是否返回预测结果
		evaluate_fn: 自定义评估函数
		show_time: 是否显示训练耗时
		
	Returns:
		如果return_predict为False，返回评分
		如果return_predict为True，返回(评分, 预测结果)的元组

	Examples
	--------
	>>> import numpy as np
	>>> from sklearn.ensemble import RandomForestClassifier
	>>> from sklearntools import train_evaluate_split
	>>> X, y = np.arange(20).reshape((10, 2)), range(10)
	>>> model = RandomForestClassifier(n_estimators=837, bootstrap=False)
	>>> train_evaluate_split(model, X, y, test_size=0.2)
	0.88
	"""
	X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=random_state)
	return train_evaluate(model, X_train, y_train, X_test, y_test, describe, verbose, return_predict, evaluate_fn, show_time)


def train_metrics(model, X_train, y_train, X_test, y_test, verbose=True, return_predict=False, show_time=False, 
				  additional_metrics: list[str] = None, target_names: list = None):
	"""训练并评估模型
	
	分类器默认使用accuracy_score评分
	回归器默认使用r2_score评分
	
	Args:
		model: 机器学习模型实例
		X_train: 训练数据特征
		y_train: 训练数据标签
		X_test: 测试数据特征
		y_test: 测试数据标签
		verbose: 是否打印评估结果
		return_predict: 是否返回预测结果
		show_time: 是否显示训练耗时
		additional_metrics: 自定义评估指标, 如二分类时'auc', 计算'auc'目标值不是是数值类型
		target_names: 目标名称
	"""
	if show_time:
		start_time = time.perf_counter()
		model.fit(X_train, y_train)
		cost_time = time.perf_counter() - start_time
		logger.info(f'耗时: {cost_time:.2f} seconds.')
	else:
		model.fit(X_train, y_train)

	prediction = model.predict(X_test)

	is_classifier = 'classifier' == model._estimator_type
	if is_classifier:
		metrics_dict = {"auc": roc_auc_score}

		acc = accuracy_score(y_test, prediction)
		if verbose:
			logger.info(f'Accuracy: {acc:.1%}')

		metrics = {"accuracy": acc}
		# 如果是二分类，则计算召回率, F1值, AUC
		if np.unique(y_train).shape[0] == 2:
			precision = precision_score(y_test, prediction, average='macro')
			recall = recall_score(y_test, prediction, average='macro')
			f1 = f1_score(y_test, prediction, average='macro')
			# auc = roc_auc_score(y_test, prediction)

			metrics["precision"] = precision
			metrics["recall"] = recall
			metrics["f1"] = f1

			if verbose:
				logger.info(f'Precision: {precision:.1%}')
				logger.info(f'Recall: {recall:.1%}')
				logger.info(f'F1: {f1:.1%}')
		
		if additional_metrics:
			for metric in additional_metrics:
				metrics[metric] = metrics_dict[metric](y_test, prediction)
				if verbose:
					logger.info(f'{metric}: {metrics[metric]:.1%}')

		if verbose:
			logger.info(f"Classification report:\n{classification_report(y_test, prediction, target_names=target_names)}")
		
		if return_predict:
			return metrics, prediction
		return metrics
	else:
		mae = mean_absolute_error(y_test, prediction)
		mse = mean_squared_error(y_test, prediction)
		rmse = np.sqrt(mse)
		r2 = r2_score(y_test, prediction)
		metrics = {"mae": mae, "mse": mse, "rmse": rmse, "r2": r2}

		if verbose:
			logger.info(f'MAE: {mae:.2f}')
			logger.info(f'MSE: {mse:.2f}')
			logger.info(f'RMSE: {rmse:.2f}')
			logger.info(f'R2: {r2:.2f}')

		if  return_predict:
			return metrics, prediction
		return metrics


def train_metrics_split(model, X, y, test_size=0.2, verbose=True, return_predict=False, random_state=42, 
						show_time=False, additional_metrics: list[str] = None, target_names: list = None):
	"""训练并评估模型（包含数据集切分）
	
	这是train_metrics的封装版本，增加了数据集切分功能
	
	Args:
		model: 机器学习模型实例
		X: 完整数据特征
		y: 完整数据标签
		test_size: 测试集比例
		verbose: 是否打印评估结果
		return_predict: 是否返回预测结果
		random_state: 随机种子
		show_time: 是否显示训练耗时
		additional_metrics: 自定义评估指标, 如二分类时'auc', 计算'auc'目标值不是是数值类型
		target_names: 目标名称
	"""
	X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=random_state)
	return train_metrics(model, X_train, y_train, X_test, y_test, verbose, return_predict, show_time, additional_metrics, target_names)
	

def search_model_params(model_class, X_train, y_train, X_test, y_test, param_grid, num_results=5, num_iter=8,
                        n_jobs: int = None, executor: ProcessPoolExecutor = None, verbose=False) -> list[dict]:
	"""搜索模型最优参数
	
	使用网格搜索方法寻找模型的最优参数组合
	
	Args:
		model_class: 模型类
		X_train: 训练数据特征
		y_train: 训练数据标签
		X_test: 测试数据特征
		y_test: 测试数据标签
		param_grid: 参数网格，字典形式
		num_results: 返回的最优参数组合数量
		num_iter: 每组参数的重复验证次数
		n_jobs: 并行进程数
		executor: 进程池执行器
		verbose: 是否打印评估结果
		
	Returns:
		最优参数组合列表

	Examples
	--------
	>>> import numpy as np
	>>> from sklearn.ensemble import RandomForestClassifier
	>>> from sklearn.model_selection import train_test_split
	>>> X, y = np.arange(20).reshape((10, 2)), range(10)
	>>> X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3)
	>>> param_grid = {'n_estimators': np.arange(800, 820, 1), 'bootstrap': [False, True]}
	>>> search_model_params(RandomForestClassifier, X_train, y_train, X_test, y_test, param_grid, num_results=3)
	[{'bootstrap': False, 'n_estimators': 565}]
	"""
	sub_n_jobs = None
	classifier = 'classifier' == model_class._estimator_type
	param_grid = ParameterGrid(param_grid)
	n_task = len(param_grid)
	logger.info(f'search_model_params 任务数: {n_task}')
	if executor is None:
		n_jobs = get_processes(n_jobs, n_task, 'search_model_params')
		if 1 == n_jobs:
			sub_n_jobs = 1
			results = [_search_params(model_class, classifier, X_train, y_train, X_test, y_test, params, verbose) for params in param_grid]
		else:
			with ProcessPoolExecutor(n_jobs) as e:
				futures = [e.submit(_search_params, model_class, classifier, X_train, y_train, X_test, y_test, params, verbose) for
				           params in param_grid]
				results = [f.result() for f in as_completed(futures)]
	else:
		futures = [executor.submit(_search_params, model_class, classifier, X_train, y_train, X_test, y_test, params, verbose) for
		           params in param_grid]
		results = [f.result() for f in as_completed(futures)]

	results.sort(key=lambda x: x[1], reverse=True)
	params = []
	for param, score in results[:num_results]:
		params.append(param)
		if classifier:
			logger.info(f'param: {param}\tscore: {score:.1%}')
		else:
			logger.info(f'param: {param}\tscore: {score:.4f}')
		_evaluate_params(model_class, classifier, X_train, y_train, X_test, y_test, param, num_iter, sub_n_jobs, executor)
	return params


def search_model_params_split(model_class, X, y, param_grid, test_size=0.2, num_results=5, num_iter=8, random_state=42,
                              n_jobs: int = None, executor: ProcessPoolExecutor = None, verbose=False) -> list[dict]:
	"""搜索模型最优参数
	
	使用网格搜索方法寻找模型的最优参数组合
	
	Args:
		model_class: 模型类
		X: 完整数据特征
		y: 完整数据标签
		param_grid: 参数网格，字典形式
		test_size: 测试集比例
		num_results: 返回的最优参数组合数量
		num_iter: 每组参数的重复验证次数
		random_state: 随机种子
		n_jobs: 并行进程数
		executor: 进程池执行器
		verbose: 是否打印评估结果
		
	Returns:
		最优参数组合列表

	Examples
	--------
	>>> import numpy as np
	>>> from sklearn.ensemble import RandomForestClassifier
	>>> X, y = np.arange(20).reshape((10, 2)), range(10)
	>>> param_grid = {'n_estimators': np.arange(800, 820, 1), 'bootstrap': [False, True]}
	>>> search_model_params_split(RandomForestClassifier, X, y, param_grid, test_size=0.2, num_results=3)
	[{'bootstrap': False, 'n_estimators': 565}]
	"""
	X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=random_state)
	return search_model_params(model_class, X_train, y_train, X_test, y_test, param_grid, num_results, num_iter, n_jobs, executor, verbose)


def search_test_size(model, X, y, test_sizes=np.arange(0.15, 0.36, 0.01), random_state=42, evaluate_fn=None,
                     n_jobs: int = None, topK=5, executor: ProcessPoolExecutor = None, verbose=False) -> float:
	"""
	Examples
	--------
	>>> search_test_size(model, X, y, random_state=42, evaluate_fn=accuracy_score)
	0.2
	"""
	classifier = 'classifier' == model._estimator_type
	n_task = len(test_sizes)
	logger.info(f'search_test_size 任务数: {n_task}')
	if executor is None:
		n_jobs = get_processes(n_jobs, n_task, 'search_test_size')
		if 1 == n_jobs:
			results = [_search_test_size(model, X, y, test_size, random_state, evaluate_fn, verbose) for test_size in test_sizes]
		else:
			with ProcessPoolExecutor(n_jobs) as e:
				futures = [e.submit(_search_test_size, model, X, y, test_size, random_state, evaluate_fn, verbose) for
				           test_size in test_sizes]
				results = [f.result() for f in as_completed(futures)]
	else:
		futures = [executor.submit(_search_test_size, model, X, y, test_size, random_state, evaluate_fn, verbose) for
		           test_size in test_sizes]
		results = [f.result() for f in as_completed(futures)]
	results.sort(key=lambda x: x[1], reverse=True)

	if classifier:
		for i, (test_size, score) in enumerate(results[:topK], 1):
			if i < topK:
				logger.info(f'test_size: {test_size:.0%} \t score: {score:.2%}')
			else:
				logger.info(f'test_size: {test_size:.0%} \t score: {score:.2%}\n')
	else:
		for i, (test_size, score) in enumerate(results[:topK], 1):
			if i < topK:
				logger.info(f'test_size: {test_size:.0%} \t score: {score:4f}')
			else:
				logger.info(f'test_size: {test_size:.0%} \t score: {score:4f}')
	return results[0][0]


def search_random_state(model, X, y, random_states=np.arange(0, 20, 1), test_size=0.2, evaluate_fn=None,
                        n_jobs: int = None, topK=5, executor: ProcessPoolExecutor = None, verbose=False) -> int:
	"""
	Examples
	--------
	>>> from sklearntools import search_random_state
	>>> search_random_state(model, X, y, test_size=0.2, evaluate_fn=accuracy_score)
	42
	"""
	classifier = 'classifier' == model._estimator_type
	n_task = len(random_states)
	logger.info(f'search_random_state 任务数: {n_task}')
	if executor is None:
		n_jobs = get_processes(n_jobs, n_task, 'search_random_state')
		if 1 == n_jobs:
			results = [_search_random_state(model, X, y, test_size, random_state, evaluate_fn, verbose) for random_state in random_states]
		else:
			with ProcessPoolExecutor(n_jobs) as e:
				futures = [e.submit(_search_random_state, model, X, y, test_size, random_state, evaluate_fn, verbose) for
				           random_state in random_states]
				results = [f.result() for f in as_completed(futures)]
	else:
		futures = [executor.submit(_search_random_state, model, X, y, test_size, random_state, evaluate_fn, verbose) for
		           random_state in random_states]
		results = [f.result() for f in as_completed(futures)]
	results.sort(key=lambda x: x[1], reverse=True)

	if classifier:
		for i, (random_state, score) in enumerate(results[:topK], 1):
			if i < topK:
				logger.info(f'random_state: {random_state} \t score: {score:.2%}')
			else:
				logger.info(f'random_state: {random_state} \t score: {score:.2%}\n')
	else:
		for i, (random_state, score) in enumerate(results[:topK], 1):
			if i < topK:
				logger.info(f'random_state: {random_state} \t score: {score:4f}')
			else:
				logger.info(f'random_state: {random_state} \t score: {score:4f}\n')
	return results[0][0]


def _search_test_size(model, X, y, test_size, random_state, evaluate_fn, verbose=False):
	if verbose:
		pid = os.getpid()
		logger.info(f"进程：{pid} 开始 search_test_size test_size: {test_size:.2f}")
		start_time = time.perf_counter()
	result = train_evaluate_split(model, X, y, test_size, None, False, False, random_state, evaluate_fn)
	if verbose:
		logger.info(f"进程：{pid} 结束 search_test_size 耗时: {(time.perf_counter()-start_time):.2f} seconds.")
	return test_size, result


def _search_random_state(model, X, y, test_size, random_state, evaluate_fn, verbose=False):
	if verbose:
		pid = os.getpid()
		logger.info(f"进程：{pid} 开始 search_random_state random_state: {random_state}")
		start_time = time.perf_counter()
	result = train_evaluate_split(model, X, y, test_size, None, False, False, random_state, evaluate_fn)
	if verbose:
		logger.info(f"进程：{pid} 结束 search_random_state 耗时: {(time.perf_counter()-start_time):.2f} seconds.")
	return random_state, result


def _search_params(model_class, classifier, X_train, y_train, X_test, y_test, params, verbose=False):
	if verbose:
		pid = os.getpid()
		logger.info(f"进程：{pid} 开始 search_params params: {params}")
		start_time = time.perf_counter()
	model = model_class(**params)
	model.fit(X_train, y_train)
	score = model.score(X_test, y_test)
	if not classifier:
		score = round(score, 4)
	if verbose:
		logger.info(f"进程：{pid} 结束 search_params 耗时: {(time.perf_counter()-start_time):.2f} seconds.")
	return params, score


def _evaluate_params(model_class, classifier, X_train, y_train, X_test, y_test, params, num_iter, n_jobs,
                     executor: ProcessPoolExecutor = None, verbose=False):
	if executor is None:
		n_jobs = get_processes(n_jobs, num_iter, 'evaluate_params')
		if 1 == n_jobs:
			results = [_search_params(model_class, classifier, X_train, y_train, X_test, y_test, params, verbose) for _ in range(num_iter)]
		else:
			with ProcessPoolExecutor(n_jobs) as e:
				futures = [e.submit(
					_search_params, model_class, classifier, X_train, y_train, X_test, y_test, params, verbose) for _ in range(num_iter)
				]
				results = [f.result() for f in as_completed(futures)]
	else:
		futures = [executor.submit(
			_search_params, model_class, classifier, X_train, y_train, X_test, y_test, params, verbose) for _ in range(num_iter)
		]
		results = [f.result() for f in as_completed(futures)]
		
	results = [result[1] for result in results]
	mean_score = sum(results) / len(results)
	
	counter = Counter(results)
	results = sorted(counter.items(), key=lambda x: x[0], reverse=True)
	if classifier:
		for score, count in results:
			logger.info(f'\tscore: {score:.1%}\tcount: {count}')
		logger.info(f'平均准确率: {mean_score:.1%}\n')
	else:
		for score, count in results:
			logger.info(f'\tscore: {score:.4f}\tcount: {count}')
		logger.info(f'平均分数: {mean_score:.4f}\n')


def multi_round_evaluate(X: np.ndarray, y: np.ndarray, *models, executor: ProcessPoolExecutor = None, verbose=False, **kwargs):
	""" 对比多个模型的多轮评分

	Args:
		models: 机器学习模型实例, 至少一个
		X: 完整数据特征
		y: 完整数据标签

	Examples
	--------
	>>> from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
	>>> multi_round_evaluate(df.values, y, RandomForestClassifier(), GradientBoostingClassifier(), num_rounds=10, test_size=0.2)
	"""
	assert len(models) >= 1, 'models must be'
	num_rounds = kwargs.pop('num_rounds') if 'num_rounds' in kwargs else 100
	test_size = kwargs.pop('test_size') if 'test_size' in kwargs else 0.2
	if executor is None:
		n_jobs = kwargs.pop('n_jobs') if 'n_jobs' in kwargs else None
		n_jobs = get_processes(n_jobs, num_rounds, 'multi_round_evaluate')
		with ProcessPoolExecutor(n_jobs) as e:
			futures = [e.submit(one_round_evaluate, X, y, test_size, *models) for _ in range(num_rounds)]
			results = [f.result() for f in as_completed(futures)]
	else:
		futures = [executor.submit(one_round_evaluate, X, y, test_size, *models, verbose=verbose) for _ in range(num_rounds)]
		results = [f.result() for f in as_completed(futures)]
	results = np.array(results)
	return results.mean(axis=0)


def one_round_evaluate(X: np.ndarray, y: np.ndarray, test_size: float, *models, verbose=False) -> float:
	""" 对比多个模型的单轮评分

	Args:
		models: 机器学习模型实例, 至少一个
		X: 完整数据特征
		y: 完整数据标签

	Examples
	--------
	>>> from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
	>>> one_round_evaluate(df.values, y, 0.2, RandomForestClassifier(), GradientBoostingClassifier())
	"""
	if verbose:
		pid = os.getpid()
		logger.info(f"进程：{pid} 开始 one_round_evaluate")
	scores = []
	X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=11)
	for i, model in enumerate(models):
		model.fit(X_train, y_train)
		scores.append(model.score(X_test, y_test))
	if verbose:
		logger.info(f"进程：{pid} 开始 one_round_evaluate")
	return scores


def get_processes(n_jobs, n_task, fn_name: str):
	"""确定并行处理的进程数
	
	根据CPU核心数、任务数和用户指定进程数，计算实际使用的进程数
	
	Args:
		n_jobs: 用户指定的进程数
		n_task: 总任务数
		fn_name: 函数名称(用于日志)
	
	Returns:
		实际使用的进程数
	"""
	cpu_count = os.cpu_count()
	n_jobs = min(n_jobs, cpu_count, n_task) if n_jobs else min(cpu_count, n_task)
	logger.info(f'{fn_name} 进程数: {n_jobs}')
	return n_jobs
