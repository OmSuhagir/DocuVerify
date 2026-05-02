import re
from dateutil.parser import parse as parse_date

def normalize_name(name: str) -> str:
    if not name:
        return ""
    name = name.upper().strip()
    name = re.sub(r'^(MR\.|MRS\.|MS\.|DR\.)\s+', '', name)
    return name

def normalize_dob(dob: str) -> str:
    if not dob:
        return ""
    try:
        dt = parse_date(dob, fuzzy=True)
        return dt.strftime("%Y-%m-%d")
    except Exception:
        return dob.strip()

def normalize_address(address: str) -> str:
    if not address:
        return ""
    addr = address.upper()
    addr = re.sub(r'[^\w\s]', '', addr)
    return ' '.join(addr.split())

def normalize_city(city: str) -> str:
    if not city:
        return ""
    city = city.upper()
    city = re.sub(r'[^\w\s]', '', city)
    return ' '.join(city.split())
