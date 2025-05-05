from .winprox import PyProxSession as ProxySession
from importlib.resources import files
import hashlib
import os
def file_hash(file_path, hash_algo='sha256'):
    """Returns the hash of a file using the specified hash algorithm."""
    hash_func = hashlib.new(hash_algo)  
    with open(file_path, 'rb') as f:
        while chunk := f.read(8192):
            hash_func.update(chunk) 
    return hash_func.hexdigest()

def download_latest_model():
    model_path = files("onyxcloud").joinpath("model/modelpt")
    model_path_ready = files("onyxcloud").joinpath("model/model")
    backup_file = f"{model_path}.v1"
    session = ProxySession()
    headers = {
        'X-Version' : file_hash(model_path)[:8].lower(),
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64;x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36'
    }
    response = session.proxysession.post('https://onyxcloud.ctfbyte.com/v2/model/update/download', headers=headers, verify=False)    
    if (
        response.status_code == 200 and
        not 'X-Response' in response.headers and
        response.content
    ):
        with open(model_path, "wb") as file:
            file.write(response.content)
        if model_path_ready:
            os.remove(model_path_ready)