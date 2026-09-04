def get_wards_zero_hospitals_query() -> str:
    return """
        SELECT w.ward_code, w.ward_name, w.pop_sum, COUNT(h.geometry) AS hospital_count, ST_AsGeoJSON(ST_Transform(w.geometry, 4326)) AS geometry
        FROM boundaries.wards w
        LEFT JOIN health.health_facilities h
            ON ST_Intersects(w.geometry, h.geometry)
        GROUP BY w.ward_code, w.ward_name, w.pop_sum, w.geometry
        HAVING COUNT(h.geometry) = 0
        ORDER BY
            w.pop_sum DESC
    """


def get_wards_zero_police_query() -> str:
    return """
        SELECT w.ward_code, w.ward_name, w.pop_sum, COUNT(p.geometry) AS police_count, ST_AsGeoJSON(ST_Transform(w.geometry, 4326)) AS geometry
        FROM boundaries.wards w
        LEFT JOIN interior_security.police_facilities p
            ON ST_Intersects(w.geometry, p.geometry)
        GROUP BY w.ward_code, w.ward_name, w.pop_sum, w.geometry
        HAVING COUNT(p.geometry) = 0
        ORDER BY
            w.pop_sum DESC
    """


def get_counties_by_school_count_query() -> str:
    return """
        SELECT c.county_code, c.county_name, c.pop_sum, COUNT(s.geometry) AS school_count, ST_AsGeoJSON(ST_Transform(c.geometry, 4326)) AS geometry
        FROM boundaries.counties c
        LEFT JOIN education.schools_facilities s
            ON ST_Intersects(c.geometry, s.geometry)
        GROUP BY c.county_code, c.county_name, c.pop_sum, c.geometry
        ORDER BY
            school_count DESC
        LIMIT 1
    """


def get_counties_poor_facility_coverage_query() -> str:
    return """
        WITH school_counts AS (
            SELECT c.county_code, COUNT(s.geometry) AS school_count
            FROM boundaries.counties c
            LEFT JOIN education.schools_facilities s
                ON ST_Intersects(c.geometry, s.geometry)
            GROUP BY c.county_code
        ),
        hospital_counts AS (
            SELECT c.county_code, COUNT(h.geometry) AS hospital_count
            FROM boundaries.counties c
            LEFT JOIN health.health_facilities h
                ON ST_Intersects(c.geometry, h.geometry)
            GROUP BY c.county_code
        ),
        police_counts AS (
            SELECT c.county_code, COUNT(p.geometry) AS police_count
            FROM boundaries.counties c
            LEFT JOIN interior_security.police_facilities p
                ON ST_Intersects(c.geometry, p.geometry)
            GROUP BY c.county_code
        )
        SELECT
            c.county_code, c.county_name, c.pop_sum,
            COALESCE(sc.school_count, 0) AS school_count,
            COALESCE(hc.hospital_count, 0) AS hospital_count,
            COALESCE(pc.police_count, 0) AS police_count,
            (
                CASE
                    WHEN COALESCE(sc.school_count, 0) > 0
                    THEN 1 ELSE 0
                END
                +
                CASE
                    WHEN COALESCE(hc.hospital_count, 0) > 0
                    THEN 1 ELSE 0
                END
                +
                CASE
                    WHEN COALESCE(pc.police_count, 0) > 0
                    THEN 1 ELSE 0
                END
            ) AS coverage_score,
            ST_AsGeoJSON(ST_Transform(c.geometry, 4326)) AS geometry
        FROM boundaries.counties c
        LEFT JOIN school_counts sc
            ON sc.county_code = c.county_code
        LEFT JOIN hospital_counts hc
            ON hc.county_code = c.county_code
        LEFT JOIN police_counts pc
            ON pc.county_code = c.county_code
        WHERE
            (
                CASE
                    WHEN COALESCE(sc.school_count, 0) > 0
                    THEN 1 ELSE 0
                END
                +
                CASE
                    WHEN COALESCE(hc.hospital_count, 0) > 0
                    THEN 1 ELSE 0
                END
                +
                CASE
                    WHEN COALESCE(pc.police_count, 0) > 0
                    THEN 1 ELSE 0
                END
            ) <= 1
        ORDER BY
            coverage_score ASC,
            c.pop_sum DESC
    """


def get_counties_zero_hospitals_query() -> str:
    return """
        SELECT c.county_code, c.county_name, c.pop_sum, COUNT(h.geometry) AS hospital_count, ST_AsGeoJSON(ST_Transform(c.geometry, 4326)) AS geometry
        FROM boundaries.counties c
        LEFT JOIN health.health_facilities h
            ON ST_Intersects(c.geometry, h.geometry)
        GROUP BY c.county_code, c.county_name, c.pop_sum, c.geometry
        HAVING COUNT(h.geometry) = 0
        ORDER BY
            c.pop_sum DESC
    """


def get_counties_zero_police_query() -> str:
    return """
        SELECT c.county_code, c.county_name, c.pop_sum, COUNT(p.geometry) AS police_count, ST_AsGeoJSON(ST_Transform(c.geometry, 4326)) AS geometry
        FROM boundaries.counties c
        LEFT JOIN interior_security.police_facilities p
            ON ST_Intersects(c.geometry, p.geometry)
        GROUP BY c.county_code, c.county_name, c.pop_sum, c.geometry
        HAVING COUNT(p.geometry) = 0
        ORDER BY
            c.pop_sum DESC
    """


def get_counties_zero_schools_query() -> str:
    return """
        SELECT c.county_code, c.county_name, c.pop_sum, COUNT(s.geometry) AS school_count, ST_AsGeoJSON(ST_Transform(c.geometry, 4326)) AS geometry
        FROM boundaries.counties c
        LEFT JOIN education.schools_facilities s
            ON ST_Intersects(c.geometry, s.geometry)
        GROUP BY c.county_code, c.county_name, c.pop_sum, c.geometry
        HAVING COUNT(s.geometry) = 0
        ORDER BY
            c.pop_sum DESC
    """


def get_wards_zero_schools_query() -> str:
    return """
        SELECT w.ward_code, w.ward_name, w.pop_sum, COUNT(s.geometry) AS school_count, ST_AsGeoJSON(ST_Transform(w.geometry, 4326)) AS geometry
        FROM boundaries.wards w
        LEFT JOIN education.schools_facilities s
            ON ST_Intersects(w.geometry, s.geometry)
        GROUP BY w.ward_code, w.ward_name, w.pop_sum, w.geometry
        HAVING COUNT(s.geometry) = 0
        ORDER BY
            w.pop_sum DESC
    """


def get_wards_no_major_facilities_query() -> str:
    return """
        WITH school_counts AS (
            SELECT w.ward_code, COUNT(s.geometry) AS school_count
            FROM boundaries.wards w
            LEFT JOIN education.schools_facilities s
                ON ST_Intersects(w.geometry, s.geometry)
            GROUP BY
                w.ward_code
        ),
        hospital_counts AS (
            SELECT w.ward_code, COUNT(h.geometry) AS hospital_count
            FROM boundaries.wards w
            LEFT JOIN health.health_facilities h
                ON ST_Intersects(w.geometry, h.geometry)
            GROUP BY
                w.ward_code
        ),
        police_counts AS (
            SELECT w.ward_code, COUNT(p.geometry) AS police_count
            FROM boundaries.wards w
            LEFT JOIN interior_security.police_facilities p
                ON ST_Intersects(w.geometry, p.geometry)
            GROUP BY
                w.ward_code
        )
        SELECT
            w.ward_code, w.ward_name, w.pop_sum,
            COALESCE(sc.school_count, 0) AS school_count,
            COALESCE(hc.hospital_count, 0) AS hospital_count,
            COALESCE(pc.police_count, 0) AS police_count,
            ST_AsGeoJSON(ST_Transform(w.geometry, 4326)) AS geometry
        FROM boundaries.wards w
        LEFT JOIN school_counts sc
            ON sc.ward_code = w.ward_code
        LEFT JOIN hospital_counts hc
            ON hc.ward_code = w.ward_code
        LEFT JOIN police_counts pc
            ON pc.ward_code = w.ward_code
        WHERE
            COALESCE(sc.school_count, 0) = 0
            AND COALESCE(hc.hospital_count, 0) = 0
            AND COALESCE(pc.police_count, 0) = 0
        ORDER BY
            w.pop_sum DESC
    """


def get_counties_most_hospitals_query() -> str:
    return """
        SELECT c.county_code, c.county_name, c.pop_sum, COUNT(h.geometry) AS hospital_count, ST_AsGeoJSON(ST_Transform(c.geometry, 4326)) AS geometry
        FROM boundaries.counties c
        LEFT JOIN health.health_facilities h
            ON ST_Intersects(c.geometry, h.geometry)
        GROUP BY c.county_code, c.county_name, c.pop_sum, c.geometry
        ORDER BY
            hospital_count DESC
        LIMIT 10
    """


def get_counties_most_police_query() -> str:
    return """
        SELECT c.county_code, c.county_name, c.pop_sum, COUNT(p.geometry) AS police_count, ST_AsGeoJSON(ST_Transform(c.geometry, 4326)) AS geometry
        FROM boundaries.counties c
        LEFT JOIN interior_security.police_facilities p
            ON ST_Intersects(c.geometry, p.geometry)
        GROUP BY c.county_code, c.county_name, c.pop_sum, c.geometry
        ORDER BY
            police_count DESC
        LIMIT 10
    """


def get_counties_fewest_schools_query() -> str:
    return """
        SELECT c.county_code, c.county_name, c.pop_sum, COUNT(s.geometry) AS school_count, ST_AsGeoJSON(ST_Transform(c.geometry, 4326)) AS geometry
        FROM boundaries.counties c
        LEFT JOIN education.schools_facilities s
            ON ST_Intersects(c.geometry, s.geometry)
        GROUP BY c.county_code, c.county_name, c.pop_sum, c.geometry
        ORDER BY
            school_count ASC,
            c.pop_sum DESC
        LIMIT 10
    """


def get_wards_most_schools_query() -> str:
    return """
        SELECT w.ward_code, w.ward_name, w.pop_sum, COUNT(s.geometry) AS school_count, ST_AsGeoJSON(ST_Transform(w.geometry, 4326)) AS geometry
        FROM boundaries.wards w
        LEFT JOIN education.schools_facilities s
            ON ST_Intersects(w.geometry, s.geometry)
        GROUP BY w.ward_code, w.ward_name, w.pop_sum, w.geometry
        ORDER BY
            school_count DESC
        LIMIT 20
    """


def get_wards_most_hospitals_query() -> str:
    return """
        SELECT w.ward_code, w.ward_name, w.pop_sum, COUNT(h.geometry) AS hospital_count, ST_AsGeoJSON(ST_Transform(w.geometry, 4326)) AS geometry
        FROM boundaries.wards w
        LEFT JOIN health.health_facilities h
            ON ST_Intersects(w.geometry, h.geometry)
        GROUP BY w.ward_code, w.ward_name, w.pop_sum, w.geometry
        ORDER BY
            hospital_count DESC
        LIMIT 20
    """


def get_schools_far_from_hospitals_query(distance_meters: float):
    return """
        SELECT s.school_id, s.name, ST_AsGeoJSON(ST_Transform(s.geometry, 4326)) AS geometry
        FROM education.schools_facilities s
        CROSS JOIN LATERAL (
            SELECT ST_Distance(s.geometry, h.geometry) AS distance_meters
            FROM health.health_facilities h
            ORDER BY s.geometry <-> h.geometry
            LIMIT 1
        ) nearest_hospital
        WHERE nearest_hospital.distance_meters > $1
        ORDER BY nearest_hospital.distance_meters DESC;
    """


def get_facilities_no_road_access_query(distance_meters: float):
    return """
        WITH facilities AS (
            SELECT school_id AS facility_id, name AS facility_name, geometry, 'school' AS facility_type
            FROM education.schools_facilities
            UNION ALL
            SELECT hospital_id AS facility_id, name AS facility_name, geometry, 'hospital' AS facility_type
            FROM health.health_facilities
            UNION ALL
            SELECT police_id AS facility_id, name AS facility_name, geometry, 'police' AS facility_type
            FROM interior_security.police_facilities
        )
        SELECT facility_id, facility_name, facility_type, ST_AsGeoJSON(ST_Transform(geometry, 4326)) AS geometry
        FROM facilities f
        WHERE NOT EXISTS (
            SELECT 1
            FROM transport.roads r
            WHERE ST_DWithin(f.geometry, r.geometry, $1)
        );
    """


def get_facilities_without_fiber_query() -> str:
    return """
        WITH facilities AS (
            SELECT 'school' AS facility_type, s.geometry, s.name AS facility_name
            FROM education.schools_facilities s
            UNION ALL
            SELECT 'hospital' AS facility_type, h.geometry, h.name AS facility_name
            FROM health.health_facilities h
            UNION ALL
            SELECT 'police' AS facility_type, p.geometry, p.name AS facility_name
            FROM interior_security.police_facilities p
        )
        SELECT f.facility_type, f.facility_name, ST_AsGeoJSON(ST_Transform(f.geometry, 4326)) AS geometry
        FROM facilities f
        WHERE NOT EXISTS (
            SELECT 1
            FROM utilities.fiber fi
            WHERE ST_DWithin(f.geometry, fi.geometry, 500)
        )
    """


def get_counties_without_electricity_query() -> str:
    return """
        SELECT c.county_code, c.county_name, c.pop_sum, ST_AsGeoJSON(ST_Transform(c.geometry, 4326)) AS geometry
        FROM boundaries.counties c
        WHERE NOT EXISTS (
            SELECT 1
            FROM utilities.electricity e
            WHERE ST_Intersects(c.geometry, e.geometry)
        )
        ORDER BY
            c.pop_sum DESC
    """


def get_wards_highest_population_query() -> str:
    return """
        SELECT ward_code, ward_name, pop_sum, ST_AsGeoJSON(ST_Transform(geometry, 4326)) AS geometry
        FROM boundaries.wards
        ORDER BY
            pop_sum DESC
        LIMIT 20
    """


def get_wards_lowest_population_query() -> str:
    return """
        SELECT ward_code, ward_name, pop_sum, ST_AsGeoJSON(ST_Transform(geometry, 4326)) AS geometry
        FROM boundaries.wards
        WHERE pop_sum IS NOT NULL
        ORDER BY
            pop_sum ASC
        LIMIT 20
    """


def get_county_highest_population_query() -> str:
    return """
        SELECT county_code, county_name, pop_sum, ST_AsGeoJSON(ST_Transform(geometry, 4326)) AS geometry
        FROM boundaries.counties
        ORDER BY
            pop_sum DESC
        LIMIT 1
    """


def get_counties_highest_population_query() -> str:
    return """
        SELECT county_code, county_name, pop_sum, ST_AsGeoJSON(ST_Transform(geometry, 4326)) AS geometry
        FROM boundaries.counties
        ORDER BY
            pop_sum DESC
        LIMIT 10
    """


def get_counties_lowest_population_query() -> str:
    return """
        SELECT county_code, county_name, pop_sum, ST_AsGeoJSON(ST_Transform(geometry, 4326)) AS geometry
        FROM boundaries.counties
        WHERE pop_sum IS NOT NULL
        ORDER BY
            pop_sum ASC
        LIMIT 10
    """


def get_counties_hospital_population_ratio_query() -> str:
    return """
        SELECT
            c.county_code, c.county_name, c.pop_sum, COUNT(h.geometry) AS hospital_count,
            CASE
                WHEN c.pop_sum > 0
                THEN
                    ROUND(
                        (
                            COUNT(h.geometry)::numeric
                            /
                            c.pop_sum
                        ) * 10000,
                        3
                    )
                ELSE 0
            END AS hospitals_per_10000_people,
            ST_AsGeoJSON(ST_Transform(c.geometry, 4326)) AS geometry
        FROM boundaries.counties c
        LEFT JOIN health.health_facilities h
            ON ST_Intersects(c.geometry, h.geometry)
        GROUP BY c.county_code, c.county_name, c.pop_sum, c.geometry
        ORDER BY
            hospitals_per_10000_people ASC
    """


def get_counties_school_population_ratio_query() -> str:
    return """
        SELECT
            c.county_code, c.county_name, c.pop_sum, COUNT(s.geometry) AS school_count,
            CASE
                WHEN c.pop_sum > 0
                THEN
                    ROUND(
                        (
                            COUNT(s.geometry)::numeric
                            /
                            c.pop_sum
                        ) * 10000,
                        3
                    )
                ELSE 0
            END AS schools_per_10000_people,
            ST_AsGeoJSON(ST_Transform(c.geometry, 4326)) AS geometry
        FROM boundaries.counties c
        LEFT JOIN education.schools_facilities s
            ON ST_Intersects(c.geometry, s.geometry)
        GROUP BY c.county_code, c.county_name, c.pop_sum, c.geometry
        ORDER BY
            schools_per_10000_people ASC
    """


def get_high_population_wards_without_hospitals_query() -> str:
    return """
        SELECT w.ward_code, w.ward_name, w.pop_sum, 0 AS hospital_count, ST_AsGeoJSON(ST_Transform(w.geometry, 4326)) AS geometry
        FROM boundaries.wards w
        WHERE NOT EXISTS (
            SELECT 1
            FROM health.health_facilities h
            WHERE ST_Intersects(w.geometry, h.geometry)
        )
        ORDER BY
            w.pop_sum DESC
        LIMIT 50
    """


def get_high_population_wards_without_major_facilities_query() -> str:
    return """
        SELECT w.ward_code, w.ward_name, w.pop_sum, 0 AS school_count, 0 AS hospital_count, 0 AS police_count, ST_AsGeoJSON(ST_Transform(w.geometry, 4326)) AS geometry
        FROM boundaries.wards w
        WHERE NOT EXISTS (
            SELECT 1
            FROM education.schools_facilities s
            WHERE ST_Intersects(w.geometry, s.geometry)
        )
        AND NOT EXISTS (
            SELECT 1
            FROM health.health_facilities h
            WHERE ST_Intersects(w.geometry, h.geometry)
        )
        AND NOT EXISTS (
            SELECT 1
            FROM interior_security.police_facilities p
            WHERE ST_Intersects(w.geometry, p.geometry)
        )
        ORDER BY
            w.pop_sum DESC
        LIMIT 50
    """