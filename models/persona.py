class Persona:
    def __init__(self, nombre):
        self.nombre = nombre
        self.movimientos = []

    def registrar_movimiento(self, movimiento):
        self.movimientos.append(movimiento)

    def calcular_totales(self):
        ingresos = sum(m.monto for m in self.movimientos if m.tipo == 'ingreso')
        gastos = sum(m.monto for m in self.movimientos if m.tipo == 'gasto')
        return ingresos, gastos

    def resumen_por_categoria(self):
        resumen = {}
        for m in self.movimientos:
            if m.categoria not in resumen:
                resumen[m.categoria] = 0
            resumen[m.categoria] += m.monto
        return resumen

    def generar_alertas(self, presupuesto):
        alertas = []
        resumen = self.resumen_por_categoria()
        for cat, monto in resumen.items():
            if cat in presupuesto.limites and monto > presupuesto.limites[cat]:
                alertas.append(f"Gasto excesivo en {cat}: ${monto} (límite: ${presupuesto.limites[cat]})")
        return alertas
