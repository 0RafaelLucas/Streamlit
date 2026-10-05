"""Camada de acesso a dados (CRUD) com SQL puro."""

import sqlite3
from datetime import datetime

import pandas as pd

from backend.models import GanhoExtra, Gasto, ResumoMensal


class MesRepository:
    """Guarda o valor base (salário) de cada mês."""

    def __init__(self, connection: sqlite3.Connection):
        self._conn = connection

    def salvar_salario(self, ano_mes: str, salario_base: float) -> None:
        with self._conn:
            self._conn.execute(
                """
                INSERT INTO meses (ano_mes, salario_base) VALUES (?, ?)
                ON CONFLICT(ano_mes) DO UPDATE SET salario_base = excluded.salario_base
                """,
                (ano_mes, salario_base),
            )

    def obter_salario(self, ano_mes: str) -> float:
        row = self._conn.execute(
            "SELECT salario_base FROM meses WHERE ano_mes = ?", (ano_mes,)
        ).fetchone()
        return row["salario_base"] if row else 0.0


class GastoRepository:
    def __init__(self, connection: sqlite3.Connection):
        self._conn = connection

    def criar(self, gasto: Gasto) -> int:
        with self._conn:
            cursor = self._conn.execute(
                "INSERT INTO gastos (ano_mes, valor, motivo, data) VALUES (?, ?, ?, ?)",
                (gasto.ano_mes, gasto.valor, gasto.motivo, gasto.data.isoformat()),
            )
        return cursor.lastrowid

    def listar(self, ano_mes: str) -> pd.DataFrame:
        return pd.read_sql_query(
            "SELECT id, valor, motivo, data FROM gastos WHERE ano_mes = ? ORDER BY data, id",
            self._conn,
            params=(ano_mes,),
            parse_dates=["data"],
        )

    def atualizar(self, gasto: Gasto) -> None:
        with self._conn:
            self._conn.execute(
                "UPDATE gastos SET valor = ?, motivo = ?, data = ? WHERE id = ?",
                (gasto.valor, gasto.motivo, gasto.data.isoformat(), gasto.id),
            )

    def remover(self, gasto_id: int) -> None:
        with self._conn:
            self._conn.execute("DELETE FROM gastos WHERE id = ?", (gasto_id,))

    def total(self, ano_mes: str) -> float:
        row = self._conn.execute(
            "SELECT COALESCE(SUM(valor), 0) AS total FROM gastos WHERE ano_mes = ?",
            (ano_mes,),
        ).fetchone()
        return round(row["total"], 2)


class GanhoExtraRepository:
    def __init__(self, connection: sqlite3.Connection):
        self._conn = connection

    def criar(self, ganho: GanhoExtra) -> int:
        with self._conn:
            cursor = self._conn.execute(
                "INSERT INTO ganhos_extras (ano_mes, valor, descricao, data) VALUES (?, ?, ?, ?)",
                (ganho.ano_mes, ganho.valor, ganho.descricao, ganho.data.isoformat()),
            )
        return cursor.lastrowid

    def listar(self, ano_mes: str) -> pd.DataFrame:
        return pd.read_sql_query(
            "SELECT id, valor, descricao, data FROM ganhos_extras "
            "WHERE ano_mes = ? ORDER BY data, id",
            self._conn,
            params=(ano_mes,),
            parse_dates=["data"],
        )

    def atualizar(self, ganho: GanhoExtra) -> None:
        with self._conn:
            self._conn.execute(
                "UPDATE ganhos_extras SET valor = ?, descricao = ?, data = ? WHERE id = ?",
                (ganho.valor, ganho.descricao, ganho.data.isoformat(), ganho.id),
            )

    def remover(self, ganho_id: int) -> None:
        with self._conn:
            self._conn.execute("DELETE FROM ganhos_extras WHERE id = ?", (ganho_id,))

    def total(self, ano_mes: str) -> float:
        row = self._conn.execute(
            "SELECT COALESCE(SUM(valor), 0) AS total FROM ganhos_extras WHERE ano_mes = ?",
            (ano_mes,),
        ).fetchone()
        return round(row["total"], 2)


class FechamentoRepository:
    """Guarda o 'retrato' salvo de cada mês (usado nos gráficos comparativos)."""

    def __init__(self, connection: sqlite3.Connection):
        self._conn = connection

    def salvar(self, resumo: ResumoMensal) -> None:
        """Insere o fechamento ou sobrescreve o existente do mesmo mês."""
        with self._conn:
            self._conn.execute(
                """
                INSERT INTO fechamentos
                    (ano_mes, salario_base, total_extras, total_gastos, saldo, atualizado_em)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(ano_mes) DO UPDATE SET
                    salario_base  = excluded.salario_base,
                    total_extras  = excluded.total_extras,
                    total_gastos  = excluded.total_gastos,
                    saldo         = excluded.saldo,
                    atualizado_em = excluded.atualizado_em
                """,
                (
                    resumo.ano_mes,
                    resumo.salario_base,
                    resumo.total_extras,
                    resumo.total_gastos,
                    resumo.saldo,
                    datetime.now().isoformat(timespec="seconds"),
                ),
            )

    def listar(self) -> pd.DataFrame:
        return pd.read_sql_query(
            "SELECT * FROM fechamentos ORDER BY ano_mes", self._conn
        )
