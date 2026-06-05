import streamlit as st
from sqlalchemy.orm import sessionmaker
from database.conexao import engine
from database.models import Curso, Matricula, StatusCurso, Usuario
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Dashboard do Aluno", page_icon="📚", layout="wide")

# --- PROTEÇÃO DE ROTA ---
# Verifica se o usuário está logado antes de mostrar o conteúdo
if not st.session_state.get('logado'):
    st.warning("🔒 Você precisa fazer login para acessar esta página.")
    st.info("Use o menu lateral para voltar à página inicial e fazer seu login.")
    st.stop() # Para a execução do script aqui

# Verifica se é realmente um estudante
if st.session_state.get('usuario_perfil').value != "ESTUDANTE":
    st.warning("⚠️ Esta área é exclusiva para o perfil Estudante.")
    st.stop()

# --- CONEXÃO COM O BANCO ---
Session = sessionmaker(bind=engine)
session = Session()

# Pega o email do usuário logado na sessão para buscar o ID dele no banco
email_usuario = session.query(Usuario).filter_by(email=st.session_state['usuario_email']).first() # Precisamos garantir que salvamos o email no app.py!
# Como não salvamos o email na etapa anterior, vamos usar o nome por enquanto (para o MVP) ou buscar o usuário atual.
# Correção ágil para o nosso MVP:
usuario_atual = session.query(Usuario).filter_by(nome=st.session_state['usuario_nome']).first()

# --- INTERFACE DO DASHBOARD ---
st.title(f"📚 Bem-vindo(a), {usuario_atual.nome}!")
st.write("Explore novos cursos ou continue de onde parou.")
st.divider()

# --- ABAS DE NAVEGAÇÃO INTERNA ---
aba_meus_cursos, aba_catalogo = st.tabs(["Em Andamento", "Catálogo de Cursos"])

with aba_meus_cursos:
    st.subheader("Meus Cursos Matriculados")
    
    # Busca as matrículas do usuário atual
    matriculas = session.query(Matricula).filter_by(estudante_id=usuario_atual.id).all()
    
    if not matriculas:
        st.info("Você ainda não está matriculado em nenhum curso. Vá para a aba 'Catálogo de Cursos' para começar!")
    else:
        for matricula in matriculas:
            curso = matricula.curso
            st.markdown(f"**{curso.titulo}**")
            st.progress(int(matricula.percentual_progresso))
            st.caption(f"Progresso: {matricula.percentual_progresso}% | Status: {'Concluído' if matricula.status_concluido else 'Em andamento'}")
            if st.button("Acessar Aulas", key=f"btn_aula_{matricula.id}"):
                # Salva o ID da matrícula na sessão para a Sala de Aula saber o que carregar
                st.session_state['matricula_ativa_id'] = matricula.id
                st.switch_page("pages/4_sala_de_aula.py") # Redireciona o usuário
            st.write("---")

with aba_catalogo:
    st.subheader("Cursos Disponíveis")
    
    # Busca apenas cursos que já foram publicados (ATIVO)
    cursos_disponiveis = session.query(Curso).filter_by(status=StatusCurso.ATIVO).all()
    
    if not cursos_disponiveis:
        st.info("Nenhum curso foi publicado pelos professores ainda.")
    else:
        for curso in cursos_disponiveis:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"### {curso.titulo}")
                st.write(curso.descricao)
                st.caption(f"Criado por: {curso.professor.nome} | Gratuito: {'Sim' if curso.is_gratuito else 'Não'}")
            
            with col2:
                # Verifica se o aluno já tem matrícula neste curso
                ja_matriculado = session.query(Matricula).filter_by(estudante_id=usuario_atual.id, curso_id=curso.id).first()
                
                if ja_matriculado:
                    st.button("Já Matriculado", disabled=True, key=f"btn_mat_{curso.id}")
                else:
                    if st.button("Matricular-se", key=f"btn_nova_mat_{curso.id}"):
                        nova_matricula = Matricula(
                            estudante_id=usuario_atual.id,
                            curso_id=curso.id,
                            data_inicio=datetime.utcnow()
                        )
                        session.add(nova_matricula)
                        session.commit()
                        st.success("Matrícula realizada com sucesso! Atualize a página.")
                        st.rerun()
            st.write("---")

session.close()