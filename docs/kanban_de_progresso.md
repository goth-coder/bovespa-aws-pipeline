# 📌 Kanban de Progresso – Tech Challenge
Projeto em dupla:
- 🧑💻 Pessoa A – **Victor** (Back: scraping, AWS, Glue Job)
- 👩💻 Pessoa B – **Adri** (Transformações, análises, docs, visualizações)
---
## ✅ Status Geral por Responsável
### 🔹Victor (Pessoa A)
#### 🔜 A FAZER
- [ ] Scraper de dados da B3 (parquet + partição diária)
- [ ] Criação do bucket S3 com versionamento
- [ ] Lambda para acionar Glue Job
- [ ] Glue Job com transformações visuais (agrupamento, renomear colunas,
cálculo com datas)
- [ ] Glue Catalog + integração com Athena

#### 🟡 EM ANDAMENTO
- 🟡 Scraper de dados da B3 (parquet + partição diária)

#### ✅ CONCLUÍDO
- ✅ Estrutura inicial do repositório criada em colaboração com Adri
- ✅ Desenho da arquitetura AWS (com Adri)
- ✅ Estrutura modular de scraping implementada e testada

---

### 🔹 Adri (Pessoa B)
#### 🔜 A FAZER
- [ ] Definir stack de ferramentas locais e controle de ambiente
- [ ] Criar template do README.md com instruções e contexto
- [ ] Estrutura de diretórios para documentação (`/docs`, `/diagrams`)
- [ ] Validar tabelas no Athena
- [ ] Notebook de visualização no Athena (opcional)
- [ ] Gravar vídeo de até 1min15 com overview da arquitetura
- [ ] Documentar o projeto completo (em Markdown)
####🟡 EM ANDAMENTO
- 🟡 Planejamento da organização de tarefas no Kanban com Victor

#### ✅ CONCLUÍDO
- ✅ Estruturação de `log_de_tarefas.md` e
`kanban_de_progresso.md`
- ✅ Diretórios criados: `/docs`, `/logs`, `/scripts`, `/lambda`
- ✅ Diagrama de arquitetura AWS criado (`diagrama_arquitetura.drawio`) – por Adri
- ✅ Remoção de referências temporais dos documentos – por Adri

---

## 📆 Etapas por Fase (Visão Linear)
| Fase | Tarefa | Responsável | Status |
|------|--------|-------------|--------|
| Fase 1 | Arquitetura do pipeline | Victor + Adri | ✅ Concluído |
| Fase 2 | Scraper B3 (dados brutos) | Victor | � Em andamento |
| Fase 3 | Lambda trigger (job Glue) | Victor | 🔜 A fazer |
| Fase 4 | ETL no Glue Studio | Victor | 🔜 A fazer |
| Fase 5 | Validação Athena e partições | Adri | 🔜 A fazer |
| Fase 6 | Visualização gráfica (Athena notebook) | Adri | 🔜 A fazer |
| Fase 7 | README + vídeo final | Adri | 🔜 A fazer |

---

## 🛑 Regras de Colaboração
- Sempre atualize este arquivo ao **iniciar** e ao **concluir** uma tarefa.
- Se houver dependência entre atividades, sinalize como **⚠ Bloqueada por...**
- Não edite arquivos do outro sem PR e consentimento.
- Revisões são feitas em dupla antes da entrega final.

---

> Autores: Victor & Adri
> Pós FIAP – Machine Learning Engineering