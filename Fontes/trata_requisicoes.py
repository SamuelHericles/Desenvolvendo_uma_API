import plotly
import plotly.express as px
from flask_restful import request
from json import loads, dumps
import util

consts = util.Consts
filtros = util.Filtros


class Requisicoes:
    def __init__(self, df_ocorrencias, df_vitimas, df_vitimas_municipios):
        self.dfOcorrencias = df_ocorrencias
        self.dfVitimas = df_vitimas
        self.dfVitimasMunicipios = df_vitimas_municipios

    def __get_arguments(self, args):  # Resgata todos os argumentos mapeados pela API
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

    def __add_cabecalho(self, data, base='', o='columns'):  # Add cabeçalho em todas as requisições
        if base != '':  # Diferenciar Infos de Bases
            column = data
        else:
            base = data.columns[-1]
            column = data[base]
        q = len(data.index)
        s = column.sum()
        m = column.mean()
        return f'{{"Info": "{base}", "Quantidade": {q}, "Soma": {s}, "Média": {m}, "Dados": {data.to_json(orient=o)}}}'

    def get_bases(self, base):
        key, cid, uf, regiao, crime, ano, mes, r, order = self.__get_arguments(request.args)
        if key in consts.API_KEYS:  # Autenticação
            if base == 'vitimas':
                data = filtros.filtro_estados(self.dfVitimas, uf, crime, ano, regiao, mes)
            elif base == 'ocorrencias':
                data = filtros.filtro_estados(self.dfOcorrencias, uf, crime, ano, regiao, mes)
            elif base == 'vitimas_municipios':
                data = filtros.filtro_municipios(self.dfVitimasMunicipios, cid, uf, regiao, mes, ano)
            else:
                return loads('{"Erro": "Por Favor, verifique a sua requisição."}')
        else:
            return loads('{"Erro": "Autenticação falhou!"}')

        if r != '':  # Foi requisitado o ranking
            data = data.sort_values(data.columns[-1], ascending=(order == 'ASC')).iloc[:r]
        elif order != '':  # Foi requisitado ordenamento sem ranking
            data = data.sort_values(data.columns[-1], ascending=(order == 'ASC'))

        return loads(self.__add_cabecalho(data, o='records'))

    def get_infos(self, pergunta):
        key = request.args['key'].lower() if 'key' in request.args else ''
        if key in consts.API_KEYS:  # Autenticação
            data = '{"Erro": "Por Favor, verifique a sua requisição."}'
            group = []
            if 'ocorrencias' in pergunta:
                data = self.dfOcorrencias
            elif 'municipios' in pergunta:
                data = self.dfVitimasMunicipios
            elif 'vitimas' in pergunta:
                data = self.dfVitimas

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

            return loads(self.__add_cabecalho(data, base=base))
        else:
            return loads('{"Erro": "Autenticação falhou!"}')


class Plots:
    def __init__(self, df_ocorrencias, df_vitimas):
        self.dfOcorrencias = df_ocorrencias
        self.dfVitimas = df_vitimas

    def __tratamento(self, plot):
        df = title = None
        if 'ocorrencias' in plot:
            df = self.dfOcorrencias
        elif 'vitimas' in plot:
            df = self.dfVitimas

        base = df.columns[-1]
        group = ['UF', 'Ano'] if 'mapa' in plot else ['UF', 'Tipo Crime', 'Ano']
        df = df.groupby(group, as_index=False)

        if 'soma' in plot:
            title = f'Soma de {base} no Brasil a cada ano'
            df = df.sum()
        elif 'media' in plot:
            title = f'Média de {base} no Brasil a cada ano'
            df = df.mean()

        return df, base, title

    def __mapa(self, df, base, title):
        return px.choropleth_mapbox(df, geojson=consts.get_geoJSON_UF_Brasil(), color=base, animation_frame='Ano',
                                    zoom=2.5, locations='UF', center={'lat': -14, 'lon': -52}, mapbox_style='white-bg',
                                    featureidkey='properties.UF', height=600, title=title)

    def __barras(self, df, base, title):
        return px.bar(df, x='UF', y=base, color='Tipo Crime', animation_frame='Ano', title=title, height=600)

    def __scatter(self, df, base, title):
        return px.scatter(df, x='Tipo Crime', y=base, color='Tipo Crime', animation_frame='Ano', opacity=0.9, size=base,
                          title=title, height=600)

    def __linha(self, df, base, title):
        return px.line(df, x='Ano', y=base, color='UF', animation_frame='Tipo Crime', title=title, height=600)

    def retorna_plot(self, plot):
        key = request.args['key'].lower() if 'key' in request.args else ''
        if key in consts.API_KEYS:  # Autenticação
            df, base, title = self.__tratamento(plot)

            fig = None
            if 'mapa' in plot:
                fig = self.__mapa(df, base, title)
            elif 'barras' in plot:
                fig = self.__barras(df, base, title)
            elif 'scatter' in plot:
                fig = self.__scatter(df, base, title)
            elif 'linha' in plot:
                fig = self.__linha(df, base, title)

            return dumps(loads(fig.to_json()), cls=plotly.utils.PlotlyJSONEncoder)
        else:
            return loads('{"Erro": "Autenticação falhou!"}')
