import pandas as pd
import streamlit as st
from database import read_from_sqlite3

# load the csv file. Some rows may have extra commans, causing pandas to fail
# df = pd.read_csv('registro_electoral_nacional.csv'




def main():
    st.set_page_config(page_title='Buscador de Venezolano', page_icon='🇻🇪', layout='wide')
    st.title('Buscador de Venezolano')

    # ask for optional filters
    cedula = st.text_input('Cedula')
    primer_nombre = st.text_input('Primer Nombre').strip()
    segundo_nombre = st.text_input('Segundo Nombre').strip()
    primer_apellido = st.text_input('Primer Apellido').strip()
    segundo_apellido = st.text_input('Segundo Apellido').strip()

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
    st.dataframe(filtered_df, hide_index=True)

main()