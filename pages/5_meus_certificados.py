import streamlit as st
import hashlib
from datetime import datetime
from sqlalchemy.orm import sessionmaker
from database.conexao import engine
from database.models import Matricula, Certificado
from fpdf import FPDF
import tempfile

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Meus Certificados", page_icon="🎓", layout="wide")

# --- PROTEÇÃO DE ROTA ---
if not st.session_state.get('logado') or st.session_state.get('usuario_perfil').value != "ESTUDANTE":
    st.warning("🔒 Acesso restrito a estudantes logados.")
    st.stop()

# --- CONEXÃO COM O BANCO ---
Session = sessionmaker(bind=engine)
session = Session()

st.title("🎓 Meus Certificados")
st.write("Aqui você encontra os diplomas de todos os cursos que já concluiu na plataforma.")
st.divider()

# Busca as matrículas do usuário atual que estão com status_concluido = True
# Usa o e-mail da sessão para garantir a segurança dos dados
usuario_nome = st.session_state['usuario_nome']
matriculas_concluidas = session.query(Matricula).join(Matricula.estudante).filter(
    Matricula.status_concluido == True,
    Matricula.estudante.has(email=st.session_state['usuario_email'])
).all()

if not matriculas_concluidas:
    st.info("Você ainda não concluiu nenhum curso. Continue assistindo às aulas para garantir seu primeiro certificado!")
else:
    for matricula in matriculas_concluidas:
        curso = matricula.curso
        
        with st.container():
            col_info, col_botao = st.columns([3, 1])
            
            with col_info:
                st.markdown(f"### {curso.titulo}")
                st.write(f"**Professor:** {curso.professor.nome}")
                st.caption("Status: Concluído (100%)")
            
            with col_botao:
                # Verifica se o certificado já existe no banco. Se não, cria a hash.
                certificado = session.query(Certificado).filter_by(matricula_id=matricula.id).first()
                
                if not certificado:
                    # Gera um código Hash único baseado no ID da matrícula e data
                    hash_base = f"{matricula.id}-{datetime.utcnow().isoformat()}"
                    codigo_unico = hashlib.sha256(hash_base.encode()).hexdigest()[:16].upper()
                    
                    certificado = Certificado(
                        matricula_id=matricula.id,
                        codigo_validacao=codigo_unico,
                        pdf_url="Gerado Dinamicamente no MVP" 
                    )
                    session.add(certificado)
                    session.commit()

                # Lógica para construir o PDF
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", 'B', 24)
                pdf.cell(200, 20, txt="CERTIFICADO DE CONCLUSAO", ln=True, align='C')
                
                pdf.set_font("Arial", '', 16)
                pdf.ln(20)
                texto_cert = f"Certificamos que {usuario_nome} concluiu com exito o curso:"
                pdf.multi_cell(0, 10, txt=texto_cert, align='C')
                
                pdf.set_font("Arial", 'B', 20)
                pdf.ln(10)
                pdf.multi_cell(0, 10, txt=curso.titulo.upper(), align='C')
                
                pdf.set_font("Arial", '', 12)
                pdf.ln(30)
                pdf.cell(200, 10, txt=f"Emitido em: {certificado.data_emissao.strftime('%d/%m/%Y')}", ln=True, align='C')
                pdf.cell(200, 10, txt=f"Codigo de Autenticidade: {certificado.codigo_validacao}", ln=True, align='C')

                # Salva o PDF em um arquivo temporário para o Streamlit poder oferecer o download
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                    pdf.output(tmp_file.name)
                    
                    with open(tmp_file.name, "rb") as file:
                        st.download_button(
                            label="📥 Baixar Certificado (PDF)",
                            data=file,
                            file_name=f"Certificado_{curso.titulo.replace(' ', '_')}.pdf",
                            mime="application/pdf",
                            key=f"dl_{matricula.id}",
                            type="primary"
                        )
        st.write("---")

session.close()