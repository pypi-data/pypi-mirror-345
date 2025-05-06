*** Settings ***
Documentation   Run palaestrAI from Jupyter Notebooks
...
...             The Jupyter Notebook kernel is a special environment for
...             palaestrAI to run it. This system test will run
...             jupyter nbconvert --execute for a given iPython notebook in
...             which a palaestrAI experiment is executed.

Library         Process
Library         OperatingSystem
# Suite Teardown  Clean Files

*** Keywords ***
Clean Files
    Remove File                     ${TEMPDIR}${/}stdout.txt
    Remove File                     ${TEMPDIR}${/}stderr.txt
    Remove File                     ${CURDIR}${/}tictactoe_integrationtest_palaestrai.html

*** Test Cases ***
check existing palaestrai modules
    ${pip_show_output} =            Run Process     pip  show  palaestrai  palaestrai-environments  palaestrai-agents
    Log Many                        ${pip_show_output.stderr}
    Log Many                        ${pip_show_output.stdout}
    Should Be Equal As Integers     ${pip_show_output.rc}   0
    Should Not Contain              ${pip_show_output.stderr}   WARNING
    Should Not Contain              ${pip_show_output.stderr}   Package(s) not found
    Should Not Contain              ${pip_show_output.stderr}   CRITICAL|ERROR
    Should Not Contain              ${pip_show_output.stderr}   CRITICAL|ERROR   

tic-tac-toe experiment run from a Jupyter Notebook  
    ${result} =                     Run Process  jupyter  nbconvert  --to  html  --execute  ${CURDIR}${/}..${/}..${/}doc${/}tutorials${/}01-tic-tac-toe_experiment.ipynb  stdout=${TEMPDIR}${/}stdout.txt  stderr=${TEMPDIR}${/}stderr.txt
    Log Many                        ${result.stdout}    ${result.stderr}
    Should Not Contain              ${result.stderr}   CRITICAL|ERROR
    Should Not Contain              ${result.stdout}   CRITICAL|ERROR     
    Should Be Equal As Integers     ${result.rc}   0
    File Should Exist               ${CURDIR}${/}..${/}..${/}doc${/}tutorials${/}01-tic-tac-toe_experiment.html