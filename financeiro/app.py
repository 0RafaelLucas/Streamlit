"""Ponto de entrada do app. Execute com: streamlit run app.py"""

import streamlit as st

from frontend.styles import aplicar_estilos

st.set_page_config(
    page_title="Controle Financeiro",
    page_icon="💰",
    layout="centered",
    initial_sidebar_state="collapsed",
)
aplicar_estilos()

navegacao = st.navigation(
    [
        st.Page("paginas/lancamentos.py", title="Lançamentos", icon="💰", default=True),
        st.Page("paginas/graficos.py", title="Gráficos", icon="📊"),
    ],
    position="top",
)
navegacao.run()
