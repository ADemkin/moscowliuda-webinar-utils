-- create inflect table for datv name
CREATE TABLE IF NOT EXISTS inflect_name (
    name VARCHAR(255) NOT NULL UNIQUE,
    name_datv VARCHAR(255),
    UNIQUE (name, name_datv)
);

-- create inflect table for datv family name
CREATE TABLE IF NOT EXISTS inflect_family_name (
    family_name VARCHAR(255) NOT NULL UNIQUE,
    family_name_datv VARCHAR(255),
    UNIQUE (family_name, family_name_datv)
);

-- create inflect table for father name
CREATE TABLE IF NOT EXISTS inflect_father_name (
    father_name VARCHAR(255) NOT NULL UNIQUE,
    father_name_datv VARCHAR(255),
    UNIQUE (father_name, father_name_datv)
);
