import pandas as pd
import streamlit as st
from database import read_from_sqlite3

# load the csv file. Some rows may have extra commans, causing pandas to fail
# df = pd.read_csv('registro_electoral_nacional.csv'




def main():
    st.title('Buscador de Venezolano')

    # ask for optional filters
    cedula = st.text_input('Cedula')
    primer_nombre = st.text_input('Primer Nombre')
    segundo_nombre = st.text_input('Segundo Nombre')
    primer_apellido = st.text_input('Primer Apellido')
    segundo_apellido = st.text_input('Segundo Apellido')

    # filter the dataframe based on the provided filters

    filters = {
        'cedula': cedula,
        'primer_nombre': primer_nombre,
        'segundo_nombre': segundo_nombre,
        'primer_apellido': primer_apellido,
        'segundo_apellido': segundo_apellido,
    }

    filtered_df = read_from_sqlite3(filters)

    # show the filtered dataframe
    st.write(filtered_df)

main()