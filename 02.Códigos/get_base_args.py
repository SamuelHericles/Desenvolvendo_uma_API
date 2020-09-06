import pandas as pd
import plotly
import plotly.express as px
from flask import Flask, render_template
from flask_restful import Resource, Api, request
from json import load, loads, dumps
from time import time_ns
import load_bases as ld

dFrame,dfOcorrencias,dfVitimas,dfVitimasMunicipios = ld.carrega_bases()
API_KEYS,MES,capitais,geoJSON_UF_Brasil,JSON_Municipios_Brasil = ld.load_tratamento()

def get_ocorrencias(df, uf='', tipo_crime='', ano='', regiao='', mes=''):  # Aplica os filtros em Ocorrencias ou Vitimas
    condition = df.index > -1  # Condição que é sempre True
    if uf != '':
        condition &= df['UF'] == uf.upper()
    if tipo_crime != '':
        condition &= df['Tipo Crime'].str.contains(tipo_crime, case=False)
    if regiao != '':
        condition &= df['Região'].str.contains(regiao, case=False)
    if ano != '':
        condition &= df['Ano'] == int(ano)
    if mes != '':
        condition &= df['Mês'].str.contains(mes.lower(), case=False)

    return df.loc[condition]


def get_vitimas_municipios(municipio='', uf='', regiao='', mes='', ano=''):  # Aplica filtro na base de municípios
    condition = dfVitimasMunicipios['Município'].str.len() > 0  # Condição que é sempre True
    if municipio != '':
        condition &= dfVitimasMunicipios['Município'].str.contains(municipio, case=False)
    if uf != '':
        condition &= dfVitimasMunicipios['Sigla UF'] == uf.upper()
    if regiao != '':
        condition &= dfVitimasMunicipios['Região'].str.contains(regiao, case=False)
    if mes != '':
        condition &= dfVitimasMunicipios['Mês/Ano'].astype(str).str.contains(MES[mes[:3].lower()])
    if ano != '':
        condition &= dfVitimasMunicipios['Mês/Ano'].astype(str).str.contains(ano)

    return dfVitimasMunicipios.loc[condition]