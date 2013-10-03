/*
2013.5.12 CKS
Finds all matches that need to be created or updated.
*/
DROP VIEW IF EXISTS issue_mapper_positionagreement CASCADE;
CREATE OR REPLACE VIEW issue_mapper_positionagreement
AS
SELECT      CONCAT(CAST(p.issue_id AS VARCHAR), '-', CAST(p.person_id AS VARCHAR), '-', CAST(pa.person_id AS VARCHAR)) AS id,
            p.issue_id,
            p.person_id AS your_person_id,
            p.polarity AS your_polarity,
            pa.person_id AS their_person_id,
            pa.polarity AS their_polarity,
            p.polarity = pa.polarity AS agree,
            p.polarity IS NULL OR pa.polarity IS NULL AS unknown
FROM        issue_mapper_position AS p
INNER JOIN  issue_mapper_positionaggregate AS pa
        ON  pa.issue_id = p.issue_id
        AND pa.date IS NULL
        AND p.deleted IS NULL;