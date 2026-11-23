pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds()
    }

    environment {
        APP_PORT = '5000'
        APP_URL = "http://localhost:5000"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Start containers') {
            steps {
                script {
                    if (isUnix()) {
                        sh '''
                            set -e
                            docker compose down --remove-orphans || true
                            docker compose up -d
                        '''
                    } else {
                        // Clean up any previous stack, then start services in detached mode.
                        bat(returnStatus: true, script: 'docker compose down --remove-orphans')
                        bat 'docker compose up -d'
                    }
                }
            }
        }

        stage('Wait for web app') {
            steps {
                script {
                    // The web container installs Python dependencies on startup, so allow enough time.
                    if (isUnix()) {
                        sh '''
                            set -e
                            echo "Waiting for ${APP_URL} ..."
                            for i in $(seq 1 60); do
                                if curl -fsS "${APP_URL}/" >/dev/null; then
                                    echo "Web app is ready."
                                    exit 0
                                fi
                                echo "Attempt $i/60: web app not ready yet"
                                sleep 5
                            done
                            echo "Web app did not become ready in time."
                            docker compose ps || true
                            docker compose logs --tail=200 || true
                            exit 1
                        '''
                    } else {
                        powershell '''
                            $ErrorActionPreference = "Stop"
                            $url = "$env:APP_URL/"
                            Write-Host "Waiting for $url ..."
                            $ready = $false

                            for ($i = 1; $i -le 60; $i++) {
                                try {
                                    $response = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 5
                                    if ($response.StatusCode -ge 200 -and $response.StatusCode -lt 500) {
                                        Write-Host "Web app is ready."
                                        $ready = $true
                                        break
                                    }
                                } catch {
                                    Write-Host "Attempt $i/60: web app not ready yet"
                                }
                                Start-Sleep -Seconds 5
                            }

                            if (-not $ready) {
                                Write-Host "Web app did not become ready in time."
                                docker compose ps
                                docker compose logs --tail=200
                                exit 1
                            }
                        '''
                    }
                }
            }
        }

        stage('Verify web page') {
            steps {
                script {
                    if (isUnix()) {
                        sh '''
                            set -e
                            docker compose ps
                            echo "---- Web page preview ----"
                            curl -fsS "${APP_URL}/" | sed -n '1,20p' || true
                            echo "--------------------------"
                            echo "Application is running."
                            echo "Open in browser: ${APP_URL}"
                            echo "If Jenkins runs on a remote agent, use that agent's hostname/IP instead of localhost and ensure port ${APP_PORT} is reachable."
                        '''
                    } else {
                        powershell '''
                            docker compose ps
                            Write-Host "---- Web page preview ----"
                            try {
                                $content = (Invoke-WebRequest -Uri "$env:APP_URL/" -UseBasicParsing -TimeoutSec 10).Content
                                $content -split "`r?`n" | Select-Object -First 20
                            } catch {
                                Write-Host "Could not fetch page preview: $($_.Exception.Message)"
                            }
                            Write-Host "--------------------------"
                            Write-Host "Application is running."
                            Write-Host "Open in browser: $env:APP_URL"
                            Write-Host "If Jenkins runs on a remote agent, use that agent's hostname/IP instead of localhost and ensure port $env:APP_PORT is reachable."
                        '''
                    }
                }
            }
        }
    }

    post {
        failure {
            script {
                if (isUnix()) {
                    sh 'docker compose ps || true'
                    sh 'docker compose logs --tail=200 || true'
                } else {
                    bat 'docker compose ps'
                    bat 'docker compose logs --tail=200'
                }
            }
        }
        success {
            echo "Containers are left running so the web page remains available. Run 'docker compose down' on the agent to stop them when finished."
        }
    }
}
