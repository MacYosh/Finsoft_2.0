import pandas as pd
from models.movimiento import Movimiento

class GestorExcel:
    @staticmethod
    def importar_movimientos(path):
        df = pd.read_excel(path)
        movimientos = []
        for _, row in df.iterrows():
            m = Movimiento(
                fecha=row['Fecha'],
                monto=row['Monto'],
                descripcion=row['Descripcion'],
                categoria=row['Categoria'],
                tipo=row['Tipo'],
                forma_pago=row['FormaPago']
            )
            movimientos.append(m)
        return movimientos

    @staticmethod
    def exportar_movimientos(path, movimientos):
        data = [m.__dict__ for m in movimientos]
        df = pd.DataFrame(data)
        df.to_excel(path, index=False)
