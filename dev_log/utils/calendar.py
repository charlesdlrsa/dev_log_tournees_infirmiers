import datetime

def get_dates_from_form(string_date_from_the_form):
    """ Function returning, in date format, the dates of the selected day, the first day and the last day
    of the week of the selected day """

    year = int(string_date_from_the_form[:4])
    month = int(string_date_from_the_form[5:7])
    day = int(string_date_from_the_form[8:10])
    date_selected = datetime.date(year, month, day)
    day_date_selected = date_selected.weekday()
    date_start_week = date_selected - datetime.timedelta(day_date_selected)
    date_end_week = date_start_week + datetime.timedelta(6)

    return date_selected, date_start_week, date_end_week
