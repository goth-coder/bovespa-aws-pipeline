# 🚀 Guia de Instalação - Pipeline Bovespa

## 📋 Checklist de Pré-requisitos

Antes de começar, certifique-se de ter:

- [ ] **Python 3.9+** instalado
- [ ] **Git** instalado
- [ ] **Conta AWS** ativa com as seguintes permissões:
  - [ ] S3: `s3:GetObject`, `s3:PutObject`, `s3:ListBucket`
  - [ ] Lambda: `lambda:CreateFunction`, `lambda:InvokeFunction`
  - [ ] Glue: `glue:CreateJob`, `glue:StartJobRun`
  - [ ] Athena: `athena:StartQueryExecution`, `athena:GetQueryResults`
- [ ] **Credenciais AWS** (Access Key ID + Secret Access Key)

---

## 🛠 Instalação Passo a Passo

### **Etapa 1: Clone e Setup**

```bash
# 1. Clone o repositório
git clone https://github.com/goth-coder/bovespa-aws-pipeline.git
cd bovespa-aws-pipeline

# 2. Crie ambiente virtual
python3 -m venv .venv

# 3. Ative o ambiente virtual
# No macOS/Linux:
source .venv/bin/activate
# No Windows:
# .venv\Scripts\activate

# 4. Atualize pip
pip install --upgrade pip

# 5. Instale dependências
pip install -r requirements.txt
```

### **Etapa 2: Configuração AWS**

```bash
# 1. Copie o template de configuração
cp .env.template .env

# 2. Edite o arquivo .env com suas credenciais
nano .env  # ou use seu editor preferido
```

**Configure o arquivo `.env`:**
```bash
# AWS Credentials
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=xyz...
AWS_SESSION_TOKEN=  # deixe vazio se não usar MFA
AWS_DEFAULT_REGION=us-east-1

# S3 Configuration
BOVESPA_S3_BUCKET=bovespa-pipeline-data-adri-victor
```

### **Etapa 3: Verificação da Instalação**

```bash
# 1. Teste a instalação Python
python --version
# Saída esperada: Python 3.9.x ou superior

# 2. Teste as dependências
python -c "import pandas, pyarrow, boto3, requests; print('✅ Todas as dependências OK')"

# 3. Teste as credenciais AWS (opcional, requer AWS CLI)
aws sts get-caller-identity
```

### **Etapa 4: Primeiro Teste**

```bash
# Execute o pipeline de teste
python test_pipeline_reset.py
```

**Saída esperada:**
```
✅ Iniciando teste do pipeline resetado...
✅ Coletando dados dos 4 endpoints da B3...
✅ 339 ações coletadas com sucesso!
✅ Processando arquivos JSON para Parquet...
✅ 5 arquivos Parquet criados com 428 registros
✅ Pipeline local executado com sucesso!
```

---

## 🧪 Validação da Instalação

### **Teste 1: Scraping**
```bash
python -c "from src.scraping.scraping import run_scraping; run_scraping()"
```

### **Teste 2: Processamento Parquet**
```bash
python -c "from src.scraping.parquet_processor import ParquetProcessor; ParquetProcessor().process_all_json_files()"
```

### **Teste 3: Suite de Testes**
```bash
pytest tests/ -v
```

**Resultado esperado:** 34/35 testes passando (97% de sucesso)

---

## ❌ Resolução de Problemas

### **Problema: ImportError ou ModuleNotFoundError**

```bash
# Solução 1: Verificar ambiente virtual
which python
# Deve apontar para .venv/bin/python

# Solução 2: Reinstalar dependências
pip install --force-reinstall -r requirements.txt

# Solução 3: Adicionar ao PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### **Problema: Erro de Credenciais AWS**

```bash
# Verificar arquivo .env
cat .env | grep AWS_ACCESS_KEY_ID

# Testar credenciais manualmente
python -c "import boto3; print(boto3.client('sts').get_caller_identity())"
```

### **Problema: Falha na API B3**

```bash
# Testar conectividade
curl -I "https://sistemaswebb3-listados.b3.com.br"

# Verificar proxy/firewall
ping sistemaswebb3-listados.b3.com.br
```

### **Problema: Erro de Permissão S3**

```bash
# Verificar se bucket existe
aws s3 ls s3://bovespa-pipeline-data-adri-victor

# Testar upload manual
echo "teste" | aws s3 cp - s3://bovespa-pipeline-data-adri-victor/teste.txt
```

---

## 🔧 Configurações Opcionais

### **AWS CLI (Recomendado)**

```bash
# Instalar AWS CLI
pip install awscli

# Configurar
aws configure
# AWS Access Key ID: [sua access key]
# AWS Secret Access Key: [sua secret key]
# Default region name: us-east-1
# Default output format: json
```

### **VS Code Extensions (Opcional)**

```bash
# Para desenvolvimento com VS Code
code --install-extension ms-python.python
code --install-extension ms-vscode.vscode-json
code --install-extension amazonwebservices.aws-toolkit-vscode
```

---

## 📊 Próximos Passos

Após a instalação bem-sucedida:

1. **✅ Instalação Concluída** - Execute `python test_pipeline_reset.py`
2. **📖 Leia a Documentação** - Consulte `README.md` para entender a arquitetura
3. **🧪 Execute Testes** - Rode `pytest -v` para validar componentes
4. **☁️ Deploy AWS** - Siga `infrastructure/README.md` para deploy
5. **📊 Configure Athena** - Use as consultas em `src/athena/queries/`

---

## 🆘 Suporte

Se encontrar problemas:

1. **Verifique os logs** em `docs/log_de_tarefas.md`
2. **Consulte troubleshooting** no `README.md`
3. **Execute debug:** `pytest -v -s tests/`

---

*Guia criado em: 05/08/2025*  
*Projeto: Tech Challenge - Pipeline Batch Bovespa*
