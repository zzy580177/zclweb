from decimal import Decimal, InvalidOperation

from datetime import datetime
day_format = "%Y-%m-%d"
day_format_s = "%Y%m%d"

def to_decimal(value, default=0):
    if value in [None, '', 'None']:
        return Decimal(str(default))    
    try:
        if isinstance(value, str) and 'e' in value.lower():
            return Decimal(float(value))
        return Decimal(str(value))
    except (ValueError, InvalidOperation, TypeError):
        return Decimal(str(default))
    
def str_to_date(value):
    if isinstance(value, str):
        s = value.strip()
        parsed = None
        for fmt in (day_format, day_format_s, "%Y/%m/%d"):
            try:
                parsed = datetime.strptime(s, fmt).date()
                break
            except Exception:
                continue
        value = parsed
    elif isinstance(value, datetime):
        value = value.date()
    return value
