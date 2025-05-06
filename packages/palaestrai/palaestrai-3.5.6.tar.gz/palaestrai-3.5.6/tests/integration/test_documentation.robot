*** Settings ***
Documentation    Build the documentation and checks for document sanity

Library         Process
Library         OperatingSystem
Library         tempfile

Test Setup      Create Tempdir
Test Teardown   Cleanup Tempdir
Suite Teardown  Clean Files

*** Keywords ***
Create Tempdir
    ${sphinx_out_dir} =             tempfile.mkdtemp  dir=${TEMPDIR}
    Set Environment Variable        sphinx_out_dir  ${sphinx_out_dir}

Cleanup Tempdir
    Remove Directory                %{sphinx_out_dir}  recursive=True

Clean Files
    Remove File                     ${TEMPDIR}${/}stdout_doc.txt
    Remove File                     ${TEMPDIR}${/}stderr_doc.txt

*** Test Cases ***
Sphinx build
    Skip If                         1   "Skipped, because the documentation is built separately."
    Start Process                   sphinx-build  -v  -a  ${CURDIR}${/}..${/}..${/}doc  %{sphinx_out_dir}  stdout=${TEMPDIR}${/}stdout_doc.txt  stderr=${TEMPDIR}${/}stderr_doc.txt  alias=sphinx
    ${result} =                     Wait For Process  handle=sphinx  timeout=300  on_timeout=kill
    Log Many                        ${result.stdout}  ${result.stderr}
    Should Not Contain              ${result.stderr}    CRITICAL|ERROR
    Should Not Contain              ${result.stdout}    CRITICAL|ERROR  
    Should Be Equal As Integers     ${result.rc}  0
    File Should Exist               %{sphinx_out_dir}${/}index.html
    File Should Exist               %{sphinx_out_dir}${/}_images${/}store_er_diagram.png
