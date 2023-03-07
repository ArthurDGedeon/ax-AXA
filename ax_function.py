#Librairies utiles
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta
import math

#Import des tables csv

tgh05 = pd.DataFrame(pd.read_csv("Tables\Tables_morta\TGH05.csv", sep = ";"))
tgf05 = pd.DataFrame(pd.read_csv("Tables\Tables_morta\TGF05.csv", sep = ";"))

def lx(age, annee_naissance, sexe) :
    """
    Retourne le nombre de personne d'age x, né l'année n, qui sont encore en vie pour un échantillon donné
    """
    coeff_lin = round(1 - age % 1, 3)
    if sexe == 1 :
        lx_axa = coeff_lin * tgh05.iloc[math.floor(age), annee_naissance - 1900 + 1] + (1 - coeff_lin) * tgh05.iloc[math.floor(age) + 1, annee_naissance - 1900 + 1]
    else :
        lx_axa = coeff_lin * tgf05.iloc[math.floor(age), annee_naissance - 1900 + 1] + (1 - coeff_lin) * tgf05.iloc[math.floor(age) + 1, annee_naissance - 1900 + 1]
    return(round(lx_axa,3))

def fin_annee(date) :
    """
    Retourne le dernier jour de l'année pour une date donnée
    """
    new_date = datetime(date.year, 12, 31)
    return(new_date)

def fin_semestre(date) :
    """
    Retourne le dernier jour du semestres pour une date donnée
    """
    if date.month <= 6 :
        new_date = datetime(date.year, 6, 30)
    else :
        new_date = datetime(date.year, 12, 31)
    return(new_date)

def fin_trimestre(date) :
    """
    Retourne le dernier jour du trimestres pour une date donnée
    """
    if date.month <= 3 :
        new_date = datetime(date.year, 3, 31)
    elif date.month <= 6 :
        new_date = datetime(date.year, 6, 30)
    elif date.month <= 9 :
        new_date = datetime(date.year, 9, 30)
    else :
        new_date = datetime(date.year, 12, 31)
    return(new_date)

def fin_mois(date) :
    """
    Retourne le dernier jour du mois pour une date donnée
    """
    new_date = datetime(date.year, date.month, 1) + relativedelta(months = 1, days = -1)
    return(new_date)

def fin_frac(date, frac) :
    """
    Retourne la date correspondant à la fin du fractionnement choisi pour une date donnée
    """
    if frac == 1 :
        new_date = fin_annee(date)
    elif frac == 2 :
        new_date = fin_semestre(date)
    elif frac == 4 :
        new_date = fin_trimestre(date)
    else :
        new_date = fin_mois(date)
    return(new_date)


def debut_mois(date) :
    """
    Retourne le premier jour du mois pour une date donnée
    """
    new_date = datetime(date.year, date.month, 1)
    return(new_date)

def age_precis(date_debut, date_fin) :
    """
    Retourne l'age d'une personne
    """
    if fin_mois(date_debut) == date_debut :
        date_debut = date_debut + relativedelta(days = 1)
    if fin_mois(date_fin) == date_fin :
        date_fin = date_fin + relativedelta(days = 1)
    
    age = (date_fin.year - date_debut.year) + (date_fin.month - date_debut.month) / 12 + (date_fin.day - date_debut.day) / 365
    age = max(age, 0)
    return(age)

def age_precis_2(date_debut, date_fin, precision = 3) :
    """
    Retourne l'age d'une personne arrondi à 3 chiffres 
    """
    date_temp_1 = fin_mois(date_debut)
    date_temp_2 = debut_mois(date_fin)

    age = round((date_temp_1.day - date_debut.day + 1)/ date_temp_1.day, precision)
    age += round(((date_temp_2 + relativedelta(days = -1)).year - date_temp_1.year) * 12 + ((date_temp_2 + relativedelta(days = -1)).month - date_temp_1.month), precision)
    age += round((date_fin.day - date_temp_2.day) / fin_mois(date_fin).day, precision)

    age = max(round(age / 12, precision), 0)
    return(age)

def ax(date_naissance_X, sexe_X, date_naissance_Y, sexe_Y, date_liquidation, date_calcul, terme, frac, prorata_deces, tx_reversion, rattrapage_rente, tx_contre_assurance, tx_frais_rente) :
    """
    Retourne l'annuité S2 comme calculé par AXA
    """
    date_calcul = datetime(date_calcul.year, date_calcul.month, 1)

    age_X_liquidation = age_precis(date_naissance_X, date_liquidation)
    age_Y_liquidation = age_precis(date_naissance_Y, date_liquidation)
    annee_naissance_X = date_naissance_X.year
    annee_naissance_Y = date_naissance_Y.year
    lx_X_liquidation = lx(age_X_liquidation, annee_naissance_X, sexe_X)
    lx_Y_liquidation = lx(age_Y_liquidation, annee_naissance_Y, sexe_Y)

    age_X_calcul = age_precis(date_naissance_X, date_calcul)
    age_Y_calcul = age_precis(date_naissance_Y, date_calcul)
    lx_X_calcul = lx(age_X_calcul, annee_naissance_X, sexe_X)
    lx_Y_calcul = lx(age_Y_calcul, annee_naissance_Y, sexe_Y)

    if terme == "AVANCE" :
        coeff_frac = 1 - (frac + 1) / (2 * frac) 
    else :
        coeff_frac = -(frac + 1) / (2 * frac) 

    Dx_X = []
    Dx_Y = []
    Dx_Y_projeté = []
    Qx_X = []
    Qx_Y = []
    Cx_X = []
    Cx_Y = []
    Cx_XY_deces_Y_apres_liquidation = []
    Cx_XY_deces_Y_apres_periode_1 = []
    Px_X = []
    Px_Y = []
    Px_XY = []

    age_X_temp = max(age_X_liquidation, age_X_calcul)
    age_Y_temp = max(age_Y_liquidation, age_Y_calcul)
    while min(age_X_temp, age_Y_temp) < 121 :

        Dx_X.append(lx(age_X_temp, annee_naissance_X, sexe_X) / lx_X_calcul)
        Dx_Y.append(lx(age_Y_temp, annee_naissance_Y, sexe_Y) / lx_Y_calcul)
        Dx_Y_projeté.append(lx(age_Y_temp + 1 / frac, annee_naissance_X, sexe_X) / lx_Y_calcul)
        if lx(age_X_temp, annee_naissance_X, sexe_X) == 0 :
            Qx_X.append(0)
        else :
            Qx_X.append(1 - lx(age_X_temp + 1, annee_naissance_X, sexe_X) / lx(age_X_temp, annee_naissance_X, sexe_X))
        if lx(age_Y_temp, annee_naissance_Y, sexe_Y) == 0 :
            Qx_Y.append(0)
        else :
            Qx_Y.append(1 - lx(age_Y_temp + 1, annee_naissance_Y, sexe_Y) / lx(age_Y_temp, annee_naissance_Y, sexe_Y))
        Cx_X.append(Dx_X[-1] * Qx_X[-1])
        Cx_Y.append(Dx_Y[-1] * Qx_Y[-1])
        Cx_XY_deces_Y_apres_liquidation.append(Dx_Y[-1] * Qx_Y[-1] * Dx_X[-1])
        Cx_XY_deces_Y_apres_periode_1.append(Dx_X[-1] * Qx_X[-1] * Dx_Y_projeté[-1])
        Px_X.append(lx(age_X_temp, annee_naissance_X, sexe_X) / min(lx_X_calcul, lx_X_liquidation))
        Px_Y.append(lx(age_Y_temp, annee_naissance_Y, sexe_Y) / min(lx_Y_calcul, lx_Y_liquidation))
        Px_XY.append(Px_X[-1] * Px_Y[-1])

        age_X_temp += 1
        age_Y_temp += 1

    Mx_X = sum(Cx_X)
    Mx_Y = sum(Cx_Y)
    Mx_XY_deces_Y_apres_liquidation = sum(Cx_XY_deces_Y_apres_liquidation)
    Mx_XY_deces_Y_apres_periode_1 = sum(Cx_XY_deces_Y_apres_periode_1)

    if prorata_deces == "COMP" :
        coeff_prorata_deces = (1 / frac) * (Mx_X + tx_reversion * (Mx_Y - Mx_XY_deces_Y_apres_liquidation - Mx_XY_deces_Y_apres_periode_1))
    elif prorata_deces == "PROP" :
        coeff_prorata_deces = (1 / frac) * tx_reversion * Mx_Y 
    else :
        coeff_prorata_deces = 0
    
    Px_X_vie = min(lx_X_liquidation / lx_X_calcul, 1)
    Px_Y_vie = min(lx_Y_liquidation / lx_Y_calcul, 1)
    Px_XY_vie = min(Px_X_vie * Px_Y_vie, 1)

    ax = sum(Px_X)
    ax_rev = sum(Px_Y)
    axy = sum(Px_XY)

    if rattrapage_rente == True or date_liquidation != "" :
        coeff_rattrapage = max(age_X_calcul - age_X_liquidation, 0)
    else :
        coeff_rattrapage = 0

    ax_simple = (ax + coeff_frac) * Px_X_vie
    ax_reversion = ax_simple + tx_reversion * (Px_Y_vie * (ax_rev + coeff_frac) - Px_XY_vie * (axy + coeff_frac))
    ax_prorata_deces = ax_reversion + coeff_prorata_deces
    
    coeff_contre_assurance = tx_contre_assurance * (ax_prorata_deces / Px_X_vie - ax_prorata_deces)

    ax_contre_assurance = ax_prorata_deces + coeff_contre_assurance
    ax_rattrapage = ax_contre_assurance + coeff_rattrapage

    if prorata_deces == "PROP" :
        ax_axa = ax_rattrapage + (1 / 2) * (1 / frac)
        flux_prorata = 0
    elif prorata_deces == "COMP" :
        ax_axa = ax_rattrapage
        flux_prorata = ax_prorata_deces - ax_rev
    else :
        ax_axa = ax_rattrapage
        flux_prorata = 0

    ax_axa *= (1 + tx_frais_rente)

    flux_rev = (ax_contre_assurance - ax_simple) * (1 + tx_frais_rente) - flux_prorata

    ax_axa -= flux_prorata + flux_rev

    return(ax_axa)

def ax_2(date_naissance_X, sexe_X, date_naissance_Y, sexe_Y, date_liquidation, date_calcul, age_depart, frac, methode_age_atteint, tx_reversion, prorata_deces, rattrapage_rente, terme, tx_contre_assurance, tx_frais_rente) :
    """
    Retourne l'annuité X2 comme calculé par AXA
    """
    date_calcul = datetime(date_calcul.year, date_calcul.month, 1)

    if methode_age_atteint == 120 :
        date_liquidation_contractuelle = fin_mois(date_naissance_X + relativedelta(years = age_depart)) + relativedelta(days = 1)
    else :
        date_liquidation_contractuelle = fin_trimestre(date_naissance_X + relativedelta(years = age_depart)) + relativedelta(days = 1)

    if rattrapage_rente : 
        date_liquidation = date_liquidation_contractuelle
    else :
        date_liquidation = max(date_calcul, date_liquidation_contractuelle)

    date_calcul_modifie = max(date_liquidation, datetime(date_calcul.year, date_calcul.month, 1))

    seconde_periode = fin_frac(date_liquidation, frac)

    age_X_liquidation = age_precis_2(date_naissance_X, date_liquidation)
    age_X_calcul_modifie = age_precis_2(date_naissance_X, date_calcul_modifie)
    if tx_reversion == 0 :
        age_Y_calcul_modifie = age_X_calcul_modifie
    else:
        age_Y_calcul_modifie = age_precis_2(date_naissance_Y, date_calcul_modifie)
    annee_naissance_X = date_naissance_X.year
    annee_naissance_Y = date_naissance_Y.year
    lx_X_calcul_modifie = lx(age_X_calcul_modifie, annee_naissance_X, sexe_X)
    lx_Y_calcul_modifie = lx(age_Y_calcul_modifie, annee_naissance_Y, sexe_Y)

    ecart_age = age_X_calcul_modifie - age_Y_calcul_modifie

    if prorata_deces == "COMP" :
        coeff_prorata_deces = 1
    elif prorata_deces == "PROP" :
        coeff_prorata_deces = 0.5
    else :
        coeff_prorata_deces = 0

    increment = 12 * (1/frac)
    periode_1_complete = False
    if date_liquidation == fin_frac(date_liquidation, frac) or (date_liquidation + relativedelta(days = -1)) == fin_frac(date_liquidation + relativedelta(days = -1), frac) :
        periode_1_complete = True

    date_temp = []
    Px_X = []
    Px_Y = []
    Qx_X = []
    Qx_Y = []
    Px_X_inv = []
    flux_prorata_deces_1 = []
    flux_prorata_deces_2 = []
    flux_prorata_deces_3 = []
    flux_base_rente = []
    flux_X = []
    flux_Y = []
    flux_prorata_deces = []

    age_X_temp = age_X_liquidation
    age_Y_temp = age_precis_2(date_naissance_Y, date_liquidation, 3)
    indice = 1
    while min(age_X_temp, age_Y_temp) < 121 :

        if indice == 1 :
            date_temp.append(date_liquidation)
        elif indice == 2 :
            date_temp.append(seconde_periode)
        else :
            date_temp.append(fin_mois(date_temp[-1] + relativedelta(months = increment)))

        age_X_temp = age_precis_2(date_naissance_X, date_temp[-1])
        age_Y_temp = age_precis_2(date_naissance_Y, date_temp[-1])
        
        Px_X.append(min(lx(age_X_temp, annee_naissance_X, sexe_X) / lx_X_calcul_modifie, 1))
        Px_Y.append(min(lx(age_Y_temp, annee_naissance_Y, sexe_Y) / lx_Y_calcul_modifie, 1))
        if indice == 1 :
            Qx_X.append(0)
            Qx_Y.append(0)
            Px_X_inv.append(0)
        else :
            Qx_X.append(Px_X[-2] - Px_X[-1])
            Qx_Y.append(Px_Y[-2] - Px_Y[-1])
            Px_X_inv.append(1 - Px_X[-2])
        if age_X_temp > age_X_liquidation :
            if indice == 2 and not(periode_1_complete) :
                if terme == "ECHU" :
                    flux_base_rente.append(age_precis_2(date_temp[-2], date_temp[-1] + relativedelta(days = 1), 6))
                else :
                    flux_base_rente.append(age_precis_2(age_precis_2(date_temp[-2], date_temp[-1], 6)))
            else :
                flux_base_rente.append(1 / frac)
        else :
            flux_base_rente.append(0)
        flux_prorata_deces_1.append(Qx_X[-1] * (coeff_prorata_deces * flux_base_rente[-1]))
        flux_prorata_deces_2.append((-Qx_X[-1] * Px_Y[-1] * tx_reversion) * (coeff_prorata_deces * flux_base_rente[-1]))
        flux_prorata_deces_3.append((Qx_Y[-1] * tx_reversion * Px_X_inv[-1]) * (coeff_prorata_deces * flux_base_rente[-1]))
        flux_X.append(Px_X[-1] * flux_base_rente[-1])
        flux_Y.append((1 -Px_X[-1]) * Px_Y[-1] * tx_reversion * flux_base_rente[-1])
        flux_prorata_deces.append(flux_prorata_deces_1[-1] + flux_prorata_deces_2[-1] + flux_prorata_deces_3[-1])

        indice += 1

    ax_X_avec_contreassurance = sum(flux_X) * (1 + tx_frais_rente)
    ax_Y_avec_contreassurance = sum(flux_Y) * (1 + tx_frais_rente)
    ax_prorata_deces_avec_contreassurance = sum(flux_prorata_deces) * (1 + tx_frais_rente)

    ax_avec_contreassurance = ax_X_avec_contreassurance + ax_Y_avec_contreassurance + ax_prorata_deces_avec_contreassurance

    age_X_calcul = age_precis_2(date_naissance_X, date_calcul)
    if tx_reversion == 0 :
        age_Y_calcul = age_X_calcul
    else:
        age_Y_calcul = age_X_calcul - ecart_age
    lx_X_calcul = lx(age_X_calcul, annee_naissance_X, sexe_X)
    lx_Y_calcul = lx(age_Y_calcul, annee_naissance_Y, sexe_Y)

    date_temp = []
    Px_X = []
    Px_Y = []
    Qx_X = []
    Qx_Y = []
    Px_X_inv = []
    flux_prorata_deces_1 = []
    flux_prorata_deces_2 = []
    flux_prorata_deces_3 = []
    flux_base_rente = []
    flux_X = []
    flux_Y = []
    flux_prorata_deces = []

    age_X_temp = age_X_liquidation
    age_Y_temp = age_precis_2(date_naissance_Y, date_liquidation, 3)
    indice = 1
    while min(age_X_temp, age_Y_temp) < 121 :

        if indice == 1 :
            date_temp.append(date_liquidation)
        elif indice == 2 :
            date_temp.append(seconde_periode)
        else :
            date_temp.append(fin_mois(date_temp[-1] + relativedelta(months = increment)))

        age_X_temp = age_precis_2(date_naissance_X, date_temp[-1])
        age_Y_temp = age_precis_2(date_naissance_Y, date_temp[-1])
        
        Px_X.append(min(lx(age_X_temp, annee_naissance_X, sexe_X) / lx_X_calcul, 1))
        Px_Y.append(min(lx(age_Y_temp, annee_naissance_Y, sexe_Y) / lx_Y_calcul, 1))
        if indice == 1 :
            Qx_X.append(0)
            Qx_Y.append(0)
            Px_X_inv.append(0)
        else :
            Qx_X.append(Px_X[-2] - Px_X[-1])
            Qx_Y.append(Px_Y[-2] - Px_Y[-1])
            Px_X_inv.append(1 - Px_X[-2])
        if age_X_temp > age_X_liquidation :
            if indice == 2 and not(periode_1_complete) :
                if terme == "ECHU" :
                    flux_base_rente.append(age_precis_2(date_temp[-2], date_temp[-1] + relativedelta(days = 1), 6))
                else :
                    flux_base_rente.append(age_precis_2(age_precis_2(date_temp[-2], date_temp[-1], 6)))
            else :
                flux_base_rente.append(1 / frac)
        else :
            flux_base_rente.append(0)
        flux_prorata_deces_1.append(Qx_X[-1] * (coeff_prorata_deces * flux_base_rente[-1]))
        flux_prorata_deces_2.append((-Qx_X[-1] * Px_Y[-1] * tx_reversion) * (coeff_prorata_deces * flux_base_rente[-1]))
        flux_prorata_deces_3.append((Qx_Y[-1] * tx_reversion * Px_X_inv[-1]) * (coeff_prorata_deces * flux_base_rente[-1]))
        flux_X.append(Px_X[-1] * flux_base_rente[-1])
        flux_Y.append((1 -Px_X[-1]) * Px_Y[-1] * tx_reversion * flux_base_rente[-1])
        flux_prorata_deces.append(flux_prorata_deces_1[-1] + flux_prorata_deces_2[-1] + flux_prorata_deces_3[-1])

        indice += 1

    ax_X_sans_contreassurance = sum(flux_X) * (1 + tx_frais_rente)
    ax_Y_sans_contreassurance = sum(flux_Y) * (1 + tx_frais_rente)
    ax_prorata_deces_sans_contreassurance = sum(flux_prorata_deces) * (1 + tx_frais_rente)

    ax_sans_contreassurance = ax_X_sans_contreassurance + ax_Y_sans_contreassurance + ax_prorata_deces_sans_contreassurance

    ax_axa = ax_sans_contreassurance + tx_contre_assurance * (ax_avec_contreassurance - ax_sans_contreassurance)

    return(ax_axa)


