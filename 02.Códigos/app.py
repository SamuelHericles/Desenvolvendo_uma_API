from flask import Flask, render_template
from flask_restful import Resource, Api, request
from json import load, loads, dumps
import func as fp
import load_bases as ld
import requisicoes as reqsis
import get_base_args as gargs

# API
app = Flask('Ocorrências Criminais')
api = Api(app)

api.add_resource(reqsis.Infos, '/info/<pergunta>')  # Rota para requisições pré-cadastradas
api.add_resource(reqsis.Bases, '/<base>')  # Rota para filtros para as três bases de dados


@app.route('/plot/<plot>')
def show_plot(plot):
    json_graph = reqsis.get_graficos(plot)
    if 'Erro' in json_graph:
        return json_graph
    else:
        return render_template('plot.html', plot=json_graph)


@app.route('/')
def help():
    return render_template('help.html')


if __name__ == '__main__':
    app.run()
