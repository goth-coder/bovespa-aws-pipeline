# 📌 Kanban de Progresso – Tech Challenge
Projeto em dupla:
- 🧑‍💻 Pessoa A – **Victor** (Back: scraping, AWS, Glue Job)
- 👩‍💻 Pessoa B – **Adri** (Transformações, análises, docs, visualizações)

---

## 📆 Etapas por Fase (Visão Linear)
| Fase | Tarefa | Responsável | Status |
|------|--------|-------------|--------|
| Fase 1 | Arquitetura do pipeline | Victor + Adri | ✅ Concluído |
| Fase 2 | Scraper B3 + Upload S3 | Victor | ✅ Concluído |
| Fase 3 | Lambda trigger (job Glue) | Victor | ✅ Concluído |
| Fase 4 | ETL no Glue Studio | Victor | 🔜 A fazer |
| Fase 5 | Validação Athena e partições | Adri | 🔜 A fazer |
| Fase 6 | Visualização gráfica (Athena notebook) | Adri | 🔜 A fazer |
| Fase 7 | README + vídeo final | Adri | 🔜 A fazer |

---

## ✅ Status Geral por Responsável
### 🔹Victor (Pessoa A)

#### 🟡 EM ANDAMENTO
- 🟡 Glue Job com transformações visuais (código base criado, pendente deploy)

#### ✅ CONCLUÍDO RECENTEMENTE
- ✅ [04/08] Lambda function para trigger do Glue Job (integração completa + 12 testes funcionais) - por Victor via Adri

#### ✅ CONCLUÍDO
- ✅ [03/08] Estrutura inicial do repositório criada em colaboração com Adri
- ✅ [03/08] Desenho da arquitetura AWS (com Adri)
- ✅ [03/08] Estrutura modular de scraping implementada e testada
- ✅ [03/08] Processador Parquet com estrutura particionada implementado
- ✅ [03/08] Criação do bucket S3 com versionamento
- ✅ [03/08] Testes do processador Parquet + estrutura S3-like
- ✅ [04/08] Upload automático para S3 (integração boto3) - por Victor
- ✅ [04/08] Testes completos do pipeline S3 na pasta tests/ - por Victor
- ✅ [04/08] Relatórios de testes scraper e fluxo completo S3 - por Victor
- ✅ [04/08] Implementação completa do scraper B3 (4 endpoints) - por Victor
- ✅ [04/08] Pipeline end-to-end scraping → parquet → S3 funcional - por Victor

---

### 🔹 Adri (Pessoa B)
#### 🟡 EM ANDAMENTO
- 🟡 Queries Athena para análise de dados (tabelas criadas, pendente validação de resultados)

#### 🔜 A FAZER
- [ ] Validar tabelas no Athena (conectar com dados do S3)
- [ ] Glue Catalog + integração com Athena (configurar schema discovery)
- [ ] Notebook de visualização no Athena (opcional)
- [ ] Gravar vídeo de até 1min15 com overview da arquitetura
- [ ] Documentar o projeto completo (atualizar README.md)

#### ✅ CONCLUÍDO
- ✅ Estruturação de `log_de_tarefas.md` e `kanban_de_progresso.md`
- ✅ Diretórios criados: `/docs`, `/tests`, `/infrastructure`
- ✅ Diagrama de arquitetura AWS criado (`diagrama_arquitetura.drawio`) – por Adri
- ✅ Remoção de referências temporais dos documentos – por Adri
- ✅ [04/08] Estrutura base de queries Athena criada (queries/, views/) - por Adri
- ✅ [04/08] Documentação de arquitetura AWS completa - por Adri
- ✅ [04/08] Implementação e testes da Lambda function (12 testes funcionais) - por Adri executando tarefa Victor
- ✅ [04/08] Teste local da Lambda: 339 ações coletadas + processamento Parquet + validação S3 - por Adri

---

## 📊 Componentes Implementados vs Pendentes

### ✅ **TOTALMENTE IMPLEMENTADO**
- **Scraping B3**: 4 endpoints funcionais (carteira dia, teórica, prévia) - 339 ações coletadas
- **Processamento Parquet**: Conversão JSON → Parquet com particionamento
- **Upload S3**: Bucket criado, estrutura particionada data_lake/ano=/mes=/dia=
- **Lambda Function**: Handler completo com integração scraping + parquet + S3 + trigger Glue
- **Testes**: Suite completa para scraping, S3 pipeline e Lambda (12 testes funcionais)
- **Documentação**: Logs, relatórios técnicos, arquitetura

### 🟡 **PARCIALMENTE IMPLEMENTADO**
- **Glue ETL**: Código base criado com transformações PySpark (etl_job.py, transformations.py)
- **Athena Queries**: Templates de queries criados, pendente validação com dados reais

### 🔜 **PENDENTE**
- **Deploy da infraestrutura AWS**: CloudFormation/Terraform
- **Glue Catalog**: Configuração de tabelas e schema discovery
- **Integração completa**: Deploy Lambda → Glue → Athena na AWS
- **Visualizações**: Dashboard ou notebook interativo

---

## 🎯 Progresso Atual - Resumo Executivo

### ✅ **FASES CONCLUÍDAS (3/7)**
- **Fase 1**: ✅ Arquitetura e planejamento
- **Fase 2**: ✅ Scraping B3 + Upload S3 (Victor)
- **Fase 3**: ✅ Lambda trigger (Victor via Adri)

### 🟡 **FASES EM ANDAMENTO (2/7)**
- **Fase 4**: 🟡 ETL Glue Studio (Victor) - código base existe
- **Fase 5**: 🟡 Athena + Glue Catalog (Adri) - queries criadas

### 🔜 **PRÓXIMAS FASES (2/7)**
- **Fase 6**: 🔜 Visualização (Adri)
- **Fase 7**: 🔜 README + vídeo (Adri)

---

## 🛑 Regras de Colaboração
- Sempre atualize este arquivo ao **iniciar** e ao **concluir** uma tarefa.
- Se houver dependência entre atividades, sinalize como **⚠ Bloqueada por...**
- Não edite arquivos do outro sem consenso.
- Revisões são feitas em dupla antes da entrega final.

---

> Última atualização: 2025-08-04  
> Autores: Victor & Adri  
> Pós FIAP – Machine Learning Engineering  
> **Status atual:** Fases 1-3 concluídas ✅ | Fases 4-5 em andamento 🟡 | **43% do projeto concluído**
