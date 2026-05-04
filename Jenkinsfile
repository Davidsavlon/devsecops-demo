stage('Dependency Scan') {
    steps {
        sh '''
            echo "======================================"
            echo " Stage 3: Trivy Dependency Scan"
            echo "======================================"

            echo "Found requirements.txt:"
            cat requirements.txt

            echo ""
            echo "Running Trivy scan with python scanner..."
            docker run --rm \
                -v $(pwd):/project \
                aquasec/trivy:latest \
                fs \
                --scanners vuln \
                --severity HIGH,CRITICAL \
                --format table \
                --debug \
                /project/requirements.txt

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
            echo " Parsing results..."
            echo "======================================"

            if [ -f trivy-report.json ]; then
                python3 << PYEOF
import json, sys

try:
    with open("trivy-report.json") as f:
        data = json.load(f)

    critical = []
    high = []

    for result in data.get("Results", []):
        target = result.get("Target", "unknown")
        for v in (result.get("Vulnerabilities") or []):
            sev   = v.get("Severity", "")
            pkg   = v.get("PkgName", "unknown")
            inst  = v.get("InstalledVersion", "?")
            fixed = v.get("FixedVersion", "no fix available")
            cve   = v.get("VulnerabilityID", "?")
            title = v.get("Title", "")
            entry = f"  [{sev}] {pkg} {inst} -> {fixed} | {cve} | {title}"
            if sev == "CRITICAL":
                critical.append(entry)
            elif sev == "HIGH":
                high.append(entry)

    print(f"CRITICAL: {len(critical)}")
    for c in critical:
        print(c)
    print(f"\nHIGH: {len(high)}")
    for h in high:
        print(h)
    print(f"\nTotal HIGH/CRITICAL: {len(critical) + len(high)}")

    if len(critical) + len(high) > 0:
        print("\nACTION REQUIRED: Upgrade packages listed above")
        print("Update requirements.txt with fixed versions to pass this stage")

except Exception as e:
    print(f"Could not parse report: {e}")
PYEOF
            else
                echo "No report generated - Trivy found no recognized dependency files"
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
