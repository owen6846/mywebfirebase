# My Web
  這是一篇建立一台VM，並在VM上部屬前後端分離的網站的文章
  
  前端使用Vue  
  後端使用Python Flask  
  資料儲存方式則使用Firebase  
  VM使用GCE  

## 先建立一台GCE VM
> 可以參考這篇文章 [終身免費的 VM 服務！Google Cloud 免費方案分享](https://kucw.io/blog/gcp-free-tier/)

## 進入GCE VM
> 步驟1 使用Google SSH進入GCE VM中  
> 步驟2 先執行```sudo apt-get update```  
> 步驟3 安裝git  
```
sudo apt-get install git  
git clone <repository_url>
```
> 步驟4 安裝python
```
sudo apt-get update
sudo apt-get install python3 python3-dev build-essential
wget https://bootstrap.pypa.io/get-pip.py
sudo python3 get-pip.py
```
> 步驟5 移動到端Python專案目錄，並install requirements
```
cd <python 專案目錄>
pip3 install -r requirements.txt
```
>> 如果需要調整 .env.production 可以用 ```vim .env.production```  
> 按```i```進入insert模式，即可輸入文字，想跳出insert模式時，按Esc回到command/normal模式即可  
> 如果想要保持修改的內容並離開，按```:```進入命令模式(Command Mode)，然後輸入 ```wq```，最後按Enter即可存檔離開。 
>> <img width="787" height="36" alt="image" src="https://github.com/user-attachments/assets/a410ff79-cba6-4500-9a46-46a83da72556" />

> 步驟6 建立一個Firebase Service Account key key  
> Go to your project's Service Accounts page in the Firebase Console.  
> Generate a new private key for a service account.  
> This will download a JSON file containing your credentials. Keep this file secure.  
> 步驟7 複製Firebae key 到VM上
```
vim firebase-credentials-dev.json copy your_firebase_key  
```
> 步驟8 背景執行python
```
nohup python3 app.py --host=0.0.0.0 --port=5000 > flask.log 2>&1 & (這是背景執行方式)
```
> 步驟8 安裝nginx
```
sudo apt install -y nginx
sudo systemctl status nginx
cd vue/dist/
sudo rm -rf /var/www/html/*
sudo cp -r * /var/www/html/
sudo nano /etc/nginx/sites-available/default 
*設定nano Ctrl+S存檔 Ctrl+Z離開
sudo nginx -t
sudo systemctl reload nginx
```


