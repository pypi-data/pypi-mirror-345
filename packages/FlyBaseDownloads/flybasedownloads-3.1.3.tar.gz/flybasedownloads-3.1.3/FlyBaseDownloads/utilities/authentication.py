#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import os
from pathlib import Path
from dotenv import load_dotenv, set_key



class Authentication:
    def __init__(self):
        """
        Inicializa la clase con la URL base del backend.
        """
        
        self.env_path = Path(__file__).resolve().parents[1] / ".env"
        load_dotenv(dotenv_path=self.env_path, override=True)
        self.base_url = os.getenv("BASE_URL")
        

    def get_user(self, username, password, email = None):
        """
        Crea un usuario nuevo o recupera uno existente mediante el backend.
        """
        endpoint = f"{self.base_url}/users/"
        data = {"email": email, "username": username, "password": password}

        response = requests.post(endpoint, json=data)

        if response.status_code == 200:
            user_id = response.json().get("id")
            print("Usuario creado exitosamente")
            set_key(str(self.env_path), "USER_ID", str(user_id))
            
        elif response.status_code == 400:  # Usuario ya existe
            print("El usuario ya existe. Intentando autenticar...")
            return self.verify_user(username, password)
        else:
            print(f"Error al registrar o autenticar el usuario: {response.status_code} - {response.text}")
            set_key(str(self.env_path), "USER_ID", "00")
            return None

    def verify_user(self, username, password):
        """
        Verifica las credenciales del usuario mediante el backend.
        """
        endpoint = f"{self.base_url}/login/"
        data = {"username": username, "password": password}

        response = requests.post(endpoint, json=data)

        if response.status_code == 200:
            user_id = response.json().get("user_id")
            print("Autenticación exitosa")
            set_key(str(self.env_path), "USER_ID", str(user_id))
        else:
            print(f"Error de autenticación: {response.status_code} - {response.text}")
            set_key(str(self.env_path), "USER_ID", "00")
            return None

