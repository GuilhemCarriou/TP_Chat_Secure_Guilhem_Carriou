import os
import logging
import dearpygui.dearpygui as dpg
from basic_gui import *
from cryptography.hazmat.primitives.ciphers import algorithms
from cryptography.hazmat.primitives.kdf.kbkdf import (
    CounterLocation,KBKDFCMAC,Mode
)
DEFAULT_VALUES = {
    "host" : "127.0.0.1",
    "port" : "6666",
    "name" : "foo",
    "pwd"  : "pwd_by_def" # Ajout d'un champ password 
}


class CypheredGUI(BasicGUI):
    
    def __init__(self) -> None:
        self._client = None
        self._callback = None
        self._log = logging.getLogger(self.__class__.__name__)

        self._key=None
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
        #AES, pkcs7, PBKDF2HMAC

    def encrypt(_in:str):
        sel=os.urandom(16) # 0 à 15 car hexa
        #utiliser seulement AES, pkcs7, PBKDF2HMAC
        kdf= KBKDFCMAC(
            algorithm=algorithms.AES,
            mode=Mode.CounterMode,
            length=2048,
            rlen=11,
            llen=11,
            location=CounterLocation.BeforeFixed,

        )
        return iv,encrypted
        


