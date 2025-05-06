*** Settings ***
Documentation   Test handling of Ctrl+C (SIGINT)
...
...             This runs the system with the dummy experiment, but hits Ctrl+C after a short amount of time.
...             The test then monitors that everything exists smoothly.
...             There are several test cases that interrupt the running process after different amounts of time.

Library         Process
Library         OperatingSystem
Library         String
Suite Teardown  Clean Files

*** Keywords ***
Clean Files
    Remove File                     stdout.txt
    Remove File                     ${TEMPDIR}${/}stdout_conf_sigint.txt
    Remove File                     ${TEMPDIR}${/}runtime_conf_sigint.yaml

Singularize Ports
    ${LOGPORT}                      Evaluate    str(24243 + random.randrange(1000 * (${PABOTQUEUEINDEX}+1)))
    ${EXECUTORPORT}                 Evaluate    str(24242 - random.randrange(1000 * (${PABOTQUEUEINDEX}+1)))
    ${result}                       Run Process         palaestrai          runtime-config-show-default     stdout=${TEMPDIR}${/}stdout_conf_sigint.txt
    ${conf} =                       Replace String      ${result.stdout}     4242        ${EXECUTORPORT}
    ${conf} =                       Replace String      ${conf}     4243        ${LOGPORT}
    Create File                     ${TEMPDIR}${/}runtime_conf_sigint.yaml        ${conf}

*** Test Cases ***
Interrupt palaestrai-experiment with the dummy test after 6 seconds.
    [Setup]                         Singularize Ports
    ${result} =                     Run Process  bash  ${CURDIR}/sigint_test_runner.sh  6  -c  ${TEMPDIR}${/}runtime_conf_sigint.yaml  stdout=stdout.txt  stderr=STDOUT  timeout=90s  on_timeout=kill
    Log                             ${result.stdout}
    ${match} =                      Should Match Regexp  ${result.stdout}   palaestrAI executor has received signal (Signals\.SIGINT|2), shutting down
    #Should Be Equal As Integers     ${result.rc}  254
    [Teardown]                      Clean Files

Interrupt palaestrai-experiment with the dummy test after 14 seconds.
    [Setup]                         Singularize Ports
    ${result} =                     Run Process  bash  ${CURDIR}/sigint_test_runner.sh  14  -c  ${TEMPDIR}${/}runtime_conf_sigint.yaml  stdout=stdout.txt  stderr=STDOUT  timeout=90s  on_timeout=kill
    Log                             ${result.stdout}
    ${match} =                      Should Match Regexp  ${result.stdout}  palaestrAI executor has received signal (Signals\.SIGINT|2), shutting down
    #Should Be Equal As Integers     ${result.rc}  254
    [Teardown]                      Clean Files

Interrupt palaestrai-experiment with the dummy test after 18 seconds.
    [Setup]                         Singularize Ports
    ${result} =                     Run Process  bash  ${CURDIR}/sigint_test_runner.sh  18  -c  ${TEMPDIR}${/}runtime_conf_sigint.yaml  stdout=stdout.txt  stderr=STDOUT  timeout=90s  on_timeout=kill
    Log                             ${result.stdout}
    ${match} =                      Should Match Regexp  ${result.stdout}    palaestrAI executor has received signal (Signals\.SIGINT|2), shutting down
    #Should Be Equal As Integers     ${result.rc}  254
    [Teardown]                      Clean Files
