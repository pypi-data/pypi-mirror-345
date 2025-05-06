*** Settings ***
Documentation   Check provided database for run experiments.
...

Library         Process
Library         OperatingSystem
Suite Teardown   Clean Files

*** Keywords ***
Clean Files
    Remove File                     ${TEMPDIR}${/}stdout_experiment_list.txt
    Remove File                     ${TEMPDIR}${/}stderr_experiment_list.txt

*** Test Cases ***
Check dummy experiment database for experiment tables.
    ${result} =                     Run Process         palaestrai     experiment-list     --database     sqlite:///${CURDIR}${/}..${/}fixtures${/}dummy_database.db    stdout=${TEMPDIR}${/}stdout_experiment_list.txt 	stderr=${TEMPDIR}${/}stderr_experiment_list.txt
    Log Many                        ${result.stdout}    ${result.stderr}
    Should Be Equal As Integers     ${result.rc}   0
