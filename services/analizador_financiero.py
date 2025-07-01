import matplotlib.pyplot as plt

class AnalizadorFinanciero:
    @staticmethod
    def graficar_resumen_por_categoria(resumen):
        categorias = list(resumen.keys())
        montos = list(resumen.values())

        plt.bar(categorias, montos)
        plt.title("Resumen por Categoría")
        plt.xlabel("Categoría")
        plt.ylabel("Monto")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

    @staticmethod
    def predecir_gasto(promedio_mensual):
        return promedio_mensual
