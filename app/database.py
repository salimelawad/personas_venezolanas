import pandas as pd
import os
from sqlalchemy import create_engine, text

POSTGRES_IP = os.getenv("POSTGRES_IP")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DATABASE = os.getenv("POSTGRES_DATABASE")

CONNECTION_STRING = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_IP}:{POSTGRES_PORT}/{POSTGRES_DATABASE}"


def read_registro():
    # Handle malformed CSV lines better - skip bad lines and continue
    df = pd.read_csv(
        "data/registro_electoral_nacional.csv",
        on_bad_lines="skip",  # Skip instead of warn to avoid noise
        low_memory=False,  # Better type inference
    )
    return df


def read_resultados():
    df = pd.read_excel("data/resultados_elecc_2013-04-14-v4.xlsx")
    df.columns = df.columns.str.replace(r"\s+", "_", regex=True)
    return df


def resultados_to_csv():
    df = read_resultados()
    df.to_csv("data/resultados.csv", index=False)


def split_csv_file(file, size):
    if not os.path.exists("data/registro/"):
        os.makedirs("data/registro/")

    with open(file, "r") as f:
        header = f.readline()
        rows = []
        current_size = 0
        part = 0

        for line in f:
            rows.append(line)
            current_size += len(line.encode("utf-8"))
            if current_size >= size:
                with open(f"data/registro/split_{part}.csv", "w") as split_file:
                    split_file.write(header)
                    split_file.writelines(rows)
                rows = []
                current_size = 0
                part += 1

        if rows:
            with open(f"data/registro/split_{part}.csv", "w") as split_file:
                split_file.write(header)
                split_file.writelines(rows)


def set_up_postgres():
    # Reads data, authenticates into postgres, creates table in database "personasvenezolanas"
    # Create connection string for pandas with performance optimizations
    print("Reading data...")
    # Read the data using existing functions
    registro_df = read_registro()
    resultados_df = read_resultados()

    print("Writing resultados table...")
    # Also create the resultados table to mimic DuckDB functionality
    resultados_df.to_sql(
        "resultados",
        CONNECTION_STRING,
        if_exists="replace",
        index=False,
        method="multi",
        chunksize=500000,  # Larger chunks for smaller table
    )

    print("Writing registro table...")
    # Use COPY method for fastest bulk insert - much faster than multi
    registro_df.to_sql(
        "registro",
        CONNECTION_STRING,
        if_exists="replace",
        index=False,
        method="multi",
        chunksize=500000,
    )


def precompute_registro_resultados():
    connection_string = f"postgresql://{USER}:{PASSWORD}@{IP}:{PORT}/{DATABASE}"
    print("Precomputing registro-resultados join...")
    with create_engine(connection_string).connect() as conn:
        conn.execute(text("DROP TABLE IF EXISTS registro_resultados_precomputed"))
        conn.execute(
            text(
                """
                CREATE TABLE registro_resultados_precomputed AS
                SELECT
                    registro."cedula",
                    registro."primer_apellido",
                    registro."segundo_apellido",
                    registro."primer_nombre",
                    registro."segundo_nombre",
                    r."Estado",
                    r."Municipio",
                    r."Parroquia"
                FROM registro
                LEFT JOIN (
                    SELECT DISTINCT "Estado", "Municipio", "Parroquia", "codigo_viejo"
                    FROM resultados
                ) AS r
                ON registro."cod_centro" = r."codigo_viejo"
                """
            )
        )
        conn.commit()
        create_trgm_indexes()


def create_trgm_indexes():
    print("Creating GIN trigram indexes...")

    with create_engine(CONNECTION_STRING).connect() as conn:
        # Ensure pg_trgm is enabled
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm"))

        # GIN + trigram indexes for substring search support
        conn.execute(
            text(
                "CREATE INDEX IF NOT EXISTS idx_registro_results_cedula "
                'ON registro_resultados_precomputed ("cedula")'
            )
        )
        conn.execute(
            text(
                "CREATE INDEX IF NOT EXISTS idx_registro_resultados_primer_apellido_trgm "
                'ON registro_resultados_precomputed USING GIN ("primer_apellido" gin_trgm_ops)'
            )
        )
        conn.execute(
            text(
                "CREATE INDEX IF NOT EXISTS idx_registro_resultados_primer_nombre_trgm "
                'ON registro_resultados_precomputed USING GIN ("primer_nombre" gin_trgm_ops)'
            )
        )
        conn.execute(
            text(
                "CREATE INDEX IF NOT EXISTS idx_registro_resultados_segundo_apellido_trgm "
                'ON registro_resultados_precomputed USING GIN ("segundo_apellido" gin_trgm_ops)'
            )
        )
        conn.execute(
            text(
                "CREATE INDEX IF NOT EXISTS idx_registro_resultados_segundo_nombre_trgm "
                'ON registro_resultados_precomputed USING GIN ("segundo_nombre" gin_trgm_ops)'
            )
        )
        conn.commit()


def read_from_postgres(filters: dict):
    engine = create_engine(CONNECTION_STRING)
    with engine.connect() as conn:
        query = """
            SELECT "cedula", "primer_apellido", "segundo_apellido", "primer_nombre", "segundo_nombre",
                   "Estado", "Municipio", "Parroquia"
            FROM registro_resultados_precomputed
            WHERE 1=1
        """
        params = {}
        for i, (key, value) in enumerate(filters.items()):
            if value:
                param_name = f"param_{i}"
                query += f' AND "{key}" ILIKE :{param_name}'
                params[param_name] = f"%{value}%"
        query += " LIMIT 100"
        print(f"Query: {query}")
        print(f"Params: {params}")
        df = pd.read_sql(text(query), conn, params=params)
    return df


if __name__ == "__main__":
    create_trgm_indexes()
    # print(read_from_postgres({"primer_apellido": "Gonzalez"}))
