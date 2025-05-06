*** Settings ***
Documentation   Test Dummy Run
...
...             Exercises the fully dummy run, checking for all sorts of
...             details of the run execution. It does not check for results
...             storage explicitly, but will make sure that all log outputs
...             indicate a safe, successful and complete execution of the
...             dummy experiment run.

Library         String
Library         Process
Library         OperatingSystem
Library         ${CURDIR}${/}ConfigFileModifier.py
Test Setup      Create Config Files

*** Variables ***
${stdout_file} =            ${TEMPDIR}${/}dummy_experiment.stdout
${stderr_file} =            ${TEMPDIR}${/}dummy_experiment.stderr

*** Keywords ***
Create Config Files
    ${result} =                     Run Process  palaestrai  runtime-config-show-default  stdout=runtime_config_file-dummyrun.yml
    ${queueidx} =                   Get Variable Value  ${PABOTQUEUEINDEX}  0
    ${LOGPORT}                      Evaluate  str(24243 + random.randrange(1000 * (${PABOTQUEUEINDEX}+1)))
    ${EXECUTORPORT}                 Evaluate  str(24242 - random.randrange(1000 * (${PABOTQUEUEINDEX}+1)))
    ${conf} =                       Replace String  ${result.stdout}  4242  ${EXECUTORPORT}
    ${conf} =                       Replace String  ${conf}  4243  ${LOGPORT}
    Set Suite Variable              $runtime_config_file  ${TEMPDIR}${/}dummyrun-test-${LOGPORT}${EXECUTORPORT}.conf.yml
    Create File                     ${runtime_config_file}.orig  ${conf}
    ${db_file_path} =               prepare_for_sqlite_store_test  ${runtime_config_file}.orig  ${runtime_config_file}  ${TEMPDIR}
    Set Suite Variable              $db_file_path
    Log File                        ${runtime_config_file}
    ${result} =                     Run Process  palaestrai  -c  ${runtime_config_file}  runtime-config-show-effective
    Log Many                        ${result.stdout}  ${result.stderr}
    ${result} =                     Run Process  palaestrai  -c  ${runtime_config_file}  database-create  stdout=${stdout_file}  stderr=${stderr_file}
    Should Be Equal As Integers     ${result.rc}   0


*** Test Cases ***
Run dummy experiment
    [Timeout]                       15min
    ${process} =                    Start Process  palaestrai  -vc  ${runtime_config_file}  experiment-start  ${CURDIR}${/}..${/}fixtures${/}dummy_run.yml    stdout=${stdout_file}  stderr=${stderr_file}
    ${result} =                     Wait For Process  ${process}  timeout=5min  on_timeout=kill
    Log Many                        ${result.stdout}  ${result.stderr}
    Should Be Equal As Integers     ${result.rc}   0
    ${brain_dir}                    Set Variable  ${EXECDIR}${/}_outputs${/}brains/Yo-ho, a dummy experiment run for me!
    File Should Exist               ${brain_dir}${/}0${/}mighty_defender.bin
    File Should Exist               ${brain_dir}${/}0${/}evil_attacker.bin
    File Should Exist               ${brain_dir}${/}1${/}mighty_defender.bin
    File Should Exist               ${brain_dir}${/}1${/}evil_attacker.bin
    ${result} =                     Run Process  sqlite3  -csv  -newline    |  ${db_file_path}  stdin=SELECT erp.id, COUNT(ma.id) FROM muscle_actions ma JOIN main.agents a on a.id = ma.agent_id JOIN main.experiment_run_phases erp on erp.id = a.experiment_run_phase_id JOIN main.experiment_run_instances eri on erp.experiment_run_instance_id = eri.id JOIN main.experiment_runs er on eri.experiment_run_id = er.id WHERE er.uid = 'Yo-ho, a dummy experiment run for me!' GROUP BY erp.id ORDER BY ma.id DESC;
    Log many                        ${result.stderr}    ${result.stdout}
    Should be equal as strings      ${result.stdout}    2,20|1,20|


Run dummy experiment with Taking Turns Simulation Controller
    [Timeout]                       15min
    ${process} =                    Start Process  palaestrai  -vc  ${runtime_config_file}  experiment-start  ${CURDIR}${/}..${/}fixtures${/}dummy_run_taking_turns.yml    stdout=${stdout_file}  stderr=${stderr_file}
    ${result} =                     Wait For Process  ${process}  timeout=5min  on_timeout=kill
    Log Many                        ${result.stdout}  ${result.stderr}
    Should Be Equal As Integers     ${result.rc}   0
    ${result} =                     Run Process  sqlite3  -csv  ${db_file_path}  stdin=WITH last_erp(id) AS (SELECT MAX(id) FROM experiment_run_phases), ma AS (SELECT *, LAG(muscle_actions.agent_id, 1, 0) OVER (ORDER BY muscle_actions.id) AS previous_agent_id FROM muscle_actions, last_erp JOIN agents ON muscle_actions.agent_id \= agents.id JOIN main.experiment_run_phases erp ON agents.experiment_run_phase_id \= erp.id WHERE NOT done AND erp.id \= last_erp.id) SELECT SUM(ma.agent_id \= ma.previous_agent_id) AS consecutive_updates FROM ma GROUP BY ma.experiment_run_phase_id;
    Should Be Equal As Integers     ${result.rc}  0
    Should Be Equal As Integers     ${result.stdout}  0
