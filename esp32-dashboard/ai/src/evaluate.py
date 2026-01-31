"""
Módulo de avaliação formal do modelo.

Gera relatórios completos com métricas, gráficos e comparações.

Versão (prof): 3 inputs -> turbidez + pH + temperatura
Outputs: [ajuste fotoperíodo, TPA%, alimentação%]
"""
import json
from typing import Dict, Any, List

import numpy as np
import torch

from .config import (
    DEVICE, MODEL_PATH, MODELS_DIR,
    RANDOM_SEED, SCALER_PATH,
    get_expected_adjustment, get_expected_tpa, get_expected_feeding
)
from .model import PhotoperiodNet
from .data_loader import prepare_data, StandardScaler


def load_model() -> PhotoperiodNet:
    """Carrega o modelo treinado."""
    model = PhotoperiodNet().to(DEVICE)

    # weights_only=True existe em versões recentes do torch; se a tua versão rebentar, muda para:
    # model.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE))
    model.load_state_dict(torch.load(MODEL_PATH, weights_only=True, map_location=DEVICE))
    model.eval()
    return model


def load_scaler() -> StandardScaler:
    """Carrega o scaler treinado (para inputs consistentes na avaliação)."""
    scaler = StandardScaler()
    scaler.load(SCALER_PATH)
    return scaler


def _calc_metrics(abs_errors: np.ndarray, errors: np.ndarray, thresholds: List[float]) -> Dict[str, float]:
    """Calcula métricas comuns para um vetor de erros."""
    metrics: Dict[str, float] = {
        "n_samples": float(abs_errors.shape[0]),
        "mse": float(np.mean(errors ** 2)),
        "mae": float(np.mean(abs_errors)),
        "rmse": float(np.sqrt(np.mean(errors ** 2))),
        "max_error": float(np.max(abs_errors)),
        "min_error": float(np.min(abs_errors)),
        "std_error": float(np.std(errors)),
    }

    for t in thresholds:
        metrics[f"accuracy_{t}"] = float(np.mean(abs_errors < t) * 100.0)

    return metrics


def _r2(labels: np.ndarray, preds: np.ndarray) -> float:
    """R² (coeficiente de determinação)."""
    ss_res = np.sum((labels - preds) ** 2)
    ss_tot = np.sum((labels - np.mean(labels)) ** 2)
    return float(1 - (ss_res / ss_tot)) if ss_tot > 0 else 0.0


def _error_distribution(abs_errors: np.ndarray) -> Dict[str, float]:
    """Distribuição de erros absolutos (percentis)."""
    return {
        "percentile_25": float(np.percentile(abs_errors, 25)),
        "percentile_50": float(np.percentile(abs_errors, 50)),
        "percentile_75": float(np.percentile(abs_errors, 75)),
        "percentile_90": float(np.percentile(abs_errors, 90)),
        "percentile_95": float(np.percentile(abs_errors, 95)),
    }


def evaluate_on_test_set() -> Dict[str, Any]:
    """
    Avaliação completa no conjunto de teste (3 outputs).
    Usa prepare_data() para garantir que o scaler e os dados estão consistentes.
    """
    print("=" * 60)
    print("AVALIAÇÃO NO CONJUNTO DE TESTE")
    print("=" * 60)

    # Carregar dados e modelo
    X_train, X_test, y_train, y_test, _scaler = prepare_data()
    model = load_model()

    X_tensor = torch.tensor(X_test, dtype=torch.float32).to(DEVICE)

    with torch.no_grad():
        pred_norm = model(X_tensor).cpu().numpy()  # (N, 3)

    # y_test já vem normalizado (N, 3)
    y_norm = y_test

    # Desnormalizar por saída
    preds_adj = pred_norm[:, 0] * 12.0
    labels_adj = y_norm[:, 0] * 12.0

    preds_tpa = pred_norm[:, 1] * 100.0
    labels_tpa = y_norm[:, 1] * 100.0

    preds_feed = pred_norm[:, 2] * 100.0
    labels_feed = y_norm[:, 2] * 100.0

    # Erros
    err_adj = preds_adj - labels_adj
    err_tpa = preds_tpa - labels_tpa
    err_feed = preds_feed - labels_feed

    abs_adj = np.abs(err_adj)
    abs_tpa = np.abs(err_tpa)
    abs_feed = np.abs(err_feed)

    # Métricas por saída
    metrics_adj = _calc_metrics(abs_adj, err_adj, thresholds=[0.5, 1, 2, 3])
    metrics_tpa = _calc_metrics(abs_tpa, err_tpa, thresholds=[5, 10, 15])
    metrics_feed = _calc_metrics(abs_feed, err_feed, thresholds=[5, 10, 15])

    # R²
    metrics_adj["r2"] = _r2(labels_adj, preds_adj)
    metrics_tpa["r2"] = _r2(labels_tpa, preds_tpa)
    metrics_feed["r2"] = _r2(labels_feed, preds_feed)

    # Distribuição de erros
    metrics_adj["error_distribution"] = _error_distribution(abs_adj)  # type: ignore[assignment]
    metrics_tpa["error_distribution"] = _error_distribution(abs_tpa)  # type: ignore[assignment]
    metrics_feed["error_distribution"] = _error_distribution(abs_feed)  # type: ignore[assignment]

    # Print resumo
    n_samples = int(abs_adj.shape[0])
    print(f"\nAmostras de teste: {n_samples}")

    def print_block(title: str, m: Dict[str, Any], unit: str, acc_keys: List[str]):
        print("\n" + "-" * 60)
        print(title)
        print("-" * 60)
        print(f"{'Métrica':<25} {'Valor':>15}")
        print("-" * 42)
        print(f"{'MAE':<25} {m['mae']:>14.2f}{unit}")
        print(f"{'RMSE':<25} {m['rmse']:>14.2f}{unit}")
        print(f"{'R²':<25} {m['r2']:>15.4f}")
        print(f"{'Erro máximo':<25} {m['max_error']:>14.2f}{unit}")
        print(f"{'Desvio padrão erro':<25} {m['std_error']:>14.2f}{unit}")
        for k in acc_keys:
            print(f"{k:<25} {m[k]:>14.1f}%")

    print_block(
        "OUTPUT 1 — AJUSTE FOTOPERÍODO",
        metrics_adj,
        "h",
        ["accuracy_0.5", "accuracy_1", "accuracy_2", "accuracy_3"],
    )
    print_block(
        "OUTPUT 2 — TPA",
        metrics_tpa,
        "%",
        ["accuracy_5", "accuracy_10", "accuracy_15"],
    )
    print_block(
        "OUTPUT 3 — ALIMENTAÇÃO",
        metrics_feed,
        "%",
        ["accuracy_5", "accuracy_10", "accuracy_15"],
    )

    return {
        "adjustment_hours": metrics_adj,
        "tpa_percent": metrics_tpa,
        "feeding_percent": metrics_feed,
        "n_samples": n_samples,
    }


def evaluate_by_turbidity_range() -> Dict[str, Any]:
    """
    Avalia o modelo por faixas de turbidez.
    Agora com 3 inputs: turbidez + pH + temperatura.
    Usa o scaler guardado para inputs consistentes.
    """
    print("\n" + "=" * 60)
    print("AVALIAÇÃO POR FAIXA DE TURBIDEZ")
    print("=" * 60)

    model = load_model()
    scaler = load_scaler()

    ranges = [
        ("Limpa (0-20%)", 0, 20),
        ("Baixa (20-40%)", 20, 40),
        ("Moderada (40-60%)", 40, 60),
        ("Alta (60-80%)", 60, 80),
        ("Crítica (80-100%)", 80, 100),
    ]

    np.random.seed(RANDOM_SEED)
    results: Dict[str, Any] = {}

    print(f"\n{'Faixa':<20} {'MAE':>8} {'Acc<1h':>10} {'Acc<2h':>10} {'N':>6}")
    print("-" * 58)

    for name, low, high in ranges:
        errors_adj: List[float] = []

        for _ in range(200):
            turbidity = float(np.random.uniform(low, high))

            # Simular pH e temperatura (para avaliação por faixa de turbidez)
            ph = float(np.random.uniform(6.6, 7.4))
            temperature = float(np.random.uniform(23.0, 28.0))

            true_adj = get_expected_adjustment(turbidity, ph=ph, temperature=temperature)

            # Input 3 features (RAW) -> aplicar scaler
            x_raw = np.array([[turbidity, ph, temperature]], dtype=np.float32)
            x_scaled = scaler.transform(x_raw)
            x = torch.tensor(x_scaled, dtype=torch.float32).to(DEVICE)

            with torch.no_grad():
                out = model(x).squeeze(0)      # (3,)
                pred_adj = out[0].item() * 12.0

            errors_adj.append(abs(pred_adj - true_adj))

        e = np.array(errors_adj, dtype=float)
        mae = float(np.mean(e))
        acc_1h = float(np.mean(e < 1) * 100.0)
        acc_2h = float(np.mean(e < 2) * 100.0)

        results[name] = {
            "adjustment_hours": {
                "mae": mae,
                "accuracy_1h": acc_1h,
                "accuracy_2h": acc_2h,
                "n_samples": int(e.shape[0]),
            }
        }

        print(f"{name:<20} {mae:>7.2f}h {acc_1h:>9.1f}% {acc_2h:>9.1f}% {int(e.shape[0]):>6}")

    return results


def compare_models() -> Dict[str, Any]:
    """
    Comparação formal entre Rede Neural e Baseline (regras) para as 3 saídas.

    Nota importante:
    Se o "GT" (ground truth) for gerado pelas regras, a baseline tende a ser perfeita.
    """
    print("\n" + "=" * 60)
    print("COMPARAÇÃO: REDE NEURAL vs BASELINE")
    print("=" * 60)

    model = load_model()
    scaler = load_scaler()
    np.random.seed(RANDOM_SEED + 42)

    n_samples = 1000

    nn_err = {"adj": [], "tpa": [], "feed": []}
    bl_err = {"adj": [], "tpa": [], "feed": []}

    for _ in range(n_samples):
        turbidity = float(np.random.uniform(0, 100))

        # Simular pH e temperatura (para comparar em vários cenários)
        ph = float(np.random.uniform(6.2, 8.0))
        temperature = float(np.random.uniform(20.0, 31.0))

        # Ground truth (regras)
        true_adj = get_expected_adjustment(turbidity, ph=ph, temperature=temperature)
        true_tpa = get_expected_tpa(turbidity, ph=ph, temperature=temperature)
        true_feed = get_expected_feeding(turbidity, ph=ph, temperature=temperature)

        # Rede neural (inputs escalados)
        x_raw = np.array([[turbidity, ph, temperature]], dtype=np.float32)
        x_scaled = scaler.transform(x_raw)
        x = torch.tensor(x_scaled, dtype=torch.float32).to(DEVICE)

        with torch.no_grad():
            out = model(x).squeeze(0)
            nn_adj = out[0].item() * 12.0
            nn_tpa = out[1].item() * 100.0
            nn_feed = out[2].item() * 100.0

        # Baseline (regras)
        bl_adj = true_adj
        bl_tpa = true_tpa
        bl_feed = true_feed

        nn_err["adj"].append(abs(nn_adj - true_adj))
        nn_err["tpa"].append(abs(nn_tpa - true_tpa))
        nn_err["feed"].append(abs(nn_feed - true_feed))

        bl_err["adj"].append(abs(bl_adj - true_adj))
        bl_err["tpa"].append(abs(bl_tpa - true_tpa))
        bl_err["feed"].append(abs(bl_feed - true_feed))

    def simple_metrics(errors: List[float], thr: float) -> Dict[str, float]:
        e = np.array(errors, dtype=float)
        return {
            "mae": float(e.mean()),
            "rmse": float(np.sqrt((e ** 2).mean())),
            "max_error": float(e.max()),
            f"accuracy_{thr}": float((e < thr).mean() * 100.0),
        }

    nn_adj_m = simple_metrics(nn_err["adj"], 2.0)
    bl_adj_m = simple_metrics(bl_err["adj"], 2.0)

    nn_tpa_m = simple_metrics(nn_err["tpa"], 10.0)
    bl_tpa_m = simple_metrics(bl_err["tpa"], 10.0)

    nn_feed_m = simple_metrics(nn_err["feed"], 10.0)
    bl_feed_m = simple_metrics(bl_err["feed"], 10.0)

    def print_cmp(title: str, nn_m: Dict[str, float], bl_m: Dict[str, float], unit: str, acc_key: str):
        print("\n" + "-" * 60)
        print(title)
        print("-" * 60)
        print(f"{'Métrica':<20} {'Neural Net':>15} {'Baseline':>15} {'Diferença':>12}")
        print("-" * 60)

        for k in ["mae", "rmse", "max_error"]:
            nnv = nn_m[k]
            blv = bl_m[k]
            diff = nnv - blv
            print(f"{k.upper():<20} {nnv:>14.2f}{unit} {blv:>14.2f}{unit} {diff:>+11.2f}{unit}")

        nn_acc = nn_m[acc_key]
        bl_acc = bl_m[acc_key]
        print(f"{acc_key:<20} {nn_acc:>14.1f}% {bl_acc:>14.1f}% {nn_acc - bl_acc:>+11.1f}%")

    print_cmp("AJUSTE FOTOPERÍODO", nn_adj_m, bl_adj_m, "h", "accuracy_2.0")
    print_cmp("TPA", nn_tpa_m, bl_tpa_m, "%", "accuracy_10.0")
    print_cmp("ALIMENTAÇÃO", nn_feed_m, bl_feed_m, "%", "accuracy_10.0")

    return {
        "neural_net": {"adj": nn_adj_m, "tpa": nn_tpa_m, "feed": nn_feed_m},
        "baseline": {"adj": bl_adj_m, "tpa": bl_tpa_m, "feed": bl_feed_m},
        "n_samples": n_samples,
        "winner_note": "Baseline aqui são as regras (GT também são regras), por isso tende a ser perfeito.",
    }


def generate_report() -> Dict[str, Any]:
    """
    Gera relatório completo de avaliação.
    """
    print("\n" + "=" * 60)
    print("RELATÓRIO COMPLETO DE AVALIAÇÃO")
    print("=" * 60)

    report = {
        "test_set_evaluation": evaluate_on_test_set(),
        "turbidity_range_analysis": evaluate_by_turbidity_range(),
        "model_comparison": compare_models(),
    }

    report_path = MODELS_DIR / "evaluation_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"\n[✓] Relatório guardado: {report_path}")

    return report


if __name__ == "__main__":
    try:
        _ = generate_report()
    except FileNotFoundError:
        print("[ERRO] Modelo não encontrado. Execute primeiro: python -m src.train")
