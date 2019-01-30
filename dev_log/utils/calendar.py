import datetime


def iso_year_start(iso_year):
    "The gregorian calendar date of the first day of the given ISO year"
    fourth_jan = datetime.date(iso_year, 1, 4)
    delta = datetime.timedelta(fourth_jan.isoweekday()-1)
    return fourth_jan - delta


def iso_to_gregorian(iso_year, iso_week, iso_day):
    "Gregorian calendar date for the given ISO year, week and day"
    year_start = iso_year_start(iso_year)
    return year_start + datetime.timedelta(days=iso_day-1, weeks=iso_week-1)


def get_dates_from_form(form_date_string):
    year = int(form_date_string[:4])
    month = int(form_date_string[5:7])
    day = int(form_date_string[8:10])
    date_selected = datetime.date(year, month, day)
    day_date_selected = date_selected.weekday()
    date_start_week = datetime.date(year, month, day) - datetime.timedelta(day_date_selected)
    date_end_week = datetime.date(year, month, day) + datetime.timedelta(7)

    return date_selected, date_start_week, date_end_week
