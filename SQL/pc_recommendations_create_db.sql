CREATE TABLE IF NOT EXISTS public.listing
(
    listing_id SERIAL PRIMARY KEY,
    vendor TEXT NOT NULL,
    model_id INTEGER REFERENCES model(model_id),
    price REAL,
    url TEXT,
    overall_rating REAL,
    CONSTRAINT vendor_len_chk CHECK (char_length(vendor) BETWEEN 1 AND 100),
    CONSTRAINT vendor_trim_chk CHECK (vendor = btrim(vendor)),
    UNIQUE (vendor, model_id, url)
);

CREATE TABLE IF NOT EXISTS public.model
(
    model_id SERIAL PRIMARY KEY,
    model_name TEXT NOT NULL UNIQUE,
    manufacturer TEXT,
    machine_type TEXT,
    os TEXT,
    processor_id INTEGER REFERENCES processor(processor_id),
    ram_gb INTEGER,
    storage_capacity_gb INTEGER,
    storage_type TEXT,
    graphics_id INTEGER REFERENCES graphics(graphics_id),
    usb_port_count INTEGER,
    classification TEXT
);

CREATE TABLE IF NOT EXISTS public.graphics
(
    graphics_id SERIAL PRIMARY KEY,
    graphics_brand TEXT NOT NULL,
    graphics_model TEXT NOT NULL,
    graphics_ram_gb INTEGER,
    graphics_ram_type TEXT,
    graphics_type TEXT CHECK (graphics_type IN ('integrated','discrete')) NOT NULL,
	UNIQUE (graphics_brand, graphics_model, graphics_ram_gb)
);

CREATE TABLE IF NOT EXISTS public.processor
(
    processor_id SERIAL PRIMARY KEY,
    processor_type TEXT NOT NULL,
    processor_brand TEXT,
    processor_speed_ghz REAL,
    UNIQUE (processor_type)
);

CREATE TABLE IF NOT EXISTS public.laptop
(
    model_id INTEGER PRIMARY KEY,
	battery_hours NUMERIC,
    battery_watt_hours NUMERIC,
    battery_mah INTEGER,
    battery_raw_text TEXT,
    screen_size NUMERIC,
    screen_resolution TEXT
);

SELECT * FROM Listing
SELECT * FROM Model
SELECT * FROM graphics
SELECT * FROM processor
SELECT * FROM laptop