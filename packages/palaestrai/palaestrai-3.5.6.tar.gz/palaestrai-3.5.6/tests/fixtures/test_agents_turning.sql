SELECT COUNT(*) are_agents_turning FROM (SELECT COUNT(agent_id) count_agent_id
              FROM (SELECT *
                            FROM muscle_actions
                                     JOIN agents ON muscle_actions.agent_id = agents.id
                                     JOIN main.experiment_run_phases erp
                                          ON agents.experiment_run_phase_id =
                                             erp.id
                                              AND muscle_actions.id % 2 = 0
                            GROUP BY agent_id, experiment_run_phase_id
                            UNION
                            SELECT *
                            FROM muscle_actions
                                     JOIN agents ON muscle_actions.agent_id = agents.id
                                     JOIN main.experiment_run_phases erp
                                          ON agents.experiment_run_phase_id =
                                             erp.id
                                              AND muscle_actions.id % 2 != 0
                            GROUP BY agent_id, experiment_run_phase_id))
WHERE count_agent_id IN (SELECT COUNT(*)
                         FROM agents)