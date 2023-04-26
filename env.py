from dotenv import load_dotenv
from os import getenv
load_dotenv() # Carregando o dotenv
SECRET = getenv("SECRET") # Pegando o segredo no dotenv
PORT = getenv("PORT") # carregando a porta dentro do dotenv
ADMIN = getenv("ADMIN") # Carregando o nome de usuário