import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import accuracy_score, f1_score, r2_score

df = pd.read_csv('AutoInsurance.csv')
# 删除INDEX列
df.drop(columns=['INDEX'], inplace=True)

X = df.drop(columns=['TARGET_FLAG', 'TARGET_AMT']).to_numpy()
y = df['TARGET_FLAG'].to_numpy()

# 拆分数据集为训练集和测试集，测试集比例为20%，设置随机种子确保结果可复现
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=63)

# 优化前
# 初始化模型
model = RandomForestClassifier()
# 使用训练集数据拟合模型
model.fit(X_train, y_train)
# 对测试集进行预测
y_pred = model.predict(X_test)
# 评估模型
print(f"优化前:   准确率: {accuracy_score(y_test, y_pred):.2%} \t F1-score: {f1_score(y_test, y_pred):.2f}")

# 优化后
# 初始化模型，参数调优
model = RandomForestClassifier(n_estimators=745, bootstrap=True)
# 使用训练集数据拟合模型
model.fit(X_train, y_train)
# 对测试集进行预测
y_pred = model.predict(X_test)
# 评估模型
print(f"优化后:   准确率: {accuracy_score(y_test, y_pred):.2%} \t F1-score: {f1_score(y_test, y_pred):.2f}")

# 再次优化
# 初始化模型，参数调优
model = RandomForestClassifier(n_estimators=745, bootstrap=True, random_state=70)
# 使用训练集数据拟合模型
model.fit(X_train, y_train)
# 对测试集进行预测
y_pred = model.predict(X_test)
# 评估模型
print(f"优化后:   准确率: {accuracy_score(y_test, y_pred):.2%} \t F1-score: {f1_score(y_test, y_pred):.2f}")

