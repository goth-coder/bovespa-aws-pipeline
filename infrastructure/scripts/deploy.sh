#!/bin/bash
# Script para deploy da infraestrutura AWS
# Pipeline Bovespa - Script de Deploy Completo
# Autor: Projeto Tech Challenge FIAP

set -e  # Parar execução em caso de erro

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configurações
PROJECT_NAME="bovespa-pipeline"
ENVIRONMENT="dev"
STACK_NAME="$PROJECT_NAME-$ENVIRONMENT"
BUCKET_NAME="bovespa-pipeline-data-adri-victor"
REGION="us-east-1"

# Verificar se AWS CLI está configurado
check_aws_cli() {
    echo -e "${BLUE}🔍 Verificando configuração AWS CLI...${NC}"
    
    if ! command -v aws &> /dev/null; then
        echo -e "${RED}❌ AWS CLI não encontrado. Instale: pip install awscli${NC}"
        exit 1
    fi
    
    if ! aws sts get-caller-identity &> /dev/null; then
        echo -e "${RED}❌ AWS CLI não configurado. Execute: aws configure${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ AWS CLI configurado${NC}"
}

# Verificar se bucket existe, criar se necessário
check_bucket() {
    echo -e "${BLUE}🪣 Verificando bucket S3: $BUCKET_NAME...${NC}"
    
    if aws s3api head-bucket --bucket "$BUCKET_NAME" 2>/dev/null; then
        echo -e "${GREEN}✅ Bucket $BUCKET_NAME já existe${NC}"
    else
        echo -e "${YELLOW}⚠️ Criando bucket $BUCKET_NAME...${NC}"
        aws s3 mb "s3://$BUCKET_NAME" --region "$REGION"
        echo -e "${GREEN}✅ Bucket criado com sucesso${NC}"
    fi
}

# Upload do código Glue para S3
upload_glue_code() {
    echo -e "${BLUE}📤 Fazendo upload do código Glue...${NC}"
    
    # Criar diretório scripts no bucket se não existir
    aws s3api put-object --bucket "$BUCKET_NAME" --key "scripts/" 2>/dev/null || true
    
    # Upload do script ETL
    aws s3 cp "../../src/glue/etl_job.py" "s3://$BUCKET_NAME/scripts/etl_job.py"
    aws s3 cp "../../src/glue/transformations.py" "s3://$BUCKET_NAME/scripts/transformations.py"
    
    echo -e "${GREEN}✅ Código Glue enviado para S3${NC}"
}

# Fazer package da Lambda
package_lambda() {
    echo -e "${BLUE}📦 Empacotando função Lambda...${NC}"
    
    # Criar diretório temporário
    TEMP_DIR="/tmp/lambda-package"
    rm -rf "$TEMP_DIR"
    mkdir -p "$TEMP_DIR"
    
    # Copiar código da Lambda
    cp "../../src/lambda/trigger_scraping.py" "$TEMP_DIR/"
    cp "../../src/lambda/requirements.txt" "$TEMP_DIR/"
    
    # Copiar módulos de scraping
    cp -r "../../src/scraping" "$TEMP_DIR/"
    
    # Instalar dependências
    cd "$TEMP_DIR"
    pip install -r requirements.txt -t .
    
    # Criar ZIP
    zip -r lambda-package.zip . -x "*.pyc" "__pycache__/*"
    
    # Upload para S3
    aws s3 cp lambda-package.zip "s3://$BUCKET_NAME/lambda/trigger_scraping.zip"
    
    cd - > /dev/null
    rm -rf "$TEMP_DIR"
    
    echo -e "${GREEN}✅ Lambda empacotada e enviada para S3${NC}"
}

# Deploy da stack CloudFormation
deploy_stack() {
    echo -e "${BLUE}🚀 Fazendo deploy da stack CloudFormation...${NC}"
    
    # Verificar se stack existe
    if aws cloudformation describe-stacks --stack-name "$STACK_NAME" --region "$REGION" &>/dev/null; then
        echo -e "${YELLOW}📝 Atualizando stack existente...${NC}"
        aws cloudformation update-stack 
            --stack-name "$STACK_NAME" 
            --template-body file://../cloudformation/main.yml 
            --parameters 
                ParameterKey=ProjectName,ParameterValue="$PROJECT_NAME" 
                ParameterKey=Environment,ParameterValue="$ENVIRONMENT" 
                ParameterKey=BucketName,ParameterValue="$BUCKET_NAME" 
            --capabilities CAPABILITY_NAMED_IAM 
            --region "$REGION"
    else
        echo -e "${YELLOW}🆕 Criando nova stack...${NC}"
        aws cloudformation create-stack 
            --stack-name "$STACK_NAME" 
            --template-body file://../cloudformation/main.yml 
            --parameters 
                ParameterKey=ProjectName,ParameterValue="$PROJECT_NAME" 
                ParameterKey=Environment,ParameterValue="$ENVIRONMENT" 
                ParameterKey=BucketName,ParameterValue="$BUCKET_NAME" 
            --capabilities CAPABILITY_NAMED_IAM 
            --region "$REGION"
    fi
    
    echo -e "${YELLOW}⏳ Aguardando conclusão do deploy...${NC}"
    aws cloudformation wait stack-update-complete --stack-name "$STACK_NAME" --region "$REGION" 2>/dev/null || 
    aws cloudformation wait stack-create-complete --stack-name "$STACK_NAME" --region "$REGION"
    
    echo -e "${GREEN}✅ Stack deployada com sucesso${NC}"
}

# Atualizar código da Lambda
update_lambda_code() {
    echo -e "${BLUE}🔄 Atualizando código da Lambda...${NC}"
    
    LAMBDA_FUNCTION_NAME="$PROJECT_NAME-trigger-$ENVIRONMENT"
    
    # Atualizar código da função
    aws lambda update-function-code 
        --function-name "$LAMBDA_FUNCTION_NAME" 
        --s3-bucket "$BUCKET_NAME" 
        --s3-key "lambda/trigger_scraping.zip" 
        --region "$REGION"
    
    echo -e "${GREEN}✅ Código da Lambda atualizado${NC}"
}

# Testar pipeline
test_pipeline() {
    echo -e "${BLUE}🧪 Testando pipeline...${NC}"
    
    LAMBDA_FUNCTION_NAME="$PROJECT_NAME-trigger-$ENVIRONMENT"
    
    # Invocar Lambda para teste
    aws lambda invoke 
        --function-name "$LAMBDA_FUNCTION_NAME" 
        --payload '{"source": "manual", "test": true}' 
        --region "$REGION" 
        response.json
    
    if grep -q "200" response.json; then
        echo -e "${GREEN}✅ Teste da Lambda: SUCESSO${NC}"
    else
        echo -e "${RED}❌ Teste da Lambda: FALHOU${NC}"
        cat response.json
    fi
    
    rm -f response.json
}

# Mostrar outputs da stack
show_outputs() {
    echo -e "${BLUE}📋 Outputs da Stack:${NC}"
    
    aws cloudformation describe-stacks 
        --stack-name "$STACK_NAME" 
        --region "$REGION" 
        --query 'Stacks[0].Outputs[*].[OutputKey,OutputValue]' 
        --output table
}

# Função principal
main() {
    echo -e "${GREEN}🚀 INÍCIO DO DEPLOY - Pipeline Bovespa AWS${NC}"
    echo "======================================================"
    
    # Executar verificações e deploy
    check_aws_cli
    check_bucket
    upload_glue_code
    package_lambda
    deploy_stack
    update_lambda_code
    test_pipeline
    show_outputs
    
    echo "======================================================"
    echo -e "${GREEN}🎉 DEPLOY CONCLUÍDO COM SUCESSO!${NC}"
    echo -e "${YELLOW}📊 Próximos passos:${NC}"
    echo "1. Verificar logs no CloudWatch"
    echo "2. Testar pipeline manualmente"
    echo "3. Configurar Athena queries"
    echo "4. Validar dados no S3"
    echo ""
    echo -e "${BLUE}🌐 Links úteis:${NC}"
    echo "• S3 Console: https://s3.console.aws.amazon.com/s3/buckets/$BUCKET_NAME"
    echo "• Lambda Console: https://console.aws.amazon.com/lambda/home?region=$REGION#/functions/$PROJECT_NAME-trigger-$ENVIRONMENT"
    echo "• Glue Console: https://console.aws.amazon.com/glue/home?region=$REGION#etl:tab=jobs"
    echo "• CloudFormation: https://console.aws.amazon.com/cloudformation/home?region=$REGION#/stacks/stackinfo?stackId=$STACK_NAME"
}

# Executar função principal
main "$@"

set -e

PROJECT_NAME="bovespa-pipeline"
ENVIRONMENT="dev"
AWS_REGION="us-east-1"

echo "🚀 Iniciando deploy da infraestrutura Bovespa Pipeline..."

# Função para deploy via CloudFormation
deploy_cloudformation() {
    echo "📦 Deploy usando CloudFormation..."
    
    aws cloudformation deploy \
        --template-file infrastructure/cloudformation/main.yml \
        --stack-name ${PROJECT_NAME}-${ENVIRONMENT} \
        --parameter-overrides \
            ProjectName=${PROJECT_NAME} \
            Environment=${ENVIRONMENT} \
        --capabilities CAPABILITY_IAM \
        --region ${AWS_REGION}
    
    echo "✅ CloudFormation deploy concluído!"
}

# Função para deploy via Terraform
deploy_terraform() {
    echo "🏗️ Deploy usando Terraform..."
    
    cd infrastructure/terraform
    
    terraform init
    terraform plan \
        -var="project_name=${PROJECT_NAME}" \
        -var="environment=${ENVIRONMENT}" \
        -var="aws_region=${AWS_REGION}"
    
    terraform apply -auto-approve \
        -var="project_name=${PROJECT_NAME}" \
        -var="environment=${ENVIRONMENT}" \
        -var="aws_region=${AWS_REGION}"
    
    cd ../..
    echo "✅ Terraform deploy concluído!"
}

# Menu de seleção
echo "Selecione o método de deploy:"
echo "1) CloudFormation"
echo "2) Terraform"
read -p "Opção (1 ou 2): " option

case $option in
    1)
        deploy_cloudformation
        ;;
    2)
        deploy_terraform
        ;;
    *)
        echo "❌ Opção inválida!"
        exit 1
        ;;
esac

echo "🎉 Deploy da infraestrutura concluído com sucesso!"
