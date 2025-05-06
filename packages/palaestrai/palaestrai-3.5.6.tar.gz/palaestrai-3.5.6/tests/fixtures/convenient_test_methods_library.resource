*** Settings ***
Documentation     Library for checking logs for palaestrAI runs
Library           String
Library           Process
Library           OperatingSystem
Library         ${CURDIR}${/}run_palaestrai.py

*** Variables ***
${stdout_file_name}                      stdout.txt
${stderr_file_name}                      stderr.txt
${grep_error_str}                        CRITICAL\\|ERROR\\|/bin/sh.*not found\\|Traceback (most recent call last):


*** Keywords ***
ArsenAI Generate
        [Arguments]                       ${stdout_file}    ${stderr_file}    ${exp_file}
        [Tags]                            ArsenAI_Generate

        ${arsenai_cmd} =                  Catenate    arsenai    generate    ${exp_file}
        ${process_alias} =                Get Current Test Name Str

        ${error_raised} =                 Run General Palaestrai Cmd With Error Monitoring    general_cmd=${arsenai_cmd}    stdout_file=${stdout_file}    stderr_file=${stderr_file}    exec_dir=${EXECDIR}    process_alias=${process_alias}    timeout_time=5 min
        RETURN                            ${error_raised}

Create Database
        [Arguments]                       ${stdout_file}    ${stderr_file}    ${runtime_config_file}=${EMPTY}
        [Tags]                            Create_Database

        ${error_raised} =                 Run Palaestrai Cmd    palaestrai_sub_cmd=database-create    stdout_file=${stdout_file}    stderr_file=${stderr_file}    runtime_config_file=${runtime_config_file}    timeout_time=5 min
        RETURN                            ${error_raised}

Run Experiment
        [Arguments]                       ${stdout_file}    ${stderr_file}    ${experiment_file}    ${runtime_config_file}=${EMPTY}    ${timeout_time}=10 min
        [Tags]                            Run_Experiment

        ${rc} =                           run_palaestrai    -vv    -c    ${runtime_config_file}    experiment-start    ${experiment_file}
        ${error_raised} =                 Run Keyword And Return Status    Should Be Equal As Integers    ${rc}    0

        #${exp_run_cmd} =                  Catenate    experiment-start    ${experiment_file}

        #${error_raised} =                 Run Palaestrai Cmd    palaestrai_sub_cmd=${exp_run_cmd}    stdout_file=${stdout_file}    stderr_file=${stderr_file}    runtime_config_file=${runtime_config_file}   timeout_time=${timeout_time}
        RETURN                            ${error_raised}

Run Palaestrai Cmd
        [Arguments]                       ${palaestrai_sub_cmd}    ${stdout_file}    ${stderr_file}    ${runtime_config_file}=${EMPTY}    ${timeout_time}=10 min
        [Tags]                            Run_Palaestrai_Cmd

        ${palaestrai_cmd} =               Create Palaestrai Cmd    sub_cmd=${palaestrai_sub_cmd}    runtime_config_file=${runtime_config_file}
        ${process_alias} =                Get Current Test Name Str

        ${error_raised} =                 Run General Palaestrai Cmd With Error Monitoring    general_cmd=${palaestrai_cmd}    stdout_file=${stdout_file}    stderr_file=${stderr_file}    exec_dir=${EXECDIR}    process_alias=${process_alias}    timeout_time=${timeout_time}
        RETURN                            ${error_raised}

Create Palaestrai Cmd
        [Documentation]                   Dynamically create the palaestrai cmd for execution
                                          # ${sub_cmd} is e.g. database-create, experiment-start etc.
        [Arguments]                       ${sub_cmd}    ${runtime_config_file}=${EMPTY}
        [Tags]                            Create_Palaestrai_Cmd

        ${palaestrai_cmd}                 Catenate    palaestrai    -vv
        IF                                "${runtime_config_file}" != "${EMPTY}"
            ${palaestrai_cmd} =           Catenate    ${palaestrai_cmd}    -c ${runtime_config_file}
        END
        ${palaestrai_cmd} =               Catenate    ${palaestrai_cmd}    ${sub_cmd}
        RETURN                            ${palaestrai_cmd}


Run General Cmd
        [Arguments]                       ${general_cmd}    ${stdout_file}    ${stderr_file}    ${exec_dir}    ${process_alias}=general_process    ${timeout_time}=10 min
        [Tags]                            Run_General_Cmd

        # Seem not to cover the streams fully (?): Process args: stdout=${stdout_file}    stderr=${stderr_file}
        ${general_cmd} =                  Catenate     ${general_cmd}    >${stdout_file}    2>${stderr_file}
        START PROCESS                     ${general_cmd}    cwd=${exec_dir}    alias=${process_alias}    shell=True
        ${result} =                       Wait For Process  handle=${process_alias}  timeout=${timeout_time}  on_timeout=kill

        ${rc_eq_zero} =                   Run Keyword And Return Status    Should Be Equal As Integers    ${result.rc}    0
        Log Many                          ${result.stdout}    ${result.stderr}
        ${process_error}                  Evaluate    not ${rc_eq_zero}
        ${logs_contain_error} =           Contain Logs Error    stdout_file=${stdout_file}    stderr_file=${stderr_file}
        ${error_raised} =                 Evaluate    ${logs_contain_error} or ${process_error}
        RETURN                            ${error_raised}

Run General Palaestrai Cmd With Error Monitoring
        [Arguments]                       ${general_cmd}    ${stdout_file}    ${stderr_file}    ${exec_dir}    ${process_alias}=general_process   ${timeout_time}=10 min
        [Tags]                            Run_General_Palaestrai_Cmd_With_Error_Monitoring

        # Seem not to cover the streams fully (?): Process args: stdout=${stdout_file}    stderr=${stderr_file}
        ${general_cmd} =                  Catenate     ${general_cmd}    >${stdout_file}    2>${stderr_file}
        START PROCESS                     ${general_cmd}    cwd=${exec_dir}    alias=${process_alias}    shell=True
        START PROCESS                     ${CURDIR}${/}continuously_monitor_log_on_error.sh    ${stdout_file}    ${stderr_file}    ${grep_error_str}    30    cwd=${exec_dir}    alias=continuously_monitor_log_on_error

        ${result} =                       Wait For Process  handle=${process_alias}  timeout=${timeout_time}  on_timeout=kill
        ${monitoring_result} =            Terminate Process  handle=continuously_monitor_log_on_error  kill=true
        Log Many                          ${monitoring_result.stdout}    ${monitoring_result.stderr}
        Kill Palaestrai Processes If Remaining

        ${rc_eq_zero} =                   Run Keyword And Return Status    Should Be Equal As Integers    ${result.rc}    0
        Log Many                          ${result.stdout}    ${result.stderr}
        ${process_error}                  Evaluate    not ${rc_eq_zero}
        ${logs_contain_error} =           Contain Logs Error    stdout_file=${stdout_file}    stderr_file=${stderr_file}
        ${error_raised} =                 Evaluate    ${logs_contain_error} or ${process_error}
        RETURN                            ${error_raised}

Contain Logs Error
        [Arguments]                       ${stdout_file}    ${stderr_file}
        [Tags]                            Contain_Logs_Error

        ${stdout_contain_no_error} =      Contain Log File Error    log_file=${stdout_file}
        ${stderr_contain_no_error} =      Contain Log File Error    log_file=${stderr_file}
        Log Errors Conditionally          ${stdout_contain_no_error}    ${stdout_file}
        Log Errors Conditionally          ${stderr_contain_no_error}    ${stderr_file}
        Log Log Files With Errors Conditionally        ${stdout_contain_no_error}    ${stdout_file}
        Log Log Files With Errors Conditionally        ${stderr_contain_no_error}    ${stderr_file}
        ${contain_error} =                Evaluate    not ${stdout_contain_no_error} or not ${stderr_contain_no_error}
        RETURN                            ${contain_error}

Contain Log File Error
        [Arguments]                       ${log_file}
        [Tags]                            Contain_Log_File_Error

        ${result} =                       Run Process    grep    -c    ${grep_error_str}    ${log_file}    timeout=1 min    on_timeout=kill
        Log Many                          ${result.stdout}    ${result.stderr}
        ${grep_result_gt_zero} =          Evaluate    ${result.stdout} > 0
        IF                                ${grep_result_gt_zero}
            ${grep_error_result} =        Run Process    grep    ${grep_error_str}    ${log_file}    timeout=1 min    on_timeout=kill
            Log                           ${grep_error_result.stdout}
        END
        ${file_contains_no_error} =       Run Keyword And Return Status    Should Be Equal As Integers    ${result.stdout}    0
        RETURN                            ${file_contains_no_error}

Log Contains String
        [Arguments]                       ${test_string}    ${log_file}
        [Tags]                            Log_Contains_String

        ${result} =                       Run Process    grep    -c    ${test_string}    ${log_file}    timeout=1 min    on_timeout=kill
        Log Many                          ${result.stdout}    ${result.stderr}
        ${file_contains_string} =         Run Keyword And Return Status    Should Be True    ${result.stdout} > 0
        RETURN                            ${file_contains_string}

Log Errors Conditionally
        [Arguments]                       ${contain_no_error}    ${log_file}
        [Tags]                            Log_Errors_Conditionally
        IF                                not ${contain_no_error}
            ${result} =                   Run Process    grep    -wns    ${grep_error_str}    -C    100    ${log_file}    timeout=1 min    on_timeout=kill
            Log Errors                    ${result}
        END

Log Errors
        [Arguments]                       ${result}
        [Tags]                            Log_Errors
        Log Many                          ${result.stdout}    ${result.stderr}

Log Log Files With Errors Conditionally
        [Arguments]                       ${contain_no_error}    ${log_file}
        [Tags]                            Log_Log_Files_With_Errors_Conditionally
        IF                                not ${contain_no_error}
            ${log_file_content} =         Get File    ${log_file}
            Log Log Files With Errors     ${log_file_content}
        END


Log Log Files With Errors
        [Arguments]                       ${log_file_content}
        [Tags]                            Log_Log_Files_With_Errors
         Log                              ${log_file_content}

Get Basename Without Extension
        [Arguments]                       ${file_path}
        [Tags]                            Get_Basename_Without_Extension
        ${result}                         Run Process    ${CURDIR}${/}extract_basename_without_extension.sh    ${file_path}    timeout=1 min    on_timeout=kill
        Should Be Equal As Integers       ${result.rc}    0
        RETURN                            ${result.stdout}
        
Remove Logs If No Error
        [Arguments]                       ${stdout_file}    ${stderr_file}    ${contain_error}
        [Tags]                            Remove_Logs_If_No_Error
        IF                                not ${contain_error}
            Remove Files                  ${stdout_file}    ${stderr_file}
        END

Kill Palaestrai Processes If Remaining
        [Tags]                            Kill_Palaestrai_Processes_If_Remaining
        ${palaestrai_kill_result} =       Run Process    ${CURDIR}${/}kill_palaestrai_from_robot.sh    timeout=1 min    on_timeout=kill
        Log Many                          ${palaestrai_kill_result.stdout}    ${palaestrai_kill_result.stderr}

Get Current Test Name Str
        [Tags]                            Get_Current_Test_Name_Str
        ${test_name_str} =                Replace String    ${TEST NAME}    ${SPACE}    _
        RETURN                            ${test_name_str}

Create Stage Log Dir
        [Arguments]                       ${stage_name}
        [Tags]                            Create_Stage_Log_Dir
        ${log_dir} =                      Set Variable    ${EXECDIR}${/}test_reports${/}${stage_name}
        Create Directory                  ${log_dir}
        RETURN                            ${log_dir}

Create Test Case Log Dir
        [Arguments]                       ${stage_name}
        [Tags]                            Create_Test_Case_Log_Dir
        ${stage_log_dir} =                Create Stage Log Dir    ${stage_name}
        ${test_name_str} =                Get Current Test Name Str
        ${log_dir} =                      Set Variable    ${stage_log_dir}${/}${test_name_str}
        Create Directory                  ${log_dir}
        RETURN                            ${log_dir}

Create Std Files
        [Arguments]                       ${stage_name}    ${log_name}
        [Tags]                            Create_Std_Files
        ${log_dir}                        Create Test Case Log Dir    ${stage_name}
        ${stdout_file}                    Set Variable    ${log_dir}${/}${log_name}_${stdout_file_name}
        ${stderr_file}                    Set Variable    ${log_dir}${/}${log_name}_${stderr_file_name}
        RETURN                            ${stdout_file}    ${stderr_file}
