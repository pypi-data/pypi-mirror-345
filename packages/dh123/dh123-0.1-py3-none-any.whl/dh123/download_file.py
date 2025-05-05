import os
import urllib.request

def download():
    url = "https://raw.githubusercontent.com/postscheduler/myrepo/main/DH/DH.Java"
    filename = "DH.Java"
    filepath = os.path.join(os.getcwd(), filename)

    urllib.request.urlretrieve(url, filepath)
    print(f"{filename} downloaded to {os.getcwd()}")
