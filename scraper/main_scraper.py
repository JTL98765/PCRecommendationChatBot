from bs4 import BeautifulSoup
from scraper import amazon_scraper
from scraper import currys_scraper

########################################################################
# This program orchestrates the scraping of the html files based on 
# the vendor extracted from the files.  For supported vendors the relevant
# vendor specific scraper component will be called.  The scraped data is
# returned to the calling application.
########################################################################

# This function looks at the canonical link to determine which vendor the html file belongs to
def detect_vendor(soup):
    canonical = soup.find("link", rel="canonical")
    if canonical and canonical.get("href"):
        url = canonical.get("href").lower()
        if "amazon." in url:
            return "amazon"
        if "currys." in url:
            return "currys"

def run(file_path):
    # Open the file at file path
    with open(file_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    # Determine which vendor the file belongs to
    vendor = detect_vendor(soup)

    # Call the relevant scraper program depending on the vendor
    if vendor == "amazon":
        pc_data = amazon_scraper.run(file_path)
    elif vendor == "currys":
        pc_data = currys_scraper.run(file_path)
    else:
        # If the vendor does not match one of the accepted vendors then generate error
        raise ValueError(f"No scraper implemented for vendor html file")

    if not pc_data:
        # If no data is found then generate error
        raise ValueError("Scraper returned empty data")

    return pc_data
