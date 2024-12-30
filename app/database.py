import pandas as pd
import duckdb
import os

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

def split_csv_file(file, size):
    if not os.path.exists('data/registro/'):
        os.makedirs('data/registro/')

    with open(file, 'r') as f:
        header = f.readline()
        rows = []
        current_size = 0
        part = 0

        for line in f:
            rows.append(line)
            current_size += len(line.encode('utf-8'))
            if current_size >= size:
                with open(f'data/registro/split_{part}.csv', 'w') as split_file:
                    split_file.write(header)
                    split_file.writelines(rows)
                rows = []
                current_size = 0
                part += 1

        if rows:
            with open(f'data/registro/split_{part}.csv', 'w') as split_file:
                split_file.write(header)
                split_file.writelines(rows)


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
    con.execute("PRAGMA memory_limit='.5GB'")
    con.execute("CREATE TABLE registro AS SELECT * FROM read_csv_auto('data/registro/*.csv', ignore_errors=True)")
    con.execute("CREATE TABLE resultados AS SELECT * FROM read_csv_auto('data/resultados.csv', ignore_errors=True)")

    data = con.execute(query).df()

    return data



if __name__ == '__main__':
    resultados_to_csv()
    split_csv_file('data/registro_electoral_nacional.csv', 50_000_000)