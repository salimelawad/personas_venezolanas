import pandas as pd
import sqlite3

def read_registro():
    df = pd.read_csv('data/registro_electoral_nacional.csv', on_bad_lines='warn')
    return df

def read_resultados():
    df = pd.read_excel('data/resultados_elecc_2013-04-14-v4.xlsx')
    return df

def write_to_sqlite3(df, table):
    conn = sqlite3.connect('data/registro.db')
    df.to_sql(table, conn, if_exists='replace', index=False)

def read_from_sqlite3(filters={}):
    conn = sqlite3.connect('data/registro.db')
    WHERES = " ".join([f"AND {key} LIKE '%{value}%'" for key, value in filters.items() if value != ''])
    query = f"""
    SELECT * FROM registro
    left join (SELECT distinct Municipio, Parroquia, codigo_viejo FROM resultados) as r
    on registro.cod_centro = r.codigo_viejo
    WHERE 1=1
    {WHERES}
    limit 100
    """
    df = pd.read_sql(query, conn)
    return df

def init_db():
    # df = read_registro()
    df2 = read_resultados()
    df2['cod_par'] = df2['cod_par'].astype(int, errors='ignore')
    df2.columns = df2.columns.str.replace(r'\s+', '_', regex=True)
    df2['codigo_viejo'] = df2['codigo_viejo'].astype(int, errors='ignore')
    # write_to_sqlite3(df, 'registro')
    write_to_sqlite3(df2, 'resultados')

if __name__ == '__main__':
    conn = sqlite3.connect('data/registro.db')
    query = 'SELECT cod_par FROM resultados limit 1000'
    df = pd.read_sql(query, conn)
    print(df)
