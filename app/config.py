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

            echo "Stage 2 PASSED - no secrets found"
        '''
    }
}
