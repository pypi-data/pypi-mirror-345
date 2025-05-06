*** Settings ***
Documentation   Test handling of single line execution
...
...             This calls the single line execution with the dummy experiment.
...             The test then monitors that the execution returns 0.

Library         Process
Library         OperatingSystem
Library         String
Library         ${CURDIR}${/}ConfigFileModifier.py
Suite Setup     Prepare Configuration
Suite Teardown  Clean Files

*** Keywords ***
Clean Files
    Remove File                     ${TEMPDIR}${/}stdout_single_line.txt
    Remove File                     ${TEMPDIR}${/}stderr_single_line.txt
    Remove File                     ${TEMPDIR}${/}runtime_conf_single_line.yaml
    Remove File                     ${TEMPDIR}${/}stdout_conf_single_line.txt
    Remove File                     ${db_file_path}

Prepare Configuration
    ${LOGPORT}                      Evaluate    str(24243 + random.randrange(1000 * (${PABOTQUEUEINDEX}+1)))
    ${EXECUTORPORT}                 Evaluate    str(24242 - random.randrange(1000 * (${PABOTQUEUEINDEX}+1)))
    ${result}                       Run Process  palaestrai  runtime-config-show-default  stdout=${TEMPDIR}${/}stdout_conf_single_line.txt
    ${conf} =                       Replace String  ${result.stdout}  4242  ${EXECUTORPORT}
    ${conf} =                       Replace String  ${conf}  4243  ${LOGPORT}
    Create File                     ${TEMPDIR}${/}runtime_conf_single_line.yaml        ${conf}
    ${db_file_path} =               prepare_for_sqlite_store_test   ${TEMPDIR}${/}runtime_conf_single_line.yaml  ${TEMPDIR}${/}runtime_conf_single_line.yaml  ${TEMPDIR}
    Set Suite Variable              $db_file_path
    ${result} =                     Run Process   palaestrai    -c  ${TEMPDIR}${/}runtime_conf_single_line.yaml  database-create   stdout=${TEMPDIR}${/}stdout_single_line.txt  stderr=${TEMPDIR}${/}stderr_single_line.txt
    Log Many                        ${result.stdout}    ${result.stderr}
    Should Be Equal As Integers     ${result.rc}    0

*** Test Cases ***
Call single line execution with the dummy experiment file.
    [Timeout]                       240
    ${result} =                     Run Process  python3  ${CURDIR}${/}..${/}fixtures${/}single_line_test.py    ${CURDIR}${/}..${/}fixtures${/}dummy_run.yml      ${TEMPDIR}${/}runtime_conf_single_line.yaml  stdout=${TEMPDIR}${/}stdout_single_line.txt  stderr=${TEMPDIR}${/}stderr_single_line.txt
    Log Many                        ${result.stdout}  ${result.stderr}
    Should Be Equal As Integers     ${result.rc}  0
