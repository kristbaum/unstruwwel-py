def is_valid_language(x, languages):
    return all(lang in languages for lang in x)

def get_invalid_language(x, languages):
    return next((lang for lang in x if lang not in languages), None)

def get_months():
    return [
        "january", "february", "march", "april", "may",
        "june", "july", "august", "september", "october",
        "november", "december"
    ]

def get_current_year():
    from datetime import datetime
    return datetime.now().year

def is_year(x):
    return str(x) in [str(year) for year in range(100, 2901)]

def is_year_addition(x):
    return str(x) in [str(year) for year in range(1, 100)]

def is_number(x):
    try:
        float(x)
        return True
    except ValueError:
        return False

def get_item(x, n=1):
    return x[n-1]
