from bs4 import BeautifulSoup
import re
import scraper.validation as validation

########################################################################
# This program extracts PC data from Amazon website html files using 
# Beautifulsoup. Data is then mapped to a pc fields dictionary file and 
# then returned to the calling application. re is used to extract certain
# values from various amazon fields.
########################################################################

def run(FILE_LOCATION):

    # Initialize Dictionaries

    # Amazon field mappings.  Some fields have two mappings although this may be old/new data.
    # May be able to remove one if no longer used.

    amazon_field_map = {
        "Brand Name": "Manufacturer",#1
        "Brand": "Manufacturer",#2
        "Item model number": "Model_Name",#1
        "Model Name": "Model_Name",#2
        "Standing screen display size": "Screen_Size",
        "Screen Resolution": "Screen_Resolution",
        "Processor Brand": "Processor_Brand",
        "Processor Series": "Processor_Type",#1
        "Processor Type": "Processor_Type",#2
        "Processor Speed": "Processor_Speed_GHZ",
        "Hard Drive Size": "Storage_Capacity_GB",
        "Hard-Drive Size": "Storage_Capacity_GB",
        "Hard Disk Description": "Storage_Type",
        "Video Processor":"Graphics_Brand",#1
        "Graphics Chipset Brand":"Graphics_Brand",#2
        "RAM Memory Installed":"RAM_GB",#1
        "RAM Size":"RAM_GB",#2
        "Maximum Memory Supported":"RAM_GB",#3
        "RAM Memory Technology":"RAM_Type",#1
        "Memory Technology": "RAM_Type",#2
        "Graphics Coprocessor": "Graphics_Model",
        "Graphics Card Ram": "Graphics_RAM_GB",#1
        "Graphics Card Ram Size": "Graphics_RAM_GB",#2
        "Graphics RAM Type": "Graphics_RAM_Type",#1
        "Graphics Ram Type": "Graphics_RAM_Type",#2
        "Operating Systems": "OS",#1
        "Operating System": "OS",#2
        "Total USB Ports":"USB_Port_Count",
    }

# The pc_fields dictionary contains the fields that will be used to update the pc database tables
    pc_fields = {
        "Vendor": "Amazon",
        "Price": None,
        "URL": None,
        "Model_Name": None,
        "Overall_Rating": None,
        "Manufacturer": None,
        "Machine_Type": None,
        "OS": None,
        "Processor_Type": None,
        "RAM_GB": None,
        "RAM_Type":None,
        "Storage_Capacity_GB": None,
        "Storage_Type": None,
        "Graphics_Brand": None,
        "Graphics_Model": None,
        "Graphics_RAM_GB": None,
        "Graphics_RAM_Type": None,
        "Graphics_Type":None,
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

    # Open html file to be scraped
    with open(FILE_LOCATION, "r", encoding="utf-8") as f:
        html = f.read()

    soup = BeautifulSoup(html, "html.parser")

    # Locate the specific table by its ID
    technical_details = {}

    tables = soup.find_all("table", class_="a-keyvalue prodDetTable")

    # Extract all product detail fields
    for table in tables:
        for row in table.find_all("tr"):
            key_cell = row.find("th")
            value_cell = row.find("td")

            if not key_cell or not value_cell:
                continue

            # Perform some formatting of the extracted fields including some special character removal
            key = key_cell.get_text(strip=True)
            key=key.replace('\u200e', '').replace('\u200f', '')
            value = value_cell.get_text(strip=True)
            value=value.replace('\u200e', '').replace('\u200f', '')
            technical_details[key] = value

    # Scrape PC Price
    amount_input = soup.find('input', {'name': 'items[0.base][customerVisiblePrice][amount]'})
    amount = None

    if amount_input and amount_input.has_attr('value'):
        amount = amount_input['value']

    if amount:
        pc_fields["Price"] = float(amount)

    # Scrape vendor url link
    canonical_link = soup.find('link', rel='canonical')
    if canonical_link and canonical_link.has_attr("href"):
        pc_fields["URL"] = canonical_link["href"]
    
    # Scrape overall rating
    span = soup.find("span", id="acrPopover")

    if span and span.has_attr("title"):
        title_text = span["title"]
        # extract rating number from title_text
        match = re.search(r'\d+(\.\d+)?', title_text)
        if match:
            pc_fields["Overall_Rating"] = float(match.group())
            
    # Configure functions that will be used to format specific fields
    FIELD_HANDLERS = {
        "Hard Disk Description": validation.convert_storage,
        "RAM Memory Installed": validation.extract_number,
        "RAM Size": validation.extract_number,
        "Maximum Memory Supported": validation.extract_number,
        "Hard Drive Size": validation.storage_capacity_conversion,
        "Hard-Drive Size": validation.storage_capacity_conversion,
        "Graphics Card Ram Size": validation.convert_to_int,
        "Graphics Card Ram": validation.convert_to_int,
        "Standing screen display size": validation.convert_screen_size,
        "Processor Speed": validation.convert_processor_speed_format,
      }

    # Load battery fields
    battery_value = technical_details.get("Lithium Battery Energy Content")

    if battery_value:
        pc_fields["Battery_Raw_Text"] = battery_value
        lower = battery_value.lower()

        # Extract watt hours
        wh_match = re.search(r'(\d+(\.\d+)?)\s*(wh|watt\s*hours?)', lower)
        if wh_match:
            pc_fields["Battery_Watt_Hours"] = float(wh_match.group(1))

        # Extract milliampere hours
        mah_match = re.search(r'(\d+)\s*(mah|milliampere\s*hour)', lower)
        if mah_match:
            pc_fields["Battery_Mah"] = int(mah_match.group(1))    


    # Load amazon fields to pc_fields dictionary
    # PC Specification Fields
    for amazon_key, raw_key in amazon_field_map.items():
        value = technical_details.get(amazon_key)

    # If pc_fields[raw_key] is not empty it has already been populated
    # This accounts for fields that originate from more than one location

        if value is not None and pc_fields[raw_key] is None:
            handler = FIELD_HANDLERS.get(amazon_key)
            pc_fields[raw_key] = handler(value) if handler else value

    # PC Machine Type.  Determining laptop based on amazon title field extract

    page_title = soup.title.string if soup.title else ""
    title_lower = page_title.lower()

    if any(word in title_lower for word in ["laptop", "macbook", "chromebook", "notebook"]):
        pc_fields["Machine_Type"] = "Laptop"    
    else:
        pc_fields["Machine_Type"] = "Desktop"
    
    # Classify Graphics Type
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