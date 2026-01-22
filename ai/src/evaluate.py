"""
Módulo de avaliação formal do modelo.

Gera relatórios completos com métricas, gráficos e comparações.
"""
import json
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import torch

from .config import (
    DEVICE, MODEL_PATH, METRICS_PATH, MODELS_DIR,
    RANDOM_SEED, get_expected_adjustment
)
from .model import PhotoperiodNet, BaselineModel
from .data_loader import prepare_data, create_dataloaders


def load_model() -> PhotoperiodNet:
    """Carrega o modelo treinado."""
    model = PhotoperiodNet().to(DEVICE)
    model.load_state_dict(torch.load(MODEL_PATH, weights_only=True, map_location=DEVICE))
    model.eval()
    return model


def evaluate_on_test_set() -> Dict[str, any]:
    """
    Avaliação completa no conjunto de teste.
    
    Returns:
        Dict com todas as métricas
    """
    print("=" * 60)
    print("AVALIAÇÃO NO CONJUNTO DE TESTE")
    print("=" * 60)
    
    # Carregar dados e modelo
    X_train, X_test, y_train, y_test, scaler = prepare_data()
    model = load_model()
    
    # Previsões
    X_tensor = torch.tensor(X_test, dtype=torch.float32).to(DEVICE)
    
    with torch.no_grad():
        predictions = model(X_tensor).cpu().numpy().flatten()
    
    # Desnormalizar
    preds = predictions * 12
    labels = y_test.flatten() * 12
    
    # Métricas
    errors = preds - labels
    abs_errors = np.abs(errors)
    
    metrics = {
        'n_samples': len(labels),
        'mse': float(np.mean(errors ** 2)),
        'mae': float(np.mean(abs_errors)),
        'rmse': float(np.sqrt(np.mean(errors ** 2))),
        'max_error': float(np.max(abs_errors)),
        'min_error': float(np.min(abs_errors)),
        'std_error': float(np.std(errors)),
        'accuracy_05h': float(np.mean(abs_errors < 0.5) * 100),
        'accuracy_1h': float(np.mean(abs_errors < 1) * 100),
        'accuracy_2h': float(np.mean(abs_errors < 2) * 100),
        'accuracy_3h': float(np.mean(abs_errors < 3) * 100),
    }
    
    # R²
    ss_res = np.sum((labels - preds) ** 2)
    ss_tot = np.sum((labels - np.mean(labels)) ** 2)
    metrics['r2'] = float(1 - (ss_res / ss_tot)) if ss_tot > 0 else 0
    
    # Distribuição de erros
    metrics['error_distribution'] = {
        'percentile_25': float(np.percentile(abs_errors, 25)),
        'percentile_50': float(np.percentile(abs_errors, 50)),
        'percentile_75': float(np.percentile(abs_errors, 75)),
        'percentile_90': float(np.percentile(abs_errors, 90)),
        'percentile_95': float(np.percentile(abs_errors, 95)),
    }
    
    # Print resultados
    print(f"\nAmostras de teste: {metrics['n_samples']}")
    print(f"\n{'Métrica':<25} {'Valor':>15}")
    print("-" * 42)
    print(f"{'MSE':<25} {metrics['mse']:>15.4f}")
    print(f"{'MAE':<25} {metrics['mae']:>14.2f}h")
    print(f"{'RMSE':<25} {metrics['rmse']:>14.2f}h")
    print(f"{'R²':<25} {metrics['r2']:>15.4f}")
    print(f"{'Erro máximo':<25} {metrics['max_error']:>14.2f}h")
    print(f"{'Desvio padrão erro':<25} {metrics['std_error']:>14.2f}h")
    print(f"\n{'Accuracy (<0.5h erro)':<25} {metrics['accuracy_05h']:>14.1f}%")
    print(f"{'Accuracy (<1h erro)':<25} {metrics['accuracy_1h']:>14.1f}%")
    print(f"{'Accuracy (<2h erro)':<25} {metrics['accuracy_2h']:>14.1f}%")
    print(f"{'Accuracy (<3h erro)':<25} {metrics['accuracy_3h']:>14.1f}%")
    
    return metrics


def evaluate_by_turbidity_range() -> Dict[str, any]:
    """
    Avalia o modelo por faixas de turbidez.
    """
    print("\n" + "=" * 60)
    print("AVALIAÇÃO POR FAIXA DE TURBIDEZ")
    print("=" * 60)
    
    model = load_model()
    
    ranges = [
        ("Limpa (0-20%)", 0, 20),
        ("Baixa (20-40%)", 20, 40),
        ("Moderada (40-60%)", 40, 60),
        ("Alta (60-80%)", 60, 80),
        ("Crítica (80-100%)", 80, 100),
    ]
    
    np.random.seed(RANDOM_SEED)
    results = {}
    
    print(f"\n{'Faixa':<20} {'MAE':>8} {'Acc<1h':>10} {'Acc<2h':>10} {'N':>6}")
    print("-" * 58)
    
    for name, low, high in ranges:
        errors = []
        
        for _ in range(200):  # 200 amostras por faixa
            turbidity = np.random.uniform(low, high)
            trend = np.random.uniform(-20, 30)
            
            # Ground truth
            true_adj = get_expected_adjustment(turbidity, trend)
            
            # Previsão
            x = torch.tensor([[
                turbidity / 100,
                turbidity / 100,
                (trend + 50) / 100,
                0.5
            ]], dtype=torch.float32).to(DEVICE)
            
            with torch.no_grad():
                pred = model(x).item() * 12
            
            errors.append(abs(pred - true_adj))
        
        mae = np.mean(errors)
        acc_1h = np.mean(np.array(errors) < 1) * 100
        acc_2h = np.mean(np.array(errors) < 2) * 100
        
        results[name] = {
            'mae': mae,
            'accuracy_1h': acc_1h,
            'accuracy_2h': acc_2h,
            'n_samples': len(errors)
        }
        
        print(f"{name:<20} {mae:>7.2f}h {acc_1h:>9.1f}% {acc_2h:>9.1f}% {len(errors):>6}")
    
    return results


def compare_models() -> Dict[str, any]:
    """
    Comparação formal entre Rede Neural e Baseline.
    """
    print("\n" + "=" * 60)
    print("COMPARAÇÃO: REDE NEURAL vs BASELINE")
    print("=" * 60)
    
    model = load_model()
    np.random.seed(RANDOM_SEED + 42)
    
    n_samples = 1000
    
    nn_results = {'errors': [], 'predictions': [], 'labels': []}
    bl_results = {'errors': [], 'predictions': [], 'labels': []}
    
    for _ in range(n_samples):
        turbidity = np.random.uniform(0, 100)
        trend = np.random.uniform(-30, 40)
        
        # Ground truth
        true_adj = get_expected_adjustment(turbidity, trend)
        
        # Neural Network
        x = torch.tensor([[
            turbidity / 100,
            turbidity / 100,
            (trend + 50) / 100,
            0.5
        ]], dtype=torch.float32).to(DEVICE)
        
        with torch.no_grad():
            nn_pred = model(x).item() * 12
        
        # Baseline
        bl_pred = BaselineModel.predict(turbidity, trend)
        
        nn_results['errors'].append(abs(nn_pred - true_adj))
        nn_results['predictions'].append(nn_pred)
        nn_results['labels'].append(true_adj)
        
        bl_results['errors'].append(abs(bl_pred - true_adj))
        bl_results['predictions'].append(bl_pred)
        bl_results['labels'].append(true_adj)
    
    # Calcular métricas
    def calc_metrics(results):
        errors = np.array(results['errors'])
        return {
            'mae': np.mean(errors),
            'rmse': np.sqrt(np.mean(errors ** 2)),
            'max_error': np.max(errors),
            'accuracy_1h': np.mean(errors < 1) * 100,
            'accuracy_2h': np.mean(errors < 2) * 100,
        }
    
    nn_metrics = calc_metrics(nn_results)
    bl_metrics = calc_metrics(bl_results)
    
    print(f"\n{'Métrica':<20} {'Neural Net':>15} {'Baseline':>15} {'Diferença':>12}")
    print("-" * 65)
    
    for metric in ['mae', 'rmse', 'max_error']:
        nn_val = nn_metrics[metric]
        bl_val = bl_metrics[metric]
        diff = nn_val - bl_val
        unit = 'h'
        print(f"{metric.upper():<20} {nn_val:>14.2f}{unit} {bl_val:>14.2f}{unit} {diff:>+11.2f}{unit}")
    
    for metric in ['accuracy_1h', 'accuracy_2h']:
        nn_val = nn_metrics[metric]
        bl_val = bl_metrics[metric]
        diff = nn_val - bl_val
        print(f"{metric:<20} {nn_val:>14.1f}% {bl_val:>14.1f}% {diff:>+11.1f}%")
    
    # Vencedor
    nn_score = (nn_metrics['accuracy_2h'] - bl_metrics['accuracy_2h'])
    if nn_score > 5:
        winner = "Rede Neural"
    elif nn_score < -5:
        winner = "Baseline"
    else:
        winner = "Empate técnico"
    
    print(f"\n→ Vencedor: {winner}")
    
    return {
        'neural_net': nn_metrics,
        'baseline': bl_metrics,
        'winner': winner,
        'n_samples': n_samples
    }


def generate_report() -> Dict[str, any]:
    """
    Gera relatório completo de avaliação.
    """
    print("\n" + "=" * 60)
    print("RELATÓRIO COMPLETO DE AVALIAÇÃO")
    print("=" * 60)
    
    report = {
        'test_set_evaluation': evaluate_on_test_set(),
        'turbidity_range_analysis': evaluate_by_turbidity_range(),
        'model_comparison': compare_models(),
    }
    
    # Guardar relatório
    report_path = MODELS_DIR / 'evaluation_report.json'
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n[✓] Relatório guardado: {report_path}")
    
    return report


if __name__ == "__main__":
    try:
        report = generate_report()
    except FileNotFoundError:
        print("[ERRO] Modelo não encontrado. Execute primeiro: python -m src.train")
