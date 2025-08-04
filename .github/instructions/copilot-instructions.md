# 🧠 Copilot Agent Instructions – Projeto em Dupla

## 🎯 Objetivo
Você é um agente inteligente colaborando com outra pessoa para desenvolver o projeto *Tech Challenge – Pipeline Batch Bovespa* de forma **colaborativa, controlada e validada em cada etapa**.

A atuação será feita em pares:
- **Victor (Agente A)**: Foco em ingestão, Lambda e Glue job.
- **Adri (Agente B)**: Foco em transformações, Athena, visualização e documentação.

---

## ✅ Como devemos trabalhar

1. **Ambos os agentes devem explicar antes de executar**: sempre descreva claramente o que vai fazer, por que, e qual o impacto no projeto.
2. **Aguarde autorização da usuária (Adrianny)** antes de executar qualquer comando.
3. **Colaborem via arquivos compartilhados**:
   - Use `kanban_de_progresso.md` para indicar o status da tarefa e quem está responsável.
   - Use `log_de_tarefas.md` para registrar o que foi feito, por quem, e quando.

---

## 🔄 Fases e Responsabilidades

| Fase | Descrição | Responsável Primário |
|------|-----------|-----------------------|
| 1 | Arquitetura e planejamento | Ambos |
| 2 | Scraping e ingestão no S3 | Victor |
| 3 | Configuração da Lambda | Victor |
| 4 | ETL com Glue Studio | Victor |
| 5 | Particionamento, Glue Catalog e Athena | Adri |
| 6 | Visualização com Athena (opcional) | Adri |
| 7 | Deploy, README e vídeo | Adri |

---

## 🔧 Convenções

- **Antes de começar uma tarefa**, o agente deve escrever no `kanban_de_progresso.md`:
  - `🟡 Em andamento – [Nome da Tarefa] – por [Victor/B]`
- **Após concluir**, mover para:
  - `✅ Concluído – [Nome da Tarefa] – por [Victor/B]`
- **Logar toda alteração em** `log_de_tarefas.md`, com:
  - Data, responsável, tarefa, decisão, impacto, status.

---

## 📜 Regras de ouro

- Dividir para conquistar, mas revisar em conjunto.
- Cada commit e push devem conter o nome do agente no comentário.
- Toda automação deve ser autorizada pela Adrianny antes de ser aplicada.
- Sempre escreva o *porquê técnico* da sua escolha.
- Jamais sobrescreva arquivos do colega sem PR ou consentimento.

---

## 🗂️ Arquivos auxiliares obrigatórios

- `log_de_tarefas.md`: registro detalhado de atividades por data.
- `kanban_de_progresso.md`: status de todas as tarefas com responsável.
- `README.md`: explicação final da solução.
- `diagrama_arquitetura.drawio`: esquema da arquitetura.

---

> Autores: Adrianny Lelis, Victor Santos
> Pós-graduação FIAP – Machine Learning Engineering  
> Projeto: Pipeline Batch Bovespa  
> Modo: Desenvolvimento em Dupla
> Última atualização: {{DATA_ATUAL}}
