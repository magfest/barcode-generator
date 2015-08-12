#!/bin/bash

apt-get update
apt-get install -y python3 python3-pip

pip3 install virtualenv

virtualenv-3.4 --always-copy env
env/bin/pip3 install -r requirements.txt

# wtf...case sensitive
mv /home/vagrant/shared/env/lib/python3.4/site-packages/crypto /home/vagrant/shared/env/lib/python3.4/site-packages/Crypto
