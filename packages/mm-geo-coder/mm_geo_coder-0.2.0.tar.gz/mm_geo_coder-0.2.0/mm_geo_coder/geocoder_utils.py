import re
from rapidfuzz import process
from mm_address_parser.parser import Parser
from mm_geo_coder.config import THRESHOLD

def parse_address(address):    
    try:     
        parser = Parser()        
        parsed_address = parser.parse(address)
        if({"village", "village_tract"} & parsed_address.keys()):
            parsed_address["township"] = parsed_address.get("town", None)
        if not parsed_address:
            parsed_address['state'] = address  
        return parsed_address
    except Exception as e:
        print(f"Error parsing address: {e}")
        return None

def clean_address(address):    
    clean_text = address.replace(",", "၊ ").replace(".", "။ ")    
    clean_text = re.sub(r'[^a-zA-Z0-9\u1000-\u109F\s/]', '', clean_text)
    return clean_text.strip()

def remove_location_words(text):
    location_words = ["တိုင်း", "တိုင်းဒေသကြီး","ပြည်နယ်", "ခရိုင်", "မြို့နယ်", "မြို့", "ရပ်ကွက်", "ရပ်", "ရွာ", "ကျေးရွာ"]
    pattern = '|'.join([re.escape(word) for word in location_words])
    cleaned_text = re.sub(pattern, '', text)
    return cleaned_text.strip()

def find_indices(lst, target, threshold=THRESHOLD):
    matches = process.extract(target, lst, score_cutoff=threshold)
    return [match[2] for match in matches]

