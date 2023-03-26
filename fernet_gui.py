import os
import base64
import logging
import dearpygui.dearpygui as dpg
from basic_gui import *
import serpent
from cryptography.hazmat.primitives.ciphers import algorithms,modes,Cipher
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import padding, hashes
from cryptography.hazmat.primitives.padding import PKCS7
from cryptography.hazmat.backends import default_backend
from cyphered_gui import*
import hashlib
from cryptography.fernet import Fernet

DEFAULT_VALUES = {
    "host" : "127.0.0.1",
    "port" : "6666",
    "name" : "foo",
    "pwd"  : "pwd_by_def" # Ajout d'un champ password 
}

SALT_BY_DEFAULT="kD5meEw298t1pOaG".encode('utf-8') # constant pour ce tp
SIZE_KEY=16
N_ITERATION=100000

class FernetGUI(CypheredGUI):
    
    def __init__(self) -> None:
        super().__init__()
        self._key=bytes()
        #self._pwd=None

   
    def run_chat(self, sender, app_data)->None:
        # callback used by the connection windows to start a chat session
        host = dpg.get_value("connection_host")
        port = int(dpg.get_value("connection_port"))
        name = dpg.get_value("connection_name")
        pwd:str = dpg.get_value("connection_pwd") 

        self._key=hashlib.sha256(pwd.encode()).digest()
        self._key=base64.b64encode(self._key)

        self._log.info(f"Connecting {name}@{host}:{port}")
        self._callback = GenericCallback()
        self._client = ChatClient(host, port)
        self._client.start(self._callback)
        self._client.register(name)

        dpg.hide_item("connection_windows")
        dpg.show_item("chat_windows")
        dpg.set_value("screen", "Connecting")

    def encrypt(self,_in:str)->tuple([bytes,bytes]):
        
        fernet=Fernet(self._key)
        encrypted=fernet.encrypt(bytes(_in,'utf-8'))
        return (encrypted)
        
    def decrypt(self,iv:bytes, encrypted:bytes)->str:
        iv=base64.b64decode(iv)
        encrypted=base64.b64decode(encrypted)
        fernet=Fernet(self._key)
        iv_decrypted=fernet.decrypt(bytes(iv,'utf-8'))
        message_decrypted=fernet.decrypt(bytes(encrypted,'utf-8'))
        result=iv_decrypted.decode('utf-8'),message_decrypted.decode('utf-8')

        return result
    
   

if __name__=="__main__":

    logging.basicConfig(level=logging.DEBUG)
    
    client_secured=FernetGUI()
    client_secured.create()
    client_secured.loop()
        


