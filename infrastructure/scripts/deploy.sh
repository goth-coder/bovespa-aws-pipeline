#!/bin/bash
# Script para deploy da infraestrutura AWS
# Pode ser usado para CloudFormation ou Terraform

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
