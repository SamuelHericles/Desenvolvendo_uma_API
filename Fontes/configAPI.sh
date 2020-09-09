#!/bin/bash

sudo apt-get update
# Instala o Python, Pip, Nginx e Gunicorn
sudo apt-get --assume-yes install python3 python3-pip nginx gunicorn3 
# Instala dependêcias da API
sudo pip3 install flask flask_restful pandas xlrd plotly

# Move a nova config e remove a antiga
sudo mv ./api_settings /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default

# Restarta o serviço do Nginx
sudo service nginx restart
#Roda o script da API
gunicorn3 app:app
