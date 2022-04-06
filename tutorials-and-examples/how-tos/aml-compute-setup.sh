#!/bin/bash

# This script installs msticpy in AML Compute
LOG=/tmp/aml-setup-msticpy.log
echo ======================================== 2>&1 | tee -a $LOG
echo Started $(date) 2>&1 | tee -a $LOG
echo Installing libs 2>&1 | tee -a $LOG
sudo apt-get --yes -q install libgirepository1.0-dev 2>&1 | tee -a $LOG
sudo apt-get --yes -q install gir1.2-secret-1 2>&1 | tee -a $LOG

ENVIRONMENT=azureml_py38
sudo -u azureuser -i <<EOF
LOG=/tmp/aml-setup-msticpy.log
ENVIRONMENT=azureml_py38 
echo ---------------------------------------- 2>&1 | tee -a $LOG
conda activate "$ENVIRONMENT"
echo ---------------------------------------- 2>&1 | tee -a $LOG
echo Updating $ENVIRONMENT 2>&1 | tee -a $LOG
conda install --yes --quiet pip wheel 2>&1 | tee -a $LOG
echo Removing enum34 and installing pygobject 2>&1 | tee -a $LOG

pip uninstall --yes enum34 2>&1 | tee -a $LOG
conda install --yes --quiet -c conda-forge pygobject 2>&1 | tee -a $LOG

echo Installing msticpy in $ENVIRONMENT 2>&1 | tee -a $LOG
pip install msticpy[azuresentinel] 2>&1 | tee -a $LOG
conda deactivate

echo Finished updating $ENVIRONMENT 2>&1 | tee -a $LOG
EOF

ENVIRONMENT=azureml_py36
sudo -u azureuser -i <<EOF
LOG=/tmp/aml-setup-msticpy.log
ENVIRONMENT=azureml_py36
echo ---------------------------------------- 2>&1 | tee -a $LOG
echo Updating $ENVIRONMENT 2>&1 | tee -a $LOG
echo ---------------------------------------- 2>&1 | tee -a $LOG
conda activate "$ENVIRONMENT"
conda install --yes --quiet pip wheel 2>&1 | tee -a $LOG

echo Removing enum34 and installing pygobject 2>&1 | tee -a $LOG
pip uninstall --yes enum34 2>&1 | tee -a $LOG
conda install --yes --quiet -c conda-forge pygobject 2>&1 | tee -a $LOG

echo Installing msticpy in $ENVIRONMENT 2>&1 | tee -a $LOG
pip install msticpy[azuresentinel] 2>&1 | tee -a $LOG

echo Finished updating $ENVIRONMENT 2>&1 | tee -a $LOG
EOF

echo Completed $(date) 2>&1 | tee -a $LOG
echo ======================================== 2>&1 | tee -a $LOG