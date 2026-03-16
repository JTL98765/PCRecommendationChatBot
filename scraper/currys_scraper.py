from bs4 import BeautifulSoup
import json
import re
import scraper.validation as validation

########################################################################
# This program extracts PC data from Currys website html files using 
# Beautifulsoup. Data is then mapped to a pc fields dictionary file and 
# then returned to the calling application. re is used to extract certain
# values from various Currys fields.
########################################################################

def run(FILE_LOCATION):

    pc_fields = {
        # This dictionary contains the fields that will be used to update the pc database tables
        "Vendor": "Currys",
        "Price": None,
        "URL": None,
        "Model_Name": None,
        "Overall_Rating": None,
        "Manufacturer": None,
        "Machine_Type": None,
        "OS": None,
        "Processor_Type": None,
        "RAM_GB": None,
        "RAM_Type": None,
        "Storage_Capacity_GB": None,
        "Storage_Type": None,
        "Graphics_Brand": None,
        "Graphics_Model": None,
        "Graphics_RAM_GB": None,
        "Graphics_RAM_Type": None,
        "Graphics_Type": None,
        "USB_Port_Count": None,
        "Classification": None,
        "Processor_Brand": None,
        "Processor_Speed_GHZ": None,
        "Review_Number": None,
        "Review_Text": None,
        "Review_Rating": None,
        "Battery_Hours": None,
        "Battery_Watt_Hours": None,
        "Battery_Mah": None,
        "Battery_Raw_Text": None,
        "Screen_Size": None,
        "Screen_Resolution": None
    }

    # Load html file
    with open(FILE_LOCATION, "r", encoding="utf-8") as f:
        html = f.read()

    soup = BeautifulSoup(html, "html.parser")

    # Extract high level product info fromn json script section

    product_json = extract_product_json(soup)

    if product_json:

        pc_fields["Model_Name"] = product_json.get("name")

        # Brand
        brand = product_json.get("brand", {})
        if isinstance(brand, dict):
            pc_fields["Manufacturer"] = brand.get("name")

        # Price
        offers = product_json.get("offers", {})
        if isinstance(offers, dict):
            price = offers.get("price")
            if price:
                pc_fields["Price"] = float(price)

        # Rating
        rating = product_json.get("aggregateRating", {})
        if isinstance(rating, dict):
            rating_value = rating.get("ratingValue")
            review_count = rating.get("reviewCount")

            if rating_value:
                pc_fields["Overall_Rating"] = float(rating_value)

            if review_count:
                pc_fields["Review_Number"] = int(review_count)

    # Load URL field

    canonical = soup.find("link", rel="canonical")
    if canonical and canonical.has_attr("href"):
        pc_fields["URL"] = canonical["href"]

    # Populate machine type

    title_text = pc_fields["Model_Name"] or ""
    title_lower = title_text.lower()

    if "laptop" in title_lower or "macbook" in title_lower or "chromebook" in title_lower:
        pc_fields["Machine_Type"] = "Laptop"
    else:
        pc_fields["Machine_Type"] = "Desktop"

    # Load fields from tech-specification-body section
    spec_sections = soup.select(".tech-specification-body")

    for section in spec_sections:
        rows = section.find_all("div", recursive=False)

        for row in rows:
            
            # Many of the required fields are in the tech-specification section
            header = row.select_one(".tech-specification-th")
            value = row.select_one(".tech-specification-td")

            if not header or not value:
                continue

            header_value=header.get_text(strip=True).lower()
            value=value.get_text(strip=True)

            # Extact OS
            if header_value == "operating system":
                pc_fields["OS"] = value

            # Extract screen size
            if header_value == "screen size":
                pc_fields["Screen_Size"] = validation.convert_screen_size(value)

            # Extract screen resolution
            if header_value == "resolution":
                pc_fields["Screen_Resolution"] = value

            # Extract storage data
            if header_value == "storage":
                pc_fields["Storage_Capacity_GB"] = validation.storage_capacity_conversion(value)
                if "ssd" in value.lower():
                    pc_fields["Storage_Type"] = "SSD"
                elif "hdd" in value.lower():
                    pc_fields["Storage_Type"] = "HDD"

            # Extract battery data
            if header_value == "battery life":
                pc_fields["Battery_Raw_Text"] = value

                # Extract battery hours value from battery life text
                hours_match = re.search(r'(\d+(\.\d+)?)\s*hours?', value)
                if hours_match:
                    pc_fields["Battery_Hours"] = float(hours_match.group(1))
          
            # Extract RAM data
            if header_value == "ram":
                pc_fields["RAM_GB"] = validation.extract_number(value)

                if "ddr5" in value.lower():
                  pc_fields["RAM_Type"] = "DDR5"
                elif "ddr4" in value.lower():
                    pc_fields["RAM_Type"] = "DDR4"

            # Load processor data
            if header_value == "processor":

                processor_model, processor_speed, processor_brand=extract_processor_info(value)    

                if processor_model:
                    pc_fields["Processor_Type"] = processor_model

                if processor_brand:
                    pc_fields["Processor_Brand"] = processor_brand

                if processor_speed:
                    pc_fields["Processor_Speed_GHZ"] = processor_speed

            # Load graphics card data
            if header_value == "graphics card":

                brand, model, ram_gb, ram_type = extract_graphics_info(value)

                if brand:
                    pc_fields["Graphics_Brand"] = brand

                if model:
                    pc_fields["Graphics_Model"] = model

                if ram_gb:
                    pc_fields["Graphics_RAM_GB"] = ram_gb

                if ram_type:
                    pc_fields["Graphics_RAM_Type"] = ram_type

    pc_fields["Graphics_Type"] = validation.classify_graphics_type(pc_fields["Graphics_Brand"],pc_fields["Graphics_Model"])
    # Normalize graphics fields
    pc_fields["Graphics_Brand"], pc_fields["Graphics_Model"], pc_fields["Graphics_Type"], pc_fields["Graphics_RAM_GB"] = \
    validation.normalise_graphics_fields(
        pc_fields["Graphics_Brand"],
        pc_fields["Graphics_Model"],
        pc_fields["Graphics_Type"],
        pc_fields["Graphics_RAM_GB"]
    )

    return pc_fields

def extract_product_json(soup):
    scripts = soup.find_all("script", type="application/ld+json")

    # Loop through all script elements to find Product script
    for script in scripts:
        try:
            data = json.loads(script.string)
            if isinstance(data, dict) and data.get("@type") == "Product":
                return data
        except:
            continue
    return None

def extract_processor_info(processor_string):
    # This function extracts various processor related fields from a string that contains the processor info

    if not processor_string:
        return None, None, None

    # Split by dash space since Currys separates processor info with "- "
    parts = [p.strip() for p in processor_string.split("- ") if p.strip()]

    processor_model = None
    processor_speed = None
    processor_brand = None

    # Loop through all parts of the split string
    for part in parts:
        lower = part.lower()

        # Extract model
        if "processor" in lower and not processor_model:
            # Remove processor string and extra whitespace from processor_model
            processor_model = re.sub(r'\bprocessor\b', '', part, flags=re.IGNORECASE).strip()
                
            # Populate processor_brand
            if "intel" in lower:
                processor_brand = "Intel"
            elif "amd" in lower:
                processor_brand = "AMD"
            elif "apple" in lower:
                processor_brand = "Apple"
        elif "apple" in lower and not processor_model:
            # Remove processor string and extra whitespace from processor_model
            processor_model = re.sub(r'\bchip\b', '', part, flags=re.IGNORECASE).strip()
                
            # Populate processor_brand
            processor_brand = "Apple"

        # Extract GHz speed and populate processor_speed
        ghz_match = re.search(r'(\d+(\.\d+)?)\s*ghz', lower)
        if ghz_match:
            processor_speed = float(ghz_match.group(1))

    return processor_model, processor_speed, processor_brand


def extract_graphics_info(graphics_string):
    # This function extracts various graphics card fields from a string that contains the graphics info

    if not graphics_string:
        return None, None, None, None

    # Split string using "- "
    parts = [p.strip() for p in graphics_string.split("- ") if p.strip()]

    brand = None
    model = None
    ram_gb = None
    ram_type = None

    # Loop through the parts list
    for part in parts:
        lower = part.lower()

        # Populate graphics brand
        if not brand:
            if "nvidia" in lower:
                brand = "NVIDIA"
            elif "intel" in lower:
                brand = "Intel"
            elif "amd" in lower:
                brand = "AMD"

        # Populate ram_type 
        ram_match = re.search(r'(\d+)\s*gb', lower)
        if ram_match:
            ram_gb = int(ram_match.group(1))

            if "gddr7" in lower:
                ram_type = "GDDR7"
            elif "gddr6" in lower:
                ram_type = "GDDR6"
            elif "gddr5" in lower:
                ram_type = "GDDR5"

        # Populate model
        if not model and not ram_match:
            model = part

    # Clean up model field (e.g. remove integrated text)
    if model:
        model = re.sub(r'^integrated\s+', '', model, flags=re.IGNORECASE)
        model = model.strip()

    return brand, model, ram_gb, ram_type