Usage Sample
''''''''''''

.. code:: python

    import numpy as np
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import train_test_split
    from sklearntools import train_evaluate, search_model_params

    X, y = np.arange(20).reshape((10, 2)), range(10)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3)

    model = RandomForestClassifier(n_estimators=837, bootstrap=False)
    train_evaluate(model, X_train, X_test, y_train, y_test)

    param_grid = {'n_estimators': np.arange(800, 820, 1), 'bootstrap': [False, True]}
    search_model_params(RandomForestClassifier, X_train, X_test, y_train, y_test, param_grid, num_results=3)
