"""
AWS Glue ETL Job principal para transformação dos dados B3.
Processa dados brutos Parquet e aplica transformações obrigatórias.
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
import boto3
from datetime import datetime

# Inicializar contextos
args = getResolvedOptions(sys.argv, ['JOB_NAME', 'BOVESPA_S3_BUCKET'])
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
        print("🚀 Iniciando job ETL B3...")
        
        # Configurações do job
        bucket_name = args.get('BOVESPA_S3_BUCKET', 'bovespa-pipeline-data-adri-victor')
        input_path = f"s3://{bucket_name}/dados/"
        output_path = f"s3://{bucket_name}/refined/"
        
        print(f"📁 Input path: {input_path}")
        print(f"📁 Output path: {output_path}")
        
        # 1. Ler dados brutos do S3
        print("📊 Lendo dados do S3...")
        df = read_parquet_data(input_path)
        
        # 2. Aplicar transformações obrigatórias
        print("🔄 Aplicando transformações...")
        df_transformed = apply_transformations(df)
        
        # 3. Salvar dados refinados com particionamento
        print("💾 Salvando dados refinados...")
        write_parquet_partitioned(df_transformed, output_path)
        
        # 4. Atualizar Glue Catalog
        print("📋 Atualizando Glue Catalog...")
        update_glue_catalog(bucket_name)
        
        print("✅ Job ETL B3 concluído com sucesso")
        
    except Exception as e:
        print(f"❌ Erro no job ETL: {str(e)}")
        raise e
    finally:
        job.commit()

def read_parquet_data(input_path: str) -> DataFrame:
    """
    Lê dados Parquet do S3 e converte para DataFrame.
    """
    print(f"📥 Lendo dados de: {input_path}")
    
    try:
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
        
        print(f"📈 DataFrame criado com {df.count()} registros")
        print(f"📋 Schema: {df.columns}")
        
        return df
        
    except Exception as e:
        print(f"❌ Erro ao ler dados: {str(e)}")
        raise e

def apply_transformations(df: DataFrame) -> DataFrame:
    """
    Aplica transformações obrigatórias do desafio Tech Challenge:
    1. Renomear 2 colunas (obrigatório)
    2. Cálculo com campos de data (obrigatório)
    3. Agrupamento numérico (sumarização, contagem ou soma) (obrigatório)
    """
    print("🔄 Aplicando transformações obrigatórias...")
    
    # TRANSFORMAÇÃO 1: Renomear 2 colunas (obrigatório)
    print("📝 Renomeando colunas...")
    df = df.withColumnRenamed("codigo", "stock_code") \
           .withColumnRenamed("acao", "company_name")
    
    # TRANSFORMAÇÃO 2: Cálculo com campos de data (obrigatório)
    print("📅 Adicionando campos de data...")
    df = df.withColumn("etl_processing_date", current_date()) \
           .withColumn("etl_processing_timestamp", current_timestamp()) \
           .withColumn("extraction_year_month", date_format(col("ano").cast("string") + "-" + 
                      lpad(col("mes").cast("string"), 2, "0") + "-01", "yyyy-MM"))
    
    # TRANSFORMAÇÃO 3: Agrupamento numérico - Agregações por setor (obrigatório)
    print("📊 Aplicando agrupamentos numéricos...")
    
    # Primeiro, criar dataframe com dados originais + campos calculados
    df_enriched = df.withColumn("total_stocks", lit(1)) \
                   .withColumn("market_cap_indicator", 
                              when(col("participacao").isNotNull() & (col("participacao") > 0.5), "High")
                              .when(col("participacao").isNotNull() & (col("participacao") > 0.1), "Medium")
                              .otherwise("Low"))
    
    # Agregação por setor e mês
    df_sector_summary = df_enriched.groupBy("setor", "extraction_year_month") \
                                   .agg(
                                       count("stock_code").alias("total_stocks_in_sector"),
                                       sum("participacao").alias("total_participation"),
                                       avg("participacao").alias("avg_participation"),
                                       max("participacao").alias("max_participation"),
                                       min("participacao").alias("min_participation"),
                                       countDistinct("company_name").alias("unique_companies")
                                   ) \
                                   .withColumn("sector_performance_level",
                                              when(col("avg_participation") > 0.5, "High Performance")
                                              .when(col("avg_participation") > 0.1, "Medium Performance")
                                              .otherwise("Low Performance"))
    
    # Adicionar ranking de setores
    window_spec = Window.orderBy(desc("total_participation"))
    df_final = df_sector_summary.withColumn("sector_rank", 
                                           row_number().over(window_spec))
    
    print(f"📊 Dados transformados: {df_final.count()} registros agregados")
    
    return df_final

def write_parquet_partitioned(df: DataFrame, output_path: str):
    """
    Salva DataFrame como Parquet particionado no S3.
    """
    print(f"💾 Salvando dados em: {output_path}")
    
    try:
        # Escrever dados particionados por ano e mês de extração
        df.write \
          .mode("overwrite") \
          .partitionBy("extraction_year_month") \
          .option("compression", "snappy") \
          .parquet(output_path)
        
        print("✅ Dados salvos com sucesso")
        
    except Exception as e:
        print(f"❌ Erro ao salvar dados: {str(e)}")
        raise e

def update_glue_catalog(bucket_name: str):
    """
    Atualiza o Glue Catalog com as novas tabelas.
    """
    try:
        glue_client = boto3.client('glue')
        database_name = 'bovespa_database'
        table_name = 'b3_sector_analysis'
        
        # Verificar se database existe
        try:
            glue_client.get_database(Name=database_name)
            print(f"📋 Database {database_name} já existe")
        except glue_client.exceptions.EntityNotFoundException:
            # Criar database
            glue_client.create_database(
                DatabaseInput={
                    'Name': database_name,
                    'Description': 'Database para dados da Bovespa B3'
                }
            )
            print(f"📋 Database {database_name} criado")
        
        # Criar/atualizar tabela
        table_input = {
            'Name': table_name,
            'StorageDescriptor': {
                'Columns': [
                    {'Name': 'setor', 'Type': 'string'},
                    {'Name': 'total_stocks_in_sector', 'Type': 'bigint'},
                    {'Name': 'total_participation', 'Type': 'double'},
                    {'Name': 'avg_participation', 'Type': 'double'},
                    {'Name': 'max_participation', 'Type': 'double'},
                    {'Name': 'min_participation', 'Type': 'double'},
                    {'Name': 'unique_companies', 'Type': 'bigint'},
                    {'Name': 'sector_performance_level', 'Type': 'string'},
                    {'Name': 'sector_rank', 'Type': 'int'}
                ],
                'Location': f's3://{bucket_name}/refined/',
                'InputFormat': 'org.apache.hadoop.hive.ql.io.parquet.MapredParquetInputFormat',
                'OutputFormat': 'org.apache.hadoop.hive.ql.io.parquet.MapredParquetOutputFormat',
                'SerdeInfo': {
                    'SerializationLibrary': 'org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe'
                }
            },
            'PartitionKeys': [
                {'Name': 'extraction_year_month', 'Type': 'string'}
            ]
        }
        
        try:
            # Tentar criar tabela
            glue_client.create_table(
                DatabaseName=database_name,
                TableInput=table_input
            )
            print(f"📋 Tabela {table_name} criada no Glue Catalog")
        except glue_client.exceptions.AlreadyExistsException:
            # Atualizar tabela existente
            glue_client.update_table(
                DatabaseName=database_name,
                TableInput=table_input
            )
            print(f"📋 Tabela {table_name} atualizada no Glue Catalog")
            
    except Exception as e:
        print(f"⚠️ Aviso: Erro ao atualizar Glue Catalog: {str(e)}")
        # Não falhar o job por causa do catalog

if __name__ == "__main__":
    main()
                         sum(col("part_percent").cast("double")).alias("total_sector_participation"),
                         avg(col("part_percent").cast("double")).alias("avg_sector_participation"),
                         max(col("part_percent").cast("double")).alias("max_sector_participation")
                     
    
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
