"""Local blood pressure regression training script with MLflow logging."""

from __future__ import annotations

import argparse
from pathlib import Path

import mlflow
import mlflow.sklearn
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.multioutput import MultiOutputRegressor

from utils import available_feature_columns, safe_train_test_split, save_regression_prediction_plot


def train(features_csv: str, experiment_name: str = "CardioTwin BP Regression") -> pd.DataFrame:
    df = pd.read_csv(features_csv)
    feature_cols = available_feature_columns(df)
    target_cols = [col for col in ["systolic_bp", "diastolic_bp"] if col in df.columns]

    X = df[feature_cols].fillna(0.0)
    y = df[target_cols].astype(float)
    X_train, X_test, y_train, y_test = safe_train_test_split(X, y)

    models = {
        "Linear Regression": LinearRegression(),
        "Random Forest Regressor": RandomForestRegressor(n_estimators=150, random_state=42),
        "Gradient Boosting Regressor": MultiOutputRegressor(GradientBoostingRegressor(random_state=42)),
    }

    mlflow.set_experiment(experiment_name)
    results = []
    artifact_dir = Path("reports/artifacts")

    for model_name, model in models.items():
        with mlflow.start_run(run_name=model_name):
            model.fit(X_train, y_train)
            predictions = model.predict(X_test)

            rmse = float(np.sqrt(mean_squared_error(y_test, predictions)))
            metrics = {
                "mae": mean_absolute_error(y_test, predictions),
                "rmse": rmse,
                "r2_score": r2_score(y_test, predictions, multioutput="variance_weighted"),
            }
            mlflow.log_params(model.get_params())
            mlflow.log_metrics(metrics)
            mlflow.sklearn.log_model(model, artifact_path="model")

            plot_path = artifact_dir / f"{model_name.lower().replace(' ', '_')}_prediction_plot.png"
            save_regression_prediction_plot(y_test, predictions, target_cols, plot_path)
            mlflow.log_artifact(str(plot_path))

            results.append({"model_name": model_name, **metrics})

    return pd.DataFrame(results).sort_values("rmse", ascending=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train CardioTwin blood pressure regression models.")
    parser.add_argument("--features-csv", required=True, help="Path to engineered features CSV.")
    parser.add_argument("--experiment-name", default="CardioTwin BP Regression")
    args = parser.parse_args()
    print(train(args.features_csv, args.experiment_name).to_string(index=False))
