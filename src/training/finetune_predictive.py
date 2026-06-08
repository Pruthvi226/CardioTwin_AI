"""Predictive model training for raw PPG windows and SSL embeddings."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import torch
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score
from torch import nn
from torch.utils.data import DataLoader, TensorDataset

from src.models.cnn_lstm import CNNLSTMClassifier
from src.models.ssl_encoder import PPGMaskedAutoencoder


def _train_classifier(
    model: nn.Module,
    x_train: np.ndarray,
    y_train: np.ndarray,
    output_path: Path,
    epochs: int = 3,
    batch_size: int = 64,
    learning_rate: float = 1e-3,
    device: str = "cpu",
) -> nn.Module:
    torch_device = torch.device(device if device == "cuda" and torch.cuda.is_available() else "cpu")
    tensor_x = torch.tensor(x_train, dtype=torch.float32)
    if tensor_x.ndim == 2:
        tensor_x = tensor_x.unsqueeze(1)
    tensor_y = torch.tensor(y_train, dtype=torch.long)
    loader = DataLoader(TensorDataset(tensor_x, tensor_y), batch_size=batch_size, shuffle=True)
    model = model.to(torch_device)
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
    criterion = nn.CrossEntropyLoss()

    model.train()
    for _ in range(max(1, epochs)):
        for batch_x, batch_y in loader:
            batch_x = batch_x.to(torch_device)
            batch_y = batch_y.to(torch_device)
            logits = model(batch_x)
            loss = criterion(logits, batch_y)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    torch.save(model.state_dict(), output_path)
    return model.cpu()


def predict_torch_classifier(model: nn.Module, x_test: np.ndarray, batch_size: int = 128) -> tuple[np.ndarray, np.ndarray]:
    """Return predicted labels and class probabilities for a PyTorch classifier."""
    tensor_x = torch.tensor(x_test, dtype=torch.float32)
    if tensor_x.ndim == 2:
        tensor_x = tensor_x.unsqueeze(1)
    loader = DataLoader(TensorDataset(tensor_x), batch_size=batch_size, shuffle=False)
    model.eval()
    probabilities: list[np.ndarray] = []
    with torch.no_grad():
        for (batch_x,) in loader:
            logits = model(batch_x)
            probabilities.append(torch.softmax(logits, dim=1).cpu().numpy())
    probs = np.concatenate(probabilities, axis=0)
    return probs.argmax(axis=1), probs


def train_cnn_lstm_classifier(
    x_train: np.ndarray,
    y_train: np.ndarray,
    output_dir: str | Path,
    epochs: int = 3,
    batch_size: int = 64,
    learning_rate: float = 1e-3,
    device: str = "cpu",
) -> CNNLSTMClassifier:
    """Train and persist the raw-window CNN-LSTM classifier."""
    model = CNNLSTMClassifier(n_classes=max(2, int(np.max(y_train)) + 1))
    return _train_classifier(
        model,
        x_train,
        y_train,
        Path(output_dir) / "CNNLSTM_raw_windows.pt",
        epochs=epochs,
        batch_size=batch_size,
        learning_rate=learning_rate,
        device=device,
    )


def train_ssl_embedding_classifier(
    ssl_model: PPGMaskedAutoencoder,
    x_train: np.ndarray,
    y_train: np.ndarray,
    x_test: np.ndarray,
) -> tuple[LogisticRegression, np.ndarray, np.ndarray]:
    """Train a logistic classifier on frozen SSL embeddings."""
    ssl_model.eval()
    with torch.no_grad():
        train_embeddings = ssl_model.encoder(torch.tensor(x_train, dtype=torch.float32).unsqueeze(1)).numpy()
        test_embeddings = ssl_model.encoder(torch.tensor(x_test, dtype=torch.float32).unsqueeze(1)).numpy()

    classifier = LogisticRegression(max_iter=1000, class_weight="balanced", random_state=42)
    classifier.fit(train_embeddings, y_train)
    probabilities = classifier.predict_proba(test_embeddings)
    predictions = probabilities.argmax(axis=1)
    return classifier, predictions, probabilities


def metrics_from_predictions(y_true: np.ndarray, y_pred: np.ndarray) -> dict[str, float]:
    """Shared accuracy/F1 metric helper."""
    return {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "f1_score": float(f1_score(y_true, y_pred, average="weighted", zero_division=0)),
    }
