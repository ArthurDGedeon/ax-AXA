import pandas as pd
from datetime import datetime

from ax_function import ax_2

param_etude = pd.DataFrame(pd.read_csv("Tables\Parametre_etude\param_etude.csv", sep = ";"))

def convert_date(date) :
    return datetime.strptime(date, "%d/%m/%Y")

def informations_creation_conjoint(raison_sociale) :
    #On crée un df avec uniquement les infos de la raison sociale
    param_contrat = param_etude[param_etude["Raison sociale"] == raison_sociale]

    #On récupère la dernière année
    millesime_max = max(param_contrat["Milésime de rattachement"])
    param_contrat = param_contrat[param_contrat["Milésime de rattachement"] == millesime_max]

    methode_ecart_age = param_contrat["Méthode pour l\'écart d\'âge"]
    ecart_age = param_contrat["Hypothèse de différence d\'âges"]

    return methode_ecart_age, ecart_age


def formattage(df) :
    df = pd.DataFrame(df)
    #On renomme les colonnes
    df.columns = ["date_naissance_X", "sexe_X", "date_naissance_Y", "sexe_Y", "date_liquidation", "date_evaluation", "fractionnement", "taux_reversion", "prorata_deces", "terme", "contre_assurance", "frais_sur_rente"]

    #On transforme la data pour qu'elle soit expoloitable
    df["taux_reversion"] = df["taux_reversion"].fillna(0)
    df["fractionnement"].replace({"M" : 12, "T" : 4, "S" : 2, "A" : 1}, inplace= True)
    df["date_naissance_X"] = df["date_naissance_X"].apply(convert_date)
    df["date_liquidation"] = df["date_liquidation"].apply(convert_date)
    df["date_evaluation"] = df["date_evaluation"].apply(convert_date)

    #Traitement des conjoints
    df["date_naissance_Y"] = df["date_naissance_Y"].fillna(df["date_naissance_X"]) #On rempli temporairement
    df["sexe_Y"] = df["sexe_Y"].fillna(df["sexe_X"]) #On rempli temporairement
    df["sexe_X"].replace({"H" : 1, "F" : 0}, inplace= True)
    df["sexe_Y"].replace({"H" : 1, "F" : 0}, inplace= True)

    return df


def calcul_ax(df) :
    df["annuitesX2"] = df.apply(lambda row : ax_2(row["date_naissance_X"], row["sexe_X"], row["date_naissance_Y"], row["sexe_Y"], row["date_liquidation"], row["date_evaluation"], row["fractionnement"], row["taux_reversion"], row["prorata_deces"], row["terme"], row["contre_assurance"], row["frais_sur_rente"]), axis =1)
    return df