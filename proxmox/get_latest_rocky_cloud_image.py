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
targetFile = "/mnt/pve/source/images/Rocky-9-GenericCloud.latest.x86_64.qcow2"

def get_remote_image():
    print("Getting remote image...")
    # Expects storage to be mapped at /mnt/pve/source
    if not Path(targetFile).is_file():
        try:
            urllib.request.urlretrieve(imageUrl, targetFile)
            urllib.request.urlretrieve(imageCheck, (targetFile + ".CHECKSUM"))
            print("> Got file.")
        except Exception as err:
            sys.exit("Error downloading file: " + str(err))
    else:
        print("> File already exists.")

def get_remote_checksum():
    print("Getting remote checksum...")
    try:
        urllib.request.urlretrieve(imageCheck, (targetFile + ".CHECKSUM"))
        print("> Got checksum.")
    except Exception as err:
        sys.exit("Error downloading checksum: " + str(err))
        
def get_sha256_checksum(file):
    print("Calculating file hash...")
    
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

print("Beginning checksum validation...")
if actual_hash == wanted_hash:
    print(f"{targetFile} checksum validation OK")
else:
    print(f"{targetFile} checksum validation FAIL")
    print(f"> Wanted : {wanted_hash}")
    print(f"> Got    : {actual_hash}")
    
    print("Removing and reaquiring image...")
    os.remove(targetFile)
    get_remote_image()
    get_remote_checksum()

print("")
print("Script is done.")