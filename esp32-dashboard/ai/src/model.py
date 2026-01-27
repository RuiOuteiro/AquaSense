"""
Definição da arquitectura da rede neural.

AquaSenseNet: Rede neural para previsão de ajuste de fotoperíodo,
TPA e alimentação com base nos níveis de turbidez da água do aquário.
"""
import torch
import torch.nn as nn

from .config import INPUT_DIM, HIDDEN_DIM, OUTPUT_DIM


class AquaSenseNet(nn.Module):
    """
    Rede Neural para sugestões de aquário.
    
    Arquitectura:
        - Entrada: 4 características (média 24h, turbidez actual, tendência, fotoperíodo base)
        - Camada oculta 1: 32 neurónios + ReLU + Dropout(0.2)
        - Camada oculta 2: 16 neurónios + ReLU + Dropout(0.2)
        - Saída: 3 valores:
            [0] ajuste fotoperíodo: Tanh [-1, 1] -> [-12, 0] horas
            [1] TPA%: Sigmoid [0, 1] -> [0, 100]%
            [2] Alimentação%: Sigmoid [0, 1] -> [0, 100]%
    """
    
    def __init__(self, input_dim: int = INPUT_DIM, hidden_dim: int = HIDDEN_DIM):
        super().__init__()
        
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.output_dim = OUTPUT_DIM
        
        # Backbone partilhado
        self.backbone = nn.Sequential(
            # Camada 1
            nn.Linear(input_dim, hidden_dim),
            nn.BatchNorm1d(hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.2),
            
            # Camada 2
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.BatchNorm1d(hidden_dim // 2),
            nn.ReLU(),
            nn.Dropout(0.2),
        )
        
        # Cabeças separadas para cada saída
        self.head_photoperiod = nn.Sequential(
            nn.Linear(hidden_dim // 2, 1),
            nn.Tanh()  # [-1, 1] -> [-12, 0] horas
        )
        
        self.head_tpa = nn.Sequential(
            nn.Linear(hidden_dim // 2, 1),
            nn.Sigmoid()  # [0, 1] -> [0, 100]%
        )
        
        self.head_feeding = nn.Sequential(
            nn.Linear(hidden_dim // 2, 1),
            nn.Sigmoid()  # [0, 1] -> [0, 100]%
        )
        
        # Inicialização de pesos Xavier
        self._init_weights()
    
    def _init_weights(self):
        """Inicialização Xavier para melhor convergência do treino."""
        for m in self.modules():
            if isinstance(m, nn.Linear):
                nn.init.xavier_uniform_(m.weight)
                if m.bias is not None:
                    nn.init.zeros_(m.bias)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass.
        
        Args:
            x: Tensor de shape (batch_size, 4)
               [média_24h, turbidez_actual, tendência, fotoperíodo_base]
               Todos normalizados para [0, 1]
        
        Returns:
            Tensor de shape (batch_size, 3)
            [ajuste_fotoperiodo, tpa, alimentacao] - todos normalizados
        """
        features = self.backbone(x)
        
        photoperiod = self.head_photoperiod(features)  # [-1, 1]
        tpa = self.head_tpa(features)                   # [0, 1]
        feeding = self.head_feeding(features)           # [0, 1]
        
        return torch.cat([photoperiod, tpa, feeding], dim=1)
    
    def predict_values(self, x: torch.Tensor) -> dict:
        """
        Previsão desnormalizada com valores reais.
        
        Returns:
            Dict com ajuste_horas, tpa_percentagem, alimentacao_percentagem
        """
        with torch.no_grad():
            output = self.forward(x)
            return {
                'ajuste_horas': output[:, 0] * 12,           # [-12, 12] (usamos [-12, 0])
                'tpa_percentagem': output[:, 1] * 100,       # [0, 100]%
                'alimentacao_percentagem': output[:, 2] * 100  # [0, 100]%
            }
    
    def count_parameters(self) -> int:
        """Devolve o número de parâmetros treináveis."""
        return sum(p.numel() for p in self.parameters() if p.requires_grad)
    
    def summary(self) -> str:
        """Devolve resumo da arquitectura."""
        return (
            f"AquaSenseNet(\n"
            f"  Input: {self.input_dim} features\n"
            f"  Hidden: {self.hidden_dim} → {self.hidden_dim // 2} neurónios\n"
            f"  Output: {self.output_dim} (fotoperíodo, TPA%, alimentação%)\n"
            f"  Parâmetros: {self.count_parameters():,}\n"
            f"  Activações: ReLU, Tanh(fotoperíodo), Sigmoid(TPA/alimentação)\n"
            f"  Regularização: BatchNorm + Dropout(0.2)\n"
            f")"
        )


class BaselineModel:
    """
    Modelo de referência baseado em regras.
    Utilizado para comparação com a rede neural.
    """
    
    @staticmethod
    def predict(turbidity: float, trend: float = 0) -> float:
        """
        Previsão com base em regras simples.
        
        Args:
            turbidity: Nível de turbidez (0-100%)
            trend: Tendência de variação
        
        Returns:
            Ajuste recomendado em horas
        """
        if turbidity > 90:
            adjustment = -10
        elif turbidity > 80:
            adjustment = -8
        elif turbidity > 70:
            adjustment = -6
        elif turbidity > 60:
            adjustment = -5
        elif turbidity > 50:
            adjustment = -4
        elif turbidity > 40:
            adjustment = -3
        elif turbidity > 30:
            adjustment = -2
        elif turbidity > 20:
            adjustment = -1
        else:
            adjustment = 0
        
        # Ajuste por tendência
        if trend > 15:
            adjustment -= 2
        elif trend > 5:
            adjustment -= 1
        
        return max(-12, adjustment)


# Alias para retrocompatibilidade
PhotoperiodNet = AquaSenseNet


if __name__ == "__main__":
    # Teste rápido
    model = AquaSenseNet()
    print(model.summary())
    
    # Teste forward
    x = torch.randn(4, INPUT_DIM)
    y = model(x)
    print(f"\nInput shape: {x.shape}")
    print(f"Output shape: {y.shape}")
    print(f"Output columns: [fotoperíodo, TPA%, alimentação%]")
    print(f"Output values:\n{y}")
    
    # Teste predict_values
    values = model.predict_values(x)
    print(f"\nValores desnormalizados:")
    print(f"  Ajuste horas: {values['ajuste_horas'].tolist()}")
    print(f"  TPA%: {values['tpa_percentagem'].tolist()}")
    print(f"  Alimentação%: {values['alimentacao_percentagem'].tolist()}")
