#!/bin/bash
# 🚀 Script de Deploy AWS - Pipeline Bovespa

set -e  # Para em caso de erro

echo "🚀 INICIANDO DEPLOY DO PIPELINE BOVESPA"
echo "========================================"

# Verificar se AWS CLI está instalado
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI não encontrado. Instale com: brew install awscli"
    exit 1
fi

# Carregar variáveis do .env
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
    echo "✅ Variáveis do .env carregadas"
else
    echo "❌ Arquivo .env não encontrado!"
    exit 1
fi

# Testar credenciais AWS
echo "🔐 Testando credenciais AWS..."
aws sts get-caller-identity || {
    echo "❌ Credenciais AWS inválidas ou expiradas!"
    echo "💡 Vá no AWS Academy > AWS Details > copie as credenciais"
    exit 1
}

echo "✅ Credenciais AWS válidas!"

# Verificar se bucket existe
echo "🪣 Verificando bucket S3..."
if aws s3 ls "s3://$BOVESPA_S3_BUCKET" 2>/dev/null; then
    echo "✅ Bucket $BOVESPA_S3_BUCKET já existe"
else
    echo "📦 Criando bucket $BOVESPA_S3_BUCKET..."
    aws s3 mb "s3://$BOVESPA_S3_BUCKET" --region $AWS_DEFAULT_REGION
    echo "✅ Bucket criado com sucesso!"
fi

# Fazer upload dos scripts para S3
echo "📤 Fazendo upload dos scripts..."

# Criar pasta scripts no S3
aws s3 cp src/glue/etl_job_complete.py "s3://$BOVESPA_S3_BUCKET/scripts/etl_job_complete.py"
echo "✅ Script Glue enviado para S3"

# Testar o pipeline localmente
echo "🧪 Testando pipeline localmente..."
/Users/adriannylelis/Workspace/bovespa-aws-pipeline/.venv/bin/python -c "
import sys
sys.path.append('src')
from scraping.scraping import B3Scraper
scraper = B3Scraper()
result = scraper.run_scraping()
print(f'✅ Scraping testado: {len(result)} arquivos gerados')
"

echo ""
echo "🎉 DEPLOY CONCLUÍDO COM SUCESSO!"
echo "================================"
echo "📊 Próximos passos:"
echo "1. ✅ Credenciais configuradas"
echo "2. ✅ Bucket S3 criado/verificado"
echo "3. ✅ Scripts enviados para S3"
echo "4. ✅ Pipeline testado localmente"
echo ""
echo "🚀 Agora você pode:"
echo "   - Executar o scraping: ./.venv/bin/python -c 'import sys; sys.path.append(\"src\"); from scraping.scraping import B3Scraper; B3Scraper().run_scraping()'"
echo "   - Processar para S3: ./.venv/bin/python tests/test_lambda_local.py"
echo ""
echo "📋 Para deploy completo (Lambda + Glue), execute: ./deploy_complete.sh"
