pipeline {
    agent any

    environment {
        VENV_DIR = 'venv'
    }

    stages {
        stage('Checkout') {
            steps {
                echo 'Checking out repository...'
                checkout scm
            }
        }

        stage('Setup venv') {
            steps {
                echo 'Creating virtualenv and installing dependencies...'
                bat '''
                echo [SETUP] Cleaning old venv (if exists)...
                if exist %VENV_DIR% rmdir /S /Q %VENV_DIR%

                echo [SETUP] Creating new virtual environment...
                python -m venv %VENV_DIR%

                echo [SETUP] Activating venv and installing requirements...
                call %VENV_DIR%\\Scripts\\activate.bat
                python -m pip install --upgrade pip
                pip install -r requirements.txt
                '''
            }
        }

        stage('Run BDD tests') {
            steps {
                echo 'Running BDD tests...'
                bat '''
                echo [TEST] Activating venv...
                call %VENV_DIR%\\Scripts\\activate.bat

                echo [TEST] Running framework.core.runner...
                python -m framework.core.runner
                '''
            }
        }
    }

    post {
        success {
            echo '✅ All BDD tests passed in Jenkins pipeline.'
        }
        failure {
            echo '❌ Some tests failed or pipeline error. Check console output.'
        }
        always {
            echo 'Archiving reports (if any)...'
            archiveArtifacts artifacts: 'reports/**/*.*', allowEmptyArchive: true
        }
    }
}
