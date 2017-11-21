#! /bin/sh

#check
if [$1 -eq '']
then
echo "Please input parameter"
exit
fi

#import anaconda
export PATH=/home/pi/berryconda3/bin:$PATH

sudo git init
sudo git config --global http.sslverify false
sudo git config --global user.name 'abednego1979'
sudo git config --global user.email 'abednego1979@163.com'

#get diff tools
sudo rm -rf diff_tools/
sudo git clone https://github.com/abednego1979/diff_tools.git
sudo chown -R pi:pi diff_tools/

#get base code
sudo rm -rf $1/
sudo git clone https://github.com/abednego1979/$1.git
sudo chown -R pi:pi $1/

#patch
cd ./diff_tools/source
python tools.py $1
cd ../../

#commit code
cd $1
sudo git add .
sudo git commit -m 'patch shell'
sudo git push -u origin master
cd ..

#clear
sudo rm -rf $1/
sudo rm -rf diff_tools/
