from services.finance_service import FinanceService
from datetime import datetime

def main():
    service = FinanceService()
    print("Bienvenido al sistema de gestión financiera personal FINSOFT.")
    print("Profe Alex inicie sesión con el nombre de usuario 'yoshua' con fines de prueba.")
    usuario = input("Ingrese su nombre de usuario: ").strip()
    if not usuario:
        print("Debe ingresar un nombre de usuario.")
        return
    service.load_data()

    while True:
        print("\nMenú:")
        print("1. Agregar ingreso")
        print("2. Agregar gasto")
        print("3. Ver resumen mensual")
        print("4. Ver proyecciones")
        print("5. Ver consejos financieros")
        print("6. Definir presupuestos por categoría")
        print("0. Salir")

        choice = input("Seleccione una opción: ")
        if choice == "1" or choice == "2":
            type_ = "income" if choice == "1" else "expense"
            from models.concepts import PREDEFINED_CONCEPTS
            print(f"Conceptos para {type_}: {PREDEFINED_CONCEPTS[type_]}")
            concept = input("Ingrese el concepto: ")
            if concept not in PREDEFINED_CONCEPTS[type_]:
                print("Concepto no válido.")
                continue
            elif concept == "Otros":
                concept = input("Ingrese el nuevo concepto: ")
                if not concept:
                    print("Concepto no puede estar vacío.")
                    continue
                if concept in PREDEFINED_CONCEPTS[type_]:
                    print("Concepto ya existe.")
                    continue
                PREDEFINED_CONCEPTS[type_].append(concept)
                print(f"Concepto '{concept}' agregado.")
                continue
            amount = float(input("Ingrese el monto: "))
            date = datetime.today().strftime('%Y-%m-%d')
            notas= input("Ingrese notas (opcional): ")
            if notas == "":
                notas = None
            else:
                notas = notas.strip()
            service.add_entry(usuario, date, amount, concept, type_, notas)
        elif choice == "3":
            service.generate_monthly_summary(usuario)
        elif choice == "4":
            print("Selecciona el metodo de proyección:")
            print("1. Promedio móvil")
            print("2. Tendencia lineal")
            print("3. Tendencia exponencial")
            print("4. Promedio móvil con tendencia")
            projection_type = input("Ingrese el número de la opción: ")
            if projection_type not in ["1", "2", "3", "4"]:
                print("Opción no válida.")
                continue
            if projection_type == "1":
                try:
                    meses = int(input("¿Cuántos meses recientes quieres usar para la proyección? (por defecto 3): ") or "3")
                except ValueError:
                    print("Entrada inválida. Se usará el valor por defecto de 3 meses.")
                    meses = 3
                print("Generando proyección de promedio móvil...")
                service.proyeccion_media_movil(usuario, meses)
            elif projection_type == "2":
                print("Generando proyección de tendencia lineal...")
                service.proyeccion_tendencia_lineal(usuario)
            elif projection_type == "3":
                print("Generando proyección de tendencia exponencial...")
                service.proyeccion_tendencia_exponencial(usuario)
            elif projection_type == "4":
                try:
                    meses = int(input("¿Cuántos meses recientes quieres usar para la proyección? (por defecto 3): ") or "3")
                except ValueError:
                    print("Entrada inválida. Se usará el valor por defecto de 3 meses.")
                    meses = 3
                print("Generando proyección de promedio móvil con tendencia...")
                service.proyeccion_promedio_movil_con_tendencia(usuario, meses)
        elif choice == "5":
            service.provide_advice(usuario)
        elif choice == "6":
            from models.concepts import PREDEFINED_CONCEPTS
            from models.presupuesto import Presupuesto
            persona = service.usuarios.get(usuario)
            if not persona:
                print("Usuario no encontrado.")
                continue
            mes = input("Ingresa el mes para el presupuesto (formato YYYY-MM): ").strip()
            if not mes:
                mes = datetime.today().strftime('%Y-%m')
            presupuesto = Presupuesto()
            print("Define el monto presupuestado para cada categoría de gasto.")
            for concepto in PREDEFINED_CONCEPTS["expense"]:
                try:
                    monto = float(input(f"Presupuesto para {concepto}: ") or "0")
                    presupuesto.establecer_presupuesto(mes, concepto, monto)
                except ValueError:
                    print("Entrada inválida. Se asignará 0.")
                    presupuesto.establecer_presupuesto(mes, concepto, 0)
            from models.alerta import Alerta
            alertas = Alerta.generar(persona, presupuesto)
            if alertas:
                print("\n⚠️  Alertas detectadas:")
                for alerta in alertas:
                    print(f"- {alerta}")
            else:
                print("✅ Todo dentro del presupuesto.")
        elif choice == "0":
            break
        else:
            print("Opción no válida.")

if __name__ == "__main__":
    main()
