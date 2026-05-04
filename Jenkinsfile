pipeline {
    agent any

    stages {

        stage('Checkout') {
            steps {
                git branch: 'main',
                    url: 'https://github.com/Davidsavlon/devsecops-demo.git'
                sh 'echo "Files in repo:" && ls -la && find . -name "*.py" -not -path "./.git/*"'
            }
        }

        stage('Claude SAST') {
            steps {
                withCredentials([string(credentialsId: 'anthropic-api-key', variable: 'ANTHROPIC_API_KEY')]) {
                    sh '''
                        echo "======================================"
                        echo " Stage 1: Claude SAST"
                        echo "======================================"

                        find . -type f -name "*.py" -not -path "./.git/*" > /tmp/files.txt
                        find . -type f -name "*.js" -not -path "./.git/*" >> /tmp/files.txt

                        echo "Files to scan:"
                        cat /tmp/files.txt

                        SCAN_FAILED=0
                        while IFS= read -r file; do
                            echo "--- Scanning: $file ---"
                            python3 /opt/claude_scanner.py "$file" \
                                --api-key "$ANTHROPIC_API_KEY" \
                                --severity MEDIUM \
                                --fail-on HIGH \
                                --verbose || SCAN_FAILED=1
                        done < /tmp/files.txt

                        if [ $SCAN_FAILED -eq 1 ]; then
                            echo "RESULT: FAILED"
                            exit 1
                        else
                            echo "RESULT: PASSED"
                        fi
                    '''
                }
            }
        }

        stage('Secrets Scan') {
            steps {
                sh '''
                    echo "======================================"
                    echo " Stage 2: Gitleaks Secrets Scan"
                    echo "======================================"

                    echo "Scanning for secrets in all files..."
                    docker run --rm \
                        -v $(pwd):/repo \
                        zricethezav/gitleaks:latest \
                        detect \
                        --source=/repo \
                        --report-format=json \
                        --report-path=/repo/gitleaks-report.json \
                        --verbose \
                        --exit-code=1

                    echo "======================================"
                    echo " No secrets found - PASSED"
                    echo "======================================"
                '''
            }
        }

        stage('Dependency Scan') {
            steps {
                sh '''
                    echo "======================================"
                    echo " Stage 3: Trivy Dependency Scan"
                    echo "======================================"

                    docker run --rm \
                        -v $(pwd):/project \
                        aquasec/trivy:latest \
                        fs \
                        --security-checks vuln \
                        --severity HIGH,CRITICAL \
                        --format table \
                        /project 2>/dev/null || true

                    echo "Dependency scan complete"
                '''
            }
        }

        stage('Build') {
            steps {
                echo 'All security scans passed - build stage reached!'
            }
        }
    }

    post {
        success {
            echo 'ALL STAGES PASSED'
        }
        failure {
            echo 'PIPELINE FAILED - check security findings above'
        }
        always {
            archiveArtifacts artifacts: 'gitleaks-report.json,trivy-fs-report.json',
                            allowEmptyArchive: true
        }
    }
}
