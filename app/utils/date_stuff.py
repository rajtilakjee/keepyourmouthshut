from datetime import datetime


def get_tomorrows_date_for_file_names() -> str:
    return datetime.now().strftime("%Y-%m-%d")
