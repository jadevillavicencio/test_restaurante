# =====================================================
# CONFIGURACIÓN DE LA BASE DE DATOS
# =====================================================

import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_NAME = os.getenv('DB_NAME', 'restaurante')
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'tu_contraseña')
    DB_PORT = os.getenv('DB_PORT', '5432')
    
    @staticmethod
    def get_db_url():
        return f"host={Config.DB_HOST} dbname={Config.DB_NAME} user={Config.DB_USER} password={Config.DB_PASSWORD} port={Config.DB_PORT}"
