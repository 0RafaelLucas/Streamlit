"""Página 2: gráficos do mês selecionado e comparativo entre meses."""

import streamlit as st

from backend.container import get_service
from backend.services import FinanceiroService
from frontend.charts import (
    CONFIG_PLOTLY,
    grafico_comparativo_meses,
    grafico_gasto_acumulado,
    grafico_ganhos_vs_gastos,
    grafico_gastos_por_motivo,
)
from frontend.components import exibir_notificacoes, seletor_de_mes
from frontend.formatters import formatar_moeda, rotulo_do_mes


def _mostrar(figura) -> None:
    st.plotly_chart(figura, config=CONFIG_PLOTLY, width="stretch")


def _aba_mes(service: FinanceiroService) -> None:
    ano_mes = seletor_de_mes("mes_graficos")
    resumo = service.resumo_mensal(ano_mes)

    if resumo.total_ganhos == 0 and resumo.total_gastos == 0:
        st.info("Ainda não há valores neste mês. Faça seus lançamentos na página Lançamentos.")
        return

    st.caption("Mostra os valores atuais do mês, mesmo que ainda não tenham sido salvos.")

    st.subheader("Valor inicial x gastos")
    _mostrar(grafico_ganhos_vs_gastos(resumo))

    gastos_por_motivo = service.gastos_por_motivo(ano_mes)
    if gastos_por_motivo.empty:
        return

    st.subheader("Gastos por motivo")
    _mostrar(grafico_gastos_por_motivo(gastos_por_motivo))

    st.subheader("Gasto acumulado no mês")
    _mostrar(grafico_gasto_acumulado(service.gastos_acumulados_no_mes(ano_mes), resumo.total_ganhos))


def _aba_comparativo(service: FinanceiroService) -> None:
    historico = service.historico_mensal()
    if historico.empty:
        st.info("Salve pelo menos um mês na página Lançamentos para ver o comparativo.")
        return

    st.caption("Considera apenas os meses que você salvou.")
    st.subheader("Ganhos x gastos por mês")
    _mostrar(grafico_comparativo_meses(historico))

    with st.expander("Ver tabela dos meses"):
        tabela = historico[["ano_mes", "total_ganhos", "total_gastos", "saldo"]].copy()
        tabela["ano_mes"] = tabela["ano_mes"].map(rotulo_do_mes)
        for coluna in ("total_ganhos", "total_gastos", "saldo"):
            tabela[coluna] = tabela[coluna].map(formatar_moeda)
        tabela.columns = ["Mês", "Ganhos", "Gastos", "Saldo"]
        st.dataframe(tabela, hide_index=True, width="stretch")


def main() -> None:
    service = get_service()
    exibir_notificacoes()

    st.title("📊 Gráficos")
    aba_mes, aba_comparativo = st.tabs(["📅 Mês", "📈 Comparativo"])
    with aba_mes:
        _aba_mes(service)
    with aba_comparativo:
        _aba_comparativo(service)


main()
