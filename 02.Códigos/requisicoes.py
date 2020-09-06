import pandas as pd
import plotly
import plotly.express as px
from flask import Flask, render_template
from flask_restful import Resource, Api, request
from json import load, loads, dumps
from time import time_ns
import func as fp
import load_bases as ld
import get_base_args as gargs

dFrame,dfOcorrencias,dfVitimas,dfVitimasMunicipios = ld.carrega_bases()
API_KEYS,MES,capitais,geoJSON_UF_Brasil,JSON_Municipios_Brasil = ld.load_tratamento()

class Bases(Resource):
    def get(self, base):
        try:
            key, cid, uf, regiao, crime, ano, mes, r, order = fp.arguments(request.args)
            if key in API_KEYS:  # Autenticação
                if base == 'vitimas':
                    data = gargs.get_ocorrencias(dfVitimas, uf, crime, ano, regiao, mes)
                elif base == 'ocorrencias':
                    data = gargs.get_ocorrencias(dfOcorrencias, uf, crime, ano, regiao, mes)
                elif base == 'vitimas_municipios':
                    data = gargs.get_vitimas_municipios(cid, uf, regiao, mes, ano)
                else:
                    return loads('{"Erro": "Por Favor, verifique a sua requisição."}')
            else:
                return loads('{"Erro": "Autenticação falhou!"}')

            if r != '':  # Foi requisitado o ranking
                data = data.sort_values(data.columns[-1], ascending=(order == 'ASC')).iloc[:r]
            elif order != '':  # Foi requisitado ordenamento sem ranking
                data = data.sort_values(data.columns[-1], ascending=(order == 'ASC'))

            return loads(fp.add_cabecalho(data, ornt='records'))
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

                return loads(fp.add_cabecalho(data, base=base))
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