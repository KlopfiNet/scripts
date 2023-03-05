# Script to download the latest RockyLinux cloud image and validate its checksum
# github.com/ThisIsntTheWay

import os
from pathlib import Path
import urllib.request
import hashlib
import sys

###################################
#           VAR + FUNC
###################################
imageUrl   = "http://download.rockylinux.org/pub/rocky/9.1/images/x86_64/Rocky-9-GenericCloud.latest.x86_64.qcow2"
imageCheck = "http://download.rockylinux.org/pub/rocky/9.1/images/x86_64/Rocky-9-GenericCloud.latest.x86_64.qcow2.CHECKSUM"
targetFile = "/mnt/pve/source/Rocky-9-GenericCloud.latest.x86_64.qcow2"

def get_remote_image():
    # Expects storage to be mapped at /mnt/pve/source
    if not Path(targetFile).is_file():
        try:
            urllib.request.urlretrieve(imageUrl, targetFile)
            urllib.request.urlretrieve(imageCheck, (targetFile + ".CHECKSUM"))
        except Exception as err:
            sys.exit("Error downloading file: " + err)

def get_remote_checksum():
    try:
        urllib.request.urlretrieve(imageCheck, (targetFile + ".CHECKSUM"))
        print("Got checksum.")
    except Exception as err:
        sys.exit("Error downloading checksum: " + err)
        
def get_sha256_checksum(file):
    # Calculate actual file hash
    actual_hash = hashlib.sha256()
    with open(file, "rb") as f:
        while True:
            data = f.read(65536)
            if not data:
                break
            actual_hash.update(data)
            return actual_hash.hexdigest()

###################################
#               MAIN
###################################

get_remote_image()
get_remote_checksum()

# CHECKSUM comparison
with open((targetFile + ".CHECKSUM"), 'r') as f:
    next(f) # The downloaded file has a comment in the first line
    wanted_hash = f.readline().split(" = ")[1].strip()

actual_hash = get_sha256_checksum(targetFile)

if actual_hash == wanted_hash:
    print(targetFile + " checksum validation OK.")
else:
    print(targetFile + " checksum validation FAIL")
    print("> Wanted : " + wanted_hash)
    print("> Got    : " + actual_hash)
    
    os.remove(targetFile)
    get_remote_image()
    get_remote_checksum()
    