import os
from dotenv import load_dotenv
from pathlib import Path
import mysql.connector

""" Funktion um den Pfad des Projektes auszulesen. """


def get_project_root() -> Path:
    return (Path(__file__).parent.parent)


env_path = Path(get_project_root()) / '.env'  # Projekt pfad zur .enf zusammenfügen
load_dotenv(dotenv_path=env_path)

""" Funktion um den Datenbank-Login bereitzustellen und enstrpechend zurück zugeben"""


def getDataBaselogin():
    db = mysql.connector.connect(
        host=os.getenv("HOST"),
        user=os.getenv("USER"),
        password=os.getenv("PASSWORD"),
        database=os.getenv("DATABASE"),
        autocommit=True
    )
    return db
