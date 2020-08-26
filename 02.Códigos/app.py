import pandas as pd
from flask import Flask
from flask_restful import Resource, Api, request
from json import loads

baseEstados = 'indicadoressegurancapublicaufmar20.xlsx'
baseMunicipios = 'indicadoressegurancapublicamunicmar20.xlsx'

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


def get_ocorrencias(df, uf='', tipo_crime='', ano='', mes=''):  # Aplica os filtros nas bases de Ocorrencias e Vitimas
    condition = df.index > -1  # Condição que é sempre True
    if uf != '':
        condition &= df['UF'] == uf.upper()
    if tipo_crime != '':
        condition &= df['Tipo Crime'].str.contains(tipo_crime, case=False)
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
    cid = args['cid'] if 'cid' in args else ''
    uf = args['uf'] if 'uf' in args else ''
    regiao = args['regiao'] if 'tipo' in args else ''
    crime = args['crime'] if 'crime' in args else ''
    ano = args['ano'] if 'ano' in args else ''
    mes = args['mes'] if 'mes' in args else ''
    r = int(args['ranking']) if 'ranking' in args else ''
    order = args['order'] if 'order' in args else 'DESC'
    est = args['est'] if 'est' in args else ''
    return cid, uf, regiao, crime, ano, mes, r, order, est


class Bases(Resource):
    def get(self, base):
        try:
            cid, uf, regiao, crime, ano, mes, r, order, est = arguments(request.args)
            if base == 'vitimas':
                data = get_ocorrencias(dfVitimas, uf, crime, ano, mes)
            elif base == 'ocorrencias':
                data = get_ocorrencias(dfOcorrencias, uf, crime, ano, mes)
            elif base == 'vitimas_municipios':
                data = get_vitimas_municipios(cid, uf, regiao, mes, ano)
            else:
                return loads('{"Erro": "Por Favor, verifique a sua requisição."}')

            if est != '':
                data = data.agg([est])
            if r != '':  # Foi requisitado o ranking
                data = data.sort_values(data.columns[-1], ascending=(order == 'ASC')).iloc[:r]
            elif order != '':  # Foi requisitado ordenamento sem ranking
                data = data.sort_values(data.columns[-1], ascending=(order == 'ASC'))

            return loads(data.to_json(orient='records', indent=4))
        except Exception as e:
            return loads(f'{{"Erro": "Por Favor, verifique a sua requisição.", "Excessão": "{e.__class__.__name__}"}}')


class Questions(Resource):
    def get(self, pergunta):
        try:
            data = '{"Erro": "Por Favor, verifique a sua requisição."}'
            if pergunta == 'media_ocorrencias_ano':
                data = dfOcorrencias.groupby(['Ano']).mean().to_json(indent=4)
            elif pergunta == 'soma_ocorrencias_estado':
                data = dfOcorrencias.groupby(['UF'])['Ocorrências'].sum().to_json(indent=4)
            elif pergunta == 'media_ocorrencias_crime':
                data = dfOcorrencias.groupby(['Tipo Crime'])['Ocorrências'].mean().to_json(indent=4)
            elif pergunta == 'menos_perigosos':
                data = dfOcorrencias.sort_values(dfOcorrencias.columns[-1]).iloc[:5].to_json(orient='records', indent=4)
            return loads(data)
        except Exception as e:
            return loads(f'{{"Erro": "Por Favor, verifique a sua requisição.", "Excessão": "{e.__class__.__name__}"}}')


# Exemplos de requisições GET para a API:
# http://127.0.0.1:5000/ocorrencias?ranking=10
# http://127.0.0.1:5000/vitimas?ano=2018
# http://127.0.0.1:5000/ocorrencias?uf=TO&crime=Estupro&mes=janeiro
# http://127.0.0.1:5000/vitimas_municipios?cid=Cruz&ano=2020&mes=jan&uf=ce
# http://127.0.0.1:5000/question/menos_perigosos

# API
app = Flask('Ocorrências Criminais')
api = Api(app)
api.add_resource(Questions, '/question/<pergunta>')  # Rota para requisições pré-cadastradas
api.add_resource(Bases, '/<base>')  # Rota para filtros para as três bases de dados

if __name__ == '__main__':
    app.run()
