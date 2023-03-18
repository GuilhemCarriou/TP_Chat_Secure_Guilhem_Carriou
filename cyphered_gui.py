import os
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

    def encrypt(self,_in:str)->tuple([bytes,bytes]):

        size_of_key=16 # in bytes, so 128 bits
        
        size_of_block=algorithms.AES128.block_size
        
        kdf= PBKDF2HMAC(
            algorithm=hashes.SHA256(),#algorithms.AES128(self._key),#SHA256?
            length=size_of_key, # 16 bytes asked for key length
            salt=SALT_BY_DEFAULT,
            iterations=100000
        )

        self._key=kdf.derive(SALT_BY_DEFAULT)#DEFAULT_VALUES["pwd"])
        

        iv=os.urandom(size_of_key) #

        padder=padding.PKCS7(size_of_block).padder()
        serialization=serpent.dumps(_in,encoding='utf-8')
        input_bytes=serpent.tobytes(serialization)
        data_padded=padder.update(input_bytes)+padder.finalize()#_in.encode('utf-8')

        cipher=Cipher(algorithms.AES128(self._key),modes.CTR(iv))
        
        encryptor =cipher.encryptor() 
        encrypted=encryptor.update(data_padded)+encryptor.finalize() # Données chiffrées
        
        return iv,encrypted
        
    def decrypt(self,iv:bytes,encrypted:bytes)->str:
        
        size_of_key=16
        kdf=PBKDF2HMAC(
            algorithms=hashes.SHA256(),#algorithms.AES128(self._key),#AES128(self._key),
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
    
    def send(self,message:str):
        iv,encrypted_message=self.encrypt(message)
        self._client.send_message(self.encrypt(message))
        #BasicGUI.send(encrypted_message)
    
    def recv(self):
        # detecter si message a déjà été déchiffrer
        # pour éviter que déchiffrement h24 pour chaque message
        if self._callback is not None:
            for user, message in self._callback.get():
                self.update_text_screen(f"{user} : {self.decrypt(message)}")
            self._callback.clear()


if __name__=="__main__":
    logging.basicConfig(level=logging.DEBUG)
    
    client_secured=CypheredGUI()
    client_secured.create()
    client_secured.loop()
        


