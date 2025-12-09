pipeline {
    agent any

    environment {
        PYTHON = 'python'
    }

    stages {
        stage('Checkout') {
            steps {
                echo "Checking out repository..."
                checkout scm
            }
        }

        stage('Setup venv') {
            steps {
                sh '''
                python -m venv venv
                . venv/bin/activate || source venv/bin/activate
                pip install --upgrade pip
                pip install -r requirements.txt
                '''
            }
        }

        stage('Run BDD tests') {
            steps {
                sh '''
                . venv/bin/activate || source venv/bin/activate
                python -m framework.core.runner
                '''
            }
        }
    }

    post {
        success {
            echo "✅ All tests passed!"
        }
        failure {
            echo "❌ Some tests failed. Check console output."
        }
    }
}
 