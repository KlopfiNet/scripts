#!/bin/bash
# Script to install various hashicorp products

if [[ $EUID > 0 ]]
  then echo "ERR: Must run as root."
  exit
fi

wget -O- https://apt.releases.hashicorp.com/gpg | gpg --dearmor | sudo tee /usr/share/keyrings/hashicorp-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list

apt update
apt install packer vault -y

# Terraform is not available for arm64 through the package repository
echo Installing terraform...
wget https://releases.hashicorp.com/terraform/1.3.9/terraform_1.3.9_linux_arm64.zip -O ./terraform.zip
unzip terraform.zip -d /usr/local/bin/
rm ./terraform.zip

echo All done.