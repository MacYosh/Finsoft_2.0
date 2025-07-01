import pandas as pd
import json
from models.concepts import PREDEFINED_CONCEPTS
from models.entry import Entry
from models.persona import Persona
from datetime import datetime
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

class FinanceService:
    def __init__(self):
        self.usuarios = {}

    def load_data(self):
        try:
            with open("data/entries.json", "r") as f:
                data = json.load(f)
                for item in data:
                    usuario = item.get("usuario", "anonimo")
                    if usuario not in self.usuarios:
                        self.usuarios[usuario] = Persona(usuario)
                    entry = Entry(item["date"], item["amount"], item["concept"], item["type"], item.get("notas", ""))
                    self.usuarios[usuario].registrar_movimiento(entry)
        except FileNotFoundError:
            print("Archivo de datos no encontrado. Se creará uno nuevo.")

    def save_data(self):
        with open("data/entries.json", "w") as f:
            all_data = []
            for usuario, persona in self.usuarios.items():
                for mov in persona.movimientos:
                    d = mov.__dict__.copy()
                    d["usuario"] = usuario
                    all_data.append(d)
            json.dump(all_data, f, indent=2)

    def add_entry(self, usuario, date, amount, concept, type_, notas):
        if concept not in PREDEFINED_CONCEPTS[type_]:
            print("Concepto no válido.")
            return
        if usuario not in self.usuarios:
            self.usuarios[usuario] = Persona(usuario)
        entry = Entry(date, amount, concept, type_, notas)
        self.usuarios[usuario].registrar_movimiento(entry)
        self.save_data()

    def generate_monthly_summary(self, usuario):
        persona = self.usuarios.get(usuario)
        if not persona:
            print("Usuario no encontrado.")
            return

        print("\nResumen mensual personalizado:")

        if not persona.movimientos:
            print("No hay entradas registradas.")
            return

        mes = input("Ingrese el mes a consultar (formato YYYY-MM): ").strip()
        
        tipo = input("¿Desea ver solo ingresos, gastos o todos? (income/expense/todos): ").strip().lower()
        if tipo not in ["income", "expense", "todos"]:
            print("Tipo no válido. Mostrando todos.")
            tipo = "todos"

        aplicar_filtro_monto = input("¿Desea filtrar por monto mínimo y máximo? (s/n): ").strip().lower()
        min_monto = 0
        max_monto = float("inf")
        if aplicar_filtro_monto == 's':
            try:
                min_monto = float(input("Monto mínimo: "))
                max_monto = float(input("Monto máximo: "))
            except ValueError:
                print("Valores inválidos. Se usará el rango completo.")

        filtradas = []
        for entry in persona.movimientos:
            if not entry.date.startswith(mes):
                continue
            if tipo != "todos" and entry.type != tipo:
                continue
            if not (min_monto <= entry.amount <= max_monto):
                continue
            filtradas.append(entry)

        if not filtradas:
            print("No hay movimientos que coincidan con los filtros.")
            return

        filtradas.sort(key=lambda x: datetime.strptime(x.date, '%Y-%m-%d'))
        for entry in filtradas:
            tipo_mov = "INGRESO" if entry.type == "income" else "GASTO"
            print(f"- {entry.date} | {tipo_mov} | {entry.concept}: ${entry.amount:.2f} | {entry.notas}")
        
        total = sum(e.amount for e in filtradas)
        print(f"\nTotal filtrado: ${total:.2f}")

    def generate_projections(self):
        print("\nProyecciones (simuladas):")
        print("Gasto estimado el próximo mes: $5000")
        print("Ingreso estimado el próximo mes: $7000")

    def proyeccion_media_movil(self, usuario, meses=3):
        from collections import defaultdict
        import pandas as pd

        persona = self.usuarios.get(usuario)
        if not persona:
            print("Usuario no encontrado.")
            return

        if not persona.movimientos:
            print("No hay datos suficientes para proyectar.")
            return

        df = pd.DataFrame([e.__dict__ for e in persona.movimientos])
        df["date"] = pd.to_datetime(df["date"])
        df["month"] = df["date"].dt.to_period("M").astype(str)
        
        resumen = df.groupby(["month", "type"])["amount"].sum().unstack(fill_value=0)
        if len(resumen) < meses:
            print("No hay suficientes meses registrados para calcular una proyección.")
            return

        promedio = resumen.tail(meses).mean()
        print("\nProyección basada en la media de los últimos", meses, "meses:")
        print(f"- Gasto estimado: ${promedio.get('expense', 0):.2f}")
        print(f"- Ingreso estimado: ${promedio.get('income', 0):.2f}")
        print(f"- Balance estimado: ${(promedio.get('income', 0) - promedio.get('expense', 0)):.2f}")

    def proyeccion_tendencia_lineal(self, usuario):

        persona = self.usuarios.get(usuario)
        if not persona:
            print("Usuario no encontrado.")
            return

        if not persona.movimientos:
            print("No hay datos suficientes para proyectar.")
            return
        try:
            meses = int(input("¿Cuántos meses recientes quieres usar para la proyección? (por defecto 3): ") or 3)
        except ValueError:
            meses = 3

        df = pd.DataFrame([e.__dict__ for e in persona.movimientos])
        df["date"] = pd.to_datetime(df["date"])
        df["month"] = df["date"].dt.to_period("M").astype(str)

        resumen = df.groupby(["month", "type"])["amount"].sum().unstack(fill_value=0).reset_index()
        resumen = resumen.tail(meses).copy()
        resumen["month_num"] = range(1, len(resumen) + 1)

        modelo = LinearRegression()

        for tipo in ["income", "expense"]:
            if tipo in resumen:
                X = resumen[["month_num"]]
                y = resumen[tipo]
                modelo.fit(X, y)
                next_month = np.array([[resumen["month_num"].iloc[-1] + 1]])
                pred = modelo.predict(pd.DataFrame({"month_num": [resumen["month_num"].iloc[-1] + 1]}))[0]
                print(f"- Proyección de {tipo}: ${pred:.2f}")
            else:
                print(f"- No hay datos para proyectar {tipo}.")

        if "income" in resumen and "expense" in resumen:
            resumen["balance"] = resumen["income"] - resumen["expense"]
            y_bal = resumen["balance"]
            modelo.fit(resumen[["month_num"]], y_bal)
            pred_bal = modelo.predict([[resumen["month_num"].iloc[-1] + 1]])[0]
            print(f"- Proyección de balance: ${pred_bal:.2f}")

    def provide_advice(self, usuario):
        print("\nConsejos financieros personalizados:")

        from collections import Counter, defaultdict
        from advice.tips import FINANCIAL_TIPS
        from datetime import date

        persona = self.usuarios.get(usuario)
        if not persona:
            print("Usuario no encontrado.")
            return

        if not persona.movimientos:
            print("No hay datos para analizar.")
            return

        today = date.today()
        if today.month == 1:
            mes_anterior = f"{today.year - 1}-12"
        else:
            mes_anterior = f"{today.year}-{today.month - 1:02d}"

        movimientos_mes_anterior = [m for m in persona.movimientos if m.date.startswith(mes_anterior)]
        if not movimientos_mes_anterior:
            print(f"No hay datos del mes {mes_anterior} para analizar.")
            return
        incomes = [e for e in movimientos_mes_anterior if e.type == "income"]
        expenses = [e for e in movimientos_mes_anterior if e.type == "expense"]

        total_income = sum(e.amount for e in incomes)
        total_expense = sum(e.amount for e in expenses)

        concept_expense_totals = defaultdict(float)
        for e in expenses:
            concept_expense_totals[e.concept] += e.amount

        concept_income_totals = defaultdict(float)
        for e in incomes:
            concept_income_totals[e.concept] += e.amount

        print(f"\n Ingresos totales: ${total_income:.2f}")
        print(f" Gastos totales: ${total_expense:.2f}")
        print(f" Balance actual: ${total_income - total_expense:.2f}")

        if total_income > 0:
            ahorro_ideal = total_income * 0.20
            print(f"\n💰 Consejo de ahorro: Intenta ahorrar al menos el 20% de tus ingresos: ${ahorro_ideal:.2f}")

        for concepto, gasto in concept_expense_totals.items():
            porcentaje = (gasto / total_income) * 100 if total_income > 0 else 0
            print(f"\n Gasto en '{concepto}': ${gasto:.2f} ({porcentaje:.1f}% del ingreso)")
            if concepto in FINANCIAL_TIPS:
                print(f" Consejo: {FINANCIAL_TIPS[concepto]}")
            else:
                print(" Consejo general: Intenta mantener este gasto por debajo del 10% del ingreso.")

        for concepto, ingreso in concept_income_totals.items():
            porcentaje = (ingreso / total_income) * 100 if total_income > 0 else 0
            print(f"\n Ingreso por '{concepto}': ${ingreso:.2f} ({porcentaje:.1f}% del total)")
            if concepto in FINANCIAL_TIPS:
                print(f" Consejo: {FINANCIAL_TIPS[concepto]}")
    def proyeccion_promedio_movil_con_tendencia(self, usuario, meses=3):
        persona = self.usuarios.get(usuario)
        if not persona:
            print("Usuario no encontrado.")
            return

        if not persona.movimientos:
            print("No hay datos suficientes para proyectar.")
            return

        df = pd.DataFrame([e.__dict__ for e in persona.movimientos])
        df["date"] = pd.to_datetime(df["date"])
        df["month"] = df["date"].dt.to_period("M").astype(str)

        resumen = df.groupby(["month", "type"])["amount"].sum().unstack(fill_value=0).reset_index()
        resumen = resumen.tail(meses).copy()
        resumen["month_num"] = range(1, len(resumen) + 1)

        modelo = LinearRegression()

        print(f"\nProyección combinando media móvil y tendencia lineal sobre los últimos {meses} meses:")

        for tipo in ["income", "expense"]:
            if tipo in resumen:
                X = resumen[["month_num"]]
                y = resumen[tipo]
                media = y.mean()
                modelo.fit(X, y)
                pred_lineal = modelo.predict([[resumen["month_num"].iloc[-1] + 1]])[0]
                proyeccion_combinada = (pred_lineal + media) / 2
                print(f"- {tipo.capitalize()}: ${proyeccion_combinada:.2f}")
            else:
                print(f"- No hay datos para proyectar {tipo}.")

        if "income" in resumen and "expense" in resumen:
            resumen["balance"] = resumen["income"] - resumen["expense"]
            y_bal = resumen["balance"]
            media_bal = y_bal.mean()
            modelo.fit(resumen[["month_num"]], y_bal)
            pred_lineal_bal = modelo.predict([[resumen["month_num"].iloc[-1] + 1]])[0]
            proyeccion_balance = (pred_lineal_bal + media_bal) / 2
            print(f"- Balance proyectado: ${proyeccion_balance:.2f}")