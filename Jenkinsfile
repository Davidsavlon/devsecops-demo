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

                    echo "======================================"
                    echo " No secrets found - PASSED"
                    echo "======================================"
                '''
            }
            post {
                failure {
                    echo 'SECRETS DETECTED - fix before proceeding'
                }
            }
        }

        stage('Dependency Scan') {
            steps {
                sh '''
                    echo "======================================"
                    echo " Stage 3: Trivy Dependency Scan"
                    echo "======================================"

                    echo "Checking for requirements.txt..."
                    if [ -f requirements.txt ]; then
                        echo "Found requirements.txt:"
                        cat requirements.txt
                    else
                        echo "No requirements.txt found"
                    fi

                    echo ""
                    echo "Running Trivy filesystem scan..."
                    docker run --rm \
                        -v $(pwd):/project \
                        aquasec/trivy:latest \
                        fs \
                        --security-checks vuln \
                        --severity HIGH,CRITICAL \
                        --format table \
                        /project

                    echo ""
                    echo "Saving detailed JSON report..."
                    docker run --rm \
                        -v $(pwd):/project \
                        aquasec/trivy:latest \
                        fs \
                        --security-checks vuln \
                        --severity HIGH,CRITICAL \
                        --format json \
                        --output /project/trivy-report.json \
                        /project 2>/dev/null || true

                    echo ""
                    echo "======================================"
                    echo " Parsing vulnerability summary..."
                    echo "======================================"

                    if [ -f trivy-report.json ]; then
                        python3 << PYEOF
import json

with open("trivy-report.json") as f:
    data = json.load(f)

critical = []
high = []

for result in data.get("Results", []):
    for v in (result.get("Vulnerabilities") or []):
        sev = v.get("Severity", "")
        pkg = v.get("PkgName", "unknown")
        installed = v.get("InstalledVersion", "?")
        fixed = v.get("FixedVersion", "no fix available")
        cve = v.get("VulnerabilityID", "?")
        entry = f"  {pkg} {installed} -> upgrade to: {fixed} ({cve})"
        if sev == "CRITICAL":
            critical.append(entry)
        elif sev == "HIGH":
            high.append(entry)

print(f"CRITICAL vulnerabilities: {len(critical)}")
for c in critical:
    print(c)

print(f"\nHIGH vulnerabilities: {len(high)}")
for h in high:
    print(h)

print(f"\nTotal HIGH/CRITICAL: {len(critical) + len(high)}")

if len(critical) > 0:
    print("\nACTION REQUIRED: Update packages to fix CRITICAL vulnerabilities")
PYEOF
                    fi

                    echo "======================================"
                    echo " Dependency scan complete"
                    echo "======================================"
                '''
            }
            post {
                always {
                    archiveArtifacts artifacts: 'trivy-report.json',
                                    allowEmptyArchive: true
                }
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
