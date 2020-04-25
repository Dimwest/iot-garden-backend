CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE SCHEMA events;

CREATE TABLE events.sensors (
   uuid UUID DEFAULT uuid_generate_v4(),
   created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
   measure_type VARCHAR(32) NOT NULL,
   unit VARCHAR(32) NOT NULL,
   value NUMERIC NOT NULL
);

CREATE TABLE events.healthchecks (
   uuid UUID DEFAULT uuid_generate_v4(),
   created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
   healthcheck_type VARCHAR(32) NOT NULL,
   unit VARCHAR(32) NOT NULL,
   value NUMERIC NOT NULL
);

CREATE TABLE events.watering (
   uuid UUID DEFAULT uuid_generate_v4(),
   created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
   quantity_ml DECIMAL NOT NULL
);
