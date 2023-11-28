requests==2.25.1 <br/>
python-telegram-bot==13.7<br/>
web3==6.3.0<br/>
<br/>
<br/>
sudo apt update <br/>
sudo apt install -y unzip xvfb libxi6 libgconf-2-4 <br/>
sudo apt install default-jdk <br/>
sudo curl -sS -o - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add <br/>
sudo bash -c "echo 'deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main' >> /etc/apt/sources.list.d/google-chrome.list" <br/>
sudo apt -y update <br/>
sudo apt -y install google-chrome-stabl<br/>
google-chrome --version<br/>
<br/>
<br/>
<br/>
pm2 start main.py --interpreter python3 --name tracker<br/>