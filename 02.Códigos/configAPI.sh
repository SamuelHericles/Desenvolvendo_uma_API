#!/bin/bash

sudo apt-get update
# Instala o Python, Pip, Nginx e Gunicorn
sudo apt-get --assume-yes install python3 python3-pip nginx gunicorn3 
# Instala dependêcias da API
sudo pip3 install flask flask_restful pandas xlrd plotly

# Baixa o código-fonte da API e arquivo de config do Nginx
wget https://raw.githubusercontent.com/SamuelHericles/Desenvolvendo_uma_API/master/02.C%C3%B3digos/app.py
wget https://raw.githubusercontent.com/SamuelHericles/Desenvolvendo_uma_API/master/02.C%C3%B3digos/api_settings

# Baixa as bases de dados
mkdir 01.Dados
cd 01.Dados
wget https://github.com/SamuelHericles/Desenvolvendo_uma_API/blob/master/01.Dados/indicadoressegurancapublicamunicmar20.xlsx?raw=true
wget https://github.com/SamuelHericles/Desenvolvendo_uma_API/blob/master/01.Dados/indicadoressegurancapublicaufmar20.xlsx?raw=true
cd ..

# Move a nova config e remove a antiga
sudo mv ./api_settings /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default

# Restarta o serviço do Nginx
sudo service nginx restart
#Roda o script da API
gunicorn3 app:app
