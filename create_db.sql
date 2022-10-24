Use ostracods_data;

CREATE TABLE slide_id_hub 
(
    slide_id CHAR(15) NOT NULL,
    core VARCHAR(31),
    sub_core VARCHAR(31),
        magnification integer,
    CONSTRAINT slide_pk primary key (slide_id)
);

CREATE TABLE slide_data
(
    slide_id CHAR(15) NOT NULL,
    width integer,
    height integer,
    slide_path VARCHAR(255),
    CONSTRAINT slide_data_pk primary key (slide_id)
);

CREATE TABLE grid_data
(
    grid_id CHAR(15) NOT NULL,
    slide_id CHAR(15),
    grid_no integer,
    width integer,
    height integer,
    status_code integer,
    grid_path VARCHAR(255),
    CONSTRAINT grid_pk primary key (grid_id)
);

CREATE TABLE grid_annotations
(
    annotation_id CHAR(15) NOT NULL,
    grid_id CHAR(15) NOT NULL,
    annotation_type VARCHAR(15) NOT NULL,
    annotation_path VARCHAR(255),
    CONSTRAINT anno_pk primary key (annotation_id)
);

CREATE TABLE annotation_data
(
    annotation_id CHAR(15) NOT NULL,
    ostracod_count integer,
    CONSTRAINT ad_pk primary key (annotation_id)
);

CREATE TABLE specimen_data
(
    specimen_id CHAR(15) NOT NULL,
    grid_id CHAR(15),
    slide_id CHAR(15),
    genus_id CHAR(15),
    species_id CHAR(15),
    width integer,
    height integer,
    status_code integer,
    specimen_path VARCHAR(255),
    CONSTRAINT specimen_pk primary key (specimen_id)
);

CREATE TABLE genus
(
    genus_id CHAR(15),
    genus VARCHAR(31),
    CONSTRAINT genus_pk primary key (genus_id)
);

CREATE TABLE species
(
    species_id CHAR(15),
    species VARCHAR(63),
    CONSTRAINT species_pk primary key (species_id)
);

CREATE TABLE status_record
(
    status_code integer,
    status_description VARCHAR(63),
    CONSTRAINT status_pk primary key (status_code)
);
