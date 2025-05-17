from datetime import date

from lib.const import MONTH2NAME


def date_range_to_text(started_at: date, finished_at: date) -> str:
    start_day = started_at.day
    finish_day = finished_at.day
    finish_month = MONTH2NAME[finished_at.month]
    text = ""
    if finished_at.month == started_at.month:
        text += f"{start_day} - {finish_day} {finish_month}"
    else:
        start_month = MONTH2NAME[started_at.month]
        text += f"{start_day} {start_month} - {finish_day} {finish_month}"
    text += "\n{finished_at.year} г."
    return text
