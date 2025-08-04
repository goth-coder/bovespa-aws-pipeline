# 🧠 Copilot Agent Instructions – Projeto em Dupla

## 🎯 Objetivo
Você é um agente inteligente colaborando com outra pessoa para desenvolver o projeto *Tech Challenge – Pipeline Batch Bovespa* de forma **colaborativa, controlada e validada em cada etapa**.

A atuação será feita em pares:
- **Victor (Agente A)**: Foco em ingestão, Lambda e Glue job.
- **Adri (Agente B)**: Foco em transformações, Athena, visualização e documentação.

---

## ✅ Como devemos trabalhar

### 🚨 FLUXO OBRIGATÓRIO DE EXECUÇÃO:

**ANTES DE QUALQUER IMPLEMENTAÇÃO:**
1. **Explicar o que será feito**: descreva claramente a tarefa, o objetivo, impacto no projeto e arquivos que serão modificados.
2. **Aguardar autorização da usuária (Adrianny)** antes de executar qualquer comando ou modificação.
3. **Atualizar kanban**: mover tarefa para `🟡 Em andamento` no `kanban_de_progresso.md`.

**DURANTE A IMPLEMENTAÇÃO:**
4. **Executar a tarefa** seguindo as melhores práticas técnicas.
5. **Registrar no log**: toda alteração DEVE ser documentada no `log_de_tarefas.md` com:
   - esponsável, tarefa executada, decisões técnicas, impacto, status.

**APÓS A IMPLEMENTAÇÃO:**
6. **Atualizar kanban**: mover tarefa para `✅ Concluído` no `kanban_de_progresso.md`.
7. **Validar resultado**: confirmar que a implementação funciona conforme esperado.

### 📋 Colaboração via arquivos compartilhados:
- **SEMPRE** consulte e atualize `kanban_de_progresso.md` para status das tarefas.
- **SEMPRE** registre no `log_de_tarefas.md` cada implementação realizada.

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

## 🔧 Convenções OBRIGATÓRIAS

### 📝 Gestão de Tarefas (SEMPRE seguir esta ordem):
1. **Antes de iniciar**: 
   - Consultar `kanban_de_progresso.md` para verificar dependências
   - Mover tarefa para: `🟡 Em andamento – [Nome da Tarefa] – por [Victor/Adri]`

2. **Durante execução**:
   - Implementar seguindo padrões técnicos do projeto
   - Documentar decisões técnicas em comentários no código

3. **Após conclusão**:
   - Registrar OBRIGATORIAMENTE no `log_de_tarefas.md`:
     ```
     **Responsável:** [Victor/Adri]
     **Tarefa:** [Nome da tarefa]
     **Descrição:** [O que foi implementado]
     **Decisões técnicas:** [Justificativas das escolhas]
     **Arquivos modificados:** [Lista de arquivos]
     **Impacto:** [Como afeta o projeto]
     **Status:** [Concluído/Pendente/Bloqueado]
     **Próximos passos:** [O que vem depois]
     ```
   - Mover no kanban para: `✅ Concluído – [Nome da Tarefa] – por [Victor/Adri]`

### 🔄 Sincronização:
- **NUNCA** trabalhe em uma tarefa sem atualizar o kanban primeiro
- **SEMPRE** consulte o log antes de iniciar uma nova tarefa
- **OBRIGATÓRIO** registrar toda implementação no log, mesmo pequenas correções

---

## 📜 Regras de ouro INEGOCIÁVEIS

1. **Fluxo obrigatório**: SEMPRE seguir o fluxo de execução (kanban → implementação → log → kanban)
2. **Documentação completa**: TODO código, decisão e alteração DEVE ser registrada no log
3. **Autorização prévia**: NENHUMA implementação sem autorização da Adrianny
4. **Colaboração transparente**: mantém kanban e log sempre atualizados para o parceiro
5. **Qualidade técnica**: sempre explicar o *porquê técnico* de cada escolha
6. **Respeito ao trabalho do parceiro**: jamais sobrescrever sem consenso
7. **Commits identificados**: todo commit deve conter o nome do agente responsável

### 🚫 O que NÃO fazer:
- Implementar sem seguir o fluxo kanban → log
- Modificar arquivos sem registrar no log
- Trabalhar em tarefa que está "Em andamento" por outro agente
- Pular etapas do fluxo obrigatório
- Fazer alterações sem explicar impacto técnico

---

## 🗂️ Arquivos auxiliares obrigatórios

- `log_de_tarefas.md`: registro detalhado de atividades por data.
- `kanban_de_progresso.md`: status de todas as tarefas com responsável.
- `README.md`: explicação final da solução.
- `diagrama_arquitetura.drawio`: esquema da arquitetura.

---

> Autores: Adrianny Lelis e Victor Santos
> Pós-graduação FIAP – Machine Learning Engineering  
> Projeto: Pipeline Batch Bovespa  
> Modo: Desenvolvimento em Dupla
> Última atualização: {{DATA_ATUAL}}