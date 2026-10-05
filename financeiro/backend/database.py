"""Conexão e criação do esquema do banco SQLite."""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "financeiro.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS meses (
    ano_mes       TEXT PRIMARY KEY,
    salario_base  REAL NOT NULL CHECK (salario_base >= 0)
);

CREATE TABLE IF NOT EXISTS gastos (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    ano_mes  TEXT NOT NULL,
    valor    REAL NOT NULL CHECK (valor > 0),
    motivo   TEXT NOT NULL,
    data     TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS ganhos_extras (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    ano_mes    TEXT NOT NULL,
    valor      REAL NOT NULL CHECK (valor > 0),
    descricao  TEXT NOT NULL,
    data       TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS fechamentos (
    ano_mes        TEXT PRIMARY KEY,
    salario_base   REAL NOT NULL,
    total_extras   REAL NOT NULL,
    total_gastos   REAL NOT NULL,
    saldo          REAL NOT NULL,
    atualizado_em  TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_gastos_mes ON gastos (ano_mes);
CREATE INDEX IF NOT EXISTS idx_extras_mes ON ganhos_extras (ano_mes);
"""


def get_connection(db_path: Path = DB_PATH) -> sqlite3.Connection:
    """Abre a conexão e garante que as tabelas existam."""
    if str(db_path) != ":memory:":
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(db_path, check_same_thread=False)
    connection.row_factory = sqlite3.Row
    connection.executescript(SCHEMA)
    return connection
