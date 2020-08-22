sudo apt-get update
sudo apt-get --assume-yes install python3 python3-pip nginx gunicorn3
sudo pip3 install flask flask_restful pandas xlrd

wget https://raw.githubusercontent.com/SamuelHericles/Desenvolvendo_uma_API/master/02.C%C3%B3digos/app.py
wget https://raw.githubusercontent.com/SamuelHericles/Desenvolvendo_uma_API/master/02.C%C3%B3digos/api_settings
sudo mv ./api_settings /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default
sudo service nginx restart

gunicorn3 app:app