"""
Carregamento e preparação de dados para treino do modelo AquaSense.

Gera dataset sintético baseado em regras (turbidez + pH + temperatura)
e prepara para treino com normalização adequada.
"""
import numpy as np
import pickle
from typing import Tuple
from pathlib import Path
import torch
from torch.utils.data import DataLoader, TensorDataset

from .config import (
    RANDOM_SEED, TEST_SIZE, BATCH_SIZE, DEVICE,
    get_expected_adjustment, get_expected_tpa, get_expected_feeding,
    SCALER_PATH
)


class StandardScaler:
    """Scaler simples para normalização de features."""
    
    def __init__(self):
        self.mean_ = None
        self.std_ = None
    
    def fit(self, X: np.ndarray) -> 'StandardScaler':
        """Calcula média e desvio padrão."""
        self.mean_ = np.mean(X, axis=0)
        self.std_ = np.std(X, axis=0)
        # Evitar divisão por zero
        self.std_[self.std_ == 0] = 1.0
        return self
    
    def transform(self, X: np.ndarray) -> np.ndarray:
        """Normaliza os dados."""
        if self.mean_ is None or self.std_ is None:
            raise ValueError("Scaler não foi ajustado. Execute fit() primeiro.")
        return (X - self.mean_) / self.std_
    
    def fit_transform(self, X: np.ndarray) -> np.ndarray:
        """Fit e transform em um passo."""
        return self.fit(X).transform(X)
    
    def save(self, path: Path):
        """Guarda scaler em ficheiro."""
        with open(path, 'wb') as f:
            pickle.dump({'mean': self.mean_, 'std': self.std_}, f)
        return self
    
    def load(self, path: Path):
        """Carrega scaler de ficheiro."""
        with open(path, 'rb') as f:
            data = pickle.load(f)
            self.mean_ = data['mean']
            self.std_ = data['std']
        return self


def generate_synthetic_data(n_samples: int = 10000, seed: int = RANDOM_SEED) -> Tuple[np.ndarray, np.ndarray]:
    """
    Gera dataset sintético para treino.
    
    Features (3):
        - turbidez (0-100)
        - pH (6.0-8.5)
        - temperatura (20-31°C)
    
    Labels (3) NORMALIZADOS:
        - ajuste fotoperíodo / 12  -> [-1, 0]
        - TPA / 100                -> [0, 1]
        - alimentação / 100        -> [0, 1]
    
    Returns:
        X: (n_samples, 3) - features
        y: (n_samples, 3) - labels normalizados
    """
    np.random.seed(seed)
    
    # Gerar features com distribuições realistas
    # Beta(2,5) concentra mais amostras em valores baixos de turbidez (realista)
    turbidity = np.random.beta(2, 5, n_samples) * 100
    
    # pH centrado em neutro com distribuição normal
    ph = np.random.normal(7.0, 0.4, n_samples)
    ph = np.clip(ph, 6.0, 8.5)
    
    # Temperatura típica de aquário tropical
    temperature = np.random.normal(25.5, 2.0, n_samples)
    temperature = np.clip(temperature, 20.0, 31.0)
    
    X = np.column_stack([turbidity, ph, temperature])
    
    # Gerar labels usando as regras
    y = np.zeros((n_samples, 3), dtype=np.float32)
    
    for i in range(n_samples):
        # Calcular labels reais
        adj = get_expected_adjustment(
            turbidity=turbidity[i],
            ph=ph[i],
            temperature=temperature[i]
        )
        tpa = get_expected_tpa(
            turbidity=turbidity[i],
            ph=ph[i],
            temperature=temperature[i]
        )
        feed = get_expected_feeding(
            turbidity=turbidity[i],
            ph=ph[i],
            temperature=temperature[i]
        )
        
        # Normalizar labels
        y[i, 0] = adj / 12.0    # [-12, 0] -> [-1, 0]
        y[i, 1] = tpa / 100.0   # [0, 100] -> [0, 1]
        y[i, 2] = feed / 100.0  # [0, 100] -> [0, 1]
    
    # Adicionar ruído pequeno para variabilidade (±2%)
    noise = np.random.normal(0, 0.02, y.shape)
    y = y + noise
    
    # Clamp para garantir ranges corretos
    y[:, 0] = np.clip(y[:, 0], -1.0, 0.0)   # ajuste
    y[:, 1] = np.clip(y[:, 1], 0.0, 1.0)    # TPA
    y[:, 2] = np.clip(y[:, 2], 0.0, 1.0)    # feeding
    
    return X.astype(np.float32), y.astype(np.float32)


def prepare_data(
    n_samples: int = 10000,
    test_size: float = TEST_SIZE,
    seed: int = RANDOM_SEED
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, StandardScaler]:
    """
    Prepara dados completos para treino e teste.
    
    Returns:
        X_train: Features de treino (normalizadas)
        X_test: Features de teste (normalizadas)
        y_train: Labels de treino (normalizadas)
        y_test: Labels de teste (normalizadas)
        scaler: Scaler ajustado (para usar em produção)
    """
    # Gerar dados
    X, y = generate_synthetic_data(n_samples, seed)
    
    # Split treino/teste
    np.random.seed(seed)
    indices = np.random.permutation(n_samples)
    n_test = int(n_samples * test_size)
    
    test_indices = indices[:n_test]
    train_indices = indices[n_test:]
    
    X_train_raw = X[train_indices]
    X_test_raw = X[test_indices]
    y_train = y[train_indices]
    y_test = y[test_indices]
    
    # Normalizar features (importante: fit APENAS no treino!)
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train_raw)
    X_test = scaler.transform(X_test_raw)
    
    # Guardar scaler para produção
    scaler.save(SCALER_PATH)
    
    print(f"[✓] Dataset preparado:")
    print(f"    Treino: {X_train.shape[0]} amostras")
    print(f"    Teste:  {X_test.shape[0]} amostras")
    print(f"[✓] Scaler guardado: {SCALER_PATH}")
    
    return X_train, X_test, y_train, y_test, scaler


def create_dataloaders(
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_val: np.ndarray = None,
    y_val: np.ndarray = None,
    batch_size: int = BATCH_SIZE
) -> Tuple[DataLoader, DataLoader]:
    """
    Cria DataLoaders para treino e validação.
    
    Args:
        X_train: Features de treino
        y_train: Labels de treino
        X_val: Features de validação (opcional)
        y_val: Labels de validação (opcional)
        batch_size: Tamanho do batch
    
    Returns:
        train_loader: DataLoader de treino
        val_loader: DataLoader de validação (ou None)
    """
    # Dataset de treino
    train_dataset = TensorDataset(
        torch.tensor(X_train, dtype=torch.float32),
        torch.tensor(y_train, dtype=torch.float32)
    )
    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=0,
        pin_memory=(DEVICE.type == "cuda")
    )
    
    # Dataset de validação
    val_loader = None
    if X_val is not None and y_val is not None:
        val_dataset = TensorDataset(
            torch.tensor(X_val, dtype=torch.float32),
            torch.tensor(y_val, dtype=torch.float32)
        )
        val_loader = DataLoader(
            val_dataset,
            batch_size=batch_size,
            shuffle=False,
            num_workers=0,
            pin_memory=(DEVICE.type == "cuda")
        )
    
    return train_loader, val_loader


if __name__ == "__main__":
    print("Gerando dataset sintético...")
    X_train, X_test, y_train, y_test, scaler = prepare_data()
    
    print(f"\n✓ Dataset gerado:")
    print(f"  Treino: {X_train.shape[0]} amostras")
    print(f"  Teste:  {X_test.shape[0]} amostras")
    print(f"  Features: {X_train.shape[1]} (turbidez, pH, temperatura)")
    print(f"  Labels: {y_train.shape[1]} (ajuste, TPA, alimentação)")
    print(f"\n✓ Ranges dos dados:")
    print(f"  Turbidez: {X_train[:, 0].min():.1f} - {X_train[:, 0].max():.1f}")
    print(f"  pH: {X_train[:, 1].min():.2f} - {X_train[:, 1].max():.2f}")
    print(f"  Temp: {X_train[:, 2].min():.1f} - {X_train[:, 2].max():.1f}°C")
    print(f"\n✓ Scaler guardado: {SCALER_PATH}")
