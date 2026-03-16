########################################################################
# This program manages the validation and update of PC specification data 
# to the PC specification tables. Tables are as follows:
# - listing 
# - model 
# - processor
# - graphics
# - laptop
########################################################################


# Verify if any critical fields are missing.  If a field that is marked as required is missing it will raise an error
def check_field(pcData, key, required=False):
    
    value = pcData.get(key)

    if value in (None, ""):
        if required:
            raise ValueError(f"Critical field missing: {key}")
        return None

    return value

# validate listing fields prior to db update
def validate_listing_data(pcData):
    validatedData = {} 
    validatedData["Vendor"] = check_field(pcData, "Vendor",True)
    validatedData["Price"] = check_field(pcData, "Price",True)
    validatedData["URL"] = check_field(pcData, "URL",True)
    validatedData["Overall_Rating"] = check_field(pcData, "Overall_Rating",False)
    return validatedData

# validate model fields prior to db update
def validate_model_data(pcData):
    validatedData = {} 
    validatedData["Model_Name"] = check_field(pcData, "Model_Name",True)
    validatedData["Manufacturer"] = check_field(pcData, "Manufacturer",False)
    validatedData["Machine_Type"] = check_field(pcData, "Machine_Type",False)
    validatedData["OS"] = check_field(pcData, "OS",False)
    validatedData["RAM_GB"] = check_field(pcData, "RAM_GB",False)
    validatedData["Storage_Capacity_GB"] = check_field(pcData, "Storage_Capacity_GB",False)
    validatedData["Storage_Type"] = check_field(pcData, "Storage_Type",False)
    return validatedData

# validate graphics fields prior to db update
def validate_graphics_data(pcData):
    validatedData = {} 
    validatedData["Graphics_Brand"] = check_field(pcData, "Graphics_Brand",False)
    validatedData["Graphics_Model"] = check_field(pcData, "Graphics_Model",False)
    validatedData["Graphics_RAM_GB"] = check_field(pcData, "Graphics_RAM_GB",False)
    validatedData["Graphics_RAM_Type"] = check_field(pcData, "Graphics_RAM_Type",False)
    validatedData["Graphics_Type"] = check_field(pcData, "Graphics_Type",False)
    return validatedData

# validate processor fields prior to db update
def validate_processor_data(pcData):
    validatedData = {} 
    validatedData["Processor_Type"] = check_field(pcData, "Processor_Type",True)
    validatedData["Processor_Brand"] = check_field(pcData, "Processor_Brand",False)
    validatedData["Processor_Speed_GHZ"] = check_field(pcData, "Processor_Speed_GHZ",False)
    return validatedData

# validate laptop fields prior to db update
def validate_laptop_data(pcData):
    validatedData = {}
    validatedData["Model_Name"] = check_field(pcData, "Model_Name",True)
    validatedData["Battery_Hours"] = check_field(pcData, "Battery_Hours",False)
    validatedData["Battery_Watt_Hours"] = check_field(pcData, "Battery_Watt_Hours",False)
    validatedData["Battery_Mah"] = check_field(pcData, "Battery_Mah",False)
    validatedData["Battery_Raw_Text"] = check_field(pcData, "Battery_Raw_Text",False)
    validatedData["Screen_Size"] = check_field(pcData, "Screen_Size",False)
    validatedData["Screen_Resolution"] = check_field(pcData, "Screen_Resolution",False)
    return validatedData

# upsert listing data to listing table
def upsert_listing(connection, validatedData, model_id):
    sql = """
    INSERT INTO listing (
        vendor,
        price,
        url,
        model_id,
        overall_rating
    )
    VALUES (%s, %s, %s, %s, %s)
    ON CONFLICT (vendor, model_id, url)
    DO UPDATE SET
        price = EXCLUDED.price,
        overall_rating = EXCLUDED.overall_rating
    RETURNING listing_id;
    """

    values = (
        validatedData["Vendor"],
        validatedData["Price"],
        validatedData["URL"],
        model_id,
        validatedData["Overall_Rating"],
    )

    return execute_upsert_return_id(connection, sql, values)

# upsert model data to model table
def upsert_model(connection, validatedData, processor_id, graphics_id):
    sql = """
    INSERT INTO model (
        model_name,
        manufacturer,
        machine_type,
        os,
        processor_id,
        ram_gb,
        storage_capacity_gb,
        storage_type,
        graphics_id
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (model_name)
    DO UPDATE SET
        manufacturer = EXCLUDED.manufacturer,
        machine_type = EXCLUDED.machine_type,
        os = EXCLUDED.os,
        processor_id = EXCLUDED.processor_id,
        ram_gb = EXCLUDED.ram_gb,
        storage_capacity_gb = EXCLUDED.storage_capacity_gb,
        storage_type = EXCLUDED.storage_type,
        graphics_id = EXCLUDED.graphics_id
    RETURNING model_id;
    """

    values = (
        validatedData["Model_Name"],
        validatedData["Manufacturer"],
        validatedData["Machine_Type"],
        validatedData["OS"],
        processor_id,
        validatedData["RAM_GB"],
        validatedData["Storage_Capacity_GB"],
        validatedData["Storage_Type"],
        graphics_id,
    )

    # perform datbase upsert and return associated record_id
    return execute_upsert_return_id(connection, sql, values)

# upsert graphics data to graphics table
def upsert_graphics(connection, validatedData):

    sql = f"""
    INSERT INTO graphics (
        graphics_brand,
        graphics_model,
        graphics_ram_gb,
        graphics_ram_type,
        graphics_type
    )
    VALUES (%s, %s, %s, %s, %s)
    ON CONFLICT (graphics_brand, graphics_model, graphics_ram_gb)
    DO UPDATE SET
        graphics_ram_type = EXCLUDED.graphics_ram_type,
        graphics_type = EXCLUDED.graphics_type
    RETURNING graphics_id;
    """

    values = (
        validatedData["Graphics_Brand"],
        validatedData["Graphics_Model"],
        validatedData.get("Graphics_RAM_GB"),
        validatedData.get("Graphics_RAM_Type"),
        validatedData["Graphics_Type"]
    )

    # perform database upsert and return associated record_id
    return execute_upsert_return_id(connection, sql, values)

# upsert processor data to processor table
def upsert_processor(connection, validatedData):
    sql = """
    INSERT INTO processor (
        processor_type,
        processor_brand,
        processor_speed_ghz
    )
    VALUES (%s, %s, %s)
    ON CONFLICT (processor_type)
    DO UPDATE SET
        processor_brand = EXCLUDED.processor_brand,
        processor_speed_ghz = EXCLUDED.processor_speed_ghz
    RETURNING processor_id;
    """

    values = (
        validatedData["Processor_Type"],
        validatedData["Processor_Brand"],
        validatedData.get("Processor_Speed_GHZ")
    )

    # perform database upsert and return associated record_id
    return execute_upsert_return_id(connection, sql, values)

# upsert laptop data to laptop table. model_id is returned from the upsert to be referenced in other tables.
def upsert_laptop(connection, validatedData, model_id):
    sql = """
    INSERT INTO laptop (
        model_id,
        battery_hours,
        battery_watt_hours,
        battery_mah,
        battery_raw_text,
        screen_size,
        screen_resolution
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (model_id)
    DO UPDATE SET
        battery_hours = EXCLUDED.battery_hours,
        battery_watt_hours = EXCLUDED.battery_watt_hours,
        battery_mah = EXCLUDED.battery_mah,
        battery_raw_text = EXCLUDED.battery_raw_text,
        screen_size = EXCLUDED.screen_size,
        screen_resolution = EXCLUDED.screen_resolution
    RETURNING model_id;
    """

    values = (
        model_id,
        validatedData["Battery_Hours"],
        validatedData["Battery_Watt_Hours"],
        validatedData["Battery_Mah"],
        validatedData["Battery_Raw_Text"],
        validatedData["Screen_Size"],
        validatedData["Screen_Resolution"],
    )

    # perform database upsert and return associated record_id
    return execute_upsert_return_id(connection, sql, values)

# Upsert database using passed connection, sql and value    
def execute_upsert_return_id(connection, sql, values):
    with connection.cursor() as cur:
        cur.execute(sql, values)
        record_id = cur.fetchone()[0]
    return record_id

# validate data and upsert data to PC recommendation tables
# Order of upserts is as follows:
# 1) Processor
# 2) Graphics
# 3) Model (uses processor_id and graphics_id)
# 4) Laptop (uses model_id)
# 5) Listing (uses model_id)
def save_pc_data(connection, pcData):    
        processorData = validate_processor_data(pcData)
        processor_id = upsert_processor(connection, processorData)

        graphicsData = validate_graphics_data(pcData)
        graphics_id = upsert_graphics(connection, graphicsData)

        modelData = validate_model_data(pcData)
        model_id = upsert_model(connection, modelData, processor_id, graphics_id)

        machine_type = check_field(pcData, "Machine_Type", False)
        if machine_type and machine_type.lower() == "laptop":
            laptopData = validate_laptop_data(pcData)
            upsert_laptop(connection, laptopData, model_id)

        listingData = validate_listing_data(pcData)
        upsert_listing(connection, listingData, model_id)

