"""
Definição da arquitectura da rede neural.

PhotoperiodNet: Rede neural para previsão de ajuste de fotoperíodo
com base nos níveis de turbidez da água do aquário.
"""
import torch
import torch.nn as nn

from .config import INPUT_DIM, HIDDEN_DIM, OUTPUT_DIM


class PhotoperiodNet(nn.Module):
    """
    Rede Neural para ajuste de fotoperíodo.
    
    Arquitectura:
        - Entrada: 4 características (média 24h, turbidez actual, tendência, fotoperíodo base)
        - Camada oculta 1: 32 neurónios + ReLU + Dropout(0.2)
        - Camada oculta 2: 16 neurónios + ReLU + Dropout(0.2)
        - Saída: 1 valor (ajuste em horas, normalizado [-1, 1])
    
    A saída passa por Tanh para limitar a [-1, 1], sendo depois
    desnormalizada para [-12, 0] horas.
    """
    
    def __init__(self, input_dim: int = INPUT_DIM, hidden_dim: int = HIDDEN_DIM):
        super().__init__()
        
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        
        self.net = nn.Sequential(
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
            
            # Output
            nn.Linear(hidden_dim // 2, OUTPUT_DIM),
            nn.Tanh()  # Limita output a [-1, 1]
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
            Tensor de shape (batch_size, 1)
            Ajuste normalizado [-1, 1], onde -1 = -12h e 0 = 0h
        """
        return self.net(x)
    
    def predict_hours(self, x: torch.Tensor) -> torch.Tensor:
        """
        Previsão desnormalizada em horas.
        
        Returns:
            Ajuste em horas [-12, 0]
        """
        with torch.no_grad():
            normalized = self.forward(x)
            return normalized * 12  # Desnormaliza: [-1,1] -> [-12,12], mas só usamos [-12,0]
    
    def count_parameters(self) -> int:
        """Devolve o número de parâmetros treináveis."""
        return sum(p.numel() for p in self.parameters() if p.requires_grad)
    
    def summary(self) -> str:
        """Devolve resumo da arquitectura."""
        return (
            f"PhotoperiodNet(\n"
            f"  Input: {self.input_dim} features\n"
            f"  Hidden: {self.hidden_dim} → {self.hidden_dim // 2} neurónios\n"
            f"  Output: 1 (ajuste fotoperíodo)\n"
            f"  Parâmetros: {self.count_parameters():,}\n"
            f"  Activação: ReLU + Tanh(output)\n"
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


if __name__ == "__main__":
    # Teste rápido
    model = PhotoperiodNet()
    print(model.summary())
    
    # Teste forward
    x = torch.randn(4, INPUT_DIM)
    y = model(x)
    print(f"\nInput shape: {x.shape}")
    print(f"Output shape: {y.shape}")
    print(f"Output values: {y.squeeze().tolist()}")
