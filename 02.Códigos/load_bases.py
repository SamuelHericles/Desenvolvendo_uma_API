import pandas as pd
import plotly
import plotly.express as px
from flask import Flask, render_template
from flask_restful import Resource, Api, request
from json import load, loads, dumps
from time import time_ns
import func as fp


def carrega_bases():
    base_estados = 'indicadoressegurancapublicaufmar20.xlsx'
    base_municipios = 'indicadoressegurancapublicamunicmar20.xlsx'

    UFs = {'Acre': 'AC', 'Alagoas': 'AL', 'Amapá': 'AP', 'Amazonas': 'AM', 'Bahia': 'BA', 'Ceará': 'CE',
        'Distrito Federal': 'DF', 'Espírito Santo': 'ES', 'Goiás': 'GO', 'Maranhão': 'MA', 'Mato Grosso': 'MT',
        'Mato Grosso do Sul': 'MS', 'Minas Gerais': 'MG', 'Pará': 'PA', 'Paraíba': 'PB', 'Paraná': 'PR',
        'Pernambuco': 'PE', 'Piauí': 'PI', 'Rio de Janeiro': 'RJ', 'Rio Grande do Norte': 'RN', 'Rio Grande do Sul': 'RS',
        'Rondônia': 'RO', 'Roraima': 'RR', 'Santa Catarina': 'SC', 'São Paulo': 'SP', 'Sergipe': 'SE', 'Tocantins': 'TO'}

    t = time_ns() // 1000000000
    print('Iniciando importação das bases...')
    # Carrega bases dos estados
    dFrame = pd.ExcelFile(f'../01.Dados/{base_estados}')
    dfOcorrencias = pd.read_excel(dFrame, 'Ocorrências')
    dfVitimas = pd.read_excel(dFrame, 'Vítimas')

    for UF in dfOcorrencias['UF'].unique():  # Modifica UF de cada registro. Ex.: Acre -> AC
        dfOcorrencias.loc[dfOcorrencias['UF'] == UF, 'UF'] = UFs[UF]
        dfVitimas.loc[dfVitimas['UF'] == UF, 'UF'] = UFs[UF]

    # Carrega bases dos municipios e as concatena
    dFrame = pd.ExcelFile(f'../01.Dados/{base_municipios}')
    dfVitimasMunicipios = pd.concat(pd.read_excel(dFrame, sheet_name=None))
    t = (time_ns() // 1000000000) - t
    print(f'Bases importadas com Sucesso! {t}s')

    return dFrame,dfOcorrencias,dfVitimas,dfVitimasMunicipios


def load_tratamento():
    API_KEYS = ['397a32e6', '5fdeb7c5', 'bcd214a2', '97bf6249', 'ed64b06b']  # CRC-32: lucas, samuel, pedro, joao, ialis
    MES = {'jan': '-01-', 'fev': '-02-', 'mar': '-03-', 'abr': '-04-', 'mai': '-05-', 'jun': '-06-',
        'jul': '-07-', 'ago': '-08-', 'set': '-09-', 'out': '-10-', 'nov': '-11-', 'dez': '-12-'}

    capitais = ['Rio Branco', 'Maceió', 'Macapá', 'Manaus', 'Salvador', 'Fortaleza', 'Brasília', 'Vitória', 'Goiânia', 
                'São Luís', 'Cuiabá', 'Campo Grande', 'Belo Horizonte', 'Belém', 'João Pessoa', 'Curitiba', 'Recife', 
                'Teresina', 'Rio De Janeiro', 'Natal', 'Porto Alegre', 'Porto Velho', 'Boa Vista', 'Florianópolis',
                'São Paulo', 'Aracaju', 'Palmas']


    geoJSON_UF_Brasil = load(open('../01.Dados/GeoJSON/Brasil.json'))
    JSON_Municipios_Brasil = load(open('../01.Dados/GeoJSON/municipios.json', 'rb'))

    return API_KEYS,MES,capitais,geoJSON_UF_Brasil,JSON_Municipios_Brasil