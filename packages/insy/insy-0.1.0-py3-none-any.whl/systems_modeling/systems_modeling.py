import numpy as np

def linear_regression(X, y):
    """
    Կատարում է գծային ռեգրեսիա (Linear Regression)՝ օգտագործելով NumPy գրադարանը։

    :param X: Անկախ փոփոխական(ներ)՝ ցուցակ կամ array-անման կառուցվածք (մեկ կամ մի քանի սյունակով)։
    :param y: Կախված փոփոխական՝ համապատասխան արժեքների ցուցակ կամ array։

    :return: Բաղադրիչներով բառարան (dict), որը ներառում է՝
        - "theta": Գործակիցների վեկտոր (ներառյալ bias/intercept),
        - "predictions": Կանխատեսված արժեքներ տրված X-երի համար,
        - "mae": Միջին բացարձակ սխալ (Mean Absolute Error),
        - "rmse": Արմատական միջին քառակուսի սխալ (Root Mean Square Error)։
"""

    X = np.array(X)
    y = np.array(y)
    X = X.reshape(-1, 1) if X.ndim == 1 else X
    X_b = np.c_[np.ones((X.shape[0], 1)), X]  # ավելացնում ենք bias term (1-երը)

    # Normal Equation (θ = (XᵗX)⁻¹Xᵗy)
    theta = np.linalg.inv(X_b.T @ X_b) @ X_b.T @ y
    predictions = X_b @ theta

    mae = np.mean(np.abs(y - predictions))
    rmse = np.sqrt(np.mean((y - predictions) ** 2))

    return {
        "theta": theta,
        "predictions": predictions,
        "mae": mae,
        "rmse": rmse
    }

def logistic_regression(X, y, lr=0.1, epochs=1000):
    """
    Կատարում է լոգիստիկ ռեգրեսիա (Logistic Regression)՝ օգտագործելով մաքուր NumPy։

    :param X: Անկախ փոփոխական(ներ)՝ ցուցակ կամ array-անման կառուցվածք։
    :param y: Կախված փոփոխական՝ 0 կամ 1 արժեքներով։
    :param lr: Սովորելու արագություն (learning rate), լռելյայն՝ 0.1։
    :param epochs: Իտերացիաների քանակ (քայլերի թիվ), լռելյայն՝ 1000։

    :return: Բառարան (dict), որը պարունակում է՝
        - "theta": Գործակիցների (պարամետրերի) վեկտոր,
        - "predictions": Կանխատեսված դասեր՝ 0 կամ 1,
        - "probabilities": Դասերի հավանականություններ (sigmoid ելք),
        - "accuracy": Ճշգրտություն՝ որպես դասակարգման ճշգրտության միջին։
"""

    X = np.array(X)
    y = np.array(y)
    X = X.reshape(-1, 1) if X.ndim == 1 else X
    X_b = np.c_[np.ones((X.shape[0], 1)), X]

    def sigmoid(z):
        return 1 / (1 + np.exp(-z))

    theta = np.zeros(X_b.shape[1])

    for _ in range(epochs):
        z = X_b @ theta
        h = sigmoid(z)
        gradient = X_b.T @ (h - y) / y.size
        theta -= lr * gradient

    predictions_proba = sigmoid(X_b @ theta)
    predictions = (predictions_proba >= 0.5).astype(int)

    accuracy = np.mean(predictions == y)

    return {
        "theta": theta,
        "predictions": predictions,
        "probabilities": predictions_proba,
        "accuracy": accuracy
    }

def polynomial_regression(X, y, degree=2):
    """
    Կատարում է պոլինոմիալ (ոչ գծային) ռեգրեսիա՝ օգտագործելով NumPy գրադարանը։

    :param X: Անկախ փոփոխական(ներ)՝ ցուցակ կամ array-անման կառուցվածք։
    :param y: Կախված փոփոխական՝ համապատասխան արժեքներով։
    :param degree: Պոլինոմի աստիճանը (օրինակ՝ 2՝ քառակուսի ռեգրեսիա)։

    :return: Բառարան (dict), որը պարունակում է՝
        - "theta": Գործակիցների վեկտոր (ներառյալ հատման անդամը՝ intercept),
        - "predictions": Կանխատեսված արժեքներ տրված X-երի համար,
        - "mae": Միջին բացարձակ սխալ (Mean Absolute Error),
        - "rmse": Արմատական միջին քառակուսի սխալ (Root Mean Square Error)։
"""

    X = np.array(X)
    y = np.array(y)
    X = X.reshape(-1, 1) if X.ndim == 1 else X

    # Ստեղծում ենք պոլինոմիալ ֆիչրներ
    X_poly = np.ones((X.shape[0], 1))
    for d in range(1, degree + 1):
        X_poly = np.c_[X_poly, X ** d]

    theta = np.linalg.inv(X_poly.T @ X_poly) @ X_poly.T @ y
    predictions = X_poly @ theta

    mae = np.mean(np.abs(y - predictions))
    rmse = np.sqrt(np.mean((y - predictions) ** 2))

    return {
        "theta": theta,
        "predictions": predictions,
        "mae": mae,
        "rmse": rmse
    }
