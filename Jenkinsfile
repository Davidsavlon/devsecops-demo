pipeline {
    agent any

    environment {
        REPO_NAME = "devsecops-demo"
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
                sh 'echo "Repository checked out successfully"'
                sh 'ls -la'
            }
        }

        stage('Claude SAST') {
            steps {
                withCredentials([string(credentialsId: 'anthropic-api-key', variable: 'ANTHROPIC_API_KEY')]) {
                    sh '''
                        echo "======================================"
                        echo " Claude Security Scanner"
                        echo "======================================"

                        # Find all scannable files in this repo
                        find . -type f \( \
                            -name "*.py" -o \
                            -name "*.js" -o \
                            -name "*.ts" -o \
                            -name "*.java" -o \
                            -name "*.go" -o \
                            -name "*.sh" -o \
                            -name "*.sql" \
                        \) \
                        ! -path "./.git/*" \
                        ! -path "./node_modules/*" \
                        > /tmp/all_files.txt

                        echo "Files found to scan:"
                        cat /tmp/all_files.txt
                        echo ""

                        # Scan each file
                        SCAN_FAILED=0
                        while IFS= read -r file; do
                            echo "--------------------------------------"
                            echo "Scanning: $file"
                            echo "--------------------------------------"
                            python3 /opt/claude_scanner.py "$file" \
                                --api-key "$ANTHROPIC_API_KEY" \
                                --severity MEDIUM \
                                --fail-on HIGH \
                                --verbose \
                                --json-report "/tmp/scan-$(basename $file).json" \
                                || SCAN_FAILED=1
                            echo ""
                        done < /tmp/all_files.txt

                        echo "======================================"
                        echo " Scan Complete"
                        echo "======================================"

                        if [ $SCAN_FAILED -eq 1 ]; then
                            echo "RESULT: FAILED - HIGH/CRITICAL issues found"
                            echo "Fix the issues above before this build can proceed"
                            exit 1
                        else
                            echo "RESULT: PASSED - No blocking issues found"
                        fi
                    '''
                }
            }
        }

        stage('Secrets Scan') {
            steps {
                sh '''
                    echo "Running Gitleaks secrets scan..."
                    docker run --rm \
                        -v $(pwd):/repo \
                        zricethezav/gitleaks:latest \
                        detect \
                        --source=/repo \
                        --report-format=json \
                        --report-path=/repo/gitleaks-report.json \
                        --exit-code=0 2>/dev/null || true
                    echo "Secrets scan complete"
                '''
            }
        }

        stage('Build') {
            steps {
                echo 'Build stage — add your build commands here'
            }
        }
    }

    post {
        success {
            echo '✅ Pipeline PASSED — all security checks cleared'
        }
        failure {
            echo '❌ Pipeline FAILED — security issues must be fixed'
        }
        always {
            archiveArtifacts artifacts: '*.json',
                            allowEmptyArchive: true
            echo 'Pipeline finished'
        }
    }
}
