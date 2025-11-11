pipeline {
    options {
        disableConcurrentBuilds(abortPrevious: true)
    }
    agent {
        docker {
            alwaysPull true
            image 'or/pipeline-router-runner:1.0.0'
            label 'RouterRunner'
            args '''
            --privileged
            -v /var/run/docker.sock:/var/run/docker.sock
            -u 0:0
            '''
        }
    }

    stages {
        stage('linting') {
            steps {
                script
                {
                    sh '''pip3 install ./router[dev]
                    cd router
                    ruff check
                    ruff format --check'''
                }
            }
        }
        stage('unittests') {
            steps {
                script
                {
                    sh '''pip3 install ./router[test]
                    cd router/functions_unittests
                    pytest'''
                }
            }
        }
    }

    post {
        success {
            echo "Mashallah ya habibi! Pipeline succeded!"
        }
        failure {
            echo "Your skills are Haram! Pipeline failed!"
        }
    }
}
