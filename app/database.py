import pandas as pd
import duckdb

def read_registro():
    df = pd.read_csv('data/registro_electoral_nacional.csv', on_bad_lines='warn')
    return df

def read_resultados():
    df = pd.read_excel('data/resultados_elecc_2013-04-14-v4.xlsx')
    df.columns = df.columns.str.replace(r'\s+', '_', regex=True)
    return df

def resultados_to_csv():
    df = read_resultados()
    df.to_csv('data/resultados.csv', index=False)

def read_from_duckdb(filters: dict):
    WHERES = " ".join([f"AND {key} ILIKE  '%{value}%'" for key, value in filters.items() if value != ''])

    query = f"""
        SELECT cedula,primer_apellido,segundo_apellido,primer_nombre,segundo_nombre,Estado,Municipio,Parroquia 
        FROM registro
        LEFT JOIN (SELECT DISTINCT Estado, Municipio, Parroquia, codigo_viejo FROM resultados) AS r
        ON registro.cod_centro = r.codigo_viejo
        WHERE 1=1
        {WHERES}
        LIMIT 100
    """

    con = duckdb.connect()
    # Read the CSV file with duckdb, ignoring errors
    con.execute("CREATE TABLE registro AS SELECT * FROM read_csv_auto('data/registro_electoral_nacional.csv', ignore_errors=True)")
    con.execute("CREATE TABLE resultados AS SELECT * FROM read_csv_auto('data/resultados.csv', ignore_errors=True)")

    data = con.execute(query).df()

    return data



if __name__ == '__main__':
    resultados_to_csv()