import pandas as pd
from json import load


class Consts:
    API_KEYS = ['397a32e6', '5fdeb7c5', 'bcd214a2', '97bf6249', 'ed64b06b']  # CRC-32: lucas, samuel, pedro, joao, ialis

    MES = {'jan': '-01-', 'fev': '-02-', 'mar': '-03-', 'abr': '-04-', 'mai': '-05-', 'jun': '-06-',
           'jul': '-07-', 'ago': '-08-', 'set': '-09-', 'out': '-10-', 'nov': '-11-', 'dez': '-12-'}

    base_estados = 'indicadoressegurancapublicaufmar20.xlsx'
    base_municipios = 'indicadoressegurancapublicamunicmar20.xlsx'

    UFs = {'Acre': 'AC', 'Alagoas': 'AL', 'Amapá': 'AP', 'Amazonas': 'AM', 'Bahia': 'BA', 'Ceará': 'CE',
           'Distrito Federal': 'DF', 'Espírito Santo': 'ES', 'Goiás': 'GO', 'Maranhão': 'MA', 'Mato Grosso': 'MT',
           'Mato Grosso do Sul': 'MS', 'Minas Gerais': 'MG', 'Pará': 'PA', 'Paraíba': 'PB', 'Paraná': 'PR',
           'Pernambuco': 'PE', 'Piauí': 'PI', 'Rio de Janeiro': 'RJ', 'Rio Grande do Norte': 'RN',
           'Rio Grande do Sul': 'RS', 'Rondônia': 'RO', 'Roraima': 'RR', 'Santa Catarina': 'SC', 'São Paulo': 'SP',
           'Sergipe': 'SE', 'Tocantins': 'TO'}

    def get_geoJSON_UF_Brasil(self=None):
        return load(open('../Bases/GeoJSON/Brasil.json'))


class LoadBases:
    def __init__(self):
        self.dfEstados = pd.ExcelFile(f'../01.Dados/{Consts.base_estados}')
        self.dfMunicipios = pd.ExcelFile(f'../01.Dados/{Consts.base_municipios}')

    def __conversaoUFs(self, df):
        for UF in df['UF'].unique():  # Modifica UF de cada registro. Ex.: Acre -> AC
            df.loc[df['UF'] == UF, 'UF'] = Consts.UFs[UF]
        return df

    def load_base_estado(self, sheet):
        df = pd.read_excel(self.dfEstados, sheet)
        return self.__conversaoUFs(df)

    def load_base_municipios(self):
        return pd.concat(pd.read_excel(self.dfMunicipios, sheet_name=None))


class Filtros:
    def filtro_estados(df, uf='', crime='', ano='', regiao='', mes=''):  # Aplica os filtros na base de Estados
        condition = df.index > -1  # Condição que é sempre True
        if uf != '':
            condition &= df['UF'] == uf.upper()
        if crime != '':
            condition &= df['Tipo Crime'].str.contains(crime, case=False)
        if regiao != '':
            condition &= df['Região'].str.contains(regiao, case=False)
        if ano != '':
            condition &= df['Ano'] == int(ano)
        if mes != '':
            condition &= df['Mês'].str.contains(mes.lower(), case=False)

        return df.loc[condition]

    def filtro_municipios(df, municipio='', uf='', regiao='', mes='', ano=''):  # Aplica filtro na base municípios
        condition = df['Município'].str.len() > 0  # Condição que é sempre True
        if municipio != '':
            condition &= df['Município'].str.contains(municipio, case=False)
        if uf != '':
            condition &= df['Sigla UF'] == uf.upper()
        if regiao != '':
            condition &= df['Região'].str.contains(regiao, case=False)
        if mes != '':
            condition &= df['Mês/Ano'].astype(str).str.contains(Consts.MES[mes[:3].lower()])
        if ano != '':
            condition &= df['Mês/Ano'].astype(str).str.contains(ano)

        return df.loc[condition]
