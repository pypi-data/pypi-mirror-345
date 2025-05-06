*** Settings ***
Documentation   Test CLI clean
...
...             This is a system test that runs the store setup, a dummy experiment and cleans it afterwards
...             to check whether the database was cleaned.

Library         String
Library         Process
Library         OperatingSystem
Library         ${CURDIR}${/}ConfigFileModifier.py
Suite Setup     Singularize Ports
Suite Teardown  Clean Files

*** Keywords ***
Clean Files
    Remove File                     ${TEMPDIR}${/}stdout*.txt
    Remove File                     ${TEMPDIR}${/}stderr*.txt
    Remove File                     ${TEMPDIR}${/}palaestrai.db
    Remove File                     ${TEMPDIR}${/}store-test.conf.yml
    Remove File                     ${TEMPDIR}${/}store-test-sqlite.yml

Singularize Ports
    ${LOGPORT}                      Evaluate    str(24243 + random.randrange(1000))
    ${EXECUTORPORT}                 Evaluate    str(24242 - random.randrange(1000))
    ${result}                       Run Process         palaestrai          runtime-config-show-default     stdout=${TEMPDIR}${/}stdout_conf_sigint.txt
    ${conf} =                       Replace String      ${result.stdout}     4242        ${EXECUTORPORT}
    ${conf} =                       Replace String      ${conf}     4243        ${LOGPORT}
    Create File                     ${TEMPDIR}${/}store-test.conf.yml        ${conf}

*** Test Cases ***
Run dummy experiment with SQLite, check for data then clean the database
    [Timeout]                       240
    ${db_file_path} =               prepare_for_sqlite_store_test   ${TEMPDIR}${/}store-test.conf.yml     ${TEMPDIR}${/}store-test-sqlite.yml      ${TEMPDIR}
    log                             SQLite store runtime configuration file created at: ${TEMPDIR}${/}store-test-sqlite.yml
    Log File                        ${TEMPDIR}${/}store-test-sqlite.yml
    ${result} =                     Run Process   palaestrai    -c  ${TEMPDIR}${/}store-test-sqlite.yml   database-create   stdout=${TEMPDIR}${/}stdout.txt     stderr=${TEMPDIR}${/}stderr.txt
    Log Many                        ${result.stdout}    ${result.stderr}
    Should Be Equal As Integers     ${result.rc}    0
    File Should Exist               ${db_file_path}
    ${result} =                     Run Process   sqlite3    ${db_file_path}   .dump     	stdout=${TEMPDIR}${/}stdout-sqlitedump.txt    stderr=${TEMPDIR}/stderr-sqlite3dump.txt
    Log Many                        ${result.stdout}    ${result.stderr}
    start process                   palaestrai    -c  ${TEMPDIR}${/}store-test-sqlite.yml   experiment-start    ${CURDIR}${/}..${/}fixtures${/}dummy_run.yml   stdout=${TEMPDIR}/stdout-sqlite3dummy.txt 	stderr=${TEMPDIR}/stderr-sqlite3dummy.txt
    ${result} =                     Wait For Process  timeout=180  on_timeout=kill
    Log Many                        ${result.stdout}    ${result.stderr}
    Should Be Equal As Integers     ${result.rc}    0
    File Should Exist               ${db_file_path}
    ${result} =                     Run Process     sqlite3     ${db_file_path}     SELECT COUNT(*) FROM experiments;
    Log Many                        ${result.stdout}    ${result.stderr}
    Should Be Equal As Integers     ${result.rc}    0
    Should Not Be Equal As Strings  ${result.stdout}    0
    Log Many                        ${result.stdout}    ${result.stderr}
    start process                   palaestrai    -c  ${TEMPDIR}${/}store-test-sqlite.yml   clean   ${CURDIR}${/}..${/}fixtures${/}dummy_run.yml   stdout=${TEMPDIR}/stdout-sqlite3dummy.txt 	stderr=${TEMPDIR}/stderr-sqlite3dummy.txt
    ${result} =                     Wait For Process  timeout=120  on_timeout=kill
    Should Be Equal As Integers     ${result.rc}    0
    File Should Exist               ${db_file_path}
    ${result} =                     Run Process     sqlite3     ${db_file_path}     SELECT COUNT(*) FROM experiments;
    log many                        ${result.stdout}    ${result.stderr}
    Should Be Equal As Integers     ${result.rc}    0
    Should Be Equal As Strings      ${result.stdout}    0
    start process                   palaestrai    -c  ${TEMPDIR}${/}store-test-sqlite.yml     experiment-start      ${CURDIR}${/}..${/}fixtures${/}dummy_run.yml   stdout=${TEMPDIR}/stdout-sqlite3dummy.txt 	stderr=${TEMPDIR}/stderr-sqlite3dummy.txt
    ${result} =                     Wait For Process  timeout=180  on_timeout=kill
    Log Many                        ${result.stdout}    ${result.stderr}
    Should Be Equal As Integers     ${result.rc}    0
    File Should Exist               ${db_file_path}
    ${result} =                     Run Process     sqlite3     ${db_file_path}     SELECT COUNT(*) FROM experiments;
    Log Many                        ${result.stdout}    ${result.stderr}
    Should Be Equal As Integers     ${result.rc}    0
    Should Not Be Equal As Strings  ${result.stdout}    0
    Log Many                        ${result.stdout}    ${result.stderr}
    start process                   palaestrai    -c  ${TEMPDIR}${/}store-test-sqlite.yml     clean     --experiment-id\=1     stdout=${TEMPDIR}/stdout-sqlite3dummy.txt 	stderr=${TEMPDIR}/stderr-sqlite3dummy.txt
    ${result} =                     Wait For Process  timeout=120  on_timeout=kill
    Should Be Equal As Integers     ${result.rc}    0
    File Should Exist               ${db_file_path}
    ${result} =                     Run Process     sqlite3     ${db_file_path}     SELECT COUNT(*) FROM experiments;
    log many                        ${result.stdout}    ${result.stderr}
    Should Be Equal As Integers     ${result.rc}    0
    Should Be Equal As Strings      ${result.stdout}    0
