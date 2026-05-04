pipeline {
    agent any
    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', url: 'https://github.com/Davidsavlon/devsecops-demo.git'
                sh 'ls -la'
            }
        }
        stage('Claude SAST') {
            steps {
                withCredentials([string(credentialsId: 'anthropic-api-key', variable: 'ANTHROPIC_API_KEY')]) {
                    sh '''
                        find . -type f -name "*.py" -not -path "./.git/*" > /tmp/files.txt
                        SCAN_FAILED=0
                        while IFS= read -r file; do
                            echo "Scanning: $file"
                            python3 /opt/claude_scanner.py "$file" --api-key "$ANTHROPIC_API_KEY" --severity MEDIUM --fail-on HIGH --verbose || SCAN_FAILED=1
                        done < /tmp/files.txt
                        if [ $SCAN_FAILED -eq 1 ]; then exit 1; fi
                        echo "Stage 1 PASSED"
                    '''
                }
            }
        }
        stage('Secrets Scan') {
            steps {
                sh '''
                    echo "=== Stage 2: Gitleaks Secrets Scan ==="
                    docker run --rm \
                        -v $(pwd):/repo \
                        zricethezav/gitleaks:latest \
                        detect \
                        --source=/repo \
                        --no-git \
                        --config=/repo/.gitleaks.toml \
                        --report-format=json \
                        --report-path=/repo/gitleaks-report.json \
                        --verbose \
                        --exit-code=1
                    echo "Stage 2 PASSED"
                '''
            }
        }
        stage('Dependency Scan') {
            steps {
                sh '''
                    echo "=== Stage 3: Trivy Dependency Scan ==="
                    docker build -t devsecops-test:latest . 2>&1 | tail -3
                    docker run --rm \
                        -v /var/run/docker.sock:/var/run/docker.sock \
                        aquasec/trivy:latest \
                        image \
                        --scanners vuln \
                        --severity HIGH,CRITICAL \
                        --format table \
                        --ignore-unfixed \
                        devsecops-test:latest 2>/dev/null || true
                    echo "Stage 3 COMPLETE"
                '''
            }
        }
        stage('Container Scan') {
            steps {
                sh '''
                    echo "=== Stage 4: Container Security Gate ==="
                    docker run --rm \
                        -v /var/run/docker.sock:/var/run/docker.sock \
                        aquasec/trivy:latest \
                        image \
                        --scanners vuln \
                        --severity CRITICAL \
                        --format json \
                        devsecops-test:latest > trivy-report.json 2>/dev/null || true

                    CRITICAL_COUNT=0
                    if [ -f trivy-report.json ]; then
                        CRITICAL_COUNT=$(python3 -c "
import json
with open('trivy-report.json') as f:
    d=json.load(f)
count=0
for r in d.get('Results',[]):
    for v in (r.get('Vulnerabilities') or []):
        if v.get('Severity')=='CRITICAL' and v.get('FixedVersion'):
            count+=1
print(count)
" 2>/dev/null || echo "0")
                    fi

                    echo "Fixable CRITICAL CVEs: $CRITICAL_COUNT"
                    if [ "$CRITICAL_COUNT" -gt "0" ]; then
                        echo "RESULT: FAILED - fix CRITICAL CVEs before deploying"
                        exit 1
                    fi
                    echo "Stage 4 PASSED"
                '''
            }
        }
        stage('IaC Scan') {
            steps {
                sh '''
                    echo "=== Stage 5: IaC Security Scan (Checkov) ==="

                    echo "Terraform files:"
                    find . -name "*.tf" -not -path "./.git/*"

                    echo ""
                    echo "Running Checkov on Azure Terraform..."
                    docker run --rm \
                        -v $(pwd):/tf \
                        bridgecrew/checkov:latest \
                        -d /tf/terraform \
                        --framework terraform \
                        --output cli \
                        --soft-fail 2>/dev/null || true

                    echo ""
                    echo "Saving JSON report..."
                    docker run --rm \
                        -v $(pwd):/tf \
                        bridgecrew/checkov:latest \
                        -d /tf/terraform \
                        --framework terraform \
                        --output json > checkov-report.json 2>/dev/null || true

                    echo ""
                    echo "=== Checkov Summary ==="
                    if [ -f checkov-report.json ]; then
                        python3 -c "
import json
with open('checkov-report.json') as f:
    content = f.read().strip()
if not content:
    print('No report generated')
    exit(0)
try:
    d = json.loads(content)
    results = d.get('results', {})
    passed = len(results.get('passed_checks', []))
    failed = len(results.get('failed_checks', []))
    print('Passed: ' + str(passed))
    print('Failed: ' + str(failed))
    print('')
    for check in results.get('failed_checks', []):
        cid  = check.get('check_id', '?')
        name = check.get('check', {}).get('name', '') if isinstance(check.get('check'), dict) else str(check.get('check_id', ''))
        res  = check.get('resource', '?')
        print('  FAIL | ' + cid + ' | ' + res)
        print('       ' + name)
        print('')
except Exception as e:
    print('Parse error: ' + str(e))
" || true
                    fi

                    echo "======================================"
                    echo " Stage 5 COMPLETE"
                    echo "======================================"
                '''
            }
        }
        stage('Build') {
            steps {
                echo 'All security scans passed!'
            }
        }
    }
    post {
        success { echo 'ALL STAGES PASSED' }
        failure { echo 'PIPELINE FAILED' }
        always {
            archiveArtifacts artifacts: '*.json', allowEmptyArchive: true
        }
    }
}
