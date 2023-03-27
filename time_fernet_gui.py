import os
import time
import base64
import logging
from cryptography.fernet import Fernet
from cryptography.fernet import InvalidToken

from fernet_gui import FernetGUI


DEFAULT_VALUES = {
    "host" : "127.0.0.1",
    "port" : "6666",
    "name" : "foo",
    "pwd"  : "pwd_by_def" # Ajout d'un champ password 
}

TIME_TO_LIVE = 30 # durée de validité message (secondes)


DEFAULT_VALUES = {
    "host" : "127.0.0.1",
    "port" : "6666",
    "name" : "foo",
    "pwd"  : "pwd_by_def" # Ajout d'un champ password 
}

SIZE_KEY=16


class TimeFernetGUI(FernetGUI):
    
    def __init__(self) -> None:
        super().__init__()


    def encrypt(self,_in:str)->tuple([bytes,bytes]):

        # génération aléatoire de la taille de la clef (16 octets=128 bits)
        # du vecteur d'initialisation
        iv=bytes(os.urandom(SIZE_KEY))
        
        # récupération de l'heure actuelle
        now_time=int(time.time())

        # déclaration de la méthode d'enchiffrement symétrique fernet
        fernet=Fernet(self._key)

        # chiffrement du message selon la méthode fernet avec la date de chiffrement précisée
        # sert de référence pour la durée de vie du message
        encrypted=fernet.encrypt_at_time(bytes(_in,'utf-8'),current_time=now_time)

        return (iv, encrypted)
        
    def decrypt(self,iv:bytes, encrypted:bytes)->str:

        # décodage depuis la base64
        iv=base64.b64decode(iv)
        encrypted=base64.b64decode(encrypted)
        # récupération de l'heure actuelle qui permettra de savoir
        # si le message est invalide
        now_time=int(time.time())

        # déclaration de la méthode dechiffrement symétrique fernet
        fernet=Fernet(self._key)

        try:
            # si le message a moins de 30 secondes, déchiffrement
            message_decrypted=fernet.decrypt_at_time(bytes(encrypted),current_time=now_time,ttl=TIME_TO_LIVE)
            result=message_decrypted.decode('utf-8')
            
            # déchiffrement réussi, retour message déchiffré
            return result
        
        # sinon, token du message ("piece d'identité du message")
        # invalide et enregistrement de l'erreur dans le log 
        except InvalidToken as err:
            logging.error("Invalid Token")
            raise InvalidToken
        

if __name__=="__main__":

    logging.basicConfig(level=logging.DEBUG)
    
    client_secured=TimeFernetGUI()
    client_secured.create()
    client_secured.loop()
        


