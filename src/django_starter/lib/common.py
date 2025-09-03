from decimal import Decimal, InvalidOperation

def to_decimal(value, default=0):
    if value in [None, '', 'None']:
        return Decimal(str(default))    
    try:
        if isinstance(value, str) and 'e' in value.lower():
            return Decimal(float(value))
        return Decimal(str(value))
    except (ValueError, InvalidOperation, TypeError):
        return Decimal(str(default))