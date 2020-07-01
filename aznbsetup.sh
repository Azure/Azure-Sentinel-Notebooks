#!/bin/bash

# Activate environment (add this to the end of .bashrc)
source ~/anaconda3_501/bin/activate
echo >> ~.bashrc
echo source ~/anaconda3_501/bin/activate >> .bashrc

echo Started environment setup
date
touch ~/.mpnb.lock
# pip
pip install --upgrade pip
pip install --disable-pip-version-check -r ~/library/requirements.txt

rm -f ~/.mpnb.lock
echo Environment setup complete
date