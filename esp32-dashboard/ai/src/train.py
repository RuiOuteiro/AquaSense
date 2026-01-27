"""
Módulo de treino do modelo.

Inclui:
- Treino simples com early stopping
- K-Fold Cross Validation
- Métricas detalhadas
- Logging de progresso
"""
import json
import time
from pathlib import Path
from typing import Dict, List, Tuple, Optional

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader

from .config import (
    DEVICE, EPOCHS, LEARNING_RATE, PATIENCE, K_FOLDS,
    MODEL_PATH, METRICS_PATH, RANDOM_SEED
)
from .model import AquaSenseNet, PhotoperiodNet, BaselineModel
from .data_loader import (
    prepare_data, create_dataloaders, StandardScaler,
    AquaSenseDataset
)


class EarlyStopping:
    """Implementação de Early Stopping."""
    
    def __init__(self, patience: int = PATIENCE, min_delta: float = 1e-4):
        self.patience = patience
        self.min_delta = min_delta
        self.counter = 0
        self.best_loss = float('inf')
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
    
    avg_loss = total_loss / n_samples
    
    # Calcular métricas adicionais (já normalizados, calculate_metrics desnormaliza)
    preds = np.vstack(all_preds)
    labels = np.vstack(all_labels)
    
    metrics = calculate_metrics(preds, labels)
    metrics['loss'] = avg_loss
    
    return avg_loss, metrics


def calculate_metrics(preds: np.ndarray, labels: np.ndarray) -> Dict[str, float]:
    """
    Calcula métricas de regressão para as 3 saídas.
    
    preds/labels shape: (n_samples, 3)
    [0] fotoperíodo (desnormalizado para horas)
    [1] TPA% (desnormalizado para 0-100)
    [2] alimentação% (desnormalizado para 0-100)
    """
    # Desnormalizar
    preds_photo = preds[:, 0] * 12
    labels_photo = labels[:, 0] * 12
    preds_tpa = preds[:, 1] * 100
    labels_tpa = labels[:, 1] * 100
    preds_feed = preds[:, 2] * 100
    labels_feed = labels[:, 2] * 100
    
    # Métricas globais (média das 3 saídas normalizadas)
    mse = np.mean((preds - labels) ** 2)
    mae = np.mean(np.abs(preds - labels))
    rmse = np.sqrt(mse)
    
    # R² global
    ss_res = np.sum((labels - preds) ** 2)
    ss_tot = np.sum((labels - np.mean(labels, axis=0)) ** 2)
    r2 = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
    
    # Métricas por saída
    # Fotoperíodo
    mae_photo = np.mean(np.abs(preds_photo - labels_photo))
    acc_1h = np.mean(np.abs(preds_photo - labels_photo) < 1) * 100
    acc_2h = np.mean(np.abs(preds_photo - labels_photo) < 2) * 100
    
    # TPA
    mae_tpa = np.mean(np.abs(preds_tpa - labels_tpa))
    acc_tpa_5 = np.mean(np.abs(preds_tpa - labels_tpa) < 5) * 100
    
    # Alimentação
    mae_feed = np.mean(np.abs(preds_feed - labels_feed))
    acc_feed_10 = np.mean(np.abs(preds_feed - labels_feed) < 10) * 100
    
    return {
        'mse': float(mse),
        'mae': float(mae),
        'rmse': float(rmse),
        'r2': float(r2),
        'mae_photoperiod': float(mae_photo),
        'accuracy_1h': float(acc_1h),
        'accuracy_2h': float(acc_2h),
        'mae_tpa': float(mae_tpa),
        'accuracy_tpa_5pct': float(acc_tpa_5),
        'mae_feeding': float(mae_feed),
        'accuracy_feed_10pct': float(acc_feed_10)
    }


def train_model(
    epochs: int = EPOCHS,
    lr: float = LEARNING_RATE,
    patience: int = PATIENCE,
    verbose: bool = True
) -> Tuple[PhotoperiodNet, Dict[str, any]]:
    """
    Treina o modelo com early stopping.
    
    Returns:
        model: Modelo treinado
        history: Histórico de treino
    """
    print("=" * 60)
    print("TREINO DO MODELO")
    print("=" * 60)
    
    # Preparar dados
    X_train, X_test, y_train, y_test, scaler = prepare_data()
    
    # Split train/val
    split = int(len(X_train) * 0.8)
    X_tr, X_val = X_train[:split], X_train[split:]
    y_tr, y_val = y_train[:split], y_train[split:]
    
    train_loader, val_loader = create_dataloaders(X_tr, y_tr, X_val, y_val)
    
    # Modelo
    model = AquaSenseNet().to(DEVICE)
    print(f"\n{model.summary()}")
    print(f"Device: {DEVICE}")
    
    # Loss e optimizer
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=lr)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode='min', factor=0.5, patience=20
    )
    
    # Early stopping
    early_stopping = EarlyStopping(patience=patience)
    
    # Histórico
    history = {
        'train_loss': [],
        'val_loss': [],
        'val_metrics': [],
        'lr': []
    }
    
    best_model_state = None
    best_val_loss = float('inf')
    start_time = time.time()
    
    print(f"\nA treinar (máx {epochs} épocas, early stopping após {patience} sem melhoria)...\n")
    
    for epoch in range(1, epochs + 1):
        # Treino
        train_loss = train_epoch(model, train_loader, criterion, optimizer)
        
        # Validação
        val_loss, val_metrics = validate(model, val_loader, criterion)
        
        # Scheduler
        scheduler.step(val_loss)
        current_lr = optimizer.param_groups[0]['lr']
        
        # Histórico
        history['train_loss'].append(train_loss)
        history['val_loss'].append(val_loss)
        history['val_metrics'].append(val_metrics)
        history['lr'].append(current_lr)
        
        # Guardar melhor modelo
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            best_model_state = model.state_dict().copy()
        
        # Log
        if verbose and epoch % 50 == 0:
            print(
                f"Época {epoch:4d} | "
                f"Train: {train_loss:.4f} | "
                f"Val: {val_loss:.4f} | "
                f"MAE: {val_metrics['mae']:.2f}h | "
                f"R²: {val_metrics['r2']:.3f}"
            )
        
        # Early stopping
        if early_stopping(val_loss):
            print(f"\n[Early Stopping] Parou na época {epoch}")
            break
    
    elapsed = time.time() - start_time
    
    # Carregar melhor modelo
    model.load_state_dict(best_model_state)
    
    # Avaliação final no test set
    test_loader, _ = create_dataloaders(X_test, y_test)
    _, test_metrics = validate(model, test_loader, criterion)
    
    # Guardar modelo
    torch.save(model.state_dict(), MODEL_PATH)
    
    # Guardar métricas
    final_metrics = {
        'epochs_trained': epoch,
        'training_time_seconds': elapsed,
        'best_val_loss': best_val_loss,
        'test_metrics': test_metrics,
        'model_params': model.count_parameters()
    }
    
    with open(METRICS_PATH, 'w') as f:
        json.dump(final_metrics, f, indent=2)
    
    print(f"\n{'=' * 60}")
    print("RESULTADOS FINAIS")
    print("=" * 60)
    print(f"Épocas treinadas: {epoch}")
    print(f"Tempo de treino: {elapsed:.1f}s")
    print(f"Melhor Val Loss: {best_val_loss:.4f}")
    print(f"\nMétricas no Test Set:")
    print(f"  MSE global:  {test_metrics['mse']:.4f}")
    print(f"  R² global:   {test_metrics['r2']:.3f}")
    print(f"\n  Fotoperíodo:")
    print(f"    MAE: {test_metrics['mae_photoperiod']:.2f}h")
    print(f"    Accuracy (<1h): {test_metrics['accuracy_1h']:.1f}%")
    print(f"    Accuracy (<2h): {test_metrics['accuracy_2h']:.1f}%")
    print(f"\n  TPA:")
    print(f"    MAE: {test_metrics['mae_tpa']:.1f}%")
    print(f"    Accuracy (<5%): {test_metrics['accuracy_tpa_5pct']:.1f}%")
    print(f"\n  Alimentação:")
    print(f"    MAE: {test_metrics['mae_feeding']:.1f}%")
    print(f"    Accuracy (<10%): {test_metrics['accuracy_feed_10pct']:.1f}%")
    print(f"\nModelo guardado: {MODEL_PATH}")
    print(f"Métricas guardadas: {METRICS_PATH}")
    
    history['final_metrics'] = final_metrics
    
    return model, history


def cross_validate(k_folds: int = K_FOLDS) -> Dict[str, any]:
    """
    K-Fold Cross Validation.
    
    Returns:
        Resultados agregados de todos os folds
    """
    print("=" * 60)
    print(f"K-FOLD CROSS VALIDATION (K={k_folds})")
    print("=" * 60)
    
    # Preparar dados (sem split)
    X_train, X_test, y_train, y_test, scaler = prepare_data()
    
    # Combinar train com val para K-Fold
    X = X_train
    y = y_train
    
    fold_size = len(X) // k_folds
    all_metrics = []
    
    for fold in range(k_folds):
        print(f"\n--- Fold {fold + 1}/{k_folds} ---")
        
        # Índices para este fold
        val_start = fold * fold_size
        val_end = val_start + fold_size
        
        X_val = X[val_start:val_end]
        y_val = y[val_start:val_end]
        X_tr = np.vstack([X[:val_start], X[val_end:]])
        y_tr = np.vstack([y[:val_start], y[val_end:]])
        
        # DataLoaders
        train_loader, val_loader = create_dataloaders(X_tr, y_tr, X_val, y_val)
        
        # Modelo novo para cada fold
        model = AquaSenseNet().to(DEVICE)
        criterion = nn.MSELoss()
        optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)
        early_stopping = EarlyStopping(patience=PATIENCE)
        
        best_val_loss = float('inf')
        
        for epoch in range(1, EPOCHS + 1):
            train_loss = train_epoch(model, train_loader, criterion, optimizer)
            val_loss, metrics = validate(model, val_loader, criterion)
            
            if val_loss < best_val_loss:
                best_val_loss = val_loss
                best_metrics = metrics.copy()
            
            if early_stopping(val_loss):
                break
        
        print(f"  Épocas: {epoch} | MAE: {best_metrics['mae']:.2f}h | R²: {best_metrics['r2']:.3f}")
        all_metrics.append(best_metrics)
    
    # Agregar resultados
    avg_metrics = {}
    std_metrics = {}
    
    for key in all_metrics[0].keys():
        values = [m[key] for m in all_metrics]
        avg_metrics[key] = np.mean(values)
        std_metrics[key] = np.std(values)
    
    print(f"\n{'=' * 60}")
    print("RESULTADOS K-FOLD (média ± std)")
    print("=" * 60)
    print(f"MAE:  {avg_metrics['mae']:.2f} ± {std_metrics['mae']:.2f}h")
    print(f"RMSE: {avg_metrics['rmse']:.2f} ± {std_metrics['rmse']:.2f}h")
    print(f"R²:   {avg_metrics['r2']:.3f} ± {std_metrics['r2']:.3f}")
    print(f"Accuracy (<1h): {avg_metrics['accuracy_1h']:.1f} ± {std_metrics['accuracy_1h']:.1f}%")
    print(f"Accuracy (<2h): {avg_metrics['accuracy_2h']:.1f} ± {std_metrics['accuracy_2h']:.1f}%")
    
    return {
        'folds': k_folds,
        'fold_metrics': all_metrics,
        'avg_metrics': avg_metrics,
        'std_metrics': std_metrics
    }


def compare_with_baseline() -> Dict[str, any]:
    """
    Compara o modelo neural com o baseline de regras.
    """
    print("\n" + "=" * 60)
    print("COMPARAÇÃO: REDE NEURAL vs BASELINE (REGRAS)")
    print("=" * 60)
    
    # Carregar modelo
    model = AquaSenseNet().to(DEVICE)
    model.load_state_dict(torch.load(MODEL_PATH, weights_only=True))
    model.eval()
    
    # Gerar dados de teste
    np.random.seed(RANDOM_SEED + 100)  # Seed diferente
    n_test = 500
    
    nn_errors = []
    baseline_errors = []
    
    for _ in range(n_test):
        turbidity = np.random.uniform(0, 100)
        trend = np.random.uniform(-30, 30)
        base_period = np.random.choice([6, 8, 10, 12])
        
        # Ground truth
        true_adj = BaselineModel.predict(turbidity, trend)
        
        # Neural Network
        x = torch.tensor([[
            turbidity / 100,
            turbidity / 100,
            (trend + 50) / 100,
            base_period / 16
        ]], dtype=torch.float32).to(DEVICE)
        
        with torch.no_grad():
            output = model(x)
            nn_pred = output[0, 0].item() * 12  # Apenas fotoperíodo para comparação
        
        # Baseline
        baseline_pred = BaselineModel.predict(turbidity, trend)
        
        nn_errors.append(abs(nn_pred - true_adj))
        baseline_errors.append(abs(baseline_pred - true_adj))
    
    nn_mae = np.mean(nn_errors)
    baseline_mae = np.mean(baseline_errors)
    
    nn_acc_1h = np.mean(np.array(nn_errors) < 1) * 100
    nn_acc_2h = np.mean(np.array(nn_errors) < 2) * 100
    baseline_acc_1h = np.mean(np.array(baseline_errors) < 1) * 100
    baseline_acc_2h = np.mean(np.array(baseline_errors) < 2) * 100
    
    print(f"\n{'Métrica':<20} {'Neural Net':>12} {'Baseline':>12}")
    print("-" * 46)
    print(f"{'MAE (horas)':<20} {nn_mae:>12.2f} {baseline_mae:>12.2f}")
    print(f"{'Accuracy <1h':<20} {nn_acc_1h:>11.1f}% {baseline_acc_1h:>11.1f}%")
    print(f"{'Accuracy <2h':<20} {nn_acc_2h:>11.1f}% {baseline_acc_2h:>11.1f}%")
    
    improvement = ((baseline_mae - nn_mae) / baseline_mae) * 100 if baseline_mae > 0 else 0
    print(f"\nMelhoria da NN sobre baseline: {improvement:+.1f}%")
    
    return {
        'neural_net': {'mae': nn_mae, 'acc_1h': nn_acc_1h, 'acc_2h': nn_acc_2h},
        'baseline': {'mae': baseline_mae, 'acc_1h': baseline_acc_1h, 'acc_2h': baseline_acc_2h},
        'improvement_pct': improvement
    }


if __name__ == "__main__":
    # Treino principal
    model, history = train_model()
    
    # Cross-validation
    cv_results = cross_validate()
    
    # Comparação com baseline
    comparison = compare_with_baseline()
