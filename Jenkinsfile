pipeline {
    agent any

    environment {
        AWS_REGION = 'us-east-1'
        ECR_REPO = 'my-repo'
        IMAGE_TAG = 'latest'
        SERVICE_NAME = 'llmops-medical-service'
    }

    stages {
        stage('Clone GitHub Repo') {
            steps {
                script {
                    echo 'Cloning GitHub repo to Jenkins...'
                    checkout scmGit(branches: [[name: '*/main']], extensions: [], userRemoteConfigs: [[credentialsId: 'github-token', url: 'https://github.com/Devmangukiya/AI-Insurance-Claim-Engine.git']])
            }
        }

        stage('Build, Scan, and Push Docker Image to ECR') {
            steps {
                withCredentials([[$class: 'AmazonWebServicesCredentialsBinding', credentialsId: 'aws-token']]) {
                    script {
                        def accountId = sh(script: "aws sts get-caller-identity --query Account --output text", returnStdout: true).trim()
                        def ecrUrl = "${accountId}.dkr.ecr.${env.AWS_REGION}.amazonaws.com/${env.ECR_REPO}"
                        def imageFullTag = "${ecrUrl}:${IMAGE_TAG}"

                        // Each command is now separate for clarity and targeted retries
                        sh "aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ecrUrl}"
                        sh "docker build -t ${env.ECR_REPO}:${IMAGE_TAG} ."
                        
                        // Run Trivy scan - '|| true' ensures the pipeline doesn't stop if vulnerabilities are found
                        
                        sh "docker tag ${env.ECR_REPO}:${IMAGE_TAG} ${imageFullTag}"

                        // SOLUTION for Network Error: Retry the push command up to 3 times if it fails
                        retry(3) {
                            echo "Attempting to push Docker image (Attempt: \$${env.RETRY_COUNT})..."
                            sh "docker push ${imageFullTag}"
                        }
                    }
                }
            }
        }

    //     stage('Deploy to AWS App Runner') {
    //         steps {
    //             withCredentials([[$class: 'AmazonWebServicesCredentialsBinding', credentialsId: 'aws-token']]) {
    //                 script {
    //                     echo "Triggering deployment to AWS App Runner..."
    //                     sh """
    //                     SERVICE_ARN=\$(aws apprunner list-services --query "ServiceSummaryList[?ServiceName=='${SERVICE_NAME}'].ServiceArn" --output text --region ${AWS_REGION})
    //                     echo "Found App Runner Service ARN: \$SERVICE_ARN"
    //                     aws apprunner start-deployment --service-arn \$SERVICE_ARN --region ${AWS_REGION}
    //                     """
    //                 }
    //             }
    //         }
        }
    }

    // SOLUTION for Disk Space: This 'post' block runs at the end of the pipeline, regardless of success or failure
    post {
        always {
            script {
                echo "Cleaning up Docker images and build cache to save space..."
                // The '-f' flag forces the prune without confirmation
                sh "docker system prune -f"
            }
        }
    }
}