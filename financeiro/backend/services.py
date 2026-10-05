"""Regras de negócio. As páginas do Streamlit só conversam com esta camada."""

import re
import sqlite3
from datetime import date

import pandas as pd

from backend.models import GanhoExtra, Gasto, ResumoMensal
from backend.repositories import (
    FechamentoRepository,
    GanhoExtraRepository,
    GastoRepository,
    MesRepository,
)

ANO_MES_PATTERN = re.compile(r"^\d{4}-(0[1-9]|1[0-2])$")


class ValidacaoError(ValueError):
    """Erro de validação que pode ser exibido ao usuário."""


def ano_mes_de(data: date) -> str:
    """Converte uma data para o formato 'YYYY-MM'."""
    return data.strftime("%Y-%m")


def _validar_ano_mes(ano_mes: str) -> None:
    if not ANO_MES_PATTERN.match(ano_mes):
        raise ValidacaoError("Mês inválido. Use o formato AAAA-MM.")


def _validar_valor(valor: float) -> float:
    if valor is None or valor <= 0:
        raise ValidacaoError("O valor deve ser maior que zero.")
    return round(float(valor), 2)


def _validar_texto(texto: str, campo: str) -> str:
    texto = (texto or "").strip()
    if not texto:
        raise ValidacaoError(f"Informe {campo}.")
    return texto


class FinanceiroService:
    def __init__(self, connection: sqlite3.Connection):
        self._meses = MesRepository(connection)
        self._gastos = GastoRepository(connection)
        self._extras = GanhoExtraRepository(connection)
        self._fechamentos = FechamentoRepository(connection)

    # ---------- Salário base ----------
    def definir_salario_base(self, ano_mes: str, valor: float) -> None:
        _validar_ano_mes(ano_mes)
        if valor is None or valor < 0:
            raise ValidacaoError("O valor recebido não pode ser negativo.")
        self._meses.salvar_salario(ano_mes, round(float(valor), 2))

    def obter_salario_base(self, ano_mes: str) -> float:
        return self._meses.obter_salario(ano_mes)

    # ---------- Gastos ----------
    def adicionar_gasto(self, valor: float, motivo: str, data: date) -> int:
        gasto = Gasto(
            ano_mes=ano_mes_de(data),
            valor=_validar_valor(valor),
            motivo=_validar_texto(motivo, "o motivo do gasto"),
            data=data,
        )
        return self._gastos.criar(gasto)

    def listar_gastos(self, ano_mes: str) -> pd.DataFrame:
        _validar_ano_mes(ano_mes)
        return self._gastos.listar(ano_mes)

    def editar_gasto(self, gasto_id: int, valor: float, motivo: str, data: date) -> None:
        gasto = Gasto(
            id=gasto_id,
            ano_mes=ano_mes_de(data),
            valor=_validar_valor(valor),
            motivo=_validar_texto(motivo, "o motivo do gasto"),
            data=data,
        )
        self._gastos.atualizar(gasto)

    def remover_gasto(self, gasto_id: int) -> None:
        self._gastos.remover(gasto_id)

    # ---------- Ganhos extras ----------
    def adicionar_ganho_extra(self, valor: float, descricao: str, data: date) -> int:
        ganho = GanhoExtra(
            ano_mes=ano_mes_de(data),
            valor=_validar_valor(valor),
            descricao=_validar_texto(descricao, "a origem do ganho extra"),
            data=data,
        )
        return self._extras.criar(ganho)

    def listar_ganhos_extras(self, ano_mes: str) -> pd.DataFrame:
        _validar_ano_mes(ano_mes)
        return self._extras.listar(ano_mes)

    def editar_ganho_extra(
        self, ganho_id: int, valor: float, descricao: str, data: date
    ) -> None:
        ganho = GanhoExtra(
            id=ganho_id,
            ano_mes=ano_mes_de(data),
            valor=_validar_valor(valor),
            descricao=_validar_texto(descricao, "a origem do ganho extra"),
            data=data,
        )
        self._extras.atualizar(ganho)

    def remover_ganho_extra(self, ganho_id: int) -> None:
        self._extras.remover(ganho_id)

    # ---------- Resumo e fechamento ----------
    def resumo_mensal(self, ano_mes: str) -> ResumoMensal:
        _validar_ano_mes(ano_mes)
        return ResumoMensal(
            ano_mes=ano_mes,
            salario_base=self._meses.obter_salario(ano_mes),
            total_extras=self._extras.total(ano_mes),
            total_gastos=self._gastos.total(ano_mes),
        )

    def salvar_fechamento(self, ano_mes: str) -> ResumoMensal:
        """Salva (ou atualiza) o retrato do mês. Pode ser chamado várias vezes."""
        resumo = self.resumo_mensal(ano_mes)
        self._fechamentos.salvar(resumo)
        return resumo

    def mes_foi_salvo(self, ano_mes: str) -> bool:
        historico = self._fechamentos.listar()
        return ano_mes in historico["ano_mes"].values

    # ---------- Dados para os gráficos (Página 2) ----------
    def gastos_por_motivo(self, ano_mes: str) -> pd.DataFrame:
        gastos = self.listar_gastos(ano_mes)
        if gastos.empty:
            return pd.DataFrame(columns=["motivo", "valor"])
        return (
            gastos.groupby("motivo", as_index=False)["valor"]
            .sum()
            .sort_values("valor", ascending=False)
        )

    def gastos_acumulados_no_mes(self, ano_mes: str) -> pd.DataFrame:
        """Gasto acumulado dia a dia, para comparar com o total de ganhos."""
        gastos = self.listar_gastos(ano_mes)
        if gastos.empty:
            return pd.DataFrame(columns=["data", "acumulado"])
        por_dia = gastos.groupby("data", as_index=False)["valor"].sum()
        por_dia["acumulado"] = por_dia["valor"].cumsum().round(2)
        return por_dia[["data", "acumulado"]]

    def historico_mensal(self) -> pd.DataFrame:
        """Fechamentos salvos de todos os meses, para o comparativo."""
        historico = self._fechamentos.listar()
        if historico.empty:
            return historico
        historico["total_ganhos"] = historico["salario_base"] + historico["total_extras"]
        return historico
