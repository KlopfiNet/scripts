# Script to download the latest Ubuntu Server image
# Usage  : python3 script.py <version>
# Example: script.py 22.04 
# github.com/ThisIsntTheWay

import os
from pathlib import Path
import urllib.request
import argparse
import requests
import hashlib
import sys

###################################
#           VAR + FUNC
###################################
parser = argparse.ArgumentParser()
parser.add_argument("version")

version = parser.parse_args().version
target = "ubuntu-{}-server-cloudimg-amd64.img".format(version)

imageUrl   = "https://cloud-images.ubuntu.com/releases/server/{}/release/{}".format(version, target)
imageCheck = "https://cloud-images.ubuntu.com/releases/server/{}/release/SHA256SUMS".format(version)
targetFile = "/mnt/pve/source/template/iso/{}".format(target)

def get_remote_image():
    print(f"{bcolors.WARNING}Getting remote image of version {version} ({imageUrl})...{bcolors.ENDC}")
    # Expects storage to be mapped at /mnt/pve/source/template/iso
    if not Path(targetFile).is_file():
        try:
            urllib.request.urlretrieve(imageUrl, targetFile)
            urllib.request.urlretrieve(imageCheck, (targetFile + ".CHECKSUM"))
            print(f"{bcolors.OKGREEN}> Got file.{bcolors.ENDC}")
        except Exception as err:
            sys.exit(f"{bcolors.FAIL}Error downloading file: {str(err)}{bcolors.ENDC}")
    else:
        print(f"{bcolors.OKCYAN}> File already exists.{bcolors.ENDC}")

def get_remote_checksum():
    print(f"{bcolors.WARNING}Getting remote checksum ({imageCheck})...{bcolors.ENDC}")
    try:
        response = requests.get(imageCheck)
        checksum = None
        
        for line in response.text.split('\n'):
            print("- " + line)
            if target in line:
                checksum = line.strip().split()[0]
                print (checksum)
                break
        
        if checksum:
            print(f"{bcolors.OKGREEN}> Got checksum ({checksum}).{bcolors.ENDC}")
            return checksum
        else:
            sys.exit(f"{bcolors.FAIL}[X] Did not find checksum for '{target}' on remote target.{bcolors.ENDC}")
            
    except Exception as err:
        sys.exit(f"{bcolors.FAIL}[X] Error downloading checksum: {str(err)}{bcolors.ENDC}")
        
def get_sha256_checksum(file):
    print(f"{bcolors.OKBLUE}Calculating file hash of {file}...{bcolors.ENDC}")
    
    # Calculate actual file hash
    hash = hashlib.sha256()
    with open(file,"rb") as f:
        # Read and update hash string value in blocks of 4K
        for byte_block in iter(lambda: f.read(4096),b""):
            hash.update(byte_block)
        return hash.hexdigest()
        
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


###################################
#               MAIN
###################################

get_remote_image()
wanted_hash = get_remote_checksum()
actual_hash = get_sha256_checksum(targetFile)

if actual_hash == wanted_hash:
    print(f"{bcolors.OKGREEN}{targetFile} checksum validation OK{bcolors.ENDC}")
else:
    print(f"{bcolors.FAIL}{targetFile} checksum validation FAIL{bcolors.ENDC}")
    print(f"{bcolors.WARNING}> Wanted : {wanted_hash}{bcolors.ENDC}")
    print(f"{bcolors.WARNING}> Got    : {bcolors.UNDERLINE}{actual_hash}{bcolors.ENDC}")
    
    print(f"{bcolors.WARNING}Removing and reaquiring image...{bcolors.ENDC}")
    os.remove(targetFile)
    get_remote_image()
    get_remote_checksum()

print("")
print(f"{bcolors.OKCYAN}Script is done.{bcolors.ENDC}")