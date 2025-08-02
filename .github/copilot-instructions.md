# 📌 Instructions for Copilot Agent (Claude Sonnet 4)

## 🏗 Contexto do Projeto
Estamos desenvolvendo um **Pipeline de Dados Batch** para ingestão, processamento e análise de dados do pregão da **B3**.  
O projeto faz parte do **Tech Challenge - Big Data Architecture** e será implementado utilizando serviços da **AWS** e **Python**.

---

## 🎯 Objetivo
Construir uma arquitetura que:
1. **Coleta dados** do site da B3 via scraping.
2. **Armazena** no **AWS S3** (Data Lake) em formato **Parquet** com partição diária.
3. **Orquestra** o processamento via **AWS Lambda**, que dispara **AWS Glue**.
4. **Processa e transforma** os dados no **AWS Glue** (modo visual) aplicando as transformações obrigatórias:
   - Agrupamento numérico (sumarização, contagem ou soma)
   - Renomear 2 colunas
   - Cálculo com campos de data
5. **Salva dados refinados** no S3 (`/refined/`) em Parquet, particionados por **data** e **nome/abreviação da ação**.
6. **Catalogação automática** no Glue Catalog.
7. **Consulta** dos dados no AWS Athena.

---

## 🛠 Tecnologias e Ferramentas
- **Python 3.10+**
- **AWS S3**
- **AWS Lambda**
- **AWS Glue**
- **AWS Athena**
- **Parquet**
- **Boto3** (SDK AWS para Python)
- **Pandas** (processamento local de dados)
- **Requests / BeautifulSoup** (scraping)

---

## 📋 Estrutura do Projeto
```bash
.
├── README.md
├── instructions.md           # Este arquivo
├── scraping/                 # Scripts de scraping da B3
├── lambda/                   # Código da função AWS Lambda
├── glue/                     # Scripts auxiliares e configs do Job Glue
├── docs/                     # Diagramas e documentação 
```

---

## 📋 Requisitos Funcionais
- [ ] Criar script de **scraping** para coletar dados do pregão da B3 (`https://sistemaswebb3-listados.b3.com.br/indexPage/day/IBOV?language=pt-br`)
- [ ] Converter dados para **Parquet**
- [ ] Adicionar **partição diária** ao salvar
- [ ] Criar bucket S3 com pastas `/raw/` e `/refined/`
- [ ] Configurar upload automático do scraping para `/raw/`
- [ ] Criar função Lambda para acionar Job Glue
- [ ] Configurar gatilho S3 → Lambda
- [ ] Criar Job Glue (modo visual) com as transformações obrigatórias
- [ ] Salvar dados refinados particionados por data e nome da ação
- [ ] Catalogar dados no Glue Catalog
- [ ] Validar consultas no AWS Athena
- [ ] (Opcional) Criar Notebook no Athena com visualização gráfica

---

## 📜 Guidelines para o Copilot Agent
1. **Sempre consultar o arquivo `README.md`** antes de gerar qualquer código ou documentação, pois ele contém o checklist atualizado e detalhes do projeto.
2. **Gerar código Python** sempre compatível com **3.10+**.
3. Ao criar código AWS, **usar Boto3** e boas práticas de segurança (variáveis de ambiente, IAM roles).
4. **Sempre** documentar funções com docstrings claras.
5. Quando gerar scripts AWS Lambda:
   - Otimizar para **tempo de execução baixo**.
   - Garantir que a função **apenas dispare** o Glue Job (não processa dados).
6. Para o scraping:
   - Usar **Requests** + **BeautifulSoup**.
   - Garantir tolerância a falhas (try/except, logs).
7. Para integração com S3:
   - Usar **upload_fileobj** ou **put_object** do Boto3.
   - Nomear arquivos com padrão: `YYYY-MM-DD.parquet` e path `/raw/dt=YYYY-MM-DD/`.
8. Para Glue:
   - Retornar exemplos de configuração no **modo visual**.
   - Garantir as três transformações obrigatórias.
9. Para Athena:
   - Fornecer queries de exemplo para validação.
10. Sempre manter consistência com a **arquitetura de pipeline definida**:
   ```plaintext
   Scraping → S3 (raw) → Lambda → Glue → S3 (refined) → Glue Catalog → Athena
   ```
11. Quando possível, fornecer **exemplos de teste unitário** para cada parte.

---

## 📊 Fluxo Esperado
```plaintext
1. Scraping coleta dados da B3
2. Salva no S3 `/raw/` (Parquet, partição diária)
3. Evento S3 aciona Lambda
4. Lambda dispara Glue Job
5. Glue processa dados e salva no `/refined/`
6. Glue Catalog atualiza tabela
7. Athena consulta dados refinados
```

---

## ✅ Objetivo Final
Ter um pipeline 100% funcional que:
- Coleta, processa e armazena dados da B3.
- É escalável e pronto para uso em produção.
- Está documentado com README e diagramas.
- Possui scripts reprodutíveis para cada etapa.
