import os
import base64
import hashlib
import logging
import dearpygui.dearpygui as dpg
from cryptography.fernet import Fernet

from chat_client import ChatClient
from cyphered_gui import CypheredGUI
from generic_callback import GenericCallback
DEFAULT_VALUES = {
    "host" : "127.0.0.1",
    "port" : "6666",
    "name" : "foo",
    "pwd"  : "pwd_by_def" # Ajout d'un champ password 
}
SIZE_KEY=16

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
        iv=bytes(os.urandom(SIZE_KEY))

        fernet=Fernet(self._key)
        encrypted=fernet.encrypt(bytes(_in,'utf-8'))
        #iv=fernet.encrypt(bytes(iv,'utf-8'))

        return (iv, encrypted)
        
    def decrypt(self,iv:bytes, encrypted:bytes)->str:
        iv=base64.b64decode(iv)
        encrypted=base64.b64decode(encrypted)

        fernet=Fernet(self._key)
        # iv_decrypted=fernet.decrypt(bytes(iv,'utf-8'))
        message_decrypted=fernet.decrypt(bytes(encrypted))

        return message_decrypted.decode('utf-8')
    
   

if __name__=="__main__":

    logging.basicConfig(level=logging.DEBUG)
    
    client_secured=FernetGUI()
    client_secured.create()
    client_secured.loop()
        


