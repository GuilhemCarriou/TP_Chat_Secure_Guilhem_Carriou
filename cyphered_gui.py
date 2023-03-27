import os
import base64
import logging
import serpent
import dearpygui.dearpygui as dpg
from chat_client import ChatClient
from generic_callback import GenericCallback
from cryptography.hazmat.primitives.padding import PKCS7
from cryptography.hazmat.primitives import padding, hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import algorithms,modes,Cipher

from basic_gui import BasicGUI

# definition des champs propres à l'interface de connexion
DEFAULT_VALUES = {
    "host" : "127.0.0.1",
    "port" : "6666",
    "name" : "foo",
    "pwd"  : "pwd_by_def" # Ajout d'un champ password 
}

# sel constant encodé
SALT_BY_DEFAULT="kD5meEw298t1pOaG".encode('utf-8') # constant pour ce tp

# taille du sel
SIZE_KEY=16

# nombre d'itération
N_ITERATION=100000


class CypheredGUI(BasicGUI):
    
    # initialisation des classes mères lorsque déclaration classe fille 
    def __init__(self) -> None:
        super().__init__()
        self._key=bytes()


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

        # méthode de dérivation de clef
        key_derivation_method=PBKDF2HMAC(
            algorithm=hashes.SHA256(), # hashage par SHA256 (découpages, compressions du sel)
            length=SIZE_KEY,
            salt=SALT_BY_DEFAULT,
            iterations=N_ITERATION
        )

        #dérivation de la clef à partir du mot de passe, par la méthode PBKDF2HMAC
        self._key=key_derivation_method.derive(pwd.encode('utf-8'))

        self._log.info(f"Connecting {name}@{host}:{port}")
        self._callback = GenericCallback()
        self._client = ChatClient(host, port)
        self._client.start(self._callback)
        self._client.register(name)

        dpg.hide_item("connection_windows")
        dpg.show_item("chat_windows")
        dpg.set_value("screen", "Connecting")

    def encrypt(self,_in:str)->tuple([bytes,bytes]):
        
        # génération aléatoire de la taille de la clef (16 octets=128 bits)
        # du vecteur d'initialisation
        iv=bytes(os.urandom(SIZE_KEY))

        # définition de la taille du bloc subissant le chiffrement AES128
        size_of_block=algorithms.AES128.block_size

        # padding des bloc selon la syntaxe PKCS7 d'enchiffrement
        padder=padding.PKCS7(size_of_block).padder()

        # 
        serialization=serpent.dumps(_in)
        input_bytes=serpent.tobytes(serialization)

        # padding des données en bytes 
        data_padded=padder.update(input_bytes)+padder.finalize()

        # préparation de la méthode de chiffrement par la méthode CTR
        # selon la clef chiffrée par AES128
        cipher=Cipher(algorithms.AES128(self._key),modes.CTR(iv))
        
        # génération de l'enchiffreur
        encryptor =cipher.encryptor() 

        # padding et finalisation
        encrypted=encryptor.update(data_padded)+encryptor.finalize() # Données chiffrées
        
        return (iv,encrypted)
        
    def decrypt(self,iv:bytes,encrypted:bytes)->str:
        
        # decodage selon le standard base64
        iv=base64.b64decode(iv)
        encrypted=base64.b64decode(encrypted)

        # préparation de la méthode de dechiffrement par la méthode CTR du v.i.
        # selon la clef chiffrée par AES128
        cipher=Cipher(algorithms.AES128(self._key),modes.CTR(iv))

        # génération du déchiffreur 
        decryptor=cipher.decryptor()
        
        # mise à jour et finalisation des données enchiffrées
        result_padded=decryptor.update(encrypted)+decryptor.finalize()

        # "de"padding
        unpadder=PKCS7(SIZE_KEY*8).unpadder()

        # finalisation
        result=unpadder.update(result_padded)+unpadder.finalize()

        return result.decode('utf-8')
    
    def send(self,message:str):
        #envoi du message chiffré
        self._client.send_message(self.encrypt(message))

    
    def recv(self):
        
        # reception et affichage des messages déchiffrés
        if self._callback is not None:
            for user, message in self._callback.get():
                self.update_text_screen(f"{user} : {self.decrypt(message[0]['data'],message[1]['data'])}")
            self._callback.clear()


if __name__=="__main__":

    logging.basicConfig(level=logging.DEBUG)
    
    client_secured=CypheredGUI()
    client_secured.create()
    client_secured.loop()
        


