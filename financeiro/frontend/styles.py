"""Estilos globais, pensados para telas de celular (toque e telas estreitas)."""

import streamlit as st

CSS = """
<style>
    .block-container {
        padding-top: 4.5rem;
        padding-bottom: 3rem;
        max-width: 820px;
    }

    /* Botões maiores, fáceis de tocar */
    .stButton > button,
    .stFormSubmitButton > button {
        min-height: 3rem;
        border-radius: 0.75rem;
        font-weight: 600;
    }

    [data-testid="stMetricValue"] {
        font-size: 1.5rem;
    }

    @media (max-width: 640px) {
        .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }
        h1 {
            font-size: 1.7rem;
        }
        h3 {
            font-size: 1.15rem;
        }
    }
</style>
"""


def aplicar_estilos() -> None:
    st.markdown(CSS, unsafe_allow_html=True)
