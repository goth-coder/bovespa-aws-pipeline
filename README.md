# 🚀 Pipeline Batch Bovespa - AWS

## 📜 Sobre o Projeto
Este projeto tem como objetivo construir um **pipeline de dados batch** para ingestão, processamento e análise dos dados do pregão da **B3**, utilizando serviços da **AWS** (S3, Glue, Lambda, Athena).  
O pipeline será responsável por realizar o **scraping** dos dados da B3, armazenar em um **Data Lake** no formato **Parquet**, processar via **AWS Glue** e disponibilizar para consulta no **AWS Athena**.

**Status:** 🚧 Em desenvolvimento

---


---

## 🛠 Tecnologias Utilizadas
- Python (para scraping e Lambda)
- AWS S3 (armazenamento Data Lake)
- AWS Lambda (orquestração do Glue)
- AWS Glue (ETL visual)
- AWS Athena (consulta SQL)
- Formato Parquet (dados otimizados)

---

## 📋 Checklist do Projeto

### **Coleta de Dados**
- [ ] Criar script de **scraping** para coletar dados do pregão da B3 (`https://sistemaswebb3-listados.b3.com.br/indexPage/day/IBOV?language=pt-br`)
- [ ] Converter dados para **Parquet**
- [ ] Adicionar **partição diária** ao salvar

### **Armazenamento no S3**
- [ ] Criar bucket S3
- [ ] Estruturar pastas `/raw/` e `/refined/`
- [ ] Configurar upload automático do scraping para `/raw/`

### **Orquestração com AWS Lambda**
- [ ] Criar função Lambda
- [ ] Configurar gatilho de evento **S3 → Lambda**
- [ ] Lambda iniciar execução do Job Glue

### **Processamento com AWS Glue**
- [ ] Criar Job ETL no modo visual
- [ ] Implementar transformações obrigatórias:
  - [ ] Agrupamento numérico (sumarização, contagem ou soma)
  - [ ] Renomear 2 colunas
  - [ ] Cálculo com campos de data
- [ ] Salvar dados refinados no S3 `/refined/`
- [ ] Particionar por **data** e **nome/abreviação da ação**
- [ ] Catalogar dados no Glue Catalog

### **Consulta e Validação**
- [ ] Consultar dados no AWS Athena
- [ ] Validar partições e formato
- [ ] (Opcional) Criar Notebook no Athena com visualização gráfica

---

## 📂 Estrutura do Projeto
```bash
bovespa-aws-pipeline/
├── 📁 scraping/           # Scripts de coleta de dados da B3
│   ├── bovespa_scraper.py    # Scraper principal com conversão para Parquet
│   └── README.md             # Documentação do módulo
│
├── 📁 lambda/             # Função AWS Lambda para orquestração
│   ├── lambda_function.py    # Detecta S3 events e dispara Glue Job
│   ├── requirements.txt      # Dependências da Lambda
│   └── README.md             # Documentação da Lambda
│
├── 📁 glue/               # Configurações do AWS Glue ETL
│   ├── glue_job_helper.py    # Helpers e configurações do Job
│   └── README.md             # Documentação das transformações
│
├── 📁 config/             # Configurações centralizadas
│   ├── settings.py           # Configurações Python
│   └── .env.example          # Exemplo de variáveis de ambiente
│
├── 📁 scripts/            # Scripts de automação e deploy
│   ├── deploy_aws.py         # Deploy automático da infraestrutura
│   └── run_local_test.py     # Testes locais e scraping
│
├── 📁 tests/              # Testes unitários e de integração
│   ├── test_scraping.py      # Testes do módulo de scraping
│   └── README.md             # Documentação dos testes
│
├── 📁 docs/               # Documentação técnica
│   ├── architecture.md       # Arquitetura detalhada
│   └── deploy.md             # Guia completo de deploy
│
├── 📁 infrastructure/     # Infrastructure as Code (Terraform)
│   └── main.tf               # Definição completa da infraestrutura AWS
│
├── 📄 QUICKSTART.md       # Guia de início rápido
├── 📄 pyproject.toml      # Configuração do projeto Python
├── 📄 requirements.txt    # Dependências Python
└── 📄 .gitignore          # Arquivos ignorados pelo Git
```
## � Quick Start

```bash
# 1. Instalar dependências
pip install -r requirements.txt

# 2. Configurar AWS
aws configure

# 3. Configurar projeto
cp config/.env.example config/.env

# 4. Testar localmente
python scripts/run_local_test.py --action test

# 5. Deploy da infraestrutura
cd infrastructure/ && terraform apply
```

📖 **Guia completo**: [QUICKSTART.md](QUICKSTART.md)

---
Fluxo esperado:
1. Scraping coleta dados da B3
2. Salva no S3 /raw/ em Parquet (partição diária)
3. Evento S3 aciona AWS Lambda
4. Lambda dispara Job Glue
5. Glue processa dados e salva no S3 /refined/
6. Glue Catalog atualiza tabela
7. Consulta no Athena

## 📜 Licença
Este projeto é de uso acadêmico para o Tech Challenge de Big Data Architecture.