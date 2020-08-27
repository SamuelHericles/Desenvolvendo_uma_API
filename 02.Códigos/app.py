import pandas as pd
import plotly
import numpy as np
import json
import plotly.graph_objs as go
from flask import Response,Flask,render_template
from flask_restful import Resource, Api, request
from json import loads
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import io
import random
import plotly.express as px
app = Flask('Ocorrências Criminais')
api = Api(app)
baseEstados = 'indicadoressegurancapublicaufmar20.xlsx'
baseMunicipios = 'indicadoressegurancapublicamunicmar20.xlsx'

API_KEYS = ['397a32e6', '5fdeb7c5', 'bcd214a2', '97bf6249', 'ed64b06b']  # CRC-32: lucas, samuel, pedro, joao, ialis
MES = {'jan': '-01-', 'fev': '-02-', 'mar': '-03-', 'abr': '-04-', 'mai': '-05-', 'jun': '-06-',
       'jul': '-07-', 'ago': '-08-', 'set': '-09-', 'out': '-10-', 'nov': '-11-', 'dez': '-12-'}
UFs = {'Acre': 'AC', 'Alagoas': 'AL', 'Amapá': 'AP', 'Amazonas': 'AM', 'Bahia': 'BA', 'Ceará': 'CE',
       'Distrito Federal': 'DF', 'Espírito Santo': 'ES', 'Goiás': 'GO', 'Maranhão': 'MA', 'Mato Grosso': 'MT',
       'Mato Grosso do Sul': 'MS', 'Minas Gerais': 'MG', 'Pará': 'PA', 'Paraíba': 'PB', 'Paraná': 'PR',
       'Pernambuco': 'PE', 'Piauí': 'PI', 'Rio de Janeiro': 'RJ', 'Rio Grande do Norte': 'RN',
       'Rio Grande do Sul': 'RS',
       'Rondônia': 'RO', 'Roraima': 'RR', 'Santa Catarina': 'SC', 'São Paulo': 'SP', 'Sergipe': 'SE', 'Tocantins': 'TO'}


# Carrega bases dos estados
dFrame = pd.ExcelFile(f'../01.Dados/{baseEstados}')
dfOcorrencias = pd.read_excel(dFrame, 'Ocorrências')
dfVitimas = pd.read_excel(dFrame, 'Vítimas')
for UF in dfOcorrencias['UF'].unique():  # Modifica UF de cada registro. Ex.: Acre -> AC
    dfOcorrencias.loc[dfOcorrencias['UF'] == UF, 'UF'] = UFs[UF]
    dfVitimas.loc[dfVitimas['UF'] == UF, 'UF'] = UFs[UF]

# Carrega bases dos municipios e as concatena
dFrame = pd.ExcelFile(f'../01.Dados/{baseMunicipios}')
dfVitimasMunicipios = pd.concat(pd.read_excel(dFrame, sheet_name=None))


def get_ocorrencias(df, uf='', tipo_crime='', ano='',regiao='', mes=''):  # Aplica os filtros nas bases de Ocorrencias e Vitimas
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


def arguments(args):  # Resgata todos os argumentos mapeados pela API
    key = args['key'].lower() if 'key' in args else ''
    cid = args['cid'] if 'cid' in args else ''
    uf = args['uf'] if 'uf' in args else ''
    regiao = args['regiao'] if 'regiao' in args else '' ## mudei aqui tava if 'tipo' in args else ''
    crime = args['crime'] if 'crime' in args else ''
    ano = args['ano'] if 'ano' in args else ''
    mes = args['mes'] if 'mes' in args else ''
    r = int(args['ranking']) if 'ranking' in args else ''
    order = args['order'] if 'order' in args else 'DESC'
    est = args['est'] if 'est' in args else ''
    return key, cid, uf, regiao, crime, ano, mes, r, order, est



class Bases(Resource):
    def get(self, base):
        try:
            key, cid, uf, regiao, crime, ano, mes, r, order, est = arguments(request.args)
            if key in API_KEYS:  # Autenticação
                if base == 'vitimas':
                    data = get_ocorrencias(dfVitimas, uf, crime, ano, regiao, mes)
                elif base == 'ocorrencias':
                    data = get_ocorrencias(dfOcorrencias, uf, crime, ano,regiao, mes)
                elif base == 'vitimas_municipios':
                    data = get_vitimas_municipios(cid, uf, regiao, mes, ano)
                else:
                    return loads('{"Erro": "Por Favor, verifique a sua requisição."}')
            else:
                return loads('{"Erro": "Autenticação falhou!"}')

            if est != '':
                if est != 'sum':
                    data = data.agg([est])
                else:
                    data = data.sum(level =0)
            if r != '':  # Foi requisitado o ranking
                data = data.sort_values(data.columns[-1], ascending=(order == 'ASC')).iloc[:r]
            elif order != '':  # Foi requisitado ordenamento sem ranking
                data = data.sort_values(data.columns[-1], ascending=(order == 'ASC'))

            return loads(data.to_json(orient='records', indent=4))
        except Exception as e:
            return loads(f'{{"Erro": "Por Favor, verifique a sua requisição.", "Excessão": "{e.__class__.__name__}"}}')


class Infos(Resource):
    def get(self, pergunta):
        try:
            key = request.args['key'].lower() if 'key' in request.args else ''
            if key in API_KEYS:  # Autenticação
                data = '{"Erro": "Por Favor, verifique a sua requisição."}'
                if pergunta == 'media_ocorrencias_ano':
                    data = dfOcorrencias.groupby(['Ano']).mean().to_json(indent=4)
                elif pergunta == 'soma_ocorrencias_ano':
                    data = dfOcorrencias.groupby(['Ano'])['Ocorrências'].sum().to_json(indent=4)
                elif pergunta == 'soma_ocorrencias_estado':
                    data = dfOcorrencias.groupby(['UF'])['Ocorrências'].sum().to_json(indent=4)
                elif pergunta == 'soma_ocorrencias_crime':
                    data = dfOcorrencias.groupby(['Tipo Crime'])['Ocorrências'].sum().to_json(indent=4)
                elif pergunta == 'media_crime_anual':
                    data = dfOcorrencias.groupby(['Ano','Tipo Crime'])['Ocorrências'].mean().to_json(indent=4)
                elif pergunta == 'media_crime_estado':
                    data = dfOcorrencias.groupby(['UF','Tipo Crime'])['Ocorrências'].mean().to_json(indent=4)
                elif pergunta == 'media_crime_estado_anual':
                    data = dfOcorrencias.groupby(['Tipo Crime','UF','Ano'])['Ocorrências'].mean().to_json(indent=4)
                elif pergunta == 'menos_perigosos':
                    data = dfOcorrencias.sort_values(dfOcorrencias.columns[-1]).iloc[:5].to_json(orient='records', indent=4)

                return loads(data)
            else:
                return loads('{"Erro": "Autenticação falhou!"}')
        except Exception as e:
            return loads(f'{{"Erro": "Por Favor, verifique a sua requisição.", "Excessão": "{e.__class__.__name__}"}}')


@app.route('/media_crime_estado_anual_grafico')
def get_graficos():
    key = request.args['key'].lower() if 'key' in request.args else ''
    if key in API_KEYS: #Autenticação
            fig = px.bar(dfVitimas,x="Região",y="Vítimas",color='UF')
            fig.write_html('./templates/index.html')

            return render_template('index.html')

### Exemplos de requisições GET para a API:

#### Teste com Bases
# vitimas

# UFs
# http://127.0.0.1:5000/vitimas?key=5fdeb7c5&uf=CE    
# http://127.0.0.1:5000/vitimas?key=5fdeb7c5&uf=CE&ano=2018    
# http://127.0.0.1:5000/vitimas?key=5fdeb7c5&uf=CE&ano=2018&crime=Le 
# http://127.0.0.1:5000/vitimas?key=5fdeb7c5&uf=CE&ano=2018&crime=Le&mes=jan 

##### ocorrencias
# UFs
# http://127.0.0.1:5000/ocorrencias?key=5fdeb7c5&uf=CE    
# http://127.0.0.1:5000/ocorrencias?key=5fdeb7c5&uf=CE&ano=2018   
# http://127.0.0.1:5000/ocorrencias?key=5fdeb7c5&uf=CE&ano=2018&crime=Le 
# http://127.0.0.1:5000/ocorrencias?key=5fdeb7c5&uf=CE&ano=2018&crime=Le&mes=jan 


##### vitimas_municipios
# Cidade
# http://127.0.0.1:5000/vitimas_municipios?key=397a32e6&cid=Marco
# http://127.0.0.1:5000/vitimas_municipios?key=397a32e6&cid=Marco&ano=2020 
# http://127.0.0.1:5000/vitimas_municipios?key=397a32e6&cid=Marco&ano=2020&mes=jan 
# http://127.0.0.1:5000/vitimas_municipios?key=397a32e6&cid=Marco&ano=2020&mes=jan&uf=ce 

##### Teste com info/
# http://127.0.0.1:5000/info/media_ocorrencias_ano?key=397a32e6
# http://127.0.0.1:5000/info/soma_ocorrencias_ano?key=397a32e6
# http://127.0.0.1:5000/info/soma_ocorrencias_crime?key=397a32e6
# http://127.0.0.1:5000/info/media_crime_anual?key=397a32e6
# http://127.0.0.1:5000/info/media_crime_estado_anual?key=397a32e6
# http://127.0.0.1:5000/info/menos_perigosos?key=397a32e6


#### Teesta com plot/Testativa com gráficos
# http://127.0.0.1:5000/media_crime_estado_anual_grafico?key=397a32e6

# API

api.add_resource(Infos, '/info/<pergunta>')  # Rota para requisições pré-cadastradas
api.add_resource(Bases, '/<base>')  # Rota para filtros para as três bases de dados


if __name__ == '__main__':
    app.run()
