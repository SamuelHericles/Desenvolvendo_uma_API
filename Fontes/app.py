from flask import Flask, render_template, url_for
from flask_restful import Api
from json import loads
from time import time
import util
import trata_requisicoes

# Inicialização
t = time()
print('Iniciando importação das bases...')

load = util.LoadBases()
dfOcorrencias = load.load_base_estado('Ocorrências')
dfVitimas = load.load_base_estado('Vítimas')
dfVitimasMunicipios = load.load_base_municipios()

print(f'Bases importadas com Sucesso! {time() - t:.2f}s')

reqs = trata_requisicoes.Requisicoes(dfOcorrencias, dfVitimas, dfVitimasMunicipios)
plots = trata_requisicoes.Plots(dfOcorrencias, dfVitimas)

# API
app = Flask('Ocorrências Criminais')
api = Api(app)


@app.route('/info/<pergunta>')  # Rota para requisições pré-cadastradas
def infos(pergunta):
    try:
        return reqs.get_infos(pergunta)
    except Exception as e:
        return loads(f'{{"Erro": "Por Favor, verifique a sua requisição.", "Excessão": "{e.__class__.__name__}"}}')


@app.route('/<base>')  # Rota para filtros para as três bases de dados
def filtros(base):
    try:
        return reqs.get_bases(base)
    except Exception as e:
        return loads(f'{{"Erro": "Por Favor, verifique a sua requisição.", "Excessão": "{e.__class__.__name__}"}}')


@app.route('/plot/<plot>')
def retorna_plots(plot):
    try:
        json_graph = plots.retorna_plot(plot)
        if 'Erro' in json_graph:
            return json_graph
        else:
            return render_template('plot.html', plot=json_graph)
    except Exception as e:
        return loads(f'{{"Erro": "Por Favor, verifique a sua requisição.", "Excessão": "{e.__class__.__name__}"}}')


@app.route('/')
def help():
    return render_template('help.html')


if __name__ == '__main__':
    app.run()
