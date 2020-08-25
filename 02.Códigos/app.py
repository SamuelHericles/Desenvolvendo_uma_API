import pandas as pd
from flask import Flask
from flask_restful import Resource, Api, request
from json import loads

baseEstados = 'indicadoressegurancapublicaufmar20.xlsx?raw=true'
baseMunicipios = 'indicadoressegurancapublicamunicmar20.xlsx?raw=true'

MES = {'jan': '-01-', 'fev': '-02-', 'mar': '-03-', 'abr': '-04-', 'mai': '-05-', 'jun': '-06-',
       'jul': '-07-', 'ago': '-08-', 'set': '-09-', 'out': '-10-', 'nov': '-11-', 'dez': '-12-'}
UFs = {'Acre': 'AC', 'Alagoas': 'AL', 'Amapá': 'AP', 'Amazonas': 'AM', 'Bahia': 'BA', 'Ceará': 'CE',
       'Distrito Federal': 'DF', 'Espírito Santo': 'ES', 'Goiás': 'GO', 'Maranhão': 'MA', 'Mato Grosso': 'MT',
       'Mato Grosso do Sul': 'MS', 'Minas Gerais': 'MG', 'Pará': 'PA', 'Paraíba': 'PB', 'Paraná': 'PR',
       'Pernambuco': 'PE', 'Piauí': 'PI', 'Rio de Janeiro': 'RJ', 'Rio Grande do Norte': 'RN', 'Rio Grande do Sul': 'RS',
       'Rondônia': 'RO', 'Roraima': 'RR', 'Santa Catarina': 'SC', 'São Paulo': 'SP', 'Sergipe': 'SE', 'Tocantins': 'TO'}

# Carrega bases dos estados
dFrame = pd.ExcelFile(f'https://github.com/SamuelHericles/Desenvolvendo_uma_API/blob/master/01.Dados/{baseEstados}')
dfOcorrencias = pd.read_excel(dFrame, 'Ocorrências')
dfVitimas = pd.read_excel(dFrame, 'Vítimas')
for UF in dfOcorrencias['UF'].unique():  # Modifica UF de cada registro. Ex.: Acre -> AC
    dfOcorrencias.loc[dfOcorrencias['UF'] == UF, 'UF'] = UFs[UF]
    dfVitimas.loc[dfVitimas['UF'] == UF, 'UF'] = UFs[UF]

# Carrega bases dos municipios e as concatena
dFrame = pd.ExcelFile(f'https://github.com/SamuelHericles/Desenvolvendo_uma_API/blob/master/01.Dados/{baseMunicipios}')
# dfVitimasMunicipios = pd.concat([pd.read_excel(dFrame, sheet) for sheet in dFrame.sheet_names], ignore_index=True)
dfVitimasMunicipios = pd.concat(pd.read_excel(dFrame, sheet_name=None))


def arguments(args):
    print(args)
    uf = args['uf'] if 'uf' in args else ''
    tipo = args['tipo'] if 'tipo' in args else ''
    ano = int(args['ano']) if 'ano' in args else ''
    mes = args['mes'] if 'mes' in args else ''
    r = int(args['ranking']) if 'ranking' in args else ''
    order = args['order'] if 'order' in args else 'DESC'
    est = args['est'] if 'est' in args else ''
    return uf, tipo, ano, mes, r, order, est


def argumentsMunicipios(args):
    cid = args['cid'] if 'cid' in args else ''
    uf = args['uf'] if 'uf' in args else ''
    regiao = args['regiao'] if 'tipo' in args else ''
    mes = args['mes'] if 'mes' in args else ''
    ano = args['ano'] if 'ano' in args else ''
    r = int(args['ranking']) if 'ranking' in args else ''
    order = args['order'] if 'order' in args else 'DESC'
    est = args['est'] if 'est' in args else ''
    return cid, uf, regiao, mes, ano, r, order, est


class Ocorrencias(Resource):
    def get(self):
        try:
            uf, tipo, ano, mes, r, order, est = arguments(request.args)
            data = get_ocorrencias(dfOcorrencias, uf, tipo, ano, mes)
            if est != '':
                data = data.agg([est])
            if r != '':  # Foi requisitado o ranking
                data = data.sort_values('Ocorrências', ascending=(order == 'ASC')).iloc[:r]
            elif order != '':  # Foi requisitado ordenamento sem ranking
                data = data.sort_values('Ocorrências', ascending=(order == 'ASC'))
            return loads(data.to_json(orient="records"))
        except Exception as e:
            return loads(f'{{"Erro": "Por Favor, verifique a sua requisição.", "Excessão": "{e.__class__.__name__}"}}')


class Vitimas(Resource):
    def get(self):
        try:
            uf, tipo, ano, mes, r, order, est = arguments(request.args)
            data = get_ocorrencias(dfVitimas, uf, tipo, ano, mes)
            if est != '':
                data = data.agg([est])
            if r != '':  # Foi requisitado o ranking
                data = data.sort_values('Vítimas', ascending=(order == 'ASC')).iloc[:r]
            elif order != '':  # Foi requisitado ordenamento sem ranking
                data = data.sort_values('Vítimas', ascending=(order == 'ASC'))
            return loads(data.to_json(orient="records"))
        except Exception as e:
            return loads(f'{{"Erro": "Por Favor, verifique a sua requisição.", "Excessão": "{e.__class__.__name__}"}}')


class Municipios(Resource):
    def get(self):
        try:
            cid, uf, regiao, mes, ano, r, order, est = argumentsMunicipios(request.args)
            data = get_vitimas_municipios(cid, uf, regiao, mes, ano)
            if est != '':
                data = data.agg([est])
            if r != '':  # Foi requisitado o ranking
                data = data.sort_values('Vítimas', ascending=(order == 'ASC')).iloc[:r]
            elif order != '':  # Foi requisitado ordenamento sem ranking
                data = data.sort_values('Vítimas', ascending=(order == 'ASC'))
            return loads(data.to_json(orient="records"))
        except Exception as e:
            return loads(f'{{"Erro": "Por Favor, verifique a sua requisição.", "Excessão": "{e.__class__.__name__}"}}')


def get_ocorrencias(df, uf='', tipo_crime='', ano='', mes='', est=''):
    '''
    Função que retorna parte do dataframe requerido
    :parameters: Filtros
    :return: Parcela do dataframe filtrado
    '''
    condition = True
    if uf != '':
        condition &= df['UF'] == uf
    if tipo_crime != '':
        condition &= df['Tipo Crime'].str.contains(tipo_crime, case=False)
    if ano != '':
        condition &= df['Ano'] == ano
    if mes != '':
        condition &= df['Mês'].str.contains(mes.lower(), case=False)
    try:
        return df.loc[condition]
    except KeyError:
        return df


def get_vitimas_municipios(municipio='', uf='', regiao='', mes='', ano='', est=''):
    condition = True
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
    try:
        return dfVitimasMunicipios.loc[condition]
    except KeyError:
        return dfVitimasMunicipios

# Exemplos de requisições GET para a API:
# http://127.0.0.1:5000/
# http://127.0.0.1:5000/?ranking=10
# http://127.0.0.1:5000/vitimas?ano=2018
# http://127.0.0.1:5000/ocorrencias?uf=TO&tipo=Estupro&mes=janeiro
# http://127.0.0.1:5000/vitimas_municipios?cid=Cruz&ano=2020&mes=jan&uf=ce


# API
app = Flask('Ocorrências Criminais')
api = Api(app)
api.add_resource(Ocorrencias, '/ocorrencias', '/')
api.add_resource(Vitimas, '/vitimas')
api.add_resource(Municipios, '/vitimas_municipios')

if __name__ == '__main__':
    app.run()
