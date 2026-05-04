pipeline {
    agent any

    stages {

        stage('Checkout') {
            steps {
                git branch: 'main',
                    url: 'https://github.com/Davidsavlon/devsecops-demo.git'
                sh 'echo "Repo cloned:" && ls -la'
            }
        }

        stage('Claude SAST') {
            steps {
                withCredentials([string(credentialsId: 'anthropic-api-key', variable: 'ANTHROPIC_API_KEY')]) {
                    sh '''
                        echo "======================================"
                        echo " Claude Security Scanner"
                        echo "======================================"

                        find . -type f -name "*.py" -not -path "./.git/*" > /tmp/files.txt
                        find . -type f -name "*.js" -not -path "./.git/*" >> /tmp/files.txt
                        find . -type f -name "*.ts" -not -path "./.git/*" >> /tmp/files.txt
                        find . -type f -name "*.java" -not -path "./.git/*" >> /tmp/files.txt
                        find . -type f -name "*.sh" -not -path "./.git/*" >> /tmp/files.txt

                        echo "Files to scan:"
                        cat /tmp/files.txt
                        echo ""

                        SCAN_FAILED=0
                        while IFS= read -r file; do
                            echo "--- Scanning: $file ---"
                            python3 /opt/claude_scanner.py "$file" --api-key "$ANTHROPIC_API_KEY" --severity MEDIUM --fail-on HIGH --verbose || SCAN_FAILED=1
                            echo ""
                        done < /tmp/files.txt

                        echo "======================================"
                        if [ $SCAN_FAILED -eq 1 ]; then
                            echo " RESULT: FAILED - HIGH/CRITICAL issues found"
                            echo "======================================"
                            exit 1
                        else
                            echo " RESULT: PASSED"
                            echo "======================================"
                        fi
                    '''
                }
            }
        }

        stage('Secrets Scan') {
            steps {
                sh '''
                    echo "Running Gitleaks secrets scan..."
                    docker run --rm -v $(pwd):/repo zricethezav/gitleaks:latest detect --source=/repo --report-format=json --report-path=/repo/gitleaks-report.json --exit-code=0 2>/dev/null || true
                    echo "Secrets scan complete"
                '''
            }
        }

        stage('Build') {
            steps {
                echo 'Security passed — build stage reached!'
            }
        }
    }

    post {
        success { echo 'ALL STAGES PASSED' }
        failure { echo 'PIPELINE FAILED — security issues found' }
        always {
            archiveArtifacts artifacts: '*.json', allowEmptyArchive: true
        }
    }
}
stage('Secrets Scan') {
    steps {
        sh '''
            echo "======================================"
            echo " Stage 2: Gitleaks Secrets Scan"
            echo "======================================"

            docker run --rm \
                -v $(pwd):/repo \
                zricethezav/gitleaks:latest \
                detect \
                --source=/repo \
                --report-format=json \
                --report-path=/repo/gitleaks-report.json \
                --exit-code=1

            echo "No secrets found - PASSED"
        '''
    }
    post {
        always {
            archiveArtifacts artifacts: 'gitleaks-report.json',
                            allowEmptyArchive: true
        }
        failure {
            echo 'SECRETS DETECTED - commit blocked!'
        }
    }
}
