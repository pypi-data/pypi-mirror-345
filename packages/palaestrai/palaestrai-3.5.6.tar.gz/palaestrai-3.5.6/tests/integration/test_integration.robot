*** Settings ***
Documentation   Integration Test of Medium Voltage ARL Scenario
...
...             Test All Components in PalaestrAI ecosystem, checking for all sorts
...             of details of the run execution. It does not check for results
...             storage explicitly, but will make sure that all log outputs
...             indicate a safe, successful and complete execution. It test 
...             all steps from generation of experiment run files via ArsenAI
...             and using all harl agents in run files then excution of experiments
...             by PalaestrAI.

Library         String
Library         Process
Library         OperatingSystem
Resource        ${CURDIR}${/}..${/}fixtures${/}convenient_test_methods_library.resource

*** Test Cases ***
Run PalaestrAI Experiments
    ${stdout_file}    ${stderr_file} =    Create Std Files    stage_name=integration    log_name=create_database
    ${contain_error} =              Create Database    stdout_file=${stdout_file}    stderr_file=${stderr_file}
    Should Be True                  not ${contain_error}

    ${stdout_file}    ${stderr_file} =    Create Std Files    stage_name=integration    log_name=create_database
    ${contain_error} =              ArsenAI Generate    stdout_file=${stdout_file}    stderr_file=${stderr_file}    exp_file=${CURDIR}${/}..${/}fixtures${/}Classic-ARL-Experiment.yml
    Should Be True                  not ${contain_error}

    ${EXPERIMENT_RUN_FILES_PATH}        List Files In Directory    ${EXECDIR}${/}palaestrai-runfiles    Classic-ARL-Experiment_run-*.yml    absolute
    FOR  ${experiment_file}  IN  @{EXPERIMENT_RUN_FILES_PATH}
        ${exp_name} =                   Get Basename Without Extension    ${experiment_file}
        ${stdout_file}  ${stderr_file} =  Create Std Files    stage_name=integration    log_name=run_experiment_${exp_name}
        ${handle} =                     Start Process    palaestrai    -vc    s    ${experiment_file}  stdout=${exp_name}.stdout  stderr=${exp_name}.stderr
        ${result} =                     Wait for process  ${handle}    timeout=10min    on_timeout=kill
        Log many                        ${result.stdout}    ${result.stderr}
        Should be equal as integers     ${result.rc}    0
    END
