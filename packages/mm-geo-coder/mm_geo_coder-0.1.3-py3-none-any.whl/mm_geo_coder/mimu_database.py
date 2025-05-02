from .geocoder_utils import parse_address, remove_location_words, find_indices
from .database_utils import DatabaseHandler
from .config import HIERARCHY_LEVEL
import pandas as pd

class MimuDatabase:
    def __init__(self):
        pass

    def search_in_mimu(self, address, limit=1):
        parsed_address = parse_address(address)       
        if not parsed_address:
            return None
        else:      
            parsed_levels = [level for level in HIERARCHY_LEVEL if level in parsed_address.keys()]      
            result = self.get_location_from_mimu(parsed_address, parsed_levels)          
            if result is None:
                return None            
            elif len(result)>=limit:
                return result[0:limit]
            else:
                return result

    def get_location_from_mimu(self, parsed_address, parsed_levels):
        if not parsed_address or not parsed_levels:
            return None
        table_name = "villages" if {"village", "village_tract"} & parsed_address.keys() else "wards"
        keys_to_remove = ["ward", "town"] if table_name == "villages" else ["village", "village_tract"]
        for key in keys_to_remove:
            parsed_address.pop(key, None)      
            parsed_levels.remove(key) if key in parsed_levels else None
            
        clean_parsed_address = {level: remove_location_words(parsed_address[level]) for level in parsed_levels}
        
        result = self.get_partial_match(table_name, clean_parsed_address, parsed_levels)
        
        if result:        
            return result
        else:        
            return self.get_fuzzy_match(table_name, clean_parsed_address, parsed_levels)

    def get_partial_match(self, table_name, clean_parsed_address, clean_parsed_levels):
          
        conditions = [f"{level}_mmr LIKE '%{clean_parsed_address[level]}%'" for level in clean_parsed_levels ]
        condition = ' AND '.join(conditions)
        db_handler = DatabaseHandler()
        base_table = db_handler.extract_base_table(table_name, condition)    
        
        if base_table.empty:
            return None
        else:       
            
            base_table["address"] = base_table[[col for col in  base_table.columns if col.endswith('mmr')]].apply(lambda x: '၊ '.join(x.dropna().astype(str)), axis=1)
            cols = ["address", clean_parsed_levels[-1] + "_pcode", 'latitude', 'longitude']
            base_table = base_table[cols].copy()        
            base_table.rename(columns={clean_parsed_levels[-1] + "_pcode": "pcode"}, inplace=True)
            
            return base_table.to_dict(orient='records') 

    def get_fuzzy_match(self, table_name, parsed_address, cleaned_parsed_levels):
        db_handler = DatabaseHandler()
        base_table = db_handler.extract_base_table(table_name)   

        if base_table.empty:
            return None
        else:            
            lowest_match_level = None
            for level in cleaned_parsed_levels:
                col = level + '_mmr'
                if col in base_table.columns:
                    indices =  find_indices(base_table[col], parsed_address[level])        
                    if indices:
                        lowest_match_level = level            
                        base_table = base_table[base_table.index.isin(indices)]
                    else:
                        break        
            base_table = base_table.reset_index(drop=True)

            if lowest_match_level is None:
                return None
            else:
                lowest_col = lowest_match_level + '_mmr' 
                cols = list(base_table.columns[list(base_table.columns).index(lowest_col):])
                if 'town_mmr' in cols and 'township_mmr' in cols:
                    cols = [col for col in cols if col != 'township_mmr']
                cols = [lowest_match_level + '_pcode'] + cols
                base_table = base_table[cols].copy()

                mmr_columns = [col for col in base_table.columns if col.endswith('mmr')]
                base_table['address'] = base_table[mmr_columns].agg(lambda x: '၊ '.join(x.dropna().astype(str)), axis=1)
                base_table.rename(columns={lowest_match_level + "_pcode": "pcode"}, inplace=True)
                base_table = base_table.drop(columns=mmr_columns, axis=1)
                base_table = base_table.drop_duplicates(subset=['pcode'], keep='first')
                
                return base_table.to_dict(orient='records') 





