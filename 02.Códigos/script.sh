#!/bin/bash

# 1 - Máquina do ubuntu no AWS 
# 2 - Pege o IP público
# 3 - Instale o PuTTY para transformar .pem em .ppk
# 4 - Instale o winSCP
# 5 - Inicie uma sessão da sua máquina AWS no winSCP
# 6 - Faça o upload dos arquivos:
#	app.py
# 	flaskapp
# 	script.sh(esse arquivo aqui)


# NÃO ESQUEÇA DE COLOCAR O IP PÚBLICO DA SUA MÁQUINA AWS NO ARQUIVO FLASK!!!

# Se houver problema que o terminal nao interpreta o script entao execute:
sed -i -e 's/\r$//' script.sh

# Permissões concedidas ao arquivo
sudo chmod 777 script.sh

# Atualiza a maquina
sudo apt-get --assume-yes update 

# Instala o python 3.8 da fonte
sudo apt --assume-yes install build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev libsqlite3-dev wget libbz2-dev
sudo wget https://www.python.org/ftp/python/3.8.0/Python-3.8.0.tgz
sudo tar -xf Python-3.8.0.tgz
cd Python-3.8.0
./configure --enable-optimizations
make -j 8
sudo make altinstall
python3.8 --version

# Instala as dependências para o desenvolvimento da API
sudo apt-get --assume-yes install nginx
sudo apt-get --assume-yes install gunicorn3
sudo apt --assume-yes install python3-pip
sudo python -m pip3 install --upgrade pip
sudo alternatives --set python  /usr/bin/python3.8

# Instala as bibliotecas necessárias para o trabalho
sudo pip3 install selenium --user
sudo pip3 install pandas
sudo pip3 install flask
sudo pip3 install flask_restful
sudo pip3 install xlrd

# Move o arquivo para rodar o servidor na marquina
sudo mv flaskapp /etc/nginx/sites-enabled/

sudo service nginx restart
cd
gunicorn3 app:app
