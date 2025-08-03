# 🏗️ Arquitetura AWS - Pipeline Bovespa B3

## 📋 **Visão Geral da Arquitetura**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   B3 Website    │    │   EventBridge   │    │   Lambda        │
│   (4 Endpoints) │    │   (Trigger      │    │   (Scraper)     │
│                 │◄───┤   Diário)       │───►│                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                         │
                                                         ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Athena        │    │   Glue Catalog  │    │   S3 Bucket     │
│   (Queries)     │◄───┤   (Schema)      │◄───┤   (Raw/Curated) │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         ▲                        ▲                      │
         │                        │                      ▼
┌─────────────────┐              │           ┌─────────────────┐
│   QuickSight    │              │           │   Glue Job      │
│   (Dashboard)   │              └───────────┤   (ETL)         │
│   [OPCIONAL]    │                          │                 │
└─────────────────┘                          └─────────────────┘
```

## 🔧 **Componentes da Arquitetura**

### **1. Ingestão de Dados**
- **Fonte**: B3 Website (4 endpoints de carteira IBOV)
- **Trigger**: EventBridge (execução diária)
- **Scraper**: Lambda Function com Python

### **2. Armazenamento Raw**
- **S3 Bucket**: `bovespa-raw-data`
- **Estrutura**: `year=2025/month=08/day=03/`
- **Formato**: JSON (raw) → Parquet (curated)

### **3. ETL/Transformação**
- **Glue Job**: Transformações visuais
  - Agrupamento por setor
  - Renomeação de colunas
  - Cálculos com datas
- **Output**: Dados particionados em Parquet

### **4. Catálogo de Dados**
- **Glue Catalog**: Schema discovery automático
- **Tabelas**: `bovespa_raw`, `bovespa_curated`

### **5. Análise**
- **Athena**: Queries SQL
- **QuickSight**: Dashboard (opcional)

## 📊 **Fluxo de Dados**

1. **EventBridge** dispara Lambda diariamente
2. **Lambda** faz scraping dos 4 endpoints B3
3. **Dados JSON** são salvos no S3 (raw)
4. **Glue Job** processa e transforma dados
5. **Parquet curated** é salvo com partições
6. **Glue Catalog** atualiza schema automaticamente
7. **Athena** disponibiliza queries SQL
8. **QuickSight** cria visualizações (opcional)

## 🎯 **Responsabilidades por Fase**

| Componente | Responsável | Status |
|------------|-------------|--------|
| Lambda Scraper | Victor | 🔜 Fase 2 |
| S3 + Partições | Victor | 🔜 Fase 2 |
| Glue Job ETL | Victor | 🔜 Fase 4 |
| Athena Queries | Adri | 🔜 Fase 5 |
| Dashboard | Adri | 🔜 Fase 6 |
| Documentação | Adri | 🔜 Fase 7 |

---

**Status**: ✅ **Fase 1 - Arquitetura Definida**  
**Próximo**: Fase 2 - Implementação do Scraper B3  
**Data**: 03/08/2025  
**Responsável**: Victor + Adri
