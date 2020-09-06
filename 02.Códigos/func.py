import pandas as pd
import plotly
import plotly.express as px
from flask import Flask, render_template
from flask_restful import Resource, Api, request
from json import load, loads, dumps
from time import time_ns

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