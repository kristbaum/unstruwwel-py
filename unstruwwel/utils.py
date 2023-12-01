from datetime import datetime, timedelta


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

def generate_date_range(start, end):
    start_date = datetime.strptime(start, '%Y-%m-%d')
    end_date = datetime.strptime(end, '%Y-%m-%d')
    return [(start_date + timedelta(days=x)).strftime('%Y-%m-%d') for x in range((end_date - start_date).days + 1)]
