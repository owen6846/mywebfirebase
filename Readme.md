
sudo apt-get update

安裝git
sudo apt-get install git
git clone https://github.com/owen6846/mywebfirebase.git

安裝python
sudo apt-get update
sudo apt-get install python3 python3-dev build-essential
wget https://bootstrap.pypa.io/get-pip.py
sudo python3 get-pip.py
pip3 install -r requirements.txt
vim .env.production 設定內容
vim firebase-credentials-dev.json copy firebase金鑰
nohup python3 app.py --host=0.0.0.0 --port=5000 > f flask.log 2>&1 &

安裝nginx
sudo apt install -y nginx
sudo systemctl status nginx
cd vue/dist/
sudo rm -rf /var/www/html/*
sudo cp -r * /var/www/html/
sudo nano /etc/nginx/sites-available/default 
*設定nano Ctrl+S存檔 Ctrl+Z離開
sudo nginx -t
sudo systemctl reload nginx

