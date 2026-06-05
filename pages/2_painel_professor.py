import streamlit as st
from sqlalchemy.orm import sessionmaker
from database.conexao import engine
from database.models import Curso, Categoria, Aula, StatusCurso, Usuario, Matricula, Certificado

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Painel do Professor", page_icon="👨‍🏫", layout="wide")

# --- PROTEÇÃO DE ROTA ---
if not st.session_state.get('logado'):
    st.warning("🔒 Você precisa fazer login para acessar esta página.")
    st.stop()

if st.session_state.get('usuario_perfil').value != "PROFESSOR":
    st.error("⚠️ Acesso Negado: Esta área é exclusiva para contas com perfil de Professor.")
    st.stop()

# --- CONEXÃO COM O BANCO ---
Session = sessionmaker(bind=engine)
session = Session()

usuario_atual = session.query(Usuario).filter_by(email=st.session_state['usuario_email']).first()

# --- INJEÇÃO DE DADOS MVP ---
categorias_existentes = session.query(Categoria).all()
if not categorias_existentes:
    categorias_iniciais = ["Tecnologia", "Negócios", "Design", "Matemática"]
    for nome_cat in categorias_iniciais:
        session.add(Categoria(nome=nome_cat, descricao=f"Cursos de {nome_cat}"))
    session.commit()
    categorias_existentes = session.query(Categoria).all()

# --- INTERFACE PRINCIPAL ---
st.title(f"👨‍🏫 Painel de Ensino: {usuario_atual.nome}")
st.write("Crie novos cursos, edite conteúdos e gerencie suas publicações.")
st.divider()

# --- ABAS DE GERENCIAMENTO ---
aba_gerenciar, aba_criar = st.tabs(["Gerenciar Meus Cursos", "Criar Novo Curso"])

# --- ABA: CRIAR NOVO CURSO ---
with aba_criar:
    st.subheader("Publicar um Novo Rascunho")
    with st.form("form_novo_curso", clear_on_submit=True):
        titulo = st.text_input("Título do Curso *")
        descricao = st.text_area("Descrição do Curso *")
        pre_req = st.text_area("Pré-requisitos")
        
        opcoes_cat = {cat.nome: cat.id for cat in categorias_existentes}
        categoria_selecionada = st.selectbox("Categoria *", options=list(opcoes_cat.keys()))
        
        st.caption("Por padrão, todo novo curso é salvo como RASCUNHO e é gratuito.")
        btn_salvar_curso = st.form_submit_button("Salvar Rascunho")
        
        if btn_salvar_curso:
            if not titulo or not descricao:
                st.error("Por favor, preencha o Título e a Descrição.")
            else:
                novo_curso = Curso(
                    titulo=titulo,
                    descricao=descricao,
                    pre_requisitos=pre_req,
                    professor_id=usuario_atual.id,
                    categoria_id=opcoes_cat[categoria_selecionada],
                    status=StatusCurso.RASCUNHO
                )
                session.add(novo_curso)
                session.commit()
                st.success("Rascunho criado com sucesso! Acesse a aba 'Gerenciar Meus Cursos'.")
                st.rerun()

# --- ABA: GERENCIAR CURSOS EXISTENTES ---
with aba_gerenciar:
    st.subheader("Cursos de minha autoria")
    
    meus_cursos = session.query(Curso).filter_by(professor_id=usuario_atual.id).all()
    
    if not meus_cursos:
        st.info("Você ainda não possui nenhum curso cadastrado.")
    else:
        for curso in meus_cursos:
            with st.expander(f"📚 {curso.titulo} | Status: {curso.status.value}"):
                
                # --- EDIÇÃO E EXCLUSÃO DO CURSO ---
                st.markdown("#### Detalhes do Curso")
                
                # Usamos um form para a edição não recarregar a tela a cada letra digitada
                with st.form(f"form_edit_{curso.id}"):
                    novo_titulo = st.text_input("Título", value=curso.titulo)
                    nova_descricao = st.text_area("Descrição", value=curso.descricao)
                    
                    if st.form_submit_button("💾 Salvar Alterações"):
                        curso.titulo = novo_titulo
                        curso.descricao = nova_descricao
                        session.commit()
                        st.success("Curso atualizado!")
                        st.rerun()
                
                # Botão de exclusão do curso (Fora do form para evitar conflitos)
                # Botão de exclusão do curso com deleção em cascata
                if st.button("🗑️ Excluir Curso Inteiro", key=f"del_curso_{curso.id}", type="primary"):
                    # 1. Busca todas as matrículas deste curso e deleta os certificados delas
                    matriculas_vinculadas = session.query(Matricula).filter_by(curso_id=curso.id).all()
                    for mat in matriculas_vinculadas:
                        session.query(Certificado).filter_by(matricula_id=mat.id).delete()
                        session.delete(mat)
                    
                    # 2. Deleta as aulas do curso
                    session.query(Aula).filter_by(curso_id=curso.id).delete()
                    
                    # 3. Finalmente, deleta o próprio curso
                    session.delete(curso)
                    
                    session.commit()
                    st.success("Curso e todas as suas dependências foram excluídos com sucesso!")
                    st.rerun()
                
                st.markdown("---")
                
                # --- GERENCIAMENTO DE AULAS ---
                st.markdown("#### Grade de Aulas")
                
                aulas = session.query(Aula).filter_by(curso_id=curso.id).order_by(Aula.ordem).all()
                if not aulas:
                    st.warning("Este curso ainda não possui nenhuma aula.")
                else:
                    for aula in aulas:
                        col_info, col_acao = st.columns([5, 1])
                        with col_info:
                            st.write(f"**{aula.ordem}.** {aula.titulo} (Link: {aula.video_url})")
                        with col_acao:
                            # Botão para excluir aula individual
                            if st.button("Excluir Aula", key=f"del_aula_{aula.id}"):
                                session.delete(aula)
                                session.commit()
                                st.rerun()
                
                # Formulário para adicionar nova aula
                st.markdown("##### Adicionar Nova Aula")
                with st.form(f"form_aula_{curso.id}", clear_on_submit=True):
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        tit_aula = st.text_input("Título da Aula *")
                        url_aula = st.text_input("URL do Vídeo (Youtube) *")
                    with col2:
                        ord_aula = st.number_input("Ordem *", min_value=1, value=len(aulas)+1)
                    
                    btn_add_aula = st.form_submit_button("Adicionar Aula")
                    
                    if btn_add_aula:
                        if not tit_aula or not url_aula:
                            st.error("Preencha título e URL da aula.")
                        else:
                            nova_aula = Aula(titulo=tit_aula, video_url=url_aula, ordem=ord_aula, curso_id=curso.id)
                            session.add(nova_aula)
                            session.commit()
                            st.success("Aula adicionada!")
                            st.rerun()
                
                # --- VALIDAÇÃO DE PUBLICAÇÃO ---
                if curso.status == StatusCurso.RASCUNHO:
                    st.markdown("---")
                    if st.button(f"🚀 Publicar Curso '{curso.titulo}'", key=f"btn_pub_{curso.id}"):
                        if not aulas:
                            st.error("Não é possível publicar: O curso precisa ter pelo menos uma aula cadastrada!")
                        else:
                            curso.status = StatusCurso.ATIVO
                            session.commit()
                            st.success("Curso publicado com sucesso!")
                            st.rerun()

session.close()