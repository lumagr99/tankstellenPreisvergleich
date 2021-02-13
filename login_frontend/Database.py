import os
from dotenv import load_dotenv
from pathlib import Path
import mysql.connector


# project_folder = os.path.expanduser("C:/Users(Sven Rust/PycharmProjects/tankstellenPreisvergleich")  # adjust as appropriate
def get_project_root() -> Path:
    return (Path(__file__).parent.parent)


get_project_root()

env_path = Path(get_project_root()) / '.env'
load_dotenv(dotenv_path=env_path)

def getDataBaselogin():
    db = mysql.connector.connect(
        host=os.getenv("HOST"),
        user=os.getenv("USER"),
        password=os.getenv("PASSWORD"),
        database=os.getenv("DATABASE"),
        autocommit=True
    )
    return db
