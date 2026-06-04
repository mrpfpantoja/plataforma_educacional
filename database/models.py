import uuid
import enum
from datetime import datetime
from sqlalchemy import Column, String, Text, Boolean, Integer, Float, DateTime, ForeignKey, Enum
from sqlalchemy.orm import declarative_base, relationship

# Base para todas as nossas classes
Base = declarative_base()

# Enums para padronizar opções
class TipoPerfil(enum.Enum):
    ESTUDANTE = "ESTUDANTE"
    PROFESSOR = "PROFESSOR"

class StatusCurso(enum.Enum):
    RASCUNHO = "RASCUNHO"
    ATIVO = "ATIVO"

class Usuario(Base):
    __tablename__ = 'usuarios'
    
    # Usando String(36) para armazenar UUIDs de forma otimizada no MySQL
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    nome = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    senha = Column(String(255), nullable=False) # Lembre-se de salvar em hash!
    data_cadastro = Column(DateTime, default=datetime.utcnow)
    
    # Diferenciador de perfil (Estudante ou Professor)
    tipo_perfil = Column(Enum(TipoPerfil), nullable=False, default=TipoPerfil.ESTUDANTE)
    mini_bio = Column(Text, nullable=True) # Apenas para professores

    # Relacionamentos
    cursos_criados = relationship("Curso", back_populates="professor")
    matriculas = relationship("Matricula", back_populates="estudante")

class Categoria(Base):
    __tablename__ = 'categorias'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    nome = Column(String(50), unique=True, nullable=False)
    descricao = Column(Text, nullable=True)
    
    cursos = relationship("Curso", back_populates="categoria")

class Curso(Base):
    __tablename__ = 'cursos'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    titulo = Column(String(150), nullable=False)
    descricao = Column(Text, nullable=False)
    pre_requisitos = Column(Text, nullable=True)
    is_gratuito = Column(Boolean, default=True)
    status = Column(Enum(StatusCurso), default=StatusCurso.RASCUNHO)
    
    # Chaves Estrangeiras
    professor_id = Column(String(36), ForeignKey('usuarios.id'), nullable=False)
    categoria_id = Column(String(36), ForeignKey('categorias.id'), nullable=False)
    
    # Relacionamentos
    professor = relationship("Usuario", back_populates="cursos_criados")
    categoria = relationship("Categoria", back_populates="cursos")
    aulas = relationship("Aula", back_populates="curso", cascade="all, delete-orphan")
    matriculas = relationship("Matricula", back_populates="curso")

class Aula(Base):
    __tablename__ = 'aulas'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    titulo = Column(String(150), nullable=False)
    video_url = Column(String(255), nullable=False)
    texto_apoio = Column(Text, nullable=True)
    ordem = Column(Integer, nullable=False)
    
    # Chave Estrangeira (Cascade delete configurado no relacionamento em 'Curso')
    curso_id = Column(String(36), ForeignKey('cursos.id', ondelete="CASCADE"), nullable=False)
    
    curso = relationship("Curso", back_populates="aulas")

class Matricula(Base):
    __tablename__ = 'matriculas'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    data_inicio = Column(DateTime, default=datetime.utcnow)
    percentual_progresso = Column(Float, default=0.0)
    status_concluido = Column(Boolean, default=False)
    
    # Chaves Estrangeiras
    estudante_id = Column(String(36), ForeignKey('usuarios.id'), nullable=False)
    curso_id = Column(String(36), ForeignKey('cursos.id'), nullable=False)
    
    # Relacionamentos
    estudante = relationship("Usuario", back_populates="matriculas")
    curso = relationship("Curso", back_populates="matriculas")
    certificado = relationship("Certificado", back_populates="matricula", uselist=False)

class Certificado(Base):
    __tablename__ = 'certificados'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    data_emissao = Column(DateTime, default=datetime.utcnow)
    codigo_validacao = Column(String(64), unique=True, nullable=False)
    pdf_url = Column(String(255), nullable=False)
    
    # Chave Estrangeira
    matricula_id = Column(String(36), ForeignKey('matriculas.id'), nullable=False)
    
    matricula = relationship("Matricula", back_populates="certificado")