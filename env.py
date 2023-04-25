from dotenv import load_dotenv
from os import getenv
load_dotenv() # Carregando o dotenv
SECRET = getenv("SECRET") # Pegando o segredo no dotenv
