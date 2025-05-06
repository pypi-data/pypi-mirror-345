*** Settings ***
Documentation   Test Termination Conditions
...
...             Exercises full experiment runs with different run defintions
...             and different termination conditions
...             (or combinations thereof).
...             Success is checked by querying the SQLite store
...             after each run.

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
    ${result} =                     Run Process  palaestrai  runtime-config-show-default  stdout=runtime_config-tc_tests.yml
    ${queueidx} =                   Get Variable Value  ${PABOTQUEUEINDEX}  0
    ${LOGPORT}                      Evaluate  str(24243 + random.randrange(1000 * (${PABOTQUEUEINDEX}+1)))
    ${EXECUTORPORT}                 Evaluate  str(24242 - random.randrange(1000 * (${PABOTQUEUEINDEX}+1)))
    ${conf} =                       Replace String  ${result.stdout}  4242  ${EXECUTORPORT}
    ${conf} =                       Replace String  ${conf}  4243  ${LOGPORT}
    Set Suite Variable              $runtime_config_file  ${TEMPDIR}${/}tc-tests-${LOGPORT}${EXECUTORPORT}.conf.yml
    Create File                     ${runtime_config_file}.orig  ${conf}
    ${db_file_path} =               prepare_for_sqlite_store_test  ${runtime_config_file}.orig  ${runtime_config_file}  ${TEMPDIR}
    Set Suite Variable              $db_file_path
    Log File                        ${runtime_config_file}
    ${result} =                     Run Process  palaestrai  -c  ${runtime_config_file}  runtime-config-show-effective
    Log Many                        ${result.stdout}  ${result.stderr}
    ${result} =                     Run Process  palaestrai  -c  ${runtime_config_file}  database-create  stdout=${stdout_file}  stderr=${stderr_file}
    Should Be Equal As Integers     ${result.rc}   0


*** Test Cases ***
Run dummy experiment with AgentObjectiveTerminationCondition and stopping environment
    [Timeout]                       15min
    ${process} =                    Start Process  palaestrai  -vc  ${runtime_config_file}  experiment-start  ${CURDIR}${/}..${/}fixtures${/}dummy_run-agent_performance_tc-envstop.yml  stdout=dummy_run-agent_performance_tc-envstop.stdout  stderr=dummy_run-agent_performance_tc-envstop.stderr
    ${result} =                     Wait For Process  ${process}  timeout=12min  on_timeout=kill
    Log Many                        ${result.stdout}  ${result.stderr}
    Should Be Equal As Integers     ${result.rc}   0
    ${result} =                     Run Process  sqlite3  -csv  -newline  |  ${db_file_path}  stdin=SELECT ma.simtimes->'myenv'->'simtime_ticks', COUNT(*) FROM muscle_actions ma GROUP BY ma.simtimes->'myenv'->'simtime_ticks' ORDER BY ma.id
    Log many                        ${result.stderr}    ${result.stdout}
    Should be equal as strings      ${result.stdout}    1,20|2,10|3,10|4,10|5,9|

Run dummy experiment with AgentObjectiveTerminationCondition and multiworker
    [Timeout]                       15min
    ${process} =                    Start Process  palaestrai  -vc  ${runtime_config_file}  experiment-start  ${CURDIR}${/}..${/}fixtures${/}dummy_run_agent_performance_tc.yml  stdout=dummy_run_agent_performance_tc.stdout  stderr=dummy_run_agent_performance_tc.stderr
    ${result} =                     Wait For Process  ${process}  timeout=12min  on_timeout=kill
    Log Many                        ${result.stdout}  ${result.stderr}
    Should Be Equal As Integers     ${result.rc}   0
    Should contain                  ${result.stdout}    AgentObjectiveTerminationCondition terminates the current phase according to Top Performer having avg10 10
    ${result} =                     Run Process  sqlite3  -csv  -newline  |  ${db_file_path}  stdin=SELECT COUNT(ma.id), SUM(ma.objective) / COUNT(DISTINCT ma.rollout_worker_uid) FROM muscle_actions ma GROUP BY ma.agent_id ORDER BY id DESC
    Log many                        ${result.stderr}    ${result.stdout}
    Should be equal as strings      ${result.stdout}    320,11169.0|
