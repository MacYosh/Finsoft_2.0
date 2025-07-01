
class Presupuesto:
    def __init__(self, presupuestos_mensuales=None):
        self.presupuestos_mensuales = presupuestos_mensuales if presupuestos_mensuales is not None else {}

    def establecer_presupuesto(self, mes, categoria, monto):
        if mes not in self.presupuestos_mensuales:
            self.presupuestos_mensuales[mes] = {}
        self.presupuestos_mensuales[mes][categoria] = monto

    def obtener_presupuesto(self, mes, categoria):
        return self.presupuestos_mensuales.get(mes, {}).get(categoria, 0)
