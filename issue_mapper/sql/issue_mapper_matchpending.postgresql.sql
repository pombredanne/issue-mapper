/*
2013.5.12 CKS
Finds all matches that need to be created or updated.
*/
DROP VIEW IF EXISTS issue_mapper_matchpending CASCADE;
CREATE OR REPLACE VIEW issue_mapper_matchpending
AS
SELECT DISTINCT CONCAT(CAST(p.id AS VARCHAR), '-', CAST(p2.id AS VARCHAR)) AS id,
                p.id AS matcher_id,
                p2.id AS matchee_id
                -- ,pos2.issue_id,m.id
FROM            issue_mapper_person AS p -- normal user person, not real
INNER JOIN      auth_user AS u ON u.id = p.user_id
            AND u.is_active = true
INNER JOIN      issue_mapper_position AS pos ON -- self-positions 
                pos.creator_id = p.id
            AND pos.person_id = pos.creator_id
            AND pos.deleted IS NULL
INNER JOIN      issue_mapper_positionaggregate AS pos2 ON -- other-positions
                pos2.issue_id = pos.issue_id
            AND pos2.person_id != pos.creator_id
            AND pos2.total_count > 0
INNER JOIN      issue_mapper_person AS p2 ON -- real person
                p2.id = pos2.person_id
            AND p2.real = true
LEFT OUTER JOIN issue_mapper_match AS m ON
                m.matcher_id = p.id
            AND m.matchee_id = p2.id
WHERE           p.real = false
            AND (m.id IS NULL OR m.updated IS NULL OR m.updated < pos2.updated OR m.updated < pos.updated);
