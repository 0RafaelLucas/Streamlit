"""Ponto único de criação do serviço, com cache do Streamlit."""

import streamlit as st

from backend.database import get_connection
from backend.services import FinanceiroService


@st.cache_resource
def get_service() -> FinanceiroService:
    """Cria uma única instância do serviço por sessão do servidor."""
    return FinanceiroService(get_connection())
