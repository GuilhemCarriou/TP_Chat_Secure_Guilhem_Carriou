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

DEFAULT_VALUES = {
    "host" : "127.0.0.1",
    "port" : "6666",
    "name" : "foo",
    "pwd"  : "pwd_by_def" # Ajout d'un champ password 
}

SALT_BY_DEFAULT="kD5meEw298t1pOaG".encode('utf-8') # constant pour ce tp
SIZE_KEY=16
N_ITERATION=100000

class CypheredGUI(BasicGUI):
    
    def __init__(self) -> None:
        super().__init__()
        self._key=bytes()
        #self._pwd=None

    # surcharge méthode pour ajouter champ password
    def _create_connection_window(self):
        with dpg.window(label="Connection", pos=(200, 150), width=400, height=300, show=False, tag="connection_windows"):
            
            for field in DEFAULT_VALUES.keys():
                with dpg.group(horizontal=True):
                    dpg.add_text(field)
                    if(field!='pwd'):
                        dpg.add_input_text(default_value=DEFAULT_VALUES[field], tag=f"connection_{field}")
                    else :
                        dpg.add_input_text(default_value=DEFAULT_VALUES[field], tag=f"connection_{field}",password=True)

            dpg.add_button(label="Connect", callback=self.run_chat)

    def run_chat(self, sender, app_data)->None:
        # callback used by the connection windows to start a chat session
        host = dpg.get_value("connection_host")
        port = int(dpg.get_value("connection_port"))
        name = dpg.get_value("connection_name")
        pwd:str = dpg.get_value("connection_pwd") 

        kdf=PBKDF2HMAC(
            algorithm=hashes.SHA256(),#algorithms.AES128(self._key),#AES128(self._key),
            length=SIZE_KEY,
            salt=SALT_BY_DEFAULT,
            iterations=N_ITERATION
        )
        self._key=kdf.derive(pwd.encode('utf-8'))

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

        size_of_block=algorithms.AES128.block_size
        padder=padding.PKCS7(size_of_block).padder()
        serialization=serpent.dumps(_in)#,encoding='utf-8'
        input_bytes=serpent.tobytes(serialization)
        data_padded=padder.update(input_bytes)+padder.finalize()#_in.encode('utf-8')

        cipher=Cipher(algorithms.AES128(self._key),modes.CTR(iv))
        
        encryptor =cipher.encryptor() 
        encrypted=encryptor.update(data_padded)+encryptor.finalize() # Données chiffrées
        print("iv ",(iv))
        print("encry ",(encrypted))
        return (iv,encrypted)
        
    def decrypt(self,iv:bytes,encrypted:bytes)->str:
        
        iv=base64.b64decode(iv)
        encrypted=base64.b64decode(encrypted)
        cipher=Cipher(algorithms.AES128(self._key),modes.CTR(iv))
        decryptor=cipher.decryptor()
        
        result_padded=decryptor.update(encrypted)+decryptor.finalize()
        unpadder=PKCS7(SIZE_KEY*8).unpadder()
        result=unpadder.update(result_padded)+unpadder.finalize()

        return result.decode('utf-8')
    
    def send(self,message:str):
        self._client.send_message(self.encrypt(message))
        #BasicGUI.send(encrypted_message)
    
    def recv(self):
        
        if self._callback is not None:
            for user, message in self._callback.get():
                self.update_text_screen(f"{user} : {self.decrypt(message[0]['data'],message[1]['data'])}")
            self._callback.clear()


if __name__=="__main__":

    logging.basicConfig(level=logging.DEBUG)
    
    client_secured=CypheredGUI()
    client_secured.create()
    client_secured.loop()
        


