"""Local classification training script with MLflow logging."""

from __future__ import annotations

import argparse
from pathlib import Path

import mlflow
import mlflow.sklearn
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score

from utils import (
    available_feature_columns,
    safe_train_test_split,
    save_confusion_matrix_plot,
    save_feature_importance_plot,
)


def train(features_csv: str, experiment_name: str = "CardioTwin Classification") -> pd.DataFrame:
    df = pd.read_csv(features_csv)
    feature_cols = available_feature_columns(df)
    target_col = "cardiovascular_status"

    X = df[feature_cols].fillna(0.0)
    y = df[target_col].astype(int)
    stratify = y if y.value_counts().min() >= 2 else None
    X_train, X_test, y_train, y_test = safe_train_test_split(X, y, stratify=stratify)

    models = {
        "Logistic Regression": LogisticRegression(max_iter=1000, multi_class="auto"),
        "Random Forest Classifier": RandomForestClassifier(n_estimators=120, random_state=42),
        "Gradient Boosting Classifier": GradientBoostingClassifier(random_state=42),
    }

    mlflow.set_experiment(experiment_name)
    results = []
    artifact_dir = Path("reports/artifacts")

    for model_name, model in models.items():
        with mlflow.start_run(run_name=model_name):
            model.fit(X_train, y_train)
            predictions = model.predict(X_test)

            metrics = {
                "accuracy": accuracy_score(y_test, predictions),
                "precision_weighted": precision_score(y_test, predictions, average="weighted", zero_division=0),
                "recall_weighted": recall_score(y_test, predictions, average="weighted", zero_division=0),
                "f1_weighted": f1_score(y_test, predictions, average="weighted", zero_division=0),
            }
            mlflow.log_params(model.get_params())
            mlflow.log_metrics(metrics)
            mlflow.sklearn.log_model(model, artifact_path="model")

            cm_path = artifact_dir / f"{model_name.lower().replace(' ', '_')}_confusion_matrix.png"
            save_confusion_matrix_plot(y_test, predictions, sorted(y.unique()), cm_path, model_name)
            mlflow.log_artifact(str(cm_path))

            if hasattr(model, "feature_importances_"):
                fi_path = artifact_dir / f"{model_name.lower().replace(' ', '_')}_feature_importance.png"
                save_feature_importance_plot(feature_cols, model.feature_importances_, fi_path, model_name)
                mlflow.log_artifact(str(fi_path))

            results.append({"model_name": model_name, **metrics})

    return pd.DataFrame(results).sort_values("f1_weighted", ascending=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train CardioTwin classification models.")
    parser.add_argument("--features-csv", required=True, help="Path to engineered features CSV.")
    parser.add_argument("--experiment-name", default="CardioTwin Classification")
    args = parser.parse_args()
    print(train(args.features_csv, args.experiment_name).to_string(index=False))
