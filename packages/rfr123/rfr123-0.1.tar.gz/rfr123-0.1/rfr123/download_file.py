import os
import urllib.request

def download():
    url = "https://raw.githubusercontent.com/postscheduler/myrepo/main/RFR/RFR.Java"
    filename = "RFR.Java"
    filepath = os.path.join(os.getcwd(), filename)

    urllib.request.urlretrieve(url, filepath)
    print(f"{filename} downloaded to {os.getcwd()}")
