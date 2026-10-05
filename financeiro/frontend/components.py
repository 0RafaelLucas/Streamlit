"""Componentes reutilizáveis da interface."""

import calendar
from collections.abc import Callable
from datetime import date

import pandas as pd
import streamlit as st

from backend.services import ValidacaoError, ano_mes_de
from frontend.formatters import formatar_data, formatar_moeda, rotulo_do_mes

MESES_PASSADOS = 36
MESES_FUTUROS = 3
FORMATO_DATA = "DD/MM/YYYY"


# ---------- Notificações ----------
def notificar(mensagem: str, icone: str = "✅") -> None:
    """Guarda uma mensagem para ser exibida após o próximo recarregamento."""
    st.session_state.setdefault("_notificacoes", []).append((mensagem, icone))


def exibir_notificacoes() -> None:
    for mensagem, icone in st.session_state.pop("_notificacoes", []):
        st.toast(mensagem, icon=icone)


def _executar_acao(acao: Callable[[], None], mensagem_sucesso: str, icone: str = "✅") -> bool:
    """Executa a ação, mostra erros de validação e recarrega a tela se der certo."""
    try:
        acao()
    except ValidacaoError as erro:
        st.error(str(erro))
        return False
    notificar(mensagem_sucesso, icone)
    st.rerun()
    return True


# ---------- Seleção de mês ----------
def _opcoes_de_mes() -> list[str]:
    hoje = date.today()
    indice_atual = hoje.year * 12 + hoje.month - 1
    opcoes = []
    for indice in range(indice_atual + MESES_FUTUROS, indice_atual - MESES_PASSADOS - 1, -1):
        ano, mes = divmod(indice, 12)
        opcoes.append(f"{ano:04d}-{mes + 1:02d}")
    return opcoes


def seletor_de_mes(chave: str) -> str:
    """Seletor de mês cujo valor é compartilhado entre as páginas."""
    opcoes = _opcoes_de_mes()
    ativo = st.session_state.get("ano_mes_ativo", ano_mes_de(date.today()))
    indice = opcoes.index(ativo) if ativo in opcoes else opcoes.index(ano_mes_de(date.today()))

    escolhido = st.selectbox(
        "Mês de referência",
        opcoes,
        index=indice,
        format_func=rotulo_do_mes,
        key=chave,
    )
    st.session_state["ano_mes_ativo"] = escolhido
    return escolhido


def limites_do_mes(ano_mes: str) -> tuple[date, date]:
    ano, mes = (int(parte) for parte in ano_mes.split("-"))
    ultimo_dia = calendar.monthrange(ano, mes)[1]
    return date(ano, mes, 1), date(ano, mes, ultimo_dia)


def _data_padrao(inicio: date, fim: date) -> date:
    hoje = date.today()
    return hoje if inicio <= hoje <= fim else inicio


# ---------- Tabelas ----------
def tabela_para_exibicao(
    lancamentos: pd.DataFrame, coluna_texto: str, rotulo_texto: str
) -> pd.DataFrame:
    """Converte os lançamentos em uma tabela já formatada para leitura."""
    return pd.DataFrame(
        {
            "Data": lancamentos["data"].dt.strftime("%d/%m"),
            rotulo_texto: lancamentos[coluna_texto],
            "Valor": lancamentos["valor"].map(formatar_moeda),
        }
    )


# ---------- Formulários de lançamento ----------
def formulario_novo_lancamento(
    chave: str,
    ano_mes: str,
    rotulo_texto: str,
    rotulo_botao: str,
    ao_salvar: Callable[[float, str, date], None],
    mensagem_sucesso: str,
) -> None:
    """Formulário de inclusão (valor, motivo/origem e data) limitado ao mês escolhido."""
    inicio, fim = limites_do_mes(ano_mes)
    versao = st.session_state.get(f"versao_{chave}", 0)
    base = f"{chave}_{ano_mes}_{versao}"

    with st.form(base):
        valor = st.number_input(
            "Valor (R$)", min_value=0.0, step=10.0, format="%.2f", key=f"{base}_valor"
        )
        texto = st.text_input(rotulo_texto, key=f"{base}_texto")
        data = st.date_input(
            "Data",
            value=_data_padrao(inicio, fim),
            min_value=inicio,
            max_value=fim,
            format=FORMATO_DATA,
            key=f"{base}_data",
        )
        enviado = st.form_submit_button(rotulo_botao, type="primary", width="stretch")

    if enviado:
        # Mudar a versão cria um formulário novo (campos limpos) só quando dá certo.
        st.session_state[f"versao_{chave}"] = versao + 1
        if not _executar_acao(lambda: ao_salvar(valor, texto, data), mensagem_sucesso):
            st.session_state[f"versao_{chave}"] = versao


def editor_de_lancamentos(
    chave: str,
    ano_mes: str,
    lancamentos: pd.DataFrame,
    coluna_texto: str,
    rotulo_texto: str,
    ao_editar: Callable[[int, float, str, date], None],
    ao_remover: Callable[[int], None],
) -> None:
    """Lista os lançamentos do mês e permite editar ou remover um deles."""
    if lancamentos.empty:
        st.info("Nenhum lançamento neste mês ainda.")
        return

    st.dataframe(
        tabela_para_exibicao(lancamentos, coluna_texto, rotulo_texto),
        hide_index=True,
        width="stretch",
    )

    with st.expander("✏️ Editar ou remover"):
        ids = lancamentos["id"].tolist()
        descricoes = {
            linha["id"]: (
                f"{linha['data']:%d/%m} · {linha[coluna_texto]} · "
                f"{formatar_moeda(linha['valor'])}"
            )
            for _, linha in lancamentos.iterrows()
        }
        # A chave muda quando a lista muda, evitando seleção apontando para item removido.
        assinatura = hash(tuple(ids))
        id_escolhido = st.selectbox(
            "Escolha o lançamento",
            ids,
            format_func=descricoes.get,
            key=f"{chave}_sel_{ano_mes}_{assinatura}",
        )
        linha = lancamentos.loc[lancamentos["id"] == id_escolhido].iloc[0]
        inicio, fim = limites_do_mes(ano_mes)
        base = f"{chave}_edit_{id_escolhido}"

        with st.form(base):
            valor = st.number_input(
                "Valor (R$)",
                min_value=0.01,
                value=float(linha["valor"]),
                step=10.0,
                format="%.2f",
                key=f"{base}_valor",
            )
            texto = st.text_input(rotulo_texto, value=linha[coluna_texto], key=f"{base}_texto")
            data = st.date_input(
                "Data",
                value=linha["data"].date(),
                min_value=inicio,
                max_value=fim,
                format=FORMATO_DATA,
                key=f"{base}_data",
            )
            salvar = st.form_submit_button("Salvar alterações", type="primary", width="stretch")
            remover = st.form_submit_button("🗑️ Remover", width="stretch")

        if salvar:
            _executar_acao(
                lambda: ao_editar(int(id_escolhido), valor, texto, data),
                "Lançamento atualizado!",
            )
        if remover:
            _executar_acao(lambda: ao_remover(int(id_escolhido)), "Lançamento removido.", "🗑️")
