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
```
## 🚀 Como Rodar a Aplicação Localmente

### 1. Pré-requisitos
* Ter o **Python** instalado na máquina.
* Ter o **MySQL** (ou MariaDB) instalado e rodando.
* Criar um banco de dados vazio no seu MySQL chamado `plataforma_edu` (ex: rodando `CREATE DATABASE plataforma_edu;` no MySQL).

### 2. Configure a Conexão
Abra o arquivo `database/conexao.py` e altere a string de conexão na variável `DATABASE_URL` com a senha real do seu usuário do banco de dados (ex: `root`).

### 3. Configuração do Ambiente Virtual
Abra o terminal na pasta raiz do projeto (`plataforma_educacional`) e crie um ambiente virtual:

```bash
python -m venv .venv
```

### 4. Instale as Dependências
[cite_start]Com o ambiente ativado (`.venv`), instale as bibliotecas necessárias:

```bash
pip install streamlit sqlalchemy pymysql cryptography fpdf
```

### 5. Construa as Tabelas do Banco de Dados
Ainda no terminal, execute o script de conexão para criar as tabelas mapeadas:

```bash
python database/conexao.py
```

### 6. Inicie a Plataforma

Por fim, inicie o servidor do Streamlit:

```bash
python -m streamlit run app.py
```

O navegador abrirá automaticamente em http://localhost:8501. Pronto!

