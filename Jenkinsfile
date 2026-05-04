pipeline {
    agent any

    stages {

        stage('Checkout') {
            steps {
                git branch: 'main',
                    url: 'https://github.com/Davidsavlon/devsecops-demo.git'
                sh 'echo "Files in repo:" && ls -la'
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
                    docker run --rm \
                        -v $(pwd):/repo \
                        zricethezav/gitleaks:latest \
                        detect \
                        --source=/repo \
                        --no-git \
                        --report-format=json \
                        --report-path=/repo/gitleaks-report.json \
                        --verbose \
                        --exit-code=1
                    echo "No secrets found - PASSED"
                '''
            }
        }

        stage('Dependency Scan') {
            steps {
                sh '''
                    echo "======================================"
                    echo " Stage 3: Trivy Dependency Scan"
                    echo "======================================"
                    echo "requirements.txt contents:"
                    cat requirements.txt

                    echo ""
                    echo "Running Trivy scan..."
                    docker run --rm \
                        -v $(pwd):/project \
                        aquasec/trivy:latest \
                        fs \
                        --scanners vuln \
                        --severity HIGH,CRITICAL \
                        --format table \
                        /project/requirements.txt || true

                    echo ""
                    echo "Saving JSON report..."
                    docker run --rm \
                        -v $(pwd):/project \
                        aquasec/trivy:latest \
                        fs \
                        --scanners vuln \
                        --severity HIGH,CRITICAL \
                        --format json \
                        --output /project/trivy-report.json \
                        /project/requirements.txt 2>/dev/null || true

                    echo ""
                    echo "======================================"
                    echo " Vulnerability Summary"
                    echo "======================================"
                    if [ -f trivy-report.json ]; then
                        python3 -c "
import json
with open('trivy-report.json') as f:
    data = json.load(f)
critical, high = [], []
for result in data.get('Results', []):
    for v in (result.get('Vulnerabilities') or []):
        sev = v.get('Severity','')
        entry = f\"  {v.get('PkgName','?')} {v.get('InstalledVersion','?')} -> {v.get('FixedVersion','no fix')} | {v.get('VulnerabilityID','?')}\"
        if sev == 'CRITICAL': critical.append(entry)
        elif sev == 'HIGH': high.append(entry)
print(f'CRITICAL: {len(critical)}')
[print(c) for c in critical]
print(f'HIGH: {len(high)}')
[print(h) for h in high]
print(f'Total: {len(critical)+len(high)}')
"
                    else
                        echo "No JSON report generated"
                    fi
                    echo "======================================"
                    echo " Dependency scan complete"
                    echo "======================================"
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
            archiveArtifacts artifacts: '*.json',
                            allowEmptyArchive: true
        }
    }
}pipeline {
    agent any

    stages {

        stage('Checkout') {
            steps {
                git branch: 'main',
                    url: 'https://github.com/Davidsavlon/devsecops-demo.git'
                sh 'echo "Files in repo:" && ls -la'
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
                    docker run --rm \
                        -v $(pwd):/repo \
                        zricethezav/gitleaks:latest \
                        detect \
                        --source=/repo \
                        --no-git \
                        --report-format=json \
                        --report-path=/repo/gitleaks-report.json \
                        --verbose \
                        --exit-code=1
                    echo "No secrets found - PASSED"
                '''
            }
        }

        stage('Dependency Scan') {
            steps {
                sh '''
                    echo "======================================"
                    echo " Stage 3: Trivy Dependency Scan"
                    echo "======================================"
                    echo "requirements.txt contents:"
                    cat requirements.txt

                    echo ""
                    echo "Running Trivy scan..."
                    docker run --rm \
                        -v $(pwd):/project \
                        aquasec/trivy:latest \
                        fs \
                        --scanners vuln \
                        --severity HIGH,CRITICAL \
                        --format table \
                        /project/requirements.txt || true

                    echo ""
                    echo "Saving JSON report..."
                    docker run --rm \
                        -v $(pwd):/project \
                        aquasec/trivy:latest \
                        fs \
                        --scanners vuln \
                        --severity HIGH,CRITICAL \
                        --format json \
                        --output /project/trivy-report.json \
                        /project/requirements.txt 2>/dev/null || true

                    echo ""
                    echo "======================================"
                    echo " Vulnerability Summary"
                    echo "======================================"
                    if [ -f trivy-report.json ]; then
                        python3 -c "
import json
with open('trivy-report.json') as f:
    data = json.load(f)
critical, high = [], []
for result in data.get('Results', []):
    for v in (result.get('Vulnerabilities') or []):
        sev = v.get('Severity','')
        entry = f\"  {v.get('PkgName','?')} {v.get('InstalledVersion','?')} -> {v.get('FixedVersion','no fix')} | {v.get('VulnerabilityID','?')}\"
        if sev == 'CRITICAL': critical.append(entry)
        elif sev == 'HIGH': high.append(entry)
print(f'CRITICAL: {len(critical)}')
[print(c) for c in critical]
print(f'HIGH: {len(high)}')
[print(h) for h in high]
print(f'Total: {len(critical)+len(high)}')
"
                    else
                        echo "No JSON report generated"
                    fi
                    echo "======================================"
                    echo " Dependency scan complete"
                    echo "======================================"
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
            archiveArtifacts artifacts: '*.json',
                            allowEmptyArchive: true
        }
    }
}
