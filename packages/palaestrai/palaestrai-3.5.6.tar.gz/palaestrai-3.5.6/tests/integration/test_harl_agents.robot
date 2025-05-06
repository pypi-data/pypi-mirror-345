*** Settings ***
Documentation   Integrationtest harl agents
...
...             PalaestrAI has a sister package 'harl' in which
...             RL agents are implemented. This test case runs
...             the dummy experiment files provided by these agents
...             to make sure all api breaking changes are caught.

Library         Process
Library         OperatingSystem
Suite Teardown  Clean Files
Suite Setup     Pull Harl

*** Keywords ***
Clean Files
    Remove File                     ${TEMPDIR}${/}stdout.txt
    Remove File                     ${TEMPDIR}${/}stderr.txt
    Remove Directory                ${TEMPDIR}${/}harl      recursive=true

Pull Harl
    Directory Should Not Exist      ${TEMPDIR}${/}harl
    Run Process                     git     clone      -b       carl-paper       https://gitlab.com/arl2/harl.git       ${TEMPDIR}${/}harl
    Directory Should Exist          ${TEMPDIR}${/}harl/tests/harl/fixtures

*** Test Cases ***
Test agents with dummy experiment file
    [Teardown]                      Clean Files
    [Timeout]                       120
    Skip                            Skipped until hARL contains only working agents again.
    @{paths} =                      List Files In Directory     ${TEMPDIR}${/}harl/tests/harl/fixtures       pattern=*.yml       absolute=true
    FOR     ${path}     IN      @{paths}
        ${result} =                     Run Process    palaestrai           experiment-start         ${path}       stdout=${TEMPDIR}${/}stdout.txt    stderr=${TEMPDIR}${/}stderr.txt
        Log Many                        ${result.stdout}    ${result.stderr}
        Should Not Contain              ${result.stderr}    CRITICAL|ERROR
        Should Not Contain              ${result.stdout}    CRITICAL|ERROR  
        Should Be Equal As Integers     ${result.rc}    0
    END


