import pandas as pd
import numpy as np
from datetime import datetime
from dateutil.relativedelta import relativedelta

from ax_function import ax_2

param_etude = pd.DataFrame(pd.read_csv("Tables\Parametre_etude\param_etude_bis.csv", sep = ";"))

def convert_date(date) :
    return datetime.strptime(date, "%d/%m/%Y")

def informations_creation_conjoint(raison_sociale) :
    #On crée un df avec uniquement les infos de la raison sociale
    param_contrat = param_etude[param_etude["Raison sociale"] == raison_sociale.upper()]

    #On récupère la dernière année
    millesime_max = max(param_contrat["Milésime de rattachement"])
    param_contrat = param_contrat[param_contrat["Milésime de rattachement"] == millesime_max]

    methode_ecart_age = param_contrat["Méthode pour l\'écart d\'âge"]
    ecart_age = param_contrat["Hypothèse de différence d\'âges"]

    return methode_ecart_age.values[0], ecart_age.values[0] #values permet de récupérer uniquement la valeur et pas les autres informations

def sexe_conjoint_fictif(df) :
    #On crée un conjoint fictif du sexe opposé
    
    df["sexe_Y"] = np.where(df["sexe_X"] == "H", "F", "H")

    return df

def date_naissance_conjoint_fictif(df) :
    #On crée la date de naissance du conjoint fictif à partir de la table de paramétrage contrat
    for index, row in df.iterrows():
        infos = informations_creation_conjoint(row["Raison sociale"])
        methode_ecart_age = infos[0]
        ecart_age = infos[1]
        
        if isinstance(methode_ecart_age, float) and np.isnan(methode_ecart_age) :
            df.at[index, "date_naissance_Y"] = (row["date_naissance_X"]).strftime("%d/%m/%Y")

        else :
            ecart_age = int(ecart_age) #c'est un float au départ
            df.at[index, "date_naissance_Y"] = (row["date_naissance_X"] + relativedelta(years = ecart_age)).strftime("%d/%m/%Y")

    return df

def formattage(df) :
    df = pd.DataFrame(df)
    #On renomme les colonnes
    df.columns = ["Raison sociale", "date_naissance_X", "sexe_X", "date_naissance_Y", "sexe_Y", "date_liquidation", "date_evaluation", "fractionnement", "taux_reversion", "prorata_deces", "terme", "contre_assurance", "frais_sur_rente", "montant_droits"]

    #On transforme la data pour qu'elle soit expoloitable
    df["taux_reversion"] = df["taux_reversion"].fillna(0)
    df["fractionnement"].replace({"M" : 12, "T" : 4, "S" : 2, "A" : 1}, inplace= True)
    df["date_naissance_X"] = df["date_naissance_X"].apply(convert_date)
    df["date_liquidation"] = df["date_liquidation"].apply(convert_date)
    df["date_evaluation"] = df["date_evaluation"].apply(convert_date)

    #Traitement des conjoints
    df = sexe_conjoint_fictif(df)
    df = date_naissance_conjoint_fictif(df)
    df["date_naissance_Y"] = df["date_naissance_Y"].apply(convert_date)
    df["sexe_X"].replace({"H" : 1, "F" : 0}, inplace= True)
    df["sexe_Y"].replace({"H" : 1, "F" : 0}, inplace= True)

    return df

def calcul_ax(df) :
    df["annuitesX2"] = df.apply(lambda row : ax_2(row["date_naissance_X"], row["sexe_X"], row["date_naissance_Y"], row["sexe_Y"], row["date_liquidation"], row["date_evaluation"], row["fractionnement"], row["taux_reversion"], row["prorata_deces"], row["terme"], row["contre_assurance"], row["frais_sur_rente"]), axis = 1)
    df["annuitesX2_hors_frais_sur_rente"] = df.apply(lambda row : ax_2(row["date_naissance_X"], row["sexe_X"], row["date_naissance_Y"], row["sexe_Y"], row["date_liquidation"], row["date_evaluation"], row["fractionnement"], row["taux_reversion"], row["prorata_deces"], row["terme"], row["contre_assurance"], 0), axis = 1)
    
    return df

def calcul_provisions(df) :
    df["montant_provision"] = df["annuitesX2"] * df["montant_droits"]
    df["montant_provision_hors_frais_sur_rente"] = df["annuitesX2_hors_frais_sur_rente"] * df["montant_droits"]

    return df



