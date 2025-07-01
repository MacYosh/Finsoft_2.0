from models.movimiento import Movimiento
from models.presupuesto import Presupuesto
from models.persona import Persona

class Alerta:
    def __init__(self, mensaje):
        self.mensaje = mensaje

    def __str__(self):
        return f"⚠️ {self.mensaje}"

    @classmethod
    def generar(cls, persona: Persona, presupuesto: Presupuesto, mes: str):
        alertas = []
        resumen = persona.resumen_por_categoria(mes)
        for cat, monto in resumen.items():
            limite = presupuesto.obtener_presupuesto(mes, cat)
            if limite > 0 and monto > limite:
                mensaje = f"En {mes}, gasto excesivo en {cat}: ${monto:.2f} (presupuesto: ${limite:.2f})"
                alertas.append(cls(mensaje))
        return alertas
