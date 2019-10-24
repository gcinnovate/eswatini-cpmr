DROP VIEW IF EXISTS flow_data_csfm_view;
DROP VIEW IF EXISTS shortnames_view;
CREATE VIEW shortnames_view AS
    SELECT
        a.short_name, b.name as facility,
        b.region_id, b.id as facility_id
    FROM
        facility_shortnames a, facilities b
    WHERE
        a.facility_id = b.id and short_name <> '';

CREATE VIEW flow_data_csfm_view AS
    SELECT
        a.month, a.year, a.report_type, a.msisdn,
        b.name AS district,
        c.name AS facility,
        (CASE
            WHEN b.name = 'Hhohho' THEN 31.136517 -- Mbabane
            WHEN b.name = 'Lubombo' THEN 31.862993 --
            WHEN b.name = 'Manzini' THEN 31.371682 --
            WHEN b.name = 'Shiselweni' THEN 31.385041 --
        END)::NUMERIC AS longitude,
        (CASE
            WHEN b.name = 'Hhohho' THEN -26.304799 --
            WHEN b.name = 'Lubombo' THEN -26.567896 --
            WHEN b.name = 'Manzini' THEN -26.507371 --
            WHEN b.name = 'Shiselweni' THEN -27.173450 -- Mhlosheni
        END)::NUMERIC AS latitude,
        a.values->>'language' lang,
        a.values->>'satisfied' satisfied,
        a.values->>'cleanliness' cleanliness,
        a.values->>'attitude' attitude,
        a.values->>'waitingtime' waitingtime,
        a.values->>'missingdrug' missingdrug,
        a.values->>'suggestion' suggestion,
        a.values->>'whyunsatisfied' whyunsatisfied,
        a.values->>'drugavailability' drugavailability,
        created
    FROM
        flow_data a
        LEFT OUTER JOIN locations AS b ON a.district = b.id
        LEFT OUTER JOIN facilities AS c ON a.facility = c.id
    WHERE
        a.report_type = 'csfm';
