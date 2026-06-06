import os
import streamlit as st
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base

# Verifica de forma segura se estamos rodando no Streamlit Cloud
# O Streamlit Cloud injeta variáveis de ambiente, o seu localhost não.
try:
    # Tenta puxar a URL direto dos secrets (vai funcionar na nuvem)
    DATABASE_URL = st.secrets["DATABASE_URL"]
except FileNotFoundError:
    # Se o arquivo não existir (que é o caso do seu computador local), cai aqui
    DATABASE_URL = "mysql+pymysql://root:SUA_SENHA_AQUI@localhost/plataforma_edu"
except Exception:
    # Segurança extra
    DATABASE_URL = "mysql+pymysql://root:SUA_SENHA_AQUI@localhost/plataforma_edu"

# Cria a engine de conexão
engine = create_engine(DATABASE_URL, echo=False)
Base = declarative_base()

# Cria as tabelas caso não existam
def init_db():
    import database.models
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_db()
    print("Banco de dados inicializado com sucesso!")