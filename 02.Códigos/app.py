import pandas as pd
import plotly
import plotly.express as px
from flask import Flask, render_template
from flask_restful import Resource, Api, request
from json import load, loads, dumps
from time import time_ns


base_estados = 'indicadoressegurancapublicaufmar20.xlsx'
base_municipios = 'indicadoressegurancapublicamunicmar20.xlsx'

API_KEYS = ['397a32e6', '5fdeb7c5', 'bcd214a2', '97bf6249', 'ed64b06b']  # CRC-32: lucas, samuel, pedro, joao, ialis
MES = {'jan': '-01-', 'fev': '-02-', 'mar': '-03-', 'abr': '-04-', 'mai': '-05-', 'jun': '-06-',
       'jul': '-07-', 'ago': '-08-', 'set': '-09-', 'out': '-10-', 'nov': '-11-', 'dez': '-12-'}
UFs = {'Acre': 'AC', 'Alagoas': 'AL', 'Amapá': 'AP', 'Amazonas': 'AM', 'Bahia': 'BA', 'Ceará': 'CE',
       'Distrito Federal': 'DF', 'Espírito Santo': 'ES', 'Goiás': 'GO', 'Maranhão': 'MA', 'Mato Grosso': 'MT',
       'Mato Grosso do Sul': 'MS', 'Minas Gerais': 'MG', 'Pará': 'PA', 'Paraíba': 'PB', 'Paraná': 'PR',
       'Pernambuco': 'PE', 'Piauí': 'PI', 'Rio de Janeiro': 'RJ', 'Rio Grande do Norte': 'RN', 'Rio Grande do Sul': 'RS',
       'Rondônia': 'RO', 'Roraima': 'RR', 'Santa Catarina': 'SC', 'São Paulo': 'SP', 'Sergipe': 'SE', 'Tocantins': 'TO'}
capitais = ['Rio Branco', 'Maceió', 'Macapá', 'Manaus', 'Salvador', 'Fortaleza', 'Brasília', 'Vitória', 'Goiânia', 
            'São Luís', 'Cuiabá', 'Campo Grande', 'Belo Horizonte', 'Belém', 'João Pessoa', 'Curitiba', 'Recife', 
            'Teresina', 'Rio De Janeiro', 'Natal', 'Porto Alegre', 'Porto Velho', 'Boa Vista', 'Florianópolis',
            'São Paulo', 'Aracaju', 'Palmas']


geoJSON_UF_Brasil = load(open('../01.Dados/GeoJSON/Brasil.json'))
JSON_Municipios_Brasil = load(open('../01.Dados/GeoJSON/municipios.json', 'rb'))

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


def arguments(args):  # Resgata todos os argumentos mapeados pela API
    key = args['key'].lower() if 'key' in args else ''
    cid = args['cid'] if 'cid' in args else ''
    uf = args['uf'] if 'uf' in args else ''
    regiao = args['regiao'] if 'regiao' in args else ''
    crime = args['crime'] if 'crime' in args else ''
    ano = args['ano'] if 'ano' in args else ''
    mes = args['mes'] if 'mes' in args else ''
    r = int(args['ranking']) if 'ranking' in args else ''
    order = args['order'] if 'order' in args else 'DESC'
    return key, cid, uf, regiao, crime, ano, mes, r, order


def add_cabecalho(data, base='', ornt='columns'):  # Add cabeçalho em todas as requisições
    if base != '':  # Diferenciar Infos de Bases
        column = data
    else:
        base = data.columns[-1]
        column = data[base]
    q = len(data.index)
    sm = column.sum()
    md = column.mean()
    return f'{{"Info": "{base}", "Quantidade": {q}, "Soma": {sm}, "Média": {md}, "Dados": {data.to_json(orient=ornt)}}}'


class Bases(Resource):
    def get(self, base):
        try:
            key, cid, uf, regiao, crime, ano, mes, r, order = arguments(request.args)
            if key in API_KEYS:  # Autenticação
                if base == 'vitimas':
                    data = get_ocorrencias(dfVitimas, uf, crime, ano, regiao, mes)
                elif base == 'ocorrencias':
                    data = get_ocorrencias(dfOcorrencias, uf, crime, ano, regiao, mes)
                elif base == 'vitimas_municipios':
                    data = get_vitimas_municipios(cid, uf, regiao, mes, ano)
                else:
                    return loads('{"Erro": "Por Favor, verifique a sua requisição."}')
            else:
                return loads('{"Erro": "Autenticação falhou!"}')

            if r != '':  # Foi requisitado o ranking
                data = data.sort_values(data.columns[-1], ascending=(order == 'ASC')).iloc[:r]
            elif order != '':  # Foi requisitado ordenamento sem ranking
                data = data.sort_values(data.columns[-1], ascending=(order == 'ASC'))

            return loads(add_cabecalho(data, ornt='records'))
        except Exception as e:
            return loads(f'{{"Erro": "Por Favor, verifique a sua requisição.", "Excessão": "{e.__class__.__name__}"}}')


class Infos(Resource):
    def get(self, pergunta):
        try:
            key = request.args['key'].lower() if 'key' in request.args else ''
            if key in API_KEYS:  # Autenticação
                data = '{"Erro": "Por Favor, verifique a sua requisição."}'
                group = []
                if 'ocorrencias' in pergunta:
                    data = dfOcorrencias
                elif 'municipios' in pergunta:
                    data = dfVitimasMunicipios
                elif 'vitimas' in pergunta:
                    data = dfVitimas

                base = data.columns[-1]

                if ('anual' in pergunta or 'mensal' in pergunta) and ('municipios' in pergunta):
                    group.append('Mês/Ano')
                elif 'anual' in pergunta:
                    group.append('Ano')
                elif 'mensal' in pergunta:
                    group.append('Mês')

                if 'crime' in pergunta:
                    group.append('Tipo Crime')
                if 'estado' in pergunta:
                    if 'municipios' in pergunta:
                        group.append('Sigla UF')
                    elif 'ocorrencias' in pergunta or 'vitimas' in pergunta:
                        group.append('UF')

                if len(group) > 0:
                    data = data.groupby(group)[data.columns[-1]]
                    if 'media' in pergunta:
                        data = data.mean()
                    elif 'soma' in pergunta:
                        data = data.sum()

                return loads(add_cabecalho(data, base=base))
            else:
                return loads('{"Erro": "Autenticação falhou!"}')
        except Exception as e:
            return loads(f'{{"Erro": "Por Favor, verifique a sua requisição.", "Excessão": "{e.__class__.__name__}"}}')


def get_graficos(plot):
    try:
        key = request.args['key'].lower() if 'key' in request.args else ''
        if key in API_KEYS:  # Autenticação
            if 'ocorrencias' in plot:
                df = dfOcorrencias
            elif 'vitimas' in plot:
                df = dfVitimas
            elif 'capitais' in plot:
                df = dfVitimasMunicipios

            base = df.columns[-1]
            if 'capitais' in plot:
                group = ['Município', 'Sigla UF', 'Mês/Ano']
            else:
                group = ['UF', 'Ano'] if 'mapa' in plot else ['UF', 'Tipo Crime', 'Ano']
                df = df.groupby(group, as_index=False)

            if 'soma' in plot:
                title = f'Soma de {base} no Brasil a cada ano'
                df = df.sum()
            elif 'media' in plot:
                title = f'Média de {base} no Brasil a cada ano'
                df = df.mean()

            if 'mapa' in plot:
                fig = px.choropleth_mapbox(df, geojson=geoJSON_UF_Brasil, color=base, animation_frame='Ano', zoom=2.5,
                                           locations='UF', center={'lat': -14, 'lon': -52}, mapbox_style='white-bg',
                                           featureidkey='properties.UF', height=600, title=title)
            elif 'capitais' in plot:
                df = df.loc[df['Município'].isin(capitais)]
                df = df.groupby(['Município'], as_index=False).sum()
                lat = [municipio['latitude'] for municipio in JSON_Municipios_Brasil if municipio['capital']]
                lng = [municipio['longitude'] for municipio in JSON_Municipios_Brasil if municipio['capital']]
                fig = px.scatter_mapbox(df, height=600, size='Vítimas', lat=lat, lon=lng, color='Município')
            elif 'barras' in plot:
                fig = px.bar(df, x='UF', y=base, color='Tipo Crime', animation_frame='Ano', title=title, height=600)
            elif 'scatter' in plot:
                fig = px.scatter(df, x='Tipo Crime', y=base, color='Tipo Crime', animation_frame='Ano',
                                 opacity=0.9, size=base, title=title, height=600)
            elif 'linha' in plot:
                fig = px.line(df, x='Ano', y=base, color='UF', animation_frame='Tipo Crime', title=title, height=600)
                fig.update_layout(updatemenus=[
                    dict(
                        buttons=list([
                            dict(
                                args=["type", "line"],
                                label="Linha",
                                method="restyle"
                            ),
                            dict(
                                args=["type", "scatter"],
                                label="Dispersão",
                                method="restyle"
                            )
                        ]),
                        direction="down",
                        pad={"r": 10, "t": 10},
                        showactive=True,
                        x=0,
                        xanchor="left",
                        y=0,
                        yanchor="top"
                    ),
                ])

            return dumps(loads(fig.to_json()), cls=plotly.utils.PlotlyJSONEncoder)
        else:
            return loads('{"Erro": "Autenticação falhou!"}')
    except Exception as e:
        return loads(f'{{"Erro": "Por Favor, verifique a sua requisição.", "Excessão": "{e.__class__.__name__}"}}')


# API
app = Flask('Ocorrências Criminais')
api = Api(app)

api.add_resource(Infos, '/info/<pergunta>')  # Rota para requisições pré-cadastradas
api.add_resource(Bases, '/<base>')  # Rota para filtros para as três bases de dados


@app.route('/plot/<plot>')
def show_plot(plot):
    json_graph = get_graficos(plot)
    if 'Erro' in json_graph:
        return json_graph
    else:
        return render_template('plot.html', plot=json_graph)


@app.route('/')
def help():
    return render_template('help.html')


if __name__ == '__main__':
    app.run()
