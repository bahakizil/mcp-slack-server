#!/bin/bash

# AWS App Runner deployment script for Slack MCP Server

set -e

# Variables
SERVICE_NAME="slack-mcp-server"
ECR_REPO="slack-mcp-server"
REGION="us-east-1"
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

echo "🚀 Starting deployment to AWS App Runner..."

# Build and push to ECR
echo "📦 Building Docker image..."
docker build --platform linux/amd64 -t $ECR_REPO .

echo "🏷️  Tagging image..."
docker tag $ECR_REPO:latest $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$ECR_REPO:latest

echo "🔐 Logging into ECR..."
aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com

echo "⬆️  Pushing to ECR..."
docker push $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$ECR_REPO:latest

echo "🎯 Updating App Runner service..."
aws apprunner start-deployment --service-arn $(aws apprunner list-services --query "ServiceSummaryList[?ServiceName=='$SERVICE_NAME'].ServiceArn" --output text)

echo "✅ Deployment initiated! Check AWS Console for status."
echo "🌐 Service will be available at: https://qg7p6udte6.us-east-1.awsapprunner.com" 