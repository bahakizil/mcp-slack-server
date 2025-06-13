#!/bin/bash

# AWS App Runner deployment script for Slack MCP Server
# This script deploys your MCP server to AWS for production use

set -e

# Load AWS configuration from aws.json if available
if [ -f "aws.json" ]; then
    echo "📋 Loading AWS configuration from aws.json..."
    AWS_ACCOUNT_ID=$(jq -r '.aws_account_id' aws.json)
    AWS_ACCESS_KEY_ID=$(jq -r '.aws_access_key_id' aws.json)
    AWS_SECRET_ACCESS_KEY=$(jq -r '.aws_secret_access_key' aws.json)
    REGION=$(jq -r '.aws_default_region' aws.json)
    SERVICE_NAME=$(jq -r '.service_name' aws.json)
    ECR_REPO=$(jq -r '.ecr_repository' aws.json)
    
    # Export AWS credentials for CLI usage
    export AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID
    export AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY
    export AWS_DEFAULT_REGION=$REGION
else
    # Fallback to environment variables or defaults
    SERVICE_NAME="${SERVICE_NAME:-slack-mcp-server}"
    ECR_REPO="${ECR_REPO:-slack-mcp-server}"
    REGION="${AWS_REGION:-us-east-1}"
fi

# Check prerequisites
check_prerequisites() {
    echo "🔍 Checking prerequisites..."
    
    # Check AWS CLI
    if ! command -v aws &> /dev/null; then
        echo "❌ AWS CLI not found. Install from: https://aws.amazon.com/cli/"
        exit 1
    fi
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        echo "❌ Docker not found. Install from: https://docker.com/get-started"
        exit 1
    fi
    
    # Check AWS credentials
    if ! aws sts get-caller-identity &> /dev/null; then
        echo "❌ AWS credentials not configured. Run: aws configure"
        exit 1
    fi
    
    # Check jq is installed for JSON parsing
    if ! command -v jq &> /dev/null; then
        echo "❌ jq not found. Install with: brew install jq (macOS) or apt install jq (Linux)"
        exit 1
    fi
    
    # Check env.json exists
    if [ ! -f "env.json" ]; then
        echo "❌ env.json not found. Run: python setup.py"
        exit 1
    fi
    
    # Check aws.json exists if not using environment variables
    if [ ! -f "aws.json" ] && [ -z "$AWS_ACCESS_KEY_ID" ]; then
        echo "❌ aws.json not found and AWS credentials not set."
        echo "   Run: python setup.py (to create aws.json)"
        echo "   Or: aws configure (to setup AWS CLI)"
        exit 1
    fi
    
    echo "✅ All prerequisites met!"
}

# Get AWS account info
get_aws_info() {
    echo "📊 Getting AWS account information..."
    
    # Use account ID from aws.json if available, otherwise get from AWS CLI
    if [ -n "$AWS_ACCOUNT_ID" ]; then
        ACCOUNT_ID=$AWS_ACCOUNT_ID
        echo "   Account ID: $ACCOUNT_ID (from aws.json)"
    else
        ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
        echo "   Account ID: $ACCOUNT_ID (from AWS CLI)"
    fi
    
    echo "   Region: $REGION"
    echo "   Service Name: $SERVICE_NAME"
    echo "   ECR Repository: $ECR_REPO"
}

# Create ECR repository if it doesn't exist
create_ecr_repo() {
    echo "🏗️  Ensuring ECR repository exists..."
    
    if ! aws ecr describe-repositories --repository-names $ECR_REPO --region $REGION &> /dev/null; then
        echo "   Creating ECR repository: $ECR_REPO"
        aws ecr create-repository --repository-name $ECR_REPO --region $REGION
    else
        echo "   ✅ ECR repository already exists"
    fi
}

# Build and push Docker image
build_and_push() {
    echo "📦 Building Docker image..."
    docker build --platform linux/amd64 -t $ECR_REPO .

    echo "🏷️  Tagging image..."
    docker tag $ECR_REPO:latest $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$ECR_REPO:latest

    echo "🔐 Logging into ECR..."
    aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com

    echo "⬆️  Pushing to ECR..."
    docker push $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$ECR_REPO:latest
    
    echo "✅ Docker image pushed successfully!"
}

# Create or update App Runner service
deploy_apprunner() {
    echo "🎯 Deploying to App Runner..."
    
    # Check if service exists
    SERVICE_ARN=$(aws apprunner list-services --query "ServiceSummaryList[?ServiceName=='$SERVICE_NAME'].ServiceArn" --output text 2>/dev/null || echo "")
    
    if [ -z "$SERVICE_ARN" ]; then
        echo "   Creating new App Runner service..."
        
        # Create service configuration
        cat > apprunner-config.json << EOF
{
  "ServiceName": "$SERVICE_NAME",
  "SourceConfiguration": {
    "ImageRepository": {
      "ImageIdentifier": "$ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$ECR_REPO:latest",
      "ImageConfiguration": $(cat env.json | jq '.ImageRepository.ImageConfiguration'),
      "ImageRepositoryType": "ECR"
    },
    "AutoDeploymentsEnabled": true
  },
  "InstanceConfiguration": {
    "Cpu": "0.25 vCPU",
    "Memory": "0.5 GB"
  }
}
EOF
        
        # Create service
        aws apprunner create-service --cli-input-json file://apprunner-config.json --region $REGION
        rm apprunner-config.json
        
        echo "   ⏳ Service creation initiated..."
        echo "   ℹ️  This may take 5-10 minutes for first deployment"
        
    else
        echo "   Updating existing service..."
        aws apprunner start-deployment --service-arn "$SERVICE_ARN" --region $REGION
        echo "   ⏳ Update deployment initiated..."
    fi
}

# Get service URL
get_service_url() {
    echo "🌐 Getting service URL..."
    
    # Wait a moment for service to be created
    sleep 5
    
    SERVICE_URL=$(aws apprunner list-services --query "ServiceSummaryList[?ServiceName=='$SERVICE_NAME'].ServiceUrl" --output text 2>/dev/null || echo "")
    
    if [ -n "$SERVICE_URL" ]; then
        echo "   📍 Service URL: https://$SERVICE_URL"
        echo "   🔧 MCP Endpoint: https://$SERVICE_URL/mcp"
        
        # Save to file for easy reference
        echo "https://$SERVICE_URL/mcp" > .deployment-url
        echo "   💾 URL saved to .deployment-url"
    else
        echo "   ⏳ Service URL not available yet, check AWS Console"
    fi
}

# Show post-deployment instructions
show_instructions() {
    echo ""
    echo "🎉 Deployment completed successfully!"
    echo "="*50
    echo ""
    echo "📋 NEXT STEPS:"
    echo ""
    echo "1. 🕐 Wait 5-10 minutes for service to be fully ready"
    echo "2. 🔍 Check deployment status in AWS Console"
    echo "3. 🧪 Test your MCP endpoint:"
    
    if [ -f ".deployment-url" ]; then
        URL=$(cat .deployment-url)
        echo "   curl $URL"
    fi
    
    echo ""
    echo "4. 🔧 Update your MCP client configuration:"
    echo "   {"
    echo "     \"mcp\": {"
    echo "       \"slack-mcp-server\": {"
    echo "         \"transport\": \"streamable-http\","
    
    if [ -f ".deployment-url" ]; then
        URL=$(cat .deployment-url)
        echo "         \"url\": \"$URL\","
    else
        echo "         \"url\": \"https://YOUR-SERVICE.us-east-1.awsapprunner.com/mcp/\","
    fi
    
    echo "         \"headers\": {"
    echo "           \"Accept\": \"application/json, text/event-stream\""
    echo "         }"
    echo "       }"
    echo "     }"
    echo "   }"
    echo ""
    echo "📚 Documentation: README.md"
    echo "🐛 Issues: https://github.com/bahakizil/mcp-slack-server/issues"
}

# Main deployment function
main() {
    echo "🚀 MCP Slack Server - AWS Deployment"
    echo "="*40
    
    check_prerequisites
    get_aws_info
    create_ecr_repo
    build_and_push
    deploy_apprunner
    get_service_url
    show_instructions
}

# Handle script interruption
trap 'echo -e "\n❌ Deployment cancelled by user"; exit 1' INT

# Run main function
main "$@" 