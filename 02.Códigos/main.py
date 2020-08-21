import pandas as pd
from flask import Flask
from flask_restful import Resource, Api, request
from json import loads

# url = 'https://github.com/SamuelHericles/Desenvolvendo_uma_API/blob/master/01.Dados/indicadoressegurancapublicamunicmar20.xlsx?raw=true'
url = 'https://github.com/SamuelHericles/Desenvolvendo_uma_API/blob/master/01.Dados/indicadoressegurancapublicaufmar20.xlsx?raw=true'

dataframe = pd.ExcelFile(url)
dfOcorrencias = pd.read_excel(dataframe, 'Ocorrências')
dfVitimas = pd.read_excel(dataframe, 'Vítimas')
dfOcorrencias.head()

app = Flask('Ocorrências Criminais')
api = Api(app)


class Ocorrencias(Resource):
    def get(self):
        args = request.args
        uf = args['uf'] if 'uf' in args else ''
        tipo = args['tipo'] if 'tipo' in args else ''
        ano = int(args['ano']) if 'ano' in args else ''
        mes = args['mes'] if 'mes' in args else ''
        return loads(get_ocorrencias(dfOcorrencias, uf, tipo, ano, mes).to_json(orient="records"))

    def post(self):
        pass

    def put(self):
        pass

    def delete(self):
        pass


def get_ocorrencias(df, uf='', tipo_crime='', ano='', mes=''):
    '''
    Função que retorna parte do dataframe requerido
    :parameters: Filtros
    :return: Parcela do dataframe filtrado
    '''
    condition = True
    if uf != '':
        condition &= (df['UF'] == uf)
    if tipo_crime != '':
        condition &= (df['Tipo Crime'] == tipo_crime)
    if ano != '':
        condition &= (df['Ano'] == ano)
    if mes != '':
        condition &= (df['Mês'] == mes)
    try:
        return df.loc[condition]
    except KeyError:
        return df


# print(get_ocorrencias(dfOcorrencias, ano=2018))
# ce = get_ocorrencias(dfVitimas, 'Ceará')
# print(ce.groupby(['Ano']).mean())

# Exemplos de requisições GET para a API:
# http://127.0.0.1:5000/ocorrencias
# http://127.0.0.1:5000/ocorrencias?uf=Ceará
# http://127.0.0.1:5000/ocorrencias?ano=2018
# http://127.0.0.1:5000/ocorrencias?uf=Tocantins&tipo=Estupro&mes=janeiro

api.add_resource(Ocorrencias, '/ocorrencias')

if __name__ == '__main__':
    app.run()
