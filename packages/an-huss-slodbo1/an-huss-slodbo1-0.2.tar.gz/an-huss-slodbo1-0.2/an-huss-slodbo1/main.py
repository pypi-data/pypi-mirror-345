def supervised_learning():
    print("hello hi")
    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt
    from sklearn.model_selection import KFold, LeaveOneOut, cross_val_predict
    from sklearn.linear_model import LogisticRegression, LinearRegression
    from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
    from sklearn.metrics import (
        accuracy_score, precision_score, recall_score, r2_score,
        roc_auc_score, roc_curve, confusion_matrix, ConfusionMatrixDisplay
    )
    from sklearn.preprocessing import StandardScaler, OneHotEncoder, LabelEncoder
    from sklearn.compose import ColumnTransformer
    from sklearn.pipeline import Pipeline
    from sklearn.impute import SimpleImputer
    from sklearn.metrics import mean_absolute_error, mean_squared_error

    path = input("Enter path to CSV file: ")
    df = pd.read_csv(path)

    target_col = input("Enter target column name: ")
    X = df.drop(columns=[target_col])
    y = df[target_col]

    is_classification = y.nunique() <= 10 and y.dtype != 'float'

    if is_classification:
        le = LabelEncoder()
        y = le.fit_transform(y)

    print("Choose model:\n1. Logistic Regression\n2. Linear Regression\n3. Decision Tree")
    model_choice = input("Enter 1/2/3: ")

    if model_choice == '1':
        model = LogisticRegression(max_iter=1000)
        model_name = "Logistic Regression"
    elif model_choice == '2':
        model = LinearRegression()
        model_name = "Linear Regression"
    elif model_choice == '3':
        model = DecisionTreeClassifier() if is_classification else DecisionTreeRegressor()
        model_name = "Decision Tree"
    else:
        raise ValueError("Invalid model choice")

    num_features = X.select_dtypes(include=['int64', 'float64']).columns.tolist()
    cat_features = X.select_dtypes(include=['object', 'category', 'bool']).columns.tolist()

    numeric_pipeline = Pipeline([
        ('imputer', SimpleImputer(strategy='mean')),
        ('scaler', StandardScaler())
    ])

    categorical_pipeline = Pipeline([
        ('imputer', SimpleImputer(strategy='most_frequent')),
        ('encoder', OneHotEncoder(handle_unknown='ignore'))
    ])

    preprocessor = ColumnTransformer([
        ('num', numeric_pipeline, num_features),
        ('cat', categorical_pipeline, cat_features)
    ])

    pipeline = Pipeline([
        ('preprocess', preprocessor),
        ('model', model)
    ])

    print("Choose cross-validation:\n1. K-Fold\n2. Leave-One-Out (LOOCV)")
    cv_choice = input("Enter 1 or 2: ")

    if cv_choice == '1':
        k = int(input("Enter number of folds (e.g. 5 or 10): "))
        cv = KFold(n_splits=k, shuffle=True, random_state=42)
    elif cv_choice == '2':
        cv = LeaveOneOut()
    else:
        raise ValueError("Invalid CV choice")

    y_pred = cross_val_predict(pipeline, X, y, cv=cv, method='predict')

    print(f"\n=== {model_name} Performance ===")

    if is_classification:
        acc = accuracy_score(y, y_pred)
        prec = precision_score(y, y_pred, average='weighted', zero_division=0)
        rec = recall_score(y, y_pred, average='weighted', zero_division=0)
        print(f"Accuracy:  {acc:.4f}")
        print(f"Precision: {prec:.4f}")
        print(f"Recall:    {rec:.4f}")

        print("\nConfusion Matrix:")
        cm = confusion_matrix(y, y_pred)
        print(cm)
        disp = ConfusionMatrixDisplay(confusion_matrix=cm)
        disp.plot(cmap='Blues')
        plt.title("Confusion Matrix")
        plt.grid(False)
        plt.show()

        if len(np.unique(y)) == 2:
            y_proba = cross_val_predict(pipeline, X, y, cv=cv, method='predict_proba')[:, 1]
            auc = roc_auc_score(y, y_proba)
            fpr, tpr, _ = roc_curve(y, y_proba)
            print(f"ROC AUC:   {auc:.4f}")
            plt.plot(fpr, tpr, label=f"ROC curve (AUC = {auc:.2f})")
            plt.plot([0, 1], [0, 1], linestyle='--')
            plt.xlabel('False Positive Rate')
            plt.ylabel('True Positive Rate')
            plt.title('ROC Curve')
            plt.legend()
            plt.grid(True)
            plt.show()
    else:
        r2 = r2_score(y, y_pred)
        mae = mean_absolute_error(y, y_pred)
        mse = mean_squared_error(y, y_pred)
        print(f"R2 Score:           {r2:.4f}")
        print(f"Mean Absolute Error: {mae:.4f}")
        print(f"Mean Squared Error:  {mse:.4f}")

