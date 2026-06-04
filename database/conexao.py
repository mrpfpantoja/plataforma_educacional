from sqlalchemy import create_engine
from models import Base

# Substitua pelas suas credenciais reais do MySQL local
# Formato: mysql+pymysql://usuario:senha@host:porta/nome_do_banco
DATABASE_URL = "mysql+pymysql://root:1234@localhost:3306/plataforma_edu"

# Cria a engine (o motor que se comunica com o banco)
engine = create_engine(DATABASE_URL, echo=True) 
# echo=True faz o console mostrar todos os comandos SQL sendo executados. 
# É ótimo para debugar agora no início!

def inicializar_banco():
    """
    Cria todas as tabelas mapeadas no arquivo models.py.
    Se a tabela já existir, ele não fará nada (é seguro rodar várias vezes).
    """
    print("Conectando ao banco de dados e criando tabelas...")
    Base.metadata.create_all(bind=engine)
    print("Tabelas criadas com sucesso!")

if __name__ == "__main__":
    inicializar_banco()