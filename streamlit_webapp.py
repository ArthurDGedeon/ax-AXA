import streamlit as st
import pandas as pd
import base64
from datetime import datetime

from ax_function import ax, ax_2

def download_csv(df):
    csv = df.to_csv(sep = ";", index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # encode the data into base64 format
    href = f'<a href="data:file/csv;base64,{b64}" download="download.csv">Download CSV File</a>'
    return href

def convert_date(date) :
    return datetime.strptime(date, "%d/%m/%Y")

def calculs_df(df) :
    df = pd.DataFrame(df)
    #On renomme les colonnes
    df.columns = ["date_naissance_X", "sexe_X", "date_naissance_Y", "sexe_Y", "date_liquidation", "date_evaluation", "fractionnement", "taux_reversion", "prorata_deces", "terme", "contre_assurance", "frais_sur_rente", "rattrapage_rente"]

    #On transforme la data pour qu'elle soit expoloitable
    df["taux_reversion"] = df["taux_reversion"].fillna(0)
    df["date_naissance_Y"] = df["date_naissance_Y"].fillna(df["date_naissance_X"])
    df["sexe_Y"] = df["sexe_Y"].fillna(df["sexe_X"])
    df["sexe_X"].replace({"H" : 1, "F" : 0}, inplace= True)
    df["sexe_Y"].replace({"H" : 1, "F" : 0}, inplace= True)
    df["fractionnement"].replace({"M" : 12, "T" : 4, "S" : 2, "A" : 1}, inplace= True)
    df["rattrapage_rente"].replace({"VRAI" : True, "FAUX" : False}, inplace= True)

    #On transforme les dates en datetime
    df["date_naissance_X"] = df["date_naissance_X"].apply(convert_date)
    df["date_naissance_Y"] = df["date_naissance_Y"].apply(convert_date)
    df["date_liquidation"] = df["date_liquidation"].apply(convert_date)
    df["date_evaluation"] = df["date_evaluation"].apply(convert_date)

    #On calcule l'ax 
    df["annuitésX2"] = df.apply(lambda row : ax_2(row["date_naissance_X"], row["sexe_X"], row["date_naissance_Y"], row["sexe_Y"], row["date_liquidation"], row["date_evaluation"], row["fractionnement"], row["taux_reversion"], row["prorata_deces"], row["terme"], row["contre_assurance"], row["frais_sur_rente"]), axis =1)
    df["Sannuité2"] = df.apply(lambda row : ax(row["date_naissance_X"], row["sexe_X"], row["date_naissance_Y"], row["sexe_Y"], row["date_liquidation"], row["date_evaluation"], row["terme"], row["fractionnement"], row["prorata_deces"], row["taux_reversion"], row["rattrapage_rente"], row["contre_assurance"], row["frais_sur_rente"]), axis =1)

    return df

st.title("Calcul des ax AXA")
st.write("Ceci est une application web qui permet de déposer un fichier CSV contenant toutes les données nécessaires au calcul des ax AXA et qui renvoie un fichier CSV contenant les résultats")

uploaded_file = st.file_uploader("Upload a CSV file", type = "csv")
if uploaded_file is not None :
    df = pd.read_csv(uploaded_file, sep = ";")
    df_to_return = calculs_df(df)
    if st.button("Download processed CSV file") :
        st.markdown(download_csv(df_to_return), unsafe_allow_html=True)
