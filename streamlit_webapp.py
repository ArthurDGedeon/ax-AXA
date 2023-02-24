import streamlit as st
import pandas as pd
import base64
from datetime import datetime

import calculs_df

def download_csv(df):
    csv = df.to_csv(sep = ";", index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # encode the data into base64 format
    href = f'<a href="data:file/csv;base64,{b64}" download="download.csv">Download CSV File</a>'
    return href

st.title("Calcul des ax AXA")
st.write("Ceci est une application web qui permet de déposer un fichier CSV contenant toutes les données nécessaires au calcul des ax AXA et qui renvoie un fichier CSV contenant les résultats")

uploaded_file = st.file_uploader("Upload a CSV file", type = "csv")
if uploaded_file is not None :
    df = pd.read_csv(uploaded_file, sep = ";")
    df_to_return = calculs_df.formattage(df)
    if st.button("Download processed CSV file") :
        st.markdown(download_csv(df_to_return), unsafe_allow_html=True)
