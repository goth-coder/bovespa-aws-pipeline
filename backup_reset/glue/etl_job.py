"""
AWS Glue ETL Job principal para transformação dos dados B3.
Processa dados brutos JSON e converte para Parquet particionado.
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

def main():
    """
    Função principal do job ETL.
    """
    try:
        print("Iniciando job ETL B3...")
        
        # Configurações do job
        input_path = "s3://bovespa-pipeline-data-adri-vic/data_lake/"
        output_path = "s3://bovespa-pipeline-data-adri-vic/refined/"
        
        # 1. Ler dados brutos do S3
        print("Lendo dados do S3...")
        df = read_json_data(input_path)
        
        # 2. Aplicar transformações obrigatórias
        print("Aplicando transformações...")
        df_transformed = apply_transformations(df)
        
        # 3. Salvar dados refinados com particionamento
        print("Salvando dados refinados...")
        write_parquet_partitioned(df_transformed, output_path)
        
        print("Job ETL B3 concluído com sucesso")
        
    except Exception as e:
        print(f"Erro no job ETL: {str(e)}")
        raise e
    finally:
def read_json_data(input_path: str) -> DataFrame:
    """
    Lê dados JSON do S3 e converte para DataFrame.
    """
    print(f"Lendo dados de: {input_path}")
    
    # Criar DynamicFrame a partir dos dados JSON no S3
    dynamic_frame = glueContext.create_dynamic_frame.from_options(
        connection_type="s3",
        connection_options={
            "paths": [input_path],
            "recurse": True
        },
        format="parquet",  # Dados já estão em Parquet
        format_options={}
    )
    
    # Converter para DataFrame do Spark
    df = dynamic_frame.toDF()
    
    print(f"DataFrame criado com {df.count()} registros")
    return df

def apply_transformations(df: DataFrame) -> DataFrame:
    """
    Aplica transformações obrigatórias do desafio:
    1. Agrupamento numérico (sumarização, contagem ou soma)
    2. Renomear 2 colunas
    3. Cálculo com campos de data
    """
    print("Aplicando transformações obrigatórias...")
    
    # TRANSFORMAÇÃO 1: Renomear 2 colunas (obrigatório)
    df = df.withColumnRenamed("codigo", "stock_code") \
           .withColumnRenamed("acao", "company_name")
    
    # TRANSFORMAÇÃO 2: Cálculo com campos de data (obrigatório)
    df = df.withColumn("extraction_date", current_date()) \
           .withColumn("processing_timestamp", current_timestamp()) \
           .withColumn("year_month", date_format(current_date(), "yyyy-MM"))
    
    # TRANSFORMAÇÃO 3: Agrupamento numérico - Soma e contagem por setor (obrigatório)
    df_aggregated = df.groupBy("setor", "year_month") \
                     .agg(
                         count("stock_code").alias("total_stocks_count"),
                         sum(col("part_percent").cast("double")).alias("total_sector_participation"),
                         avg(col("part_percent").cast("double")).alias("avg_sector_participation"),
                         max(col("part_percent").cast("double")).alias("max_sector_participation")
                     )
    
    # Adicionar dados individuais das ações também
    df_with_metrics = df.withColumn("sector_rank", 
                                   row_number().over(
                                       Window.partitionBy("setor")
                                            .orderBy(col("part_percent").desc())
                                   ))
    
    print("Transformações aplicadas com sucesso")
    return df_with_metrics

def write_parquet_partitioned(df: DataFrame, output_path: str):
    """
    Salva dados refinados em Parquet particionado por data e setor.
    """
    print(f"Salvando dados refinados em: {output_path}")
    
    # Particionar por data e setor
    df.write \
      .mode("overwrite") \
      .partitionBy("year_month", "setor") \
      .parquet(output_path)
    
    # Registrar no Glue Catalog
    sink = glueContext.getSink(
        path=output_path,
        connection_type="s3",
        updateBehavior="UPDATE_IN_DATABASE",
        partitionKeys=["year_month", "setor"],
        compression="snappy",
        enableUpdateCatalog=True,
        updateCatalogOptions={"database": "bovespa_db", "tableName": "bovespa_refined"}
    )
    
    print("Dados salvos e catalogados com sucesso")

if __name__ == "__main__":
    main()

def read_json_data(input_path: str) -> DataFrame:
    """
    Lê dados JSON do S3.
    
    Args:
        input_path: Caminho dos dados de entrada
        
    Returns:
        DataFrame com dados carregados
    """
    # TODO: Implementar leitura de dados JSON
    pass

def apply_transformations(df: DataFrame) -> DataFrame:
    """
    Aplica transformações nos dados.
    
    Args:
        df: DataFrame de entrada
        
    Returns:
        DataFrame transformado
    """
    # TODO: Implementar transformações
    # - Agrupamento por setor
    # - Renomeação de colunas
    # - Cálculos com datas
    pass

def write_parquet_partitioned(df: DataFrame, output_path: str) -> None:
    """
    Escreve dados em formato Parquet particionado.
    
    Args:
        df: DataFrame para salvar
        output_path: Caminho de saída
    """
    # TODO: Implementar escrita particionada
    pass

if __name__ == "__main__":
    main()
