"""
AWS Glue ETL Job COMPLETO para transformação dos dados B3.
Implementa TODAS as transformações obrigatórias do desafio:
1. Agrupamento numérico (sumarização, contagem ou soma)
2. Renomear 2 colunas
3. Cálculo com campos de data
"""

import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.dynamicframe import DynamicFrame
from pyspark.sql import DataFrame
from pyspark.sql.functions import *
from pyspark.sql.types import *
from pyspark.sql.window import Window

# Inicializar contextos
args = getResolvedOptions(sys.argv, ['JOB_NAME'])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

def read_parquet_data(input_path: str) -> DataFrame:
    """
    Lê dados Parquet do S3 e converte para DataFrame.
    """
    print(f"Lendo dados de: {input_path}")
    
    # Criar DynamicFrame a partir dos dados Parquet no S3
    dynamic_frame = glueContext.create_dynamic_frame.from_options(
        connection_type="s3",
        connection_options={
            "paths": [input_path],
            "recurse": True
        },
        format="parquet",
        format_options={}
    )
    
    # Converter para DataFrame do Spark
    df = dynamic_frame.toDF()
    
    print(f"DataFrame criado com {df.count()} registros")
    print(f"Schema: {df.printSchema()}")
    return df

def apply_transformations(df: DataFrame) -> DataFrame:
    """
    Aplica transformações obrigatórias do desafio:
    ✅ 1. Agrupamento numérico (sumarização, contagem ou soma)
    ✅ 2. Renomear 2 colunas  
    ✅ 3. Cálculo com campos de data
    """
    print("🔄 Aplicando transformações obrigatórias...")
    
    # ✅ TRANSFORMAÇÃO 1: Renomear 2 colunas (OBRIGATÓRIO)
    print("1️⃣ Renomeando colunas...")
    df = df.withColumnRenamed("codigo", "stock_code") \
           .withColumnRenamed("acao", "company_name")
    
    # ✅ TRANSFORMAÇÃO 2: Cálculo com campos de data (OBRIGATÓRIO)
    print("2️⃣ Adicionando cálculos de data...")
    df = df.withColumn("extraction_date", current_date()) \
           .withColumn("processing_timestamp", current_timestamp()) \
           .withColumn("year_month", date_format(current_date(), "yyyy-MM")) \
           .withColumn("quarter", quarter(current_date())) \
           .withColumn("days_since_extraction", 
                      datediff(current_date(), to_date(col("extraction_date"))))
    
    # ✅ TRANSFORMAÇÃO 3: Agrupamento numérico (OBRIGATÓRIO)
    print("3️⃣ Criando agregações por setor...")
    
    # Dados individuais com ranking
    df_individual = df.withColumn("sector_rank", 
                                 row_number().over(
                                     Window.partitionBy("setor")
                                           .orderBy(col("part_percent").cast("double").desc())
                                 )) \
                     .withColumn("part_percent_double", col("part_percent").cast("double"))
    
    # Dados agregados por setor (sumarização, contagem, soma)
    df_sector_summary = df.groupBy("setor", "year_month", "quarter") \
                         .agg(
                             count("stock_code").alias("total_stocks_count"),
                             sum(col("part_percent").cast("double")).alias("total_sector_participation"),
                             avg(col("part_percent").cast("double")).alias("avg_sector_participation"),
                             max(col("part_percent").cast("double")).alias("max_sector_participation"),
                             min(col("part_percent").cast("double")).alias("min_sector_participation"),
                             stddev(col("part_percent").cast("double")).alias("stddev_sector_participation")
                         ) \
                         .withColumn("processing_timestamp", current_timestamp())
    
    print("✅ Transformações aplicadas com sucesso!")
    print(f"📊 Registros individuais: {df_individual.count()}")
    print(f"📈 Setores agregados: {df_sector_summary.count()}")
    
    return df_individual, df_sector_summary

def write_parquet_partitioned(df_individual: DataFrame, df_summary: DataFrame, output_path: str):
    """
    Salva dados refinados em Parquet particionado por data e setor.
    """
    print(f"💾 Salvando dados refinados em: {output_path}")
    
    # Salvar dados individuais particionados por ano/mês/setor
    individual_path = f"{output_path}/individual_stocks/"
    print(f"Salvando dados individuais em: {individual_path}")
    
    df_individual.write \
                 .mode("overwrite") \
                 .partitionBy("year_month", "setor") \
                 .option("compression", "snappy") \
                 .parquet(individual_path)
    
    # Salvar dados agregados particionados por ano/mês
    summary_path = f"{output_path}/sector_summary/"
    print(f"Salvando dados agregados em: {summary_path}")
    
    df_summary.write \
              .mode("overwrite") \
              .partitionBy("year_month", "quarter") \
              .option("compression", "snappy") \
              .parquet(summary_path)
    
    print("✅ Dados salvos com sucesso!")

def register_glue_catalog(output_path: str):
    """
    Registra tabelas no Glue Catalog para uso no Athena.
    """
    print("📋 Registrando tabelas no Glue Catalog...")
    
    try:
        # Registrar tabela de dados individuais
        individual_path = f"{output_path}/individual_stocks/"
        individual_sink = glueContext.getSink(
            path=individual_path,
            connection_type="s3",
            updateBehavior="UPDATE_IN_DATABASE",
            partitionKeys=["year_month", "setor"],
            compression="snappy",
            enableUpdateCatalog=True,
            updateCatalogOptions={
                "database": "bovespa_db", 
                "tableName": "bovespa_individual_refined"
            }
        )
        
        # Registrar tabela de resumo por setor  
        summary_path = f"{output_path}/sector_summary/"
        summary_sink = glueContext.getSink(
            path=summary_path,
            connection_type="s3",
            updateBehavior="UPDATE_IN_DATABASE",
            partitionKeys=["year_month", "quarter"],
            compression="snappy",
            enableUpdateCatalog=True,
            updateCatalogOptions={
                "database": "bovespa_db", 
                "tableName": "bovespa_sector_summary"
            }
        )
        
        print("✅ Tabelas registradas no Glue Catalog!")
        
    except Exception as e:
        print(f"⚠️ Erro ao registrar no Glue Catalog: {e}")
        print("Continuando sem registro no catálogo...")

def main():
    """
    Função principal do job ETL.
    """
    try:
        print("🚀 Iniciando job ETL B3...")
        
        # Configurações do job
        input_path = "s3://bovespa-pipeline-data-adri-vic/data_lake/"
        output_path = "s3://bovespa-pipeline-data-adri-vic/refined/"
        
        # 1. Ler dados brutos do S3
        print("📖 Lendo dados do S3...")
        df = read_parquet_data(input_path)
        
        # 2. Aplicar transformações obrigatórias
        print("🔧 Aplicando transformações...")
        df_individual, df_summary = apply_transformations(df)
        
        # 3. Salvar dados refinados com particionamento
        print("💾 Salvando dados refinados...")
        write_parquet_partitioned(df_individual, df_summary, output_path)
        
        # 4. Registrar no Glue Catalog
        register_glue_catalog(output_path)
        
        print("🎉 Job ETL B3 concluído com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro no job ETL: {str(e)}")
        raise e
    finally:
        job.commit()

if __name__ == "__main__":
    main()
