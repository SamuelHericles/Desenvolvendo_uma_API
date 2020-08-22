import pandas as pd
from flask import Flask
from flask_restful import Resource, Api, request
from json import loads

urlCidades = 'https://github.com/SamuelHericles/Desenvolvendo_uma_API/blob/master/01.Dados/indicadoressegurancapublicamunicmar20.xlsx?raw=true'
urlUFs = 'https://github.com/SamuelHericles/Desenvolvendo_uma_API/blob/master/01.Dados/indicadoressegurancapublicaufmar20.xlsx?raw=true'

dataframe = pd.ExcelFile(urlUFs)
dfOcorrencias = pd.read_excel(dataframe, 'Ocorrências')
dfVitimas = pd.read_excel(dataframe, 'Vítimas')

dataframe = pd.ExcelFile(urlCidades)
dfVitimasMunicipios = pd.concat([pd.read_excel(dataframe, sheet) for sheet in dataframe.sheet_names], ignore_index=True)
# dfVitimasMunicipios = pd.read_excel(dataframe, dataframe.sheet_names[0])
# for sheet in dataframe.sheet_names[1:]:
#     data = pd.read_excel(dataframe, sheet)
#     print(sheet)
#     dfVitimasMunicipios.append(data, ignore_index=False)

MES = {'jan': '-01-', 'fev': '-02-', 'mar': '-03-', 'abr': '-04-', 'mai': '-05-', 'jun': '-06-', 'jul': '-07-',
       'ago': '-08-', 'set': '-09-', 'out': '-10-', 'nov': '-11-', 'jan': '-01-', 'jan': '-01-', 'dez': '-12-'}

app = Flask('Ocorrências Criminais')
api = Api(app)


def arguments(args):
    uf = args['uf'] if 'uf' in args else ''
    tipo = args['tipo'] if 'tipo' in args else ''
    ano = int(args['ano']) if 'ano' in args else ''
    mes = args['mes'] if 'mes' in args else ''
    r = int(args['ranking']) if 'ranking' in args else ''
    order = args['order'] if 'order' in args else 'DESC'
    return uf, tipo, ano, mes, r, order


def argumentsMunicipios(args):
    cid = args['cid'] if 'cid' in args else ''
    uf = args['uf'] if 'uf' in args else ''
    regiao = args['regiao'] if 'tipo' in args else ''
    mes = args['mes'] if 'mes' in args else ''
    ano = args['ano'] if 'ano' in args else ''
    r = int(args['ranking']) if 'ranking' in args else ''
    order = args['order'] if 'order' in args else 'DESC'
    return cid, uf, regiao, mes, ano, r, order


class Ocorrencias(Resource):
    def get(self):
        uf, tipo, ano, mes, r, order = arguments(request.args)
        data = get_ocorrencias(dfOcorrencias, uf, tipo, ano, mes)
        if r != '':  # Foi requisitado o ranking
            data = data.sort_values('Ocorrências', ascending=(order == 'ASC')).iloc[:r]
        return loads(data.to_json(orient="records"))


class Vitimas(Resource):
    def get(self):
        uf, tipo, ano, mes, r, order = arguments(request.args)
        data = get_ocorrencias(dfVitimas, uf, tipo, ano, mes)
        if r != '':  # Foi requisitado o ranking
            data = data.sort_values('Vítimas', ascending=(order == 'ASC')).iloc[:r]
        return loads(data.to_json(orient="records"))


class Municipios(Resource):
    def get(self):
        cid, uf, regiao, mes, ano, r, order = argumentsMunicipios(request.args)
        data = get_vitimas_municipios(cid, uf, regiao, mes, ano)
        if r != '':  # Foi requisitado o ranking
            data = data.sort_values('Vítimas', ascending=(order == 'ASC')).iloc[:r]
        return loads(data.to_json(orient="records"))


def get_ocorrencias(df, uf='', tipo_crime='', ano='', mes=''):
    '''
    Função que retorna parte do dataframe requerido
    :parameters: Filtros
    :return: Parcela do dataframe filtrado
    '''
    condition = True
    if uf != '':
        condition &= (df['UF'].str.contains())
    if tipo_crime != '':
        condition &= (df['Tipo Crime'].str.contains(tipo_crime))
    if ano != '':
        condition &= (df['Ano'] == ano)
    if mes != '':
        condition &= (df['Mês'].str.contains(mes.lower()))
    try:
        return df.loc[condition]
    except KeyError:
        return df


def get_vitimas_municipios(municipio='', uf='', regiao='', mes='', ano=''):
    condition = True
    if municipio != '':
        condition &= (dfVitimasMunicipios['Município'].str.contains(municipio))
    if uf != '':
        condition &= (dfVitimasMunicipios['Sigla UF'] == uf.upper())
    if regiao != '':
        condition &= (dfVitimasMunicipios['Região'] == regiao.upper())
    if mes != '':
        condition &= (dfVitimasMunicipios['Mês/Ano'].astype(str).str.contains(MES[mes[:3].lower()]))
    if ano != '':
        condition &= (dfVitimasMunicipios['Mês/Ano'].astype(str).str.contains(ano))
    try:
        return dfVitimasMunicipios.loc[condition]
    except KeyError:
        return dfVitimasMunicipios

# Testes
# print(get_ocorrencias(dfOcorrencias, ano=2018))
# ce = get_ocorrencias(dfVitimas, 'Ceará')
# print(ce.groupby(['Ano']).mean())
# print(get_ocorrencias(dfOcorrencias, 'Acre').sort_values('Ocorrências', ascending=False).iloc[:10])

# Exemplos de requisições GET para a API:
# http://127.0.0.1:5000/
# http://127.0.0.1:5000/?ranking=10
# http://127.0.0.1:5000/vitimas?ano=2018
# http://127.0.0.1:5000/ocorrencias?uf=Tocantins&tipo=Estupro&mes=janeiro
# http://127.0.0.1:5000/vitimas_municipios?cid=Cruz&ano=2020&mes=jan&uf=ce


api.add_resource(Ocorrencias, '/ocorrencias', '/')
api.add_resource(Vitimas, '/vitimas')
api.add_resource(Municipios, '/vitimas_municipios')

if __name__ == '__main__':
    app.run()
