"""
Módulo de carregamento e preparação de dados.

Suporta:
- Dados reais da base de dados MySQL
- Dados sintéticos para treino inicial
- Normalização com StandardScaler
- DataLoaders para treino em lotes
"""
import json
from pathlib import Path
from typing import Tuple, Optional, List

import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader, TensorDataset
import joblib

try:
    import mysql.connector
    HAS_MYSQL = True
except ImportError:
    HAS_MYSQL = False

from .config import (
    DB_CONFIG, BATCH_SIZE, TEST_SIZE, RANDOM_SEED,
    DATA_DIR, SCALER_PATH, get_expected_adjustment
)


class StandardScaler:
    """
    Normalizador de características (alternativa ao sklearn).
    Normaliza para média=0, desvio padrão=1.
    """
    
    def __init__(self):
        self.mean_ = None
        self.std_ = None
        self.fitted = False
    
    def fit(self, X: np.ndarray) -> 'StandardScaler':
        """Calcula média e desvio padrão dos dados."""
        self.mean_ = np.mean(X, axis=0)
        self.std_ = np.std(X, axis=0)
        self.std_[self.std_ == 0] = 1  # Evitar divisão por zero
        self.fitted = True
        return self
    
    def transform(self, X: np.ndarray) -> np.ndarray:
        """Aplica a normalização aos dados."""
        if not self.fitted:
            raise RuntimeError("Scaler não foi fitted. Chama fit() primeiro.")
        return (X - self.mean_) / self.std_
    
    def fit_transform(self, X: np.ndarray) -> np.ndarray:
        """Ajusta e transforma num único passo."""
        return self.fit(X).transform(X)
    
    def inverse_transform(self, X: np.ndarray) -> np.ndarray:
        """Reverte a normalização aplicada."""
        return X * self.std_ + self.mean_
    
    def save(self, path: Path):
        """Guarda o normalizador em ficheiro."""
        joblib.dump({'mean': self.mean_, 'std': self.std_}, path)
    
    def load(self, path: Path) -> 'StandardScaler':
        """Carrega o normalizador de ficheiro."""
        data = joblib.load(path)
        self.mean_ = data['mean']
        self.std_ = data['std']
        self.fitted = True
        return self


class AquaSenseDataset(Dataset):
    """Conjunto de dados personalizado para o aquário."""
    
    def __init__(self, X: np.ndarray, y: np.ndarray):
        self.X = torch.tensor(X, dtype=torch.float32)
        self.y = torch.tensor(y, dtype=torch.float32)
    
    def __len__(self) -> int:
        return len(self.X)
    
    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor]:
        return self.X[idx], self.y[idx]


def fetch_real_data() -> List[Tuple]:
    """
    Obtém dados reais de turbidez da base de dados.
    
    Returns:
        Lista de tuplos (dia, hora, turbidez_média)
    """
    if not HAS_MYSQL:
        print("[WARN] mysql-connector não instalado, a usar apenas dados sintéticos")
        return []
    
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Contar total de registos
        cursor.execute(
            "SELECT COUNT(*) FROM leituras_sensores WHERE tipo_sensor = 'turbidity'"
        )
        total = cursor.fetchone()[0]
        print(f"[DB] Total de registos de turbidez: {total}")
        
        if total == 0:
            cursor.close()
            conn.close()
            return []
        
        # Obter dados agrupados por hora
        cursor.execute("""
            SELECT 
                DATE(data_hora) as dia,
                HOUR(data_hora) as hora,
                AVG(valor) as turbidez_media
            FROM leituras_sensores 
            WHERE tipo_sensor = 'turbidity'
            AND data_hora >= DATE_SUB(NOW(), INTERVAL 90 DAY)
            GROUP BY DATE(data_hora), HOUR(data_hora)
            ORDER BY dia, hora
        """)
        
        rows = cursor.fetchall()
        print(f"[DB] Registos agrupados (últimos 90 dias): {len(rows)}")
        
        cursor.close()
        conn.close()
        
        return rows
        
    except Exception as e:
        print(f"[WARN] Erro ao conectar à BD: {e}")
        return []


def generate_synthetic_data(n_samples: int = 2000) -> Tuple[np.ndarray, np.ndarray]:
    """
    Gera dados sintéticos para treino.
    
    Simula diferentes cenários de turbidez com variação realista.
    
    Args:
        n_samples: Número de amostras a gerar
    
    Returns:
        X: Features (n_samples, 4)
        y: Labels (n_samples, 1)
    """
    np.random.seed(RANDOM_SEED)
    
    X = []
    y = []
    
    for _ in range(n_samples):
        # Simular cenário
        scenario = np.random.choice(['clean', 'moderate', 'dirty', 'critical'], 
                                    p=[0.3, 0.35, 0.25, 0.1])
        
        if scenario == 'clean':
            turbidity_24h = np.random.uniform(0, 25)
            turbidity_now = turbidity_24h + np.random.normal(0, 5)
        elif scenario == 'moderate':
            turbidity_24h = np.random.uniform(20, 50)
            turbidity_now = turbidity_24h + np.random.normal(0, 10)
        elif scenario == 'dirty':
            turbidity_24h = np.random.uniform(45, 75)
            turbidity_now = turbidity_24h + np.random.normal(5, 10)
        else:  # critical
            turbidity_24h = np.random.uniform(70, 100)
            turbidity_now = turbidity_24h + np.random.normal(5, 8)
        
        # Limitar a 0-100
        turbidity_24h = np.clip(turbidity_24h, 0, 100)
        turbidity_now = np.clip(turbidity_now, 0, 100)
        
        # Calcular tendência
        trend = turbidity_now - turbidity_24h
        
        # Fotoperíodo base (variado)
        base_photoperiod = np.random.choice([6, 8, 10, 12])
        
        # Features normalizadas
        features = [
            turbidity_24h / 100.0,
            turbidity_now / 100.0,
            (trend + 50) / 100.0,  # Normalizar tendência [-50, 50] -> [0, 1]
            base_photoperiod / 16.0
        ]
        
        # Label: ajuste esperado baseado nas regras
        adjustment = get_expected_adjustment(turbidity_now, trend)
        label = adjustment / 12.0  # Normalizar para [-1, 0]
        
        X.append(features)
        y.append([label])
    
    return np.array(X, dtype=np.float32), np.array(y, dtype=np.float32)


def process_real_data(rows: List[Tuple]) -> Tuple[Optional[np.ndarray], Optional[np.ndarray]]:
    """
    Processa dados reais da BD para formato de treino.
    
    Args:
        rows: Lista de (dia, hora, turbidez_média)
    
    Returns:
        X, y: Arrays de features e labels, ou (None, None) se insuficiente
    """
    if len(rows) < 7:
        print(f"[DB] Dados insuficientes: {len(rows)} < 7")
        return None, None
    
    X = []
    y = []
    
    # Janela deslizante de 6 leituras
    for i in range(6, len(rows)):
        # Média das últimas 6 leituras
        recent = [float(rows[j][2]) for j in range(i-6, i)]
        avg_recent = np.mean(recent)
        
        # Leitura actual
        turbidity_now = float(rows[i][2])
        
        # Tendência
        trend = turbidity_now - avg_recent
        
        # Fotoperíodo base (assumir 8h)
        base_photoperiod = 8
        
        # Features
        features = [
            avg_recent / 100.0,
            turbidity_now / 100.0,
            (trend + 50) / 100.0,
            base_photoperiod / 16.0
        ]
        
        # Label
        adjustment = get_expected_adjustment(turbidity_now, trend)
        label = adjustment / 12.0
        
        X.append(features)
        y.append([label])
    
    print(f"[DB] Amostras geradas de dados reais: {len(X)}")
    
    return np.array(X, dtype=np.float32), np.array(y, dtype=np.float32)


def prepare_data(
    use_real_data: bool = True,
    synthetic_samples: int = 2000
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, StandardScaler]:
    """
    Prepara dados para treino.
    
    Args:
        use_real_data: Se deve tentar usar dados reais da BD
        synthetic_samples: Número de amostras sintéticas
    
    Returns:
        X_train, X_test, y_train, y_test, scaler
    """
    X_real, y_real = None, None
    
    # Tentar carregar dados reais
    if use_real_data:
        real_rows = fetch_real_data()
        if len(real_rows) >= 7:
            X_real, y_real = process_real_data(real_rows)
    
    # Gerar dados sintéticos
    print(f"[SYNTH] A gerar {synthetic_samples} amostras sintéticas...")
    X_synth, y_synth = generate_synthetic_data(synthetic_samples)
    
    # Combinar dados
    if X_real is not None and len(X_real) > 0:
        print(f"[DATA] Combinando {len(X_real)} reais + {len(X_synth)} sintéticos")
        X = np.vstack([X_real, X_synth])
        y = np.vstack([y_real, y_synth])
    else:
        print(f"[DATA] Usando apenas {len(X_synth)} amostras sintéticas")
        X = X_synth
        y = y_synth
    
    # Shuffle
    np.random.seed(RANDOM_SEED)
    indices = np.random.permutation(len(X))
    X = X[indices]
    y = y[indices]
    
    # Train/Test split
    split_idx = int(len(X) * (1 - TEST_SIZE))
    X_train, X_test = X[:split_idx], X[split_idx:]
    y_train, y_test = y[:split_idx], y[split_idx:]
    
    # Normalização
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)
    
    # Guardar scaler
    scaler.save(SCALER_PATH)
    print(f"[SCALER] Guardado em: {SCALER_PATH}")
    
    print(f"[DATA] Train: {len(X_train)} | Test: {len(X_test)}")
    
    return X_train, X_test, y_train, y_test, scaler


def create_dataloaders(
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_val: np.ndarray = None,
    y_val: np.ndarray = None,
    batch_size: int = BATCH_SIZE
) -> Tuple[DataLoader, Optional[DataLoader]]:
    """
    Cria DataLoaders para treino.
    
    Returns:
        train_loader, val_loader (ou None se não houver validação)
    """
    train_dataset = AquaSenseDataset(X_train, y_train)
    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=0,
        pin_memory=True
    )
    
    val_loader = None
    if X_val is not None and y_val is not None:
        val_dataset = AquaSenseDataset(X_val, y_val)
        val_loader = DataLoader(
            val_dataset,
            batch_size=batch_size,
            shuffle=False,
            num_workers=0,
            pin_memory=True
        )
    
    return train_loader, val_loader


if __name__ == "__main__":
    # Teste
    print("=== Teste de Data Loading ===\n")
    
    X_train, X_test, y_train, y_test, scaler = prepare_data()
    
    print(f"\nShapes:")
    print(f"  X_train: {X_train.shape}")
    print(f"  y_train: {y_train.shape}")
    print(f"  X_test: {X_test.shape}")
    print(f"  y_test: {y_test.shape}")
    
    train_loader, _ = create_dataloaders(X_train, y_train)
    print(f"\nBatches no train_loader: {len(train_loader)}")
