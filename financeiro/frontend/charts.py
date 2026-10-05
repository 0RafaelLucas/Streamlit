"""Construção dos gráficos Plotly (layout compacto para celular)."""

import pandas as pd
import plotly.graph_objects as go

from backend.models import ResumoMensal
from frontend.formatters import formatar_moeda, rotulo_curto_do_mes

COR_GANHO = "#2E9E6B"
COR_EXTRA = "#7CCBA2"
COR_GASTO = "#E5484D"
COR_SALDO = "#3B82F6"

CONFIG_PLOTLY = {"displayModeBar": False}


def _aplicar_layout(fig: go.Figure, altura: int = 340, horizontal: bool = False) -> go.Figure:
    """Layout comum: sem zoom por arrasto (não atrapalha a rolagem no celular)."""
    fig.update_layout(
        height=altura,
        margin=dict(l=8, r=8, t=36, b=8),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
        separators=",.",
        dragmode=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    eixo_valores = fig.update_xaxes if horizontal else fig.update_yaxes
    eixo_categorias = fig.update_yaxes if horizontal else fig.update_xaxes

    eixo_valores(
        tickprefix="R$ ",
        gridcolor="rgba(128,128,128,0.2)",
        fixedrange=True,
        automargin=True,
    )
    eixo_categorias(showgrid=False, fixedrange=True, automargin=True)
    return fig


def grafico_ganhos_vs_gastos(resumo: ResumoMensal) -> go.Figure:
    """Valor inicial do mês comparado com extras, gastos e saldo."""
    categorias = ["Valor inicial", "Extras", "Gastos", "Saldo"]
    valores = [resumo.salario_base, resumo.total_extras, resumo.total_gastos, resumo.saldo]
    cores = [COR_GANHO, COR_EXTRA, COR_GASTO, COR_SALDO]

    fig = go.Figure(
        go.Bar(
            x=categorias,
            y=valores,
            marker_color=cores,
            text=[formatar_moeda(valor) for valor in valores],
            textposition="outside",
            cliponaxis=False,
            hoverinfo="skip",
        )
    )
    fig.update_layout(showlegend=False, margin=dict(l=8, r=8, t=48, b=8))
    return _aplicar_layout(fig, altura=340)


def grafico_gastos_por_motivo(gastos_por_motivo: pd.DataFrame) -> go.Figure:
    """Barras horizontais: quanto foi gasto em cada motivo."""
    dados = gastos_por_motivo.sort_values("valor", ascending=True)
    fig = go.Figure(
        go.Bar(
            x=dados["valor"],
            y=dados["motivo"],
            orientation="h",
            marker_color=COR_GASTO,
            text=dados["valor"].map(formatar_moeda),
            textposition="auto",
            hoverinfo="skip",
        )
    )
    fig.update_layout(showlegend=False)
    altura = max(260, 52 * len(dados) + 60)
    return _aplicar_layout(fig, altura=altura, horizontal=True)


def grafico_gasto_acumulado(acumulado: pd.DataFrame, total_ganhos: float) -> go.Figure:
    """Gasto acumulado dia a dia, com a linha do total de ganhos como limite."""
    fig = go.Figure(
        go.Scatter(
            x=acumulado["data"],
            y=acumulado["acumulado"],
            mode="lines+markers",
            name="Gasto acumulado",
            line=dict(color=COR_GASTO, width=3),
            fill="tozeroy",
            fillcolor="rgba(229, 72, 77, 0.12)",
        )
    )
    maior_valor = max(total_ganhos, float(acumulado["acumulado"].max()))
    fig.update_yaxes(range=[0, maior_valor * 1.15])

    if total_ganhos > 0:
        fig.add_hline(
            y=total_ganhos,
            line_dash="dash",
            line_color=COR_GANHO,
            annotation_text="Total de ganhos",
            annotation_position="top left",
        )
    fig.update_layout(showlegend=False)
    fig = _aplicar_layout(fig, altura=320)
    fig.update_xaxes(tickformat="%d/%m")
    return fig


def grafico_comparativo_meses(historico: pd.DataFrame) -> go.Figure:
    """Ganhos x gastos de cada mês salvo, com a linha do saldo."""
    meses = historico["ano_mes"].map(rotulo_curto_do_mes)

    fig = go.Figure()
    fig.add_bar(x=meses, y=historico["total_ganhos"], name="Ganhos", marker_color=COR_GANHO)
    fig.add_bar(x=meses, y=historico["total_gastos"], name="Gastos", marker_color=COR_GASTO)
    fig.add_scatter(
        x=meses,
        y=historico["saldo"],
        name="Saldo",
        mode="lines+markers",
        line=dict(color=COR_SALDO, width=3),
    )
    fig.update_layout(barmode="group")
    return _aplicar_layout(fig, altura=380)
