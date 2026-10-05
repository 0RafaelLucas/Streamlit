"""Modelos de dados usados entre as camadas."""

from dataclasses import dataclass
from datetime import date


@dataclass
class Gasto:
    ano_mes: str
    valor: float
    motivo: str
    data: date
    id: int | None = None


@dataclass
class GanhoExtra:
    ano_mes: str
    valor: float
    descricao: str
    data: date
    id: int | None = None


@dataclass
class ResumoMensal:
    ano_mes: str
    salario_base: float
    total_extras: float
    total_gastos: float

    @property
    def total_ganhos(self) -> float:
        return round(self.salario_base + self.total_extras, 2)

    @property
    def saldo(self) -> float:
        return round(self.total_ganhos - self.total_gastos, 2)

    @property
    def percentual_gasto(self) -> float:
        """Percentual do total de ganhos que já foi gasto."""
        if self.total_ganhos == 0:
            return 0.0
        return round(self.total_gastos / self.total_ganhos * 100, 2)
