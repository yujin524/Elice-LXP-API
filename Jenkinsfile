pipeline {
    agent any

    options {
        gitLabConnection('GitLab-integration')
        // MR에서는 develop이 아니라 MR 소스 브랜치를 직접 checkout하기 위해 자동 checkout을 끕니다.
        skipDefaultCheckout(true)
        // 동일한 Jenkins Job의 빌드가 겹치면 새 빌드는 기존 빌드가 끝날 때까지 대기합니다.
        disableConcurrentBuilds()
    }

    environment {
        RUN_LIVE_API_TESTS = '1'
        DISCORD_WEBHOOK_URL = credentials('discord-webhook-url')
        ELICE_ID = credentials('elice-id')
        ELICE_PW = credentials('elice-pw')
        API_BASE_URL = credentials('api-base-url')
        REST_BASE_URL = credentials('rest-base-url')
        COURSE_BASE_URL = credentials('course-base-url')
        DASHBOARD_BASE_URL = credentials('dashboard-base-url')
        AUTH_URL = credentials('auth-url')
        DISCORD_TEAM_NAME = 'team-3'
        DISCORD_PROJECT_NAME = '200_project'
        SLACK_TEAM_NAME = 'team-3'
        SLACK_PROJECT_NAME = '200_project'
    }

    stages {
        stage('Checkout') {
            steps {
                script {
                    boolean isMergeRequest = env.gitlabActionType == 'MERGE' || env.gitlabMergeRequestIid?.trim()

                    if (isMergeRequest) {
                        String sourceBranch = env.gitlabSourceBranch?.trim()
                        String sourceRevision = env.gitlabMergeRequestLastCommit?.trim()

                        if (!sourceBranch) {
                            error('GitLab MR 소스 브랜치(gitlabSourceBranch)를 확인할 수 없습니다.')
                        }

                        echo "MR 사전 검증: ${sourceBranch} -> ${env.gitlabTargetBranch ?: 'develop'}"
                        echo "MR 번호: ${env.gitlabMergeRequestIid ?: '확인 불가'}"

                        checkout([
                            $class: 'GitSCM',
                            branches: [[name: sourceRevision ?: "*/${sourceBranch}"]],
                            userRemoteConfigs: scm.userRemoteConfigs
                        ])

                        sh 'git rev-parse HEAD'
                        updateGitlabCommitStatus name: 'mr-static-check', state: 'running'
                    } else {
                        checkout scm
                    }
                }
            }
        }

        stage('Install dependencies') {
            steps {
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }

        stage('MR static check') {
            when {
                expression {
                    env.gitlabActionType == 'MERGE' || env.gitlabMergeRequestIid?.trim()
                }
            }
            steps {
                sh '''
                    . venv/bin/activate
                    ruff check conftest.py config apis utils tests \
                        --select E9,F63,F7,F82
                '''
            }
        }

        stage('MR pytest collection check') {
            when {
                expression {
                    env.gitlabActionType == 'MERGE' || env.gitlabMergeRequestIid?.trim()
                }
            }
            steps {
                sh '''
                    . venv/bin/activate
                    pytest --collect-only --strict-markers -q \
                        -p no:tests.api.plugins.api_reporting \
                        -o addopts="-q -p no:cacheprovider --import-mode=importlib"
                '''
            }
        }

        stage('MR fixture setup plan') {
            when {
                expression {
                    env.gitlabActionType == 'MERGE' || env.gitlabMergeRequestIid?.trim()
                }
            }
            environment {
                // 실제 fixture를 실행하지 않고, prod 안전 Skip 대상까지 포함한 의존 관계만 검사합니다.
                TEST_ENV = 'dev'
                ALLOW_PROD_AUTHZ_MUTATION_TESTS = '1'
            }
            steps {
                sh '''
                    . venv/bin/activate
                    set +e
                    pytest --setup-plan --strict-markers -q \
                        -p no:tests.api.plugins.api_reporting \
                        -o addopts="-q -p no:cacheprovider --import-mode=importlib" \
                        > mr-fixture-plan.txt 2>&1
                    status=$?
                    if [ $status -ne 0 ]; then
                        cat mr-fixture-plan.txt
                    fi
                    exit $status
                '''
            }
        }

        stage('Run API tests (prod)') {
            when {
                expression {
                    !(env.gitlabActionType == 'MERGE' || env.gitlabMergeRequestIid?.trim())
                }
            }
            steps {
                catchError(buildResult: 'FAILURE', stageResult: 'FAILURE') {
                    sh '''
                        rm -rf reports
                        rm -rf logs
                        . venv/bin/activate
                        set +e
                        pytest --ignore=tests/unit \
                            -o log_file=logs/api-tests-prod.log \
                            --ignore=tests/api/course_edu \
                            --ignore=tests/api/classroom_edu \
                            --ignore=tests/api/board \
                            --ignore=tests/api/schedule/positive/test_edit_schedule.py \
                            --ignore=tests/api/schedule/positive/test_delete_schedule.py \
                            --ignore=tests/api/schedule/validation/test_edit_schedule.py \
                            --ignore=tests/api/schedule/validation/test_delete_schedule.py \
                            --ignore=tests/api/schedule/positive/test_post_schedule.py \
                            --ignore=tests/api/schedule/authentication/test_post_schedule.py \
                            --ignore=tests/api/schedule/validation/test_post_schedule.py \
                            --ignore=tests/api/schedule/scenario/test_schedule_create_read_delete.py
                        status=$?
                        mv reports/api-summary.json reports/api-summary-prod.json
                        exit $status
                    '''
                }
            }
        }

        stage('Run dev-only tests (dev)') {
            when {
                expression {
                    !(env.gitlabActionType == 'MERGE' || env.gitlabMergeRequestIid?.trim())
                }
            }
            environment {
                TEST_ENV = 'dev'
                ELICE_ID = credentials('dev-elice-id')
                ELICE_PW = credentials('dev-elice-pw')
                LEARNER_ID = credentials('dev-learner-id')
                LEARNER_PW = credentials('dev-learner-pw')
                DEV_EDUCATOR_A_ID = credentials('DEV_EDUCATOR_A_ID')
                DEV_EDUCATOR_A_PW = credentials('DEV_EDUCATOR_A_PW')
                DEV_EDUCATOR_B_ID = credentials('DEV_EDUCATOR_B_ID')
                DEV_EDUCATOR_B_PW = credentials('DEV_EDUCATOR_B_PW')
                DEV_LEARNER_A_ID = credentials('DEV_LEARNER_A_ID')
                DEV_LEARNER_A_PW = credentials('DEV_LEARNER_A_PW')
                DEV_LEARNER_B_ID = credentials('DEV_LEARNER_B_ID')
                DEV_LEARNER_B_PW = credentials('DEV_LEARNER_B_PW')
                DEV_OUTSIDER_ID = credentials('DEV_OUTSIDER_ID')
                DEV_OUTSIDER_PW = credentials('DEV_OUTSIDER_PW')
                AUTHZ_CLASSROOM_ID = credentials('AUTHZ_CLASSROOM_ID')
                API_BASE_URL = credentials('dev-api-base-url')
                REST_BASE_URL = credentials('dev-rest-base-url')
                EDU_REST_BASE_URL = credentials('dev-rest-base-url')
                DASHBOARD_BASE_URL = credentials('dev-dashboard-base-url')
                AUTH_URL = credentials('dev-auth-url')
                ELICE_ORG_NAME_SHORT = 'academy'
                CLASSROOM_LOOKUP_MODE = 'available'
                CLASSROOM_REQUIRE_OPENED = 'true'
                CLASSROOM_REQUIRE_COURSE = 'true'
            }
            steps {
                // --clean-alluredir을 빼서 prod 스테이지가 쓴 allure-results를 지우지 않고 이어서 쌓는다.
                sh '''
                    . venv/bin/activate
                    pytest tests/api/course_edu \
                        tests/api/classroom_edu \
                        tests/api/board \
                        tests/api/schedule/positive/test_edit_schedule.py \
                        tests/api/schedule/positive/test_delete_schedule.py \
                        tests/api/schedule/validation/test_edit_schedule.py \
                        tests/api/schedule/validation/test_delete_schedule.py \
                        tests/api/schedule/positive/test_post_schedule.py \
                        tests/api/schedule/authentication/test_post_schedule.py \
                        tests/api/schedule/validation/test_post_schedule.py \
                        tests/api/schedule/scenario/test_schedule_create_read_delete.py \
                        -o addopts="-v -s -p no:cacheprovider --import-mode=importlib --alluredir=allure-results --tb=short --show-capture=no" \
                        -o log_file=logs/api-tests-dev.log
                '''
            }
        }
    }

    post {
        always {
            script {
                boolean isMergeRequest = env.gitlabActionType == 'MERGE' || env.gitlabMergeRequestIid?.trim()

                if (isMergeRequest) {
                    echo 'MR 사전 검증 빌드이므로 API Allure 리포트와 Discord/Slack 알림을 생성하지 않습니다.'
                } else {
                    env.GIT_BRANCH_NAME = (env.GIT_BRANCH ?: env.BRANCH_NAME ?: 'develop').replaceFirst('^origin/', '')
                    env.GIT_AUTHOR_NAME = sh(script: 'git log -1 --pretty=%an', returnStdout: true).trim()
                    env.GIT_COMMIT_MESSAGE = sh(script: 'git log -1 --pretty=%s', returnStdout: true).trim()
                    env.ALLURE_REPORT_URL = "${env.BUILD_URL}allure/"

                    allure includeProperties: false, jdk: '', results: [[path: 'allure-results']]
                    archiveArtifacts artifacts: 'logs/*.log', allowEmptyArchive: true

                    sh '''
                        . venv/bin/activate
                        python utils/notifyscripts/notify_discord.py
                    '''

                    try {
                        withCredentials([
                            string(
                                credentialsId: 'slack-webhook-url',
                                variable: 'SLACK_WEBHOOK_URL'
                            )
                        ]) {
                            sh '''
                                . venv/bin/activate
                                python utils/notifyscripts/notify_slack.py
                            '''
                        }
                    } catch (Exception ignored) {
                        echo 'Slack Credential 또는 알림 전송을 확인해 주세요. Slack 알림을 건너뜁니다.'
                    }

                    try {
                        withCredentials([
                            string(
                                credentialsId: 'gitlab-issue-bot-token',
                                variable: 'GITLAB_API_TOKEN'
                            )
                        ]) {
                            sh '''
                                . venv/bin/activate
                                python utils/notifyscripts/notify_gitlab_issue.py
                            '''
                        }
                    } catch (Exception e) {
                        echo "GitLab 이슈 자동 등록을 건너뜁니다 (credential 미등록 또는 스크립트 오류): ${e.getMessage()}"
                    }
                }
            }
        }
        success {
            script {
                if (env.gitlabActionType == 'MERGE' || env.gitlabMergeRequestIid?.trim()) {
                    updateGitlabCommitStatus name: 'mr-static-check', state: 'success'
                }
            }
        }
        failure {
            script {
                if (env.gitlabActionType == 'MERGE' || env.gitlabMergeRequestIid?.trim()) {
                    updateGitlabCommitStatus name: 'mr-static-check', state: 'failed'
                }
            }
        }
        aborted {
            script {
                if (env.gitlabActionType == 'MERGE' || env.gitlabMergeRequestIid?.trim()) {
                    updateGitlabCommitStatus name: 'mr-static-check', state: 'canceled'
                }
            }
        }
    }
}
