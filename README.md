# 🎓 Plataforma Educacional MVP

Uma plataforma web educacional gratuita projetada para conectar estudantes e professores. O sistema permite a criação de cursos, matrícula de alunos, acompanhamento de progresso aula a aula e a emissão automática de certificados autênticos em PDF.

## ✨ Principais Funcionalidades
* **Autenticação de Usuários:** Cadastro e login seguros com separação de perfis (Estudante e Professor) e senhas criptografadas.
* **Painel do Professor:** Área exclusiva para o instrutor criar cursos, definir pré-requisitos, estruturar aulas e gerenciar a publicação.
* **Dashboard do Estudante:** Vitrine do catálogo de cursos ativos e painel de acompanhamento das matrículas em andamento.
* **Sala de Aula Virtual:** Ambiente de consumo de conteúdo com validação de progresso dinâmico sempre que uma aula é concluída.
* **Certificação Antifraude:** Emissão automática de diplomas em PDF contendo um código de validação único (hash) assim que o aluno atinge 100% de progresso.

## 🛠️ Tecnologias e Dependências
* **Linguagem:** Python
* **Interface (Frontend):** Streamlit
* **Banco de Dados:** MySQL
* **ORM:** SQLAlchemy
* **Geração de PDF:** fpdf
* **Comunicação e Segurança:** pymysql, cryptography, hashlib

## 📂 Estrutura do Projeto
```text
plataforma_educacional/
│
├── app.py                  # Ponto de entrada (Login e Cadastro)
├── .gitignore              # Arquivos ignorados pelo Git
│
├── pages/                  # Páginas do Menu Lateral (Streamlit)
│   ├── 1_dashboard_aluno.py
│   ├── 2_painel_professor.py
│   ├── 4_sala_de_aula.py
│   └── 5_meus_certificados.py
│
└── database/               # Lógica de Dados
    ├── conexao.py          # Conexão e inicialização do MySQL
    └── models.py           # Modelagem de tabelas SQLAlchemy
