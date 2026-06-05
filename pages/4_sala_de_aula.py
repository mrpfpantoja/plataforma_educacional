import streamlit as st
from sqlalchemy.orm import sessionmaker
from database.conexao import engine
from database.models import Matricula, Aula

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Sala de Aula", page_icon="▶️", layout="wide")

# --- PROTEÇÃO E VERIFICAÇÃO DE ROTA ---
if not st.session_state.get('logado') or st.session_state.get('usuario_perfil').value != "ESTUDANTE":
    st.warning("🔒 Acesso restrito a estudantes logados.")
    st.stop()

# Verifica se o aluno clicou em um curso no Dashboard
if 'matricula_ativa_id' not in st.session_state:
    st.info("Nenhum curso selecionado. Volte ao Dashboard para escolher um curso.")
    if st.button("Voltar ao Dashboard"):
        st.switch_page("pages/1_dashboard_aluno.py")
    st.stop()

# --- CONEXÃO COM O BANCO ---
Session = sessionmaker(bind=engine)
session = Session()

# Busca os dados da matrícula e do curso
matricula_id = st.session_state['matricula_ativa_id']
matricula = session.query(Matricula).filter_by(id=matricula_id).first()
curso = matricula.curso
aulas = session.query(Aula).filter_by(curso_id=curso.id).order_by(Aula.ordem).all()

if not aulas:
    st.error("Este curso ainda não possui aulas cadastradas pelo professor.")
    st.stop()

# --- LÓGICA DE PROGRESSO MVP ---
total_aulas = len(aulas)
# Calcula quanto cada aula vale em porcentagem (Ex: 4 aulas = 25% cada)
peso_por_aula = 100.0 / total_aulas 

# Descobre qual aula o aluno deve assistir com base no progresso atual
# Se o progresso é 50% e a aula vale 25%, ele está na aula de índice 2
indice_aula_atual = int((matricula.percentual_progresso + 0.1) // peso_por_aula)

# Previne que o índice ultrapasse o total de aulas (caso já tenha concluído)
if indice_aula_atual >= total_aulas:
    indice_aula_atual = total_aulas - 1
    curso_finalizado = True
else:
    curso_finalizado = matricula.status_concluido

aula_atual = aulas[indice_aula_atual]

# --- INTERFACE DA SALA DE AULA ---
col_voltar, col_titulo = st.columns([1, 8])
with col_voltar:
    if st.button("⬅️ Voltar"):
        del st.session_state['matricula_ativa_id']
        st.switch_page("pages/1_dashboard_aluno.py")

st.title(f"📖 {curso.titulo}")
st.progress(int(matricula.percentual_progresso))
st.caption(f"Progresso: {int(matricula.percentual_progresso)}% concluído")
st.divider()

col_video, col_lista = st.columns([3, 1])

# --- PLAYER DE VÍDEO (Esquerda) ---
with col_video:
    st.subheader(f"Aula {aula_atual.ordem}: {aula_atual.titulo}")
    
    # O Streamlit tenta renderizar a URL se for do YouTube, caso contrário mostra um link
    try:
        st.video(aula_atual.video_url)
    except:
        st.info(f"🔗 [Clique aqui para acessar o material/vídeo da aula]({aula_atual.video_url})")
    
    st.write("---")
    
    if curso_finalizado:
        st.success("🎉 Você concluiu todas as aulas deste curso!")
    else:
        # Botão para avançar o progresso
        if st.button("✅ Marcar aula como Concluída e Avançar", type="primary"):
            novo_progresso = matricula.percentual_progresso + peso_por_aula
            
            # Se passou de 99%, arredonda para 100 e marca como concluído
            if novo_progresso >= 99.9:
                matricula.percentual_progresso = 100.0
                matricula.status_concluido = True
            else:
                matricula.percentual_progresso = novo_progresso
                
            session.commit()
            st.rerun()

# --- LISTA DE AULAS (Direita) ---
with col_lista:
    st.markdown("### Conteúdo do Curso")
    for i, aula in enumerate(aulas):
        if i < indice_aula_atual or curso_finalizado:
            st.write(f"✅ {aula.ordem}. {aula.titulo}")
        elif i == indice_aula_atual:
            st.write(f"▶️ **{aula.ordem}. {aula.titulo}**")
        else:
            st.write(f"🔒 {aula.ordem}. {aula.titulo}")

session.close()