import os
import logging
import dearpygui.dearpygui as dpg
from basic_gui import *

from cryptography.hazmat.primitives.ciphers import algorithms,modes,Cipher
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.padding import PKCS7

DEFAULT_VALUES = {
    "host" : "127.0.0.1",
    "port" : "6666",
    "name" : "foo",
    "pwd"  : "pwd_by_def" # Ajout d'un champ password 
}
SALT_BY_DEFAULT="kD5meEw298t1pOaG".encode('utf-8') # constant pour ce tp

class CypheredGUI(BasicGUI):
    
    def __init__(self) -> None:
        super.init()
        self._key=bytes()
        #self._pwd=None

    # surcharge méthode pour ajouter champ password
    def _fonction_create_connection_window(self):
        with dpg.window(label="Connection", pos=(200, 150), width=400, height=300, show=False, tag="connection_windows"):
            
            for field in DEFAULT_VALUES.keys():
                with dpg.group(horizontal=True):
                    dpg.add_text(field)
                    dpg.add_input_text(default_value=DEFAULT_VALUES[field], tag=f"connection_{field}")

            dpg.add_button(label="Connect", callback=self.run_chat)

    def run_chat(self, sender, app_data)->None:
        # callback used by the connection windows to start a chat session
        host = dpg.get_value("connection_host")
        port = int(dpg.get_value("connection_port"))
        name = dpg.get_value("connection_name")
        pwd = dpg.get_value("connection_pwd") 


        self._log.info(f"Connecting {name}@{host}:{port}")
        self._callback = GenericCallback()
        self._client = ChatClient(host, port)
        self._client.start(self._callback)
        self._client.register(name)

        #self.key=

        dpg.hide_item("connection_windows")
        dpg.show_item("chat_windows")
        dpg.set_value("screen", "Connecting")

    def encrypt(_in:str)->tuple(bytes,bytes):

        size_of_key=16 # in bytes, so 128 bits
        
        size_of_block=algorithms.AES128.block_size

        kdf= PBKDF2HMAC(
            algorithm=algorithms.AES128(),
            length=size_of_key, # 16 bytes asked for key length
            salt=SALT_BY_DEFAULT,
            iterations=100000,
        )

        self._key=kdf.derive(DEFAULT_VALUES["pwd"])

        iv=os.urandom(size_of_key) #

        padder=padding.PKCS7(size_of_block).padder()
        data_padded=padder.update(_in.encode('utf-8'))+padder.finalize()

        cipher=Cipher(algorithms.AES128(self._key),modes.CTR(iv))
        
        encryptor =cipher.encryptor() 
        encrypted=encryptor.update(data_padded)+encryptor.finalize() # Données chiffrées
        
        return iv,encrypted
        
    def decrypt(iv,encrypted:tuple(bytes,bytes))->str:
        
        size_of_key=16
        kdf=PBKDF2HMAC(
            algorithms=algorithms.AES128(),
            length=size_of_key,
            salt=SALT_BY_DEFAULT,
            iterations=100000
        )
        self._key=kdf.derive(DEFAULT_VALUES["pwd"])

        cipher=Cipher(algorithms.AES128(self._key),modes.CTR(iv))
        decryptor=cipher.decryptor()
        
        result_padded=decryptor.update(encrypted)+decryptor.finalize()
        unpadder=PKCS7(size_of_key*8).unpadder()
        result=unpadder.update(result_padded)+unpadder.finalize()

        return result.decode('utf-8')


