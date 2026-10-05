"""Página 1: lançamentos do mês (valor recebido, ganhos extras e gastos)."""

import pandas as pd
import streamlit as st

from backend.container import get_service
from backend.models import ResumoMensal
from backend.services import FinanceiroService, ValidacaoError
from frontend.components import (
    editor_de_lancamentos,
    exibir_notificacoes,
    formulario_novo_lancamento,
    notificar,
    seletor_de_mes,
    tabela_para_exibicao,
)
from frontend.formatters import formatar_moeda, formatar_percentual


def _aba_resumo(resumo: ResumoMensal, service: FinanceiroService, ano_mes: str) -> None:
    colunas = st.columns(3)
    colunas[0].metric("Ganhos", formatar_moeda(resumo.total_ganhos), border=True)
    colunas[1].metric("Gastos", formatar_moeda(resumo.total_gastos), border=True)
    colunas[2].metric("Saldo", formatar_moeda(resumo.saldo), border=True)

    st.progress(
        min(resumo.percentual_gasto / 100, 1.0),
        text=f"{formatar_percentual(resumo.percentual_gasto)} dos ganhos já foram gastos",
    )
    if resumo.saldo < 0:
        st.warning("Você gastou mais do que recebeu neste mês.")

    st.subheader("Ganhos")
    extras = service.listar_ganhos_extras(ano_mes)
    linhas_ganhos = pd.DataFrame(
        [{"Data": "—", "Origem": "Valor recebido", "Valor": formatar_moeda(resumo.salario_base)}]
    )
    if not extras.empty:
        extras_formatados = tabela_para_exibicao(extras, "descricao", "Origem")
        linhas_ganhos = pd.concat([linhas_ganhos, extras_formatados], ignore_index=True)
    st.dataframe(linhas_ganhos, hide_index=True, width="stretch")

    st.subheader("Gastos")
    gastos = service.listar_gastos(ano_mes)
    if gastos.empty:
        st.info("Nenhum gasto lançado neste mês.")
    else:
        st.dataframe(
            tabela_para_exibicao(gastos, "motivo", "Motivo"),
            hide_index=True,
            width="stretch",
        )


def _aba_ganhos(
    service: FinanceiroService, ano_mes: str, resumo: ResumoMensal
) -> None:
    st.subheader("Valor recebido no mês")
    with st.form(f"salario_{ano_mes}"):
        salario = st.number_input(
            "Quanto você recebe (R$)",
            min_value=0.0,
            value=float(resumo.salario_base),
            step=100.0,
            format="%.2f",
            key=f"salario_valor_{ano_mes}",
        )
        salvar_salario = st.form_submit_button("Salvar valor", type="primary", width="stretch")

    if salvar_salario:
        try:
            service.definir_salario_base(ano_mes, salario)
        except ValidacaoError as erro:
            st.error(str(erro))
        else:
            notificar("Valor recebido atualizado!")
            st.rerun()

    st.divider()
    st.subheader("Ganho extra")
    st.caption("Dinheiro que entrou além do valor recebido (ex.: pagamento de uma dívida).")
    formulario_novo_lancamento(
        chave="extra",
        ano_mes=ano_mes,
        rotulo_texto="De onde veio?",
        rotulo_botao="Adicionar ganho extra",
        ao_salvar=service.adicionar_ganho_extra,
        mensagem_sucesso="Ganho extra adicionado!",
    )
    editor_de_lancamentos(
        chave="extra",
        ano_mes=ano_mes,
        lancamentos=service.listar_ganhos_extras(ano_mes),
        coluna_texto="descricao",
        rotulo_texto="Origem",
        ao_editar=service.editar_ganho_extra,
        ao_remover=service.remover_ganho_extra,
    )


def _aba_gastos(service: FinanceiroService, ano_mes: str) -> None:
    st.subheader("Novo gasto")
    formulario_novo_lancamento(
        chave="gasto",
        ano_mes=ano_mes,
        rotulo_texto="Motivo do gasto",
        rotulo_botao="Adicionar gasto",
        ao_salvar=service.adicionar_gasto,
        mensagem_sucesso="Gasto adicionado!",
    )
    editor_de_lancamentos(
        chave="gasto",
        ano_mes=ano_mes,
        lancamentos=service.listar_gastos(ano_mes),
        coluna_texto="motivo",
        rotulo_texto="Motivo",
        ao_editar=service.editar_gasto,
        ao_remover=service.remover_gasto,
    )


def _secao_salvar_mes(service: FinanceiroService, ano_mes: str) -> None:
    st.divider()
    if service.mes_foi_salvo(ano_mes):
        st.caption("✅ Este mês já foi salvo. Salve de novo para incluir as mudanças.")
    else:
        st.caption("Este mês ainda não foi salvo no histórico dos gráficos.")

    if st.button("💾 Salvar mês", type="primary", width="stretch"):
        service.salvar_fechamento(ano_mes)
        notificar("Mês salvo no histórico!", "💾")
        st.rerun()


def main() -> None:
    service = get_service()
    exibir_notificacoes()

    st.title("💰 Lançamentos")
    ano_mes = seletor_de_mes("mes_lancamentos")
    resumo = service.resumo_mensal(ano_mes)

    aba_resumo, aba_ganhos, aba_gastos = st.tabs(["📋 Resumo", "💵 Ganhos", "🧾 Gastos"])
    with aba_resumo:
        _aba_resumo(resumo, service, ano_mes)
    with aba_ganhos:
        _aba_ganhos(service, ano_mes, resumo)
    with aba_gastos:
        _aba_gastos(service, ano_mes)

    _secao_salvar_mes(service, ano_mes)


main()
