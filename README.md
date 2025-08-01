# 🚀 AnyMarket Description Scrapper

Um sistema completo para extração e aprimoramento automático de documentação de APIs do AnyMarket, com integração de IA para melhoramento das descrições dos campos.

## 📋 Índice

- [Visão Geral](#-visão-geral)
- [Funcionalidades](#-funcionalidades)
- [Arquitetura](#-arquitetura)
- [Pré-requisitos](#-pré-requisitos)
- [Configuração do Ambiente Virtual](#-configuração-do-ambiente-virtual)
- [Instalação Alternativa](#-instalação-alternativa-requirementstxt)
- [Configuração](#-configuração)
- [Como Usar](#-como-usar)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [Exemplos de Uso](#-exemplos-de-uso)
- [Troubleshooting](#-troubleshooting)
- [Contribuição](#-contribuição)

## 🎯 Visão Geral

O **AnyMarket Description Scrapper** é uma ferramenta automatizada que:

1. **Extrai** documentação de APIs do AnyMarket usando web scraping
2. **Normaliza** os dados extraídos para padrão snake_case
3. **Aprimora** as descrições usando IA (Google Gemini)

### 🔄 Fluxo Completo

```
📡 Web Scraping → 🔧 Normalização → 🤖 IA Enhancement
```

## ✨ Funcionalidades

### 🕷️ DataRequester

- **Web Scraping** automatizado com Selenium
- **Extração hierárquica** de campos com prefixos inteligentes
- **Detecção automática** de arrays e objetos aninhados
- **Filtragem de conteúdo** para evitar dados irrelevantes
- **Retry automático** em caso de falhas

### 🐍 DataWrangler

- **Normalização snake_case** de todos os campos
- **Processamento em lote** de múltiplos arquivos
- **Validação de dados** antes e após normalização
- **Estatísticas detalhadas** do processamento

### 🤖 GoogleAgent

- **IA Enhancement** usando Google Gemini 2.5 Flash-Lite
- **Timeout inteligente** (20s + retry automático)
- **Rate limiting** otimizado para conta paga
- **Fallback descriptions** em caso de falha
- **Estatísticas de requests** e performance

## 🏗️ Arquitetura

```
app/
├── packages/
│   ├── DataRequester.py    # Web scraping + extração
│   ├── DataWrangler.py     # Normalização snake_case
│   └── GoogleAgent.py      # IA enhancement
├── assets/                 # Dados extraídos
│   ├── *.json             # Dados originais
│   ├── out/*.json         # Dados normalizados
│   └── agent/*.json       # Dados com IA enhancement
├── configurations/
│   └── configurations.py  # Configurações globais
└── main.py                # Ponto de entrada
```

## 📋 Pré-requisitos

### 🐍 Python

- Python 3.8 ou superior
- pip (gerenciador de pacotes)

### 🌐 Chrome WebDriver

- Google Chrome instalado
- ChromeDriver compatível com sua versão do Chrome

### 🔑 API Keys

- Google Gemini API Key (para IA enhancement)

## � Configuração do Ambiente Virtual

### 📦 Método Recomendado: pyproject.toml

> **💡 Por que usar pyproject.toml?**
>
> - ✅ **Padrão moderno** do Python (PEP 518)
> - ✅ **Instalação em modo editável** (`-e .`)
> - ✅ **Gerenciamento automático** de dependências
> - ✅ **Metadados centralizados** do projeto
> - ✅ **Compatível com ferramentas** modernas (poetry, pip-tools)
> - ✅ **Separação clara** entre deps de produção e desenvolvimento

#### 1. Clone o repositório

```bash
git clone <repository-url>
cd "Extrator de documentação"
```

#### 2. Crie o ambiente virtual

```bash
# Windows (PowerShell)
python -m venv .venv
.venv\Scripts\Activate.ps1

# Windows (CMD)
python -m venv .venv
.venv\Scripts\activate.bat

# Linux/macOS
python -m venv .venv
source .venv/bin/activate
```

#### 3. Atualize o pip e instale o projeto

```bash
# Atualize o pip para a versão mais recente
python -m pip install --upgrade pip

# Instale o projeto em modo editável com pyproject.toml
pip install -e .

# Para instalar dependências de desenvolvimento também
pip install -e ".[dev]"
```

#### 4. Verificar instalação

```bash
# Verificar se o projeto foi instalado corretamente
pip list | findstr anymarket

# Testar importação dos módulos
python -c "from app.packages.DataRequester import DataRequester; print('✅ DataRequester OK')"
python -c "from app.packages.DataWrangler import DataWrangler; print('✅ DataWrangler OK')"
python -c "from app.packages.GoogleAgent import GoogleAgent; print('✅ GoogleAgent OK')"
```

### 🔄 Desativar o Ambiente Virtual

```bash
# Para desativar o ambiente virtual
deactivate
```

### 🖥️ Integração com IDEs

#### VS Code

```json
// .vscode/settings.json
{
  "python.defaultInterpreterPath": "./.venv/Scripts/python.exe",
  "python.terminal.activateEnvironment": true,
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": false,
  "python.linting.flake8Enabled": true
}
```

#### PyCharm

1. **File** → **Settings** → **Project** → **Python Interpreter**
2. **Add Interpreter** → **Existing Environment**
3. Selecione: `.venv\Scripts\python.exe`

#### Jupyter Notebook

```bash
# Instalar kernel do ambiente virtual no Jupyter
python -m ipykernel install --user --name=anymarket-env --display-name="AnyMarket Scrapper"

# Iniciar Jupyter
jupyter notebook
# Selecionar kernel: "AnyMarket Scrapper"
```

### 📋 Dependências Incluídas no pyproject.toml

#### Dependências Principais:

- `selenium>=4.34.0` - Automação web
- `beautifulsoup4>=4.13.0` - Parsing HTML
- `requests>=2.32.0` - Requisições HTTP
- `python-dotenv>=1.1.0` - Variáveis de ambiente
- `google-generativeai` - Google Gemini AI
- `colorama` - Cores no terminal
- `tqdm` - Barras de progresso

#### Dependências de Desenvolvimento (opcionais):

- `pytest` - Framework de testes
- `black` - Formatação de código
- `flake8` - Linting
- `mypy` - Type checking

### 🛠️ Comandos Úteis do Ambiente Virtual

#### Gerenciamento de Dependências

```bash
# Listar pacotes instalados
pip list

# Listar pacotes instalados em formato requirements
pip freeze

# Verificar dependências do projeto
pip show anymarket-description-scrapper

# Atualizar todas as dependências
pip list --outdated
pip install --upgrade <package-name>

# Reinstalar o projeto após mudanças
pip install -e . --force-reinstall
```

### 💡 Melhores Práticas

#### ✅ Recomendações

- **Sempre** ative o ambiente virtual antes de trabalhar
- **Use** `pip install -e .` para instalação em modo editável
- **Mantenha** o arquivo `pyproject.toml` atualizado
- **Teste** regularmente com `pip check`
- **Documente** mudanças de dependências

#### ❌ Evite

- Instalar pacotes globalmente quando trabalhando no projeto
- Misturar `pip` e `conda` no mesmo ambiente
- Commitar a pasta `.venv` no Git (já está no .gitignore)
- Usar `sudo` com pip (em Linux/macOS)

#### 🔐 Segurança

```bash
# Verificar vulnerabilidades em dependências
pip audit

# Gerar arquivo de dependências com hashes (mais seguro)
pip freeze --all > requirements-lock.txt
```

#### Limpeza e Manutenção

```bash
# Limpar cache do pip
pip cache purge

# Verificar dependências inconsistentes
pip check

# Remover ambiente virtual (se necessário recriar)
deactivate
rmdir /s .venv  # Windows
rm -rf .venv    # Linux/macOS
```

## �🚀 Instalação Alternativa (requirements.txt)

### 1. Clone o repositório

```bash
git clone <repository-url>
cd "Extrator de documentação"
```

### 2. Instale as dependências

```bash
pip install -r requirements.txt
```

### 3. Baixe o ChromeDriver

#### Opção A: Download Manual

1. Acesse [ChromeDriver Downloads](https://chromedriver.chromium.org/downloads)
2. Baixe a versão compatível com seu Chrome
3. **Coloque o arquivo `chromedriver.exe` na pasta raiz do projeto**

#### Opção B: Verificação Automática

```bash
# Verificar versão do Chrome
chrome --version

# Baixar ChromeDriver correspondente
# Exemplo: Chrome 118.x.x.x → ChromeDriver 118.x.x.x
```

### 4. Configure as variáveis de ambiente

```bash
# Crie um arquivo .env na raiz do projeto
echo "GOOGLE_API_KEY=sua_api_key_aqui" > .env
```

## ⚙️ Configuração

### 🔧 Configurações Básicas

Edite `app/configurations/configurations.py`:

```python
# Configurações do Chrome WebDriver
WEBDRIVER_CONFIG = {
    "headless": True,          # Executar sem interface gráfica
    "window_size": (1920, 1080),
    "page_load_timeout": 30,
    "implicit_wait": 10,
    "max_retries": 3,
    "delay_between_requests": 2.0
}

# Endpoints para extrair
ENDPOINTS = [
    {
        "table": "categories",
        "url": "https://anymarketdoc.stoplight.io/docs/v3-doc-pt-br/d9d52de92b659-categories-id"
    },
    # ... mais endpoints
]
```

### 🤖 Configurações da IA

```python
# GoogleAgent settings
GOOGLE_AI_CONFIG = {
    "fast_mode": True,         # Delays otimizados
    "timeout": 20,             # Timeout por request
    "max_retries": 2,          # Tentativas por campo
    "model": "gemini-2.5-flash-lite"
}
```

## 📖 Como Usar

### 🎮 Modo Interativo (Recomendado)

```bash
python main.py --interactive
```

### 🚀 Modo Completo (Pipeline Completo)

```bash
# Executar todo o pipeline
python main.py
```

### 🧪 Modos de Teste

#### Testar DataWrangler

```bash
python main.py --wrangler
```

#### Testar GoogleAgent

```bash
python main.py --agent
```

#### Testar Endpoint Específico

```bash
python main.py --test "categories,https://anymarketdoc.stoplight.io/docs/v3-doc-pt-br/d9d52de92b659-categories-id"
```

#### Executar com Chrome Visível

```bash
python main.py --no-headless
```

## 📁 Estrutura do Projeto

```
Extrator de documentação/
├── 📄 README.md                    # Esta documentação
├── 📄 pyproject.toml               # Configuração do projeto (TOML)
├── 📄 requirements.txt             # Dependências Python (alternativa)
├── 📄 .gitignore                   # Arquivos ignorados pelo Git
├── 📄 .env                         # Variáveis de ambiente (criar)
├── 🔧 chromedriver.exe             # ChromeDriver (baixar)
├── 📄 main.py                      # Ponto de entrada
├── 📁 .venv/                       # Ambiente virtual (criado automaticamente)
├── 📁 .vscode/                     # Configurações VS Code
│   └── 📄 settings.json            # Configurações do Python/IDE
├── 📁 app/
│   ├── 📄 __init__.py
│   ├── 📁 packages/
│   │   ├── 📄 __init__.py
│   │   ├── 🕷️ DataRequester.py     # Web scraping
│   │   ├── 🐍 DataWrangler.py      # Normalização
│   │   └── 🤖 GoogleAgent.py       # IA enhancement
│   ├── 📁 configurations/
│   │   ├── 📄 __init__.py
│   │   └── ⚙️ configurations.py    # Configurações
│   └── 📁 assets/                  # Dados extraídos
│       ├── 📄 *.json              # Dados originais
│       ├── 📁 out/
│       │   └── 📄 *_normalized.json # Dados normalizados
│       └── 📁 agent/
│           └── 📄 *_enhanced.json   # Dados com IA
└── 📁 scripts/                     # Scripts auxiliares
    └── 📄 utils.py                 # Utilitários gerais
```

## 💡 Exemplos de Uso

### 📊 Exemplo de Dados Extraídos

#### Dados Originais (DataRequester)

```json
{
  "table_name": "categories",
  "fields": [
    {
      "name": "id",
      "description": "ID da categoria",
      "field_type": "integer",
      "original_name": "id"
    }
  ]
}
```

#### Dados Normalizados (DataWrangler)

```json
{
  "table_name": "categories",
  "fields": [
    {
      "name": "category_id",
      "description": "ID da categoria",
      "field_type": "integer",
      "original_name": "id"
    }
  ]
}
```

#### Dados Enhanced (GoogleAgent)

```json
{
  "table_name": "categories",
  "fields": [
    {
      "name": "category_id",
      "description": "ID da categoria",
      "field_type": "integer",
      "original_name": "id",
      "enhanced_description": "This field represents the unique identifier for categories in the AnyMarket categories endpoint."
    }
  ],
  "enhancement_summary": {
    "total_fields_enhanced": 16,
    "failed_enhancements": 0,
    "model_used": "gemini-2.5-flash-lite"
  }
}
```

### 🎯 Exemplo de Pipeline Completo

```bash
# 1. Extrair dados (9 endpoints)
python main.py

# Output:
# ✅ categories: 16 campos extraídos
# ✅ devolutions: 52 campos extraídos
# ✅ Total: 200+ campos extraídos

# 2. Normalizar dados
python main.py --wrangler

# Output:
# ✅ 9/9 arquivos normalizados
# 🐍 200+ campos convertidos para snake_case

# 3. Aplicar IA enhancement
python main.py --agent

# Output:
# 🤖 200+ campos aprimorados com Gemini 2.5
# ⏱️ Tempo total: ~45s
# 📡 Requests: 200 (1 por campo)
```

## 🛠️ Troubleshooting

### ❌ Problemas Comuns

#### 🐍 Problemas com Ambiente Virtual

```bash
# Erro: pip não reconhecido após ativar ambiente virtual
# Solução Windows: Use python -m pip ao invés de apenas pip
python -m pip install --upgrade pip

# Erro: Scripts\Activate.ps1 não pode ser executado (Windows)
# Solução: Alterar política de execução do PowerShell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Erro: Módulos não encontrados após instalação
# Solução: Verificar se está no ambiente virtual correto
which python  # Linux/macOS
where python   # Windows

# Verificar se o ambiente virtual está ativo (deve mostrar (.venv))
# Se não estiver ativo, execute novamente:
.venv\Scripts\Activate.ps1  # Windows PowerShell
```

#### 🌐 ChromeDriver

```bash
# Erro: 'chromedriver' executable needs to be in PATH
# Solução: Certifique-se que chromedriver.exe está na pasta raiz
```

#### Timeout do GoogleAgent

```bash
# Erro: Request timeout after 20s
# Solução: Verifique sua conexão com a internet e API key
```

#### API Key inválida

```bash
# Erro: Invalid API key
# Solução: Verifique se a GOOGLE_API_KEY está correta no arquivo .env
```

### 🔧 Logs e Debug

#### Ativar logs detalhados

```python
# Em DataRequester.py
logging.basicConfig(level=logging.DEBUG)
```

#### Executar sem headless (ver navegador)

```bash
python main.py --no-headless
```

#### Verificar arquivos gerados

```bash
# Dados originais
ls app/assets/*.json

# Dados normalizados
ls app/assets/out/*.json

# Dados com IA
ls app/assets/agent/*.json
```

### 📊 Monitoramento de Performance

#### DataRequester

- ⏱️ Tempo médio: ~30s para 9 endpoints
- 📊 Taxa de sucesso: ~95%
- 🔄 Retry automático: 3 tentativas

#### GoogleAgent

- ⏱️ Tempo médio: ~200ms por campo
- 📡 Rate limiting: 60 RPM
- ⚡ Timeout: 20s + retry

## 🤝 Contribuição

### 📝 Como Contribuir

1. **Fork** o repositório
2. **Clone** sua fork
3. **Crie** uma branch para sua feature
4. **Implemente** suas melhorias
5. **Teste** thoroughly
6. **Abra** um Pull Request

### 🎯 Áreas para Contribuição

- 🔧 **Novos endpoints** do AnyMarket
- 🤖 **Melhorias na IA** (prompts, modelos)
- 📊 **Integração com outros sistemas** de dados
- 🧪 **Testes automatizados**
- 📚 **Documentação** adicional
- 🔄 **Novos formatos de output** (CSV, Excel, etc.)

### 📋 Padrões de Código

- **Python**: PEP 8
- **Commits**: Conventional Commits
- **Documentação**: Docstrings + Markdown
- **Logs**: Structured logging com emojis

---

## 📞 Suporte

Para dúvidas, problemas ou sugestões:

1. **Issues**: Abra uma issue no repositório
2. **Documentation**: Consulte este README
3. **Logs**: Verifique os logs detalhados do sistema

---

**🎉 Desenvolvido com ❤️ para automatizar a extração e aprimoramento de documentação de APIs do AnyMarket**
