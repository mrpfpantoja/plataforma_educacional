import os
import streamlit as st
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base

# Verifica se está rodando no Streamlit Cloud (onde os secrets existem)
if "DATABASE_URL" in st.secrets:
    DATABASE_URL = st.secrets["DATABASE_URL"]
else:
    # Se estiver rodando no seu computador (localhost), usa o banco local
    DATABASE_URL = "mysql+pymysql://root:1234@localhost/plataforma_edu"

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