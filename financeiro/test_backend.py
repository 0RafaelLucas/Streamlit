"""Teste rápido do backend (rode: python test_backend.py)."""

from datetime import date
from pathlib import Path

from backend.database import get_connection
from backend.services import FinanceiroService, ValidacaoError

service = FinanceiroService(get_connection(Path(":memory:")))
mes = "2026-10"

service.definir_salario_base(mes, 1000)
service.adicionar_gasto(150.50, "Mercado", date(2026, 10, 2))
service.adicionar_gasto(80, "Transporte", date(2026, 10, 5))
service.adicionar_gasto(49.5, "Mercado", date(2026, 10, 7))
service.adicionar_ganho_extra(200, "Dívida recebida", date(2026, 10, 6))

resumo = service.salvar_fechamento(mes)
assert resumo.total_ganhos == 1200 and resumo.total_gastos == 280 and resumo.saldo == 920

service.adicionar_ganho_extra(100, "Freela", date(2026, 10, 20))
service.salvar_fechamento(mes)  # salva de novo, sobrescrevendo
historico = service.historico_mensal()
assert len(historico) == 1 and historico.loc[0, "saldo"] == 1020

service.definir_salario_base("2026-11", 1000)
service.adicionar_gasto(300, "Aluguel", date(2026, 11, 1))
service.salvar_fechamento("2026-11")
assert len(service.historico_mensal()) == 2

print(service.gastos_por_motivo(mes))
print(service.gastos_acumulados_no_mes(mes))
print(service.historico_mensal())

try:
    service.adicionar_gasto(-5, "x", date.today())
except ValidacaoError as error:
    print("Validação ok:", error)

print("Todos os testes passaram.")
