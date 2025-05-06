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

*** Test Cases ***
check existing palaestrai modules
    ${pip_show_output} =            Run Process     pip  show  palaestrai  palaestrai-environments  palaestrai-agents  midas-palaestrai  midas-mosaik  midas-powergrid
    Log Many                        ${pip_show_output.stderr}   ${pip_show_output.stdout}
    Should Be Equal As Integers     ${pip_show_output.rc}   0
    Should Not Contain              ${pip_show_output.stderr}   WARNING
    Should Not Contain              ${pip_show_output.stderr}   Package(s) not found
    Should Not Contain              ${pip_show_output.stderr}   CRITICAL|ERROR
    Should Not Contain              ${pip_show_output.stdout}   CRITICAL|ERROR     

midas medium voltage experiment run from a Jupyter Notebook
    Start Process                   jupyter  nbconvert    --to    html   --execute   ${CURDIR}${/}midas_integrationtest_palaestrai.ipynb    stdout=${TEMPDIR}${/}stdout.txt     stderr=${TEMPDIR}${/}stderr.txt  alias=arl-integrationtest    cwd=${EXECDIR}
    ${result} =                     Wait For Process  handle=arl-integrationtest  timeout=60 min  on_timeout=kill
    Log Many                        ${result.stdout}    ${result.stderr}
    Should Be Equal As Integers     ${result.rc}   0
    Should Not Contain              ${result.stderr}   CRITICAL|ERROR
    Should Not Contain              ${result.stdout}   CRITICAL|ERROR  
    File Should Exist               ${CURDIR}${/}midas_integrationtest_palaestrai.html

Check the existence of agents brain files
    File Should Exist              _outputs/brains/Classic-ARL-Experiment-0/0/Sauron SAC (autocurriculum-training)-sac_actor.bin
    File Should Exist              _outputs/brains/Classic-ARL-Experiment-0/0/Gandalf SAC (autocurriculum-training)-sac_actor.bin
    File Should Exist              _outputs/brains/Classic-ARL-Experiment-0/0/Sauron SAC (autocurriculum-training)-sac_actor_target.bin
    File Should Exist              _outputs/brains/Classic-ARL-Experiment-0/0/Sauron SAC (autocurriculum-training)-sac_critic.bin
    File Should Exist              _outputs/brains/Classic-ARL-Experiment-0/0/Sauron SAC (autocurriculum-training)-sac_critic_target.bin
    File Should Exist              _outputs/brains/Classic-ARL-Experiment-0/0/Gandalf SAC (autocurriculum-training)-sac_actor_target.bin
    File Should Exist              _outputs/brains/Classic-ARL-Experiment-0/0/Gandalf SAC (autocurriculum-training)-sac_critic.bin
    File Should Exist              _outputs/brains/Classic-ARL-Experiment-0/0/Gandalf SAC (autocurriculum-training)-sac_critic_target.bin
    File Should Exist              _outputs/brains/Classic-ARL-Experiment-0/1/Sauron SAC (autocurriculum-training)-sac_actor.bin
    File Should Exist              _outputs/brains/Classic-ARL-Experiment-0/1/Gandalf SAC (autocurriculum-training)-sac_actor.bin
    File Should Exist              _outputs/brains/Classic-ARL-Experiment-0/1/Sauron SAC (autocurriculum-training)-sac_actor_target.bin
    File Should Exist              _outputs/brains/Classic-ARL-Experiment-0/1/Sauron SAC (autocurriculum-training)-sac_critic.bin
    File Should Exist              _outputs/brains/Classic-ARL-Experiment-0/1/Gandalf SAC (autocurriculum-training)-sac_actor_target.bin
    File Should Exist              _outputs/brains/Classic-ARL-Experiment-0/1/Gandalf SAC (autocurriculum-training)-sac_critic.bin
    File Should Exist              _outputs/brains/Classic-ARL-Experiment-0/1/Sauron SAC (autocurriculum-training)-sac_critic_target.bin
    File Should Exist              _outputs/brains/Classic-ARL-Experiment-0/1/Gandalf SAC (autocurriculum-training)-sac_critic_target.bin