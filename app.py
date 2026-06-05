import streamlit as st
import hashlib
from sqlalchemy.orm import sessionmaker
from database.conexao import engine
from database.models import Usuario, TipoPerfil

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Plataforma Educacional", page_icon="🎓", layout="centered")

# --- FUNÇÕES AUXILIARES ---
def hash_senha(senha):
    """Criptografa a senha usando SHA-256 para não salvar em texto puro no banco."""
    return hashlib.sha256(senha.encode()).hexdigest()

# Criando a sessão de comunicação com o banco de dados
Session = sessionmaker(bind=engine)
session = Session()

# Inicializando variáveis de estado (Session State) para manter o usuário logado
if 'logado' not in st.session_state:
    st.session_state['logado'] = False
    st.session_state['usuario_nome'] = ""
    st.session_state['usuario_perfil'] = ""

# --- INTERFACE PRINCIPAL ---
st.title("🎓 Bem-vindo à Plataforma Educacional")
st.write("Aprenda e ensine em um só lugar. Totalmente gratuito.")

# Se o usuário já estiver logado, mostramos uma mensagem de boas-vindas
if st.session_state['logado']:
    st.success(f"Olá, {st.session_state['usuario_nome']}! Você está logado como {st.session_state['usuario_perfil'].value}.")
    
    if st.button("Sair (Logout)"):
        st.session_state['logado'] = False
        st.session_state['usuario_nome'] = ""
        st.session_state['usuario_perfil'] = ""
        st.rerun()
        
    st.info("O painel de controle (Dashboard) será construído nas próximas etapas!")

# Se não estiver logado, mostramos as opções de Login e Cadastro
else:
    # Usamos abas para separar as funcionalidades na mesma tela
    aba_login, aba_cadastro = st.tabs(["🔑 Login", "📝 Cadastro"])

    # --- ABA DE LOGIN ---
    with aba_login:
        st.subheader("Acesse sua conta")
        with st.form("form_login"):
            email_login = st.text_input("E-mail")
            senha_login = st.text_input("Senha", type="password")
            btn_login = st.form_submit_button("Entrar")

            if btn_login:
                if not email_login or not senha_login:
                    st.warning("Por favor, preencha todos os campos.")
                else:
                    senha_criptografada = hash_senha(senha_login)
                    # Busca o usuário no banco de dados
                    usuario = session.query(Usuario).filter_by(email=email_login, senha=senha_criptografada).first()

                    if usuario:
                        # Salva os dados na sessão do Streamlit
                        st.session_state['logado'] = True
                        st.session_state['usuario_nome'] = usuario.nome
                        st.session_state['usuario_email'] = usuario.email
                        st.session_state['usuario_perfil'] = usuario.tipo_perfil
                        st.success("Login realizado com sucesso!")
                        st.rerun() # Recarrega a página para atualizar a interface
                    else:
                        st.error("E-mail ou senha incorretos.")

    # --- ABA DE CADASTRO ---
    with aba_cadastro:
        st.subheader("Crie sua conta gratuitamente")
        with st.form("form_cadastro"):
            nome_cad = st.text_input("Nome Completo")
            email_cad = st.text_input("E-mail")
            senha_cad = st.text_input("Senha", type="password")
            senha_confirma = st.text_input("Confirme sua Senha", type="password")
            perfil_cad = st.selectbox("Qual o seu perfil?", ["Estudante", "Professor"])
            
            btn_cadastrar = st.form_submit_button("Cadastrar")

            if btn_cadastrar:
                if not nome_cad or not email_cad or not senha_cad:
                    st.warning("Preencha todos os campos obrigatórios.")
                elif senha_cad != senha_confirma:
                    st.error("As senhas não coincidem.")
                else:
                    # Verifica se o e-mail já existe no banco
                    usuario_existente = session.query(Usuario).filter_by(email=email_cad).first()
                    if usuario_existente:
                        st.error("Este e-mail já está cadastrado.")
                    else:
                        # Define o Enum correto baseado na escolha
                        tipo_enum = TipoPerfil.ESTUDANTE if perfil_cad == "Estudante" else TipoPerfil.PROFESSOR
                        
                        # Cria o novo usuário
                        novo_usuario = Usuario(
                            nome=nome_cad,
                            email=email_cad,
                            senha=hash_senha(senha_cad),
                            tipo_perfil=tipo_enum
                        )
                        
                        try:
                            session.add(novo_usuario)
                            session.commit()
                            st.success("Cadastro realizado com sucesso! Você já pode fazer login na aba ao lado.")
                        except Exception as e:
                            session.rollback()
                            st.error(f"Ocorreu um erro ao cadastrar: {e}")

# Fecha a sessão no final do script para não sobrecarregar o banco
session.close()