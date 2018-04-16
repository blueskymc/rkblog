USE `rk_blog`;

DROP VIEW
IF EXISTS `view_dcs_project`;
CREATE VIEW `view_dcs_project` AS (
    SELECT
        `project_dcs`.`id` AS `id`,
        `dcs`.`name` AS `dcsname`,
        `project`.`name` AS `projectname`,
        `subsystem`.`name` AS `sysname`,
        `hmi_mode`.`name` AS `hminame`,
        `config_mode`.`name` AS `cfgname`,
        `project_dcs`.`pro_out` AS `outname`
    FROM
        (
            (
                `dcs` LEFT JOIN `project_dcs` ON ((`dcs`.`id` = `project_dcs`.`dcs_id`))
            )
            LEFT JOIN `project` ON ((`project_dcs`.`project_id` = `project`.`id`))
            LEFT JOIN `subsystem` ON ((`project_dcs`.`sys_id` = `subsystem`.`id`))
            LEFT JOIN `hmi_mode` ON ((`project_dcs`.`hmi_id` = `hmi_mode`.`id`))
            LEFT JOIN `config_mode` ON ((`project_dcs`.`cfg_id` = `config_mode`.`id`))
        )
);

DROP VIEW
IF EXISTS `view_project_dcs`;
CREATE VIEW `view_project_dcs` AS (
    SELECT
        `project_dcs`.`id` AS `id`,
        `project`.`name` AS `projectname`,
        `dcs`.`name` AS `dcsname`,
        `subsystem`.`name` AS `sysname`,
        `hmi_mode`.`name` AS `hminame`,
        `config_mode`.`name` AS `cfgname`,
        `project_dcs`.`pro_out` AS `outname`
    FROM
        (
            (
                `project` LEFT JOIN `project_dcs` ON ((`project`.`id` = `project_dcs`.`project_id`))
            )
            LEFT JOIN `dcs` ON ((`project_dcs`.`dcs_id` = `dcs`.`id`))
            LEFT JOIN `subsystem` ON ((`project_dcs`.`sys_id` = `subsystem`.`id`))
            LEFT JOIN `hmi_mode` ON ((`project_dcs`.`hmi_id` = `hmi_mode`.`id`))
            LEFT JOIN `config_mode` ON ((`project_dcs`.`cfg_id` = `config_mode`.`id`))
        )
);