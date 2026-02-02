"""
Módulo de treino do modelo.

Inclui:
- Treino simples com early stopping
- K-Fold Cross Validation
- Métricas detalhadas
- Logging de progresso

Versão (prof): 3 inputs -> turbidez + pH + temperatura
Outputs: ajuste fotoperíodo, TPA%, alimentação%
"""
import json
import time
from typing import Dict, List, Tuple

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader

from .config import (
    DEVICE, EPOCHS, LEARNING_RATE, PATIENCE, K_FOLDS,
    MODEL_PATH, METRICS_PATH, RANDOM_SEED, SCALER_PATH
)
from .model import AquaSenseNet, PhotoperiodNet, BaselineModel
from .data_loader import prepare_data, create_dataloaders, StandardScaler


class EarlyStopping:
    """Implementação de Early Stopping."""

    def __init__(self, patience: int = PATIENCE, min_delta: float = 1e-4):
        self.patience = patience
        self.min_delta = min_delta
        self.counter = 0
        self.best_loss = float("inf")
        self.should_stop = False

    def __call__(self, val_loss: float) -> bool:
        if val_loss < self.best_loss - self.min_delta:
            self.best_loss = val_loss
            self.counter = 0
        else:
            self.counter += 1
            if self.counter >= self.patience:
                self.should_stop = True
        return self.should_stop


def train_epoch(
    model: nn.Module,
    train_loader: DataLoader,
    criterion: nn.Module,
    optimizer: optim.Optimizer
) -> float:
    """Treina uma época."""
    model.train()
    total_loss = 0.0
    n_samples = 0

    for X_batch, y_batch in train_loader:
        X_batch = X_batch.to(DEVICE)
        y_batch = y_batch.to(DEVICE)

        optimizer.zero_grad()
        outputs = model(X_batch)
        loss = criterion(outputs, y_batch)
        loss.backward()
        optimizer.step()

        total_loss += loss.item() * X_batch.size(0)
        n_samples += X_batch.size(0)

    return total_loss / n_samples


def validate(
    model: nn.Module,
    val_loader: DataLoader,
    criterion: nn.Module
) -> Tuple[float, Dict[str, float]]:
    """Valida o modelo e calcula métricas."""
    model.eval()
    total_loss = 0.0
    n_samples = 0

    all_preds = []
    all_labels = []

    with torch.no_grad():
        for X_batch, y_batch in val_loader:
            X_batch = X_batch.to(DEVICE)
            y_batch = y_batch.to(DEVICE)

            outputs = model(X_batch)
            loss = criterion(outputs, y_batch)

            total_loss += loss.item() * X_batch.size(0)
            n_samples += X_batch.size(0)

            all_preds.append(outputs.cpu().numpy())
            all_labels.append(y_batch.cpu().numpy())

    avg_loss = total_loss / max(1, n_samples)

    preds = np.vstack(all_preds)
    labels = np.vstack(all_labels)

    metrics = calculate_metrics(preds, labels)
    metrics["loss"] = float(avg_loss)

    return float(avg_loss), metrics


def calculate_metrics(preds: np.ndarray, labels: np.ndarray) -> Dict[str, float]:
    """
    Calcula métricas de regressão para as 3 saídas.

    preds/labels shape: (n_samples, 3)
    [0] ajuste (horas)   -> *12
    [1] TPA%             -> *100
    [2] alimentação%     -> *100
    """
    # Desnormalizar
    preds_adj_h = preds[:, 0] * 12.0
    labels_adj_h = labels[:, 0] * 12.0

    preds_tpa = preds[:, 1] * 100.0
    labels_tpa = labels[:, 1] * 100.0

    preds_feed = preds[:, 2] * 100.0
    labels_feed = labels[:, 2] * 100.0

    # Métricas globais (no espaço normalizado)
    mse = float(np.mean((preds - labels) ** 2))
    mae = float(np.mean(np.abs(preds - labels)))
    rmse = float(np.sqrt(mse))

    # R² global (normalizado)
    ss_res = float(np.sum((labels - preds) ** 2))
    ss_tot = float(np.sum((labels - np.mean(labels, axis=0)) ** 2))
    r2 = float(1 - (ss_res / ss_tot)) if ss_tot > 0 else 0.0

    # Por saída (em unidades reais)
    # Ajuste (horas)
    mae_adj = float(np.mean(np.abs(preds_adj_h - labels_adj_h)))
    acc_1h = float(np.mean(np.abs(preds_adj_h - labels_adj_h) < 1) * 100.0)
    acc_2h = float(np.mean(np.abs(preds_adj_h - labels_adj_h) < 2) * 100.0)

    # TPA (%)
    mae_tpa = float(np.mean(np.abs(preds_tpa - labels_tpa)))
    acc_tpa_5 = float(np.mean(np.abs(preds_tpa - labels_tpa) < 5) * 100.0)
    acc_tpa_10 = float(np.mean(np.abs(preds_tpa - labels_tpa) < 10) * 100.0)

    # Alimentação (%)
    mae_feed = float(np.mean(np.abs(preds_feed - labels_feed)))
    acc_feed_10 = float(np.mean(np.abs(preds_feed - labels_feed) < 10) * 100.0)

    return {
        "mse": mse,
        "mae": mae,     # MAE global normalizado (não é "h")
        "rmse": rmse,
        "r2": r2,

        "mae_photoperiod": mae_adj,
        "accuracy_1h": acc_1h,
        "accuracy_2h": acc_2h,

        "mae_tpa": mae_tpa,
        "accuracy_tpa_5pct": acc_tpa_5,
        "accuracy_tpa_10pct": acc_tpa_10,

        "mae_feeding": mae_feed,
        "accuracy_feed_10pct": acc_feed_10,
    }


def train_model(
    epochs: int = EPOCHS,
    lr: float = LEARNING_RATE,
    patience: int = PATIENCE,
    verbose: bool = True
) -> Tuple[PhotoperiodNet, Dict[str, object]]:
    """
    Treina o modelo com early stopping.
    """
    print("=" * 60)
    print("TREINO DO MODELO (3 sensores)")
    print("=" * 60)

    X_train, X_test, y_train, y_test, _scaler = prepare_data()

    # Split train/val
    split = int(len(X_train) * 0.8)
    X_tr, X_val = X_train[:split], X_train[split:]
    y_tr, y_val = y_train[:split], y_train[split:]

    train_loader, val_loader = create_dataloaders(X_tr, y_tr, X_val, y_val)

    model = AquaSenseNet().to(DEVICE)

    # Evitar rebentar se não tiver summary()/count_parameters()
    if hasattr(model, "summary"):
        try:
            print(f"\n{model.summary()}")
        except Exception:
            pass
    print(f"Device: {DEVICE}")

    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=lr)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode="min", factor=0.5, patience=20
    )

    early_stopping = EarlyStopping(patience=patience)

    history: Dict[str, object] = {
        "train_loss": [],
        "val_loss": [],
        "val_metrics": [],
        "lr": []
    }

    best_model_state = None
    best_val_loss = float("inf")
    start_time = time.time()

    print(f"\nA treinar (máx {epochs} épocas, early stopping após {patience} sem melhoria)...\n")

    for epoch in range(1, epochs + 1):
        train_loss = train_epoch(model, train_loader, criterion, optimizer)
        val_loss, val_metrics = validate(model, val_loader, criterion)

        scheduler.step(val_loss)
        current_lr = float(optimizer.param_groups[0]["lr"])

        history["train_loss"].append(float(train_loss))
        history["val_loss"].append(float(val_loss))
        history["val_metrics"].append(val_metrics)
        history["lr"].append(current_lr)

        if val_loss < best_val_loss:
            best_val_loss = float(val_loss)
            best_model_state = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}

        # Log (correto: horas para fotoperíodo, % para TPA/feeding)
        if verbose and (epoch % 50 == 0 or epoch == 1):
            print(
                f"Época {epoch:4d} | "
                f"Train: {train_loss:.4f} | Val: {val_loss:.4f} | "
                f"Adj MAE: {val_metrics['mae_photoperiod']:.2f}h | "
                f"TPA MAE: {val_metrics['mae_tpa']:.1f}% | "
                f"Feed MAE: {val_metrics['mae_feeding']:.1f}% | "
                f"R²: {val_metrics['r2']:.3f}"
            )

        if early_stopping(val_loss):
            print(f"\n[Early Stopping] Parou na época {epoch}")
            break

    elapsed = float(time.time() - start_time)

    if best_model_state is not None:
        model.load_state_dict(best_model_state)

    # Avaliação final no test set
    test_loader, _ = create_dataloaders(X_test, y_test)
    _, test_metrics = validate(model, test_loader, criterion)

    # Guardar modelo (state_dict)
    torch.save(model.state_dict(), MODEL_PATH)

    # Guardar métricas
    model_params = None
    if hasattr(model, "count_parameters"):
        try:
            model_params = int(model.count_parameters())
        except Exception:
            model_params = None

    final_metrics = {
        "epochs_trained": int(epoch),
        "training_time_seconds": elapsed,
        "best_val_loss": float(best_val_loss),
        "test_metrics": test_metrics,
        "model_params": model_params
    }

    with open(METRICS_PATH, "w", encoding="utf-8") as f:
        json.dump(final_metrics, f, indent=2, ensure_ascii=False)

    print(f"\n{'=' * 60}")
    print("RESULTADOS FINAIS")
    print("=" * 60)
    print(f"Épocas treinadas: {epoch}")
    print(f"Tempo de treino: {elapsed:.1f}s")
    print(f"Melhor Val Loss: {best_val_loss:.4f}")

    print("\nMétricas no Test Set:")
    print(f"  MSE global (norm):  {test_metrics['mse']:.4f}")
    print(f"  R² global (norm):   {test_metrics['r2']:.3f}")

    print("\n  Ajuste fotoperíodo:")
    print(f"    MAE: {test_metrics['mae_photoperiod']:.2f}h")
    print(f"    Accuracy (<1h): {test_metrics['accuracy_1h']:.1f}%")
    print(f"    Accuracy (<2h): {test_metrics['accuracy_2h']:.1f}%")

    print("\n  TPA:")
    print(f"    MAE: {test_metrics['mae_tpa']:.1f}%")
    print(f"    Accuracy (<5%): {test_metrics['accuracy_tpa_5pct']:.1f}%")
    print(f"    Accuracy (<10%): {test_metrics['accuracy_tpa_10pct']:.1f}%")

    print("\n  Alimentação:")
    print(f"    MAE: {test_metrics['mae_feeding']:.1f}%")
    print(f"    Accuracy (<10%): {test_metrics['accuracy_feed_10pct']:.1f}%")

    print(f"\nModelo guardado: {MODEL_PATH}")
    print(f"Métricas guardadas: {METRICS_PATH}")

    history["final_metrics"] = final_metrics
    return model, history


def cross_validate(k_folds: int = K_FOLDS) -> Dict[str, object]:
    """
    K-Fold Cross Validation.
    """
    print("=" * 60)
    print(f"K-FOLD CROSS VALIDATION (K={k_folds})")
    print("=" * 60)

    X_train, _X_test, y_train, _y_test, _scaler = prepare_data()

    X = X_train
    y = y_train

    fold_size = len(X) // k_folds
    all_metrics: List[Dict[str, float]] = []

    for fold in range(k_folds):
        print(f"\n--- Fold {fold + 1}/{k_folds} ---")

        val_start = fold * fold_size
        val_end = val_start + fold_size if fold < k_folds - 1 else len(X)

        X_val = X[val_start:val_end]
        y_val = y[val_start:val_end]
        X_tr = np.vstack([X[:val_start], X[val_end:]])
        y_tr = np.vstack([y[:val_start], y[val_end:]])

        train_loader, val_loader = create_dataloaders(X_tr, y_tr, X_val, y_val)

        model = AquaSenseNet().to(DEVICE)
        criterion = nn.MSELoss()
        optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)
        early_stopping = EarlyStopping(patience=PATIENCE)

        best_val_loss = float("inf")
        best_metrics: Dict[str, float] = {}

        for epoch in range(1, EPOCHS + 1):
            _ = train_epoch(model, train_loader, criterion, optimizer)
            val_loss, metrics = validate(model, val_loader, criterion)

            if val_loss < best_val_loss:
                best_val_loss = float(val_loss)
                best_metrics = metrics.copy()

            if early_stopping(val_loss):
                break

        print(
            f"  Épocas: {epoch} | "
            f"Adj MAE: {best_metrics.get('mae_photoperiod', 0):.2f}h | "
            f"TPA MAE: {best_metrics.get('mae_tpa', 0):.1f}% | "
            f"Feed MAE: {best_metrics.get('mae_feeding', 0):.1f}% | "
            f"R²: {best_metrics.get('r2', 0):.3f}"
        )
        all_metrics.append(best_metrics)

    avg_metrics: Dict[str, float] = {}
    std_metrics: Dict[str, float] = {}

    keys = list(all_metrics[0].keys()) if all_metrics else []
    for key in keys:
        values = [m[key] for m in all_metrics]
        avg_metrics[key] = float(np.mean(values))
        std_metrics[key] = float(np.std(values))

    print(f"\n{'=' * 60}")
    print("RESULTADOS K-FOLD (média ± std)")
    print("=" * 60)
    print(f"Adj MAE:  {avg_metrics.get('mae_photoperiod', 0):.2f} ± {std_metrics.get('mae_photoperiod', 0):.2f}h")
    print(f"TPA MAE:  {avg_metrics.get('mae_tpa', 0):.1f} ± {std_metrics.get('mae_tpa', 0):.1f}%")
    print(f"Feed MAE: {avg_metrics.get('mae_feeding', 0):.1f} ± {std_metrics.get('mae_feeding', 0):.1f}%")
    print(f"R²:       {avg_metrics.get('r2', 0):.3f} ± {std_metrics.get('r2', 0):.3f}")

    return {
        "folds": int(k_folds),
        "fold_metrics": all_metrics,
        "avg_metrics": avg_metrics,
        "std_metrics": std_metrics
    }


def compare_with_baseline() -> Dict[str, object]:
    """
    Compara o modelo neural com o baseline de regras (3 sensores).

    Nota: se os labels/GT forem gerados pelas mesmas regras, o baseline tende a ser perfeito.
    Aqui comparamos erros absolutos NN vs baseline sobre o mesmo GT.
    """
    print("\n" + "=" * 60)
    print("COMPARAÇÃO: REDE NEURAL vs BASELINE (REGRAS) — 3 sensores")
    print("=" * 60)

    # Carregar modelo
    model = AquaSenseNet().to(DEVICE)
    model.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE, weights_only=True))
    model.eval()

    # Carregar scaler (para inputs comparáveis ao treino)
    scaler = StandardScaler()
    scaler.load(SCALER_PATH)

    np.random.seed(RANDOM_SEED + 100)
    n_test = 500

    nn_err_adj: List[float] = []
    nn_err_tpa: List[float] = []
    nn_err_feed: List[float] = []

    # Baseline vs GT (deve dar 0.0 se GT = regras)
    bl_err_adj: List[float] = []
    bl_err_tpa: List[float] = []
    bl_err_feed: List[float] = []

    for _ in range(n_test):
        turbidity = float(np.random.uniform(0, 100))
        ph = float(np.random.uniform(6.2, 8.0))
        temperature = float(np.random.uniform(20.0, 31.0))

        # Ground truth pelas regras
        gt = BaselineModel.predict(turbidity, ph=ph, temperature=temperature)
        true_adj = float(gt.adjustment_hours)
        true_tpa = float(gt.tpa_percent)
        true_feed = float(gt.feeding_percent)

        # Input escalado
        x_raw = np.array([[turbidity, ph, temperature]], dtype=np.float32)
        x_scaled = scaler.transform(x_raw)
        x = torch.tensor(x_scaled, dtype=torch.float32).to(DEVICE)

        with torch.no_grad():
            out = model(x).squeeze(0)
            nn_adj = float(out[0].item()) * 12.0
            nn_tpa = float(out[1].item()) * 100.0
            nn_feed = float(out[2].item()) * 100.0

        nn_err_adj.append(abs(nn_adj - true_adj))
        nn_err_tpa.append(abs(nn_tpa - true_tpa))
        nn_err_feed.append(abs(nn_feed - true_feed))

        # Baseline vs GT (idealmente 0)
        bl_err_adj.append(abs(true_adj - true_adj))
        bl_err_tpa.append(abs(true_tpa - true_tpa))
        bl_err_feed.append(abs(true_feed - true_feed))

    def summarize(errors: List[float], thr: float) -> Dict[str, float]:
        e = np.array(errors, dtype=float)
        return {
            "mae": float(e.mean()),
            "rmse": float(np.sqrt((e ** 2).mean())),
            "max_error": float(e.max()),
            "accuracy": float((e < thr).mean() * 100.0),
            "thr": float(thr)
        }

    nn_adj_m = summarize(nn_err_adj, 2.0)
    nn_tpa_m = summarize(nn_err_tpa, 10.0)
    nn_feed_m = summarize(nn_err_feed, 10.0)

    print("\nNeural Net (erros vs GT):")
    print(f"  Ajuste: MAE {nn_adj_m['mae']:.2f}h | Acc<{nn_adj_m['thr']:.0f}h {nn_adj_m['accuracy']:.1f}%")
    print(f"  TPA:    MAE {nn_tpa_m['mae']:.1f}% | Acc<{nn_tpa_m['thr']:.0f}% {nn_tpa_m['accuracy']:.1f}%")
    print(f"  Feed:   MAE {nn_feed_m['mae']:.1f}% | Acc<{nn_feed_m['thr']:.0f}% {nn_feed_m['accuracy']:.1f}%")

    print("\nBaseline (regras) vs GT (regras): tende a ser 0 por definição.")
    print("  (isto é normal se o teu dataset sintético/labels vêm das mesmas regras)")

    return {
        "n_samples": int(n_test),
        "neural_net": {"adj": nn_adj_m, "tpa": nn_tpa_m, "feed": nn_feed_m},
        "baseline_note": "Baseline é o mesmo que o GT quando labels vêm das regras."
    }


if __name__ == "__main__":
    _model, _history = train_model()
    _cv_results = cross_validate()
    _comparison = compare_with_baseline()
