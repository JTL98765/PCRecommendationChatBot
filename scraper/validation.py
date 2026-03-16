import re

########################################################################
# This program performs validation and formatting for fields being 
# scraped from vendor html files
########################################################################

STORAGE_TYPE_MAP = {
    "M.2": "SSD",
    "NVME": "SSD",
    "SSD": "SSD",
    "HDD": "HDD",
}    

# Convert Storage Type to standard format as defined in STORAGE_TYPE_MAP
def convert_storage(inputString: str):
    key = inputString.strip().upper()
    return STORAGE_TYPE_MAP.get(key,inputString)

# Extract numerical value from string
def extract_number(inputString: str):
    value=re.search(r'\d+(\.\d+)?', inputString).group()
    value=float(value)
    return int(value)

# Convert TB representation to GB (e.g. 1 TB=1000)
def storage_capacity_conversion(inputString: str):
    inputString = inputString.lower()
    value = float(re.search(r'\d+(\.\d+)?', inputString).group())
    if "tb" in inputString:
        return int(value*1000)
    if "." in inputString:
        return int(value * 1000)
    return int(value)

# Convert value to integer
def convert_to_int(inputValue):
    value = re.search(r'\d+(\.\d+)?', str(inputValue))
    return int(float(value.group())) if value else 0

# Extracts numerical battery life value from string
def convert_battery_format(inputValue):
    inputValue = re.search(r'\d+', inputValue).group()
    return int(inputValue)

# Extracts numerical value from screen size value
def convert_screen_size(inputValue):
    inputValue = re.search(r'\d+', inputValue).group()
    return int(inputValue)

# Extracts numerical value from processor speed value
def convert_processor_speed_format(inputValue):
    value = float(re.search(r'\d+(\.\d+)?', inputValue).group())
    return value

# Extracts numerical value from gpu value
def convert_gpu_format(inputValue):
    value = float(re.search(r'\d+(\.\d+)?', inputValue).group())
    return value

# Try and determine if graphics card is discrete or integrated
def classify_graphics_type(brand, model):

    if not brand and not model:
        return "integrated"

    brand = (brand or "").lower()
    model = (model or "").lower()

    # Discrete patterns
    if brand == "nvidia":
        return "discrete"

    discrete_keywords = [
        "rtx", "gtx", "arc", "quadro"
    ]

    # Specific case for radeon rx graphics cards. Look for rx followed by number.
    if re.search(r'rx\s*\d{3,4}', model):
        return "discrete"

    # Integrated
    integrated_keywords = [
        "intel uhd", "iris", "radeon graphics", "vega"
    ]

    if any(keyword in model for keyword in discrete_keywords):
        return "discrete"

    if any(keyword in model for keyword in integrated_keywords):
        return "integrated"

    # If brand suggests integrated
    if brand == "intel":
        return "integrated"

    # Default
    return "integrated"

def normalise_graphics_fields(graphics_brand,graphics_model,graphics_type,graphics_ram_gb):

    # Handle missing model
    if not graphics_model:
        if graphics_type == "integrated":
            graphics_model = "Integrated Graphics"
        else:
            graphics_model = "Unknown"

    # Handle missing brand for integrated
    if graphics_type == "integrated":
        graphics_brand = graphics_brand or "Integrated"
        graphics_ram_gb = graphics_ram_gb or 0

    return graphics_brand,graphics_model,graphics_type,graphics_ram_gb