"""Funções de formatação de valores para exibição (padrão brasileiro)."""

import pandas as pd

MESES = (
    "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro",
)


def formatar_moeda(valor: float) -> str:
    """1234.5 -> 'R$ 1.234,50'."""
    texto = f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {texto}"


def formatar_percentual(valor: float) -> str:
    return f"{valor:.1f}".replace(".", ",") + "%"


def formatar_data(data: pd.Timestamp) -> str:
    return data.strftime("%d/%m/%Y")


def rotulo_do_mes(ano_mes: str) -> str:
    """'2026-10' -> 'Outubro/2026'."""
    ano, mes = ano_mes.split("-")
    return f"{MESES[int(mes) - 1]}/{ano}"


def rotulo_curto_do_mes(ano_mes: str) -> str:
    """'2026-10' -> 'Out/26'."""
    ano, mes = ano_mes.split("-")
    return f"{MESES[int(mes) - 1][:3]}/{ano[2:]}"
