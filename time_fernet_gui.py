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


class TimeFernetGUI(FernetGUI):
    
    def __init__(self) -> None:
        super().__init__()
        self._key=bytes()
        #self._pwd=None

    def encrypt(self,_in:str)->tuple([bytes,bytes]):
        now_time=int(time.time())
        fernet=Fernet(self._key)
        encrypted=fernet.encrypt_at_time(bytes(_in,'utf-8'),current_time=now_time)
        return (encrypted)
        
    def decrypt(self,iv:bytes, encrypted:bytes)->str:
        iv=base64.b64decode(iv)
        encrypted=base64.b64decode(encrypted)
        now_time=int(time.time())
        fernet=Fernet(self._key)
        try:
            iv_decrypted=fernet.decrypt_at_time(bytes(iv,'utf-8'),now_time,ttl=TIME_TO_LIVE)
            message_decrypted=fernet.decrypt_at_time(bytes(encrypted,'utf-8'),now_time,ttl=TIME_TO_LIVE)
            
            result=iv_decrypted.decode('utf-8'),message_decrypted.decode('utf-8')
            return result
        except InvalidToken as err:
            logging.error("Invalid Token")
            raise InvalidToken
        
    
   

if __name__=="__main__":

    logging.basicConfig(level=logging.DEBUG)
    
    client_secured=TimeFernetGUI()
    client_secured.create()
    client_secured.loop()
        


