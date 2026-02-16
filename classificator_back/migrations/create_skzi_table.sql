-- Миграция: создать таблицу skzi
CREATE TABLE IF NOT EXISTS skzi (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMP NOT NULL DEFAULT now(),
    updated_at TIMESTAMP NOT NULL DEFAULT now(),
    equipment_id UUID NOT NULL UNIQUE REFERENCES equipment(id) ON DELETE CASCADE,
    registration_number VARCHAR NOT NULL UNIQUE,
    act_of_receiving_skzi VARCHAR,
    date_of_act_of_receiving TIMESTAMP,
    sertificate_number VARCHAR,
    end_date_of_sertificate TIMESTAMP,
    date_of_creation_skzi TIMESTAMP,
    nubmer_of_jornal VARCHAR,
    issued_to_whoom VARCHAR
);
