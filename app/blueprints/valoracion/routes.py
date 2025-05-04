from . import valoracion
from flask import render_template, redirect, request, flash, session, jsonify, make_response
from flask_login import login_required
from sqlalchemy import (
    text
)
from app.extensions import Session, db, role_required
from app.extensions import db
from app.extensions import limiter

from app.gdrive_management import Gdrive
import app.blueprints.resume.inserts as inserts
import locale

import pandas as pd
import numpy as np

# def electre_from_excel(filename):
#     excel = pd.read_excel(filename)
    
#     features = excel.drop([len(excel)-2, len(excel)-1], axis=0).to_numpy() #elimino últimas dos filas
#     weights = excel.iloc[-2, 1:].to_numpy() # Penúltima fila, sin columna de nombres
#     maxMinArray = excel.iloc[-1, 1:].to_list() # Última fila, sin columna de nombres
#     clean_features = np.delete(features, 0, axis=1) #elimino columna de nombres

#     tonormalize = np.zeros(clean_features.shape)
#     cont = 0

#     for critery in maxMinArray:
#         if critery == 'max':
#             tonormalize[:, cont] = clean_features[:, cont]**2
#         elif critery == 'min':
#             tonormalize[:, cont] = 1/clean_features[:, cont]**2
#         cont += 1

#     sumNormal = []
#     for i in range(len(maxMinArray)):
#         sumNormal.append(sum(tonormalize[:, i]))

#     cont = 0
#     normalized = np.zeros(clean_features.shape)

#     for critery in maxMinArray:
#         if critery == 'max':
#             normalized[:, cont] = clean_features[:, cont]/(sumNormal[cont]**(1/2))
#         elif critery == 'min':
#             normalized[:, cont] = (1/clean_features[:, cont])/(sumNormal[cont]**(1/2))
#         cont += 1

#     pondered = np.zeros(clean_features.shape)
#     cont = 0
#     for i in weights:
#         pondered[:, cont] = normalized[:, cont]*i
#         cont += 1

#     # Concordancia
#     concordance = np.zeros((clean_features.shape[0], clean_features.shape[0]))
#     for i in range(clean_features.shape[0]):
#         for j in range(clean_features.shape[0]):
#             if j > i:
#                 for k in range(pondered.shape[1]):
#                     if pondered[i,k] > pondered[j, k]:
#                         concordance[i,j] = concordance[i,j] + weights[k]
#             elif j < i:
#                 for k in range(pondered.shape[1]):
#                     if pondered[i,k] < pondered[j, k]:
#                         concordance[i,j] = concordance[i,j] + weights[k]
#     umbralconcord = np.sum(concordance)/(concordance.shape[0]**2-concordance.shape[1])

#     # Diferencias
#     differences = []
#     for j in range(clean_features.shape[0]):
#         for k in range(clean_features.shape[0]):
#             differences.append(pondered[j, :] - pondered[k, :])
#     differences = np.array(differences)
#     idx = []
#     for i in range(differences.shape[0]):
#         if np.sum(differences[i,:]) == 0:
#             idx.append(i)

#     MDN = []
#     MDT = []
#     discordance = []
#     for i in range(differences.shape[0]):
#         MDN.append(min(differences[i, :]))
#         MDT.append(max(abs(differences[i, :])))
#     for i in range(differences.shape[0]):
#         if MDT[i] != 0:
#             discordance.append(abs(MDN[i]/MDT[i]))
#         else:
#             discordance.append(0)

#     discordance = np.nan_to_num(np.array(discordance))
#     umbraldiscord = np.sum(discordance)/(concordance.shape[0]**2-concordance.shape[1])

#     # Concordancia D y Discordancia D
#     concordance_d = np.zeros((clean_features.shape[0], clean_features.shape[0]))
#     discordance_d = np.zeros((clean_features.shape[0], clean_features.shape[0]))
#     for i in range(clean_features.shape[0]):
#         for j in range(clean_features.shape[0]):
#             if concordance[i, j] >= umbralconcord:
#                 concordance_d[i, j] = 1
#             else:
#                 concordance_d[i, j] = 0

#             if discordance[i*clean_features.shape[0] + j] <= umbraldiscord: # Aquí se accede a la lista 'discordance' de manera adecuada
#                 discordance_d[i, j] = 1
#             else:
#                 discordance_d[i, j] = 0

#     # Dominancia
#     ag_dominance = np.array(concordance_d)*np.array(discordance_d)
#     ag_dominance = ag_dominance.reshape(clean_features.shape[0], clean_features.shape[0])
#     superior = []
#     inferior = []
#     for i in range(clean_features.shape[0]):
#         superior.append(np.sum(ag_dominance[i, :]))
#         inferior.append(np.sum(ag_dominance[:, i]))

#     dominance = np.array(superior)-np.array(inferior)
#     dominance2 = np.array(superior)-np.array(inferior)
#     dominance2 = np.sort(dominance2)

#     final_names = pd.DataFrame(excel.iloc[:-2, 0], columns= ['Nombres'])
#     Puntajes = dominance2
#     final_punt = pd.DataFrame(dominance2, columns=['Puntajes'])
#     final_rank = pd.DataFrame(Puntajes, columns= ['Preferencia']).rank(ascending=False)
#     final_class = pd.concat([final_names,final_punt, final_rank], axis=1)
    
#     return final_class

# def topsis_from_excel(filename):
#     # Carga de datos
#     excel = pd.read_excel(filename)
#     features = excel.drop([len(excel)-2, len(excel)-1], axis=0).to_numpy() # elimino las dos últimas filas
#     weights = excel.iloc[-2, 1:].to_numpy() # penúltima fila, excluyendo la columna de nombres
#     objectives = excel.iloc[-1, 1:].to_numpy() # última fila, excluyendo la columna de nombres
#     clean_features = features[:, 1:].astype(np.float64) # elimino columna de nombres y aseguro tipo float64

#     # Normalización
#     normalized = clean_features / np.sqrt((clean_features**2).sum(axis=0))
    
#     # Ponderación
#     weighted = normalized * weights
    
#     # Determinación de soluciones ideales
#     ideal_positive = np.where(objectives == 'max', weighted.max(axis=0), weighted.min(axis=0))
#     ideal_negative = np.where(objectives == 'min', weighted.max(axis=0), weighted.min(axis=0))
    
#     # Cálculo de distancias a las soluciones ideales
#     distance_positive = (((weighted - ideal_positive) ** 2).sum(axis=1))**.5
#     distance_negative = (((weighted - ideal_negative) ** 2).sum(axis=1))**.5
    
#     # Cálculo del coeficiente de proximidad relativo
#     proximity_coefficient = distance_negative / (distance_positive + distance_negative)
    
#     # Crear dataframe con resultados
#     names = features[:, 0]
#     result = pd.DataFrame({
#         'Nombres': names,
#         'Coeficiente': proximity_coefficient
#     })
#     result['Ranking'] = result['Coeficiente'].rank(ascending=False)
    
#     return result

# def promethee_from_excel(filename):
#     # Carga de datos
#     excel = pd.read_excel(filename)
#     features = excel.drop([len(excel)-2, len(excel)-1], axis=0).to_numpy()
#     objectives = excel.iloc[-1, 1:].to_numpy()
#     clean_features = features[:, 1:].astype(np.float64)
    
#     n_alternatives = clean_features.shape[0]
    
#     # Función de preferencia (usamos el tipo I: usual)
#     def preference_function(difference):
#         return np.where(difference > 0, 1, 0)
    
#     # Matriz de preferencia para cada criterio
#     preference_matrices = []
#     for j in range(clean_features.shape[1]):
#         matrix = np.zeros((n_alternatives, n_alternatives))
#         for i in range(n_alternatives):
#             for k in range(n_alternatives):
#                 if objectives[j] == 'max':
#                     matrix[i, k] = preference_function(clean_features[i, j] - clean_features[k, j])
#                 else:  # 'min'
#                     matrix[i, k] = preference_function(clean_features[k, j] - clean_features[i, j])
#         preference_matrices.append(matrix)
    
#     # Flujos positivos y negativos
#     phi_plus = np.mean(np.sum(preference_matrices, axis=0), axis=1)
#     phi_minus = np.mean(np.sum(preference_matrices, axis=0), axis=0)
    
#     # Crear dataframe con resultados
#     names = features[:, 0]
#     result = pd.DataFrame({
#         'Nombres': names,
#         'Phi Plus': phi_plus,
#         'Phi Minus': phi_minus,
#         'Net Flow': phi_plus - phi_minus
#     })
#     result['RankingPromethee'] = result['Net Flow'].rank(ascending=False, method='first')
    
#     return result

# def vikor_from_excel(filename):
#     # Cargar el archivo Excel
#     data = pd.read_excel(filename)
    
#     # Extraer los nombres de las alternativas
#     names = data["Nombres"][:-2].values
    
#     # Extraer los datos de las alternativas y criterios
#     features = data.iloc[:-2, 1:].values
    
#     # Extraer los pesos y objetivos
#     weights = data.iloc[-2, 1:].values
#     objectives = data.iloc[-1, 1:].values
    
#     # Normalizar la matriz
#     min_values = features.min(axis=0)
#     max_values = features.max(axis=0)
    
#     normalized = np.zeros(features.shape)
#     for i in range(features.shape[1]):
#         if objectives[i] == "max":
#             normalized[:, i] = (features[:, i] - min_values[i]) / (max_values[i] - min_values[i])
#         else:
#             normalized[:, i] = (max_values[i] - features[:, i]) / (max_values[i] - min_values[i])
    
#     # Obtener la matriz ponderada
#     weighted = normalized * weights
    
#     # Calcular los valores S y R
#     S = weighted.sum(axis=1)
#     R = weighted.max(axis=1)
    
#     # Calcular los valores Q
#     v = 0.5
#     S_min, S_max = S.min(), S.max()
#     R_min, R_max = R.min(), R.max()
#     Q = v * (S - S_min) / (S_max - S_min) + (1 - v) * (R - R_min) / (R_max - R_min)
    
#     # Crear DataFrame para los resultados
#     result_df = pd.DataFrame({
#         'Nombres': names,
#         'S': S,
#         'R': R,
#         'Q': Q
#     })
    
#     result_df['Ranking Q'] = result_df['Q'].rank()
#     result_df['Ranking S'] = result_df['S'].rank()
#     result_df['Ranking R'] = result_df['R'].rank()
    
#     return result_df


# filename = 'Datos motos.xlsx'

# print('Topsis')
# topsis_df  = topsis_from_excel(filename)
# print(topsis_df)

# print('='*100)
# print('Electre')
# electre_df  = electre_from_excel(filename)
# print(electre_df)


# print('='*100)
# print('Promethee')
# promethee_df  = promethee_from_excel(filename)
# print(promethee_df )


# print('='*100)
# print('Vikor')
# vikor_df  = vikor_from_excel(filename)
# print(vikor_df)
# print('Q es el ponderado entre s y r')
# print('='*100)


# all_dfs = [topsis_df, electre_df, promethee_df, vikor_df]
# merged_df = all_dfs[0][['Nombres']].copy()

# for df in all_dfs:
#     merged_df = merged_df.merge(df, on='Nombres')

# merged_df['Ponderado'] = (merged_df['Preferencia'] + merged_df['Ranking'] + merged_df['RankingPromethee'] + merged_df['Ranking R']) / 4
# merged_df = merged_df.sort_values('Ponderado').reset_index(drop=True)

# print(merged_df[['Nombres', 'Ponderado']])


@valoracion.route("/", methods = ["GET","POST"])
@login_required
@role_required('admin')
def funcionamiento_base():
    if request.method == 'POST':
        print(request.form.items())
    


    return render_template('tabla_valoracion.html', title = 'Valoración de gastos')