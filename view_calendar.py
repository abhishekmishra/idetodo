import calendar
import webbrowser
import tempfile
from datetime import date, timedelta
from jinja2 import Template
import pandas as pd

weekly_agenda_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <title>Daily Agenda for {{ from_date }} to {{ to_date }}</title>
</head>
<body>

    <ul id="tasks">
    {% for key, value in tasks.iterrows() %}
        <li id="day_{{ loop.index0 }}">
            <div>Date: {{ value['due'] }}</div>
            <div>{{ value['task'] }}</div>
        </li>
    {% endfor %}
    </ul>

    {# a comment #}
</body>
</html>
"""


def weekly_agenda(tasks, get_config=lambda x, d: d, today=None):
    weekdays = list(calendar.day_name)
    if today is None:
        today = date.today()

    df = pd.DataFrame([x.as_dict() for x in tasks])
    print(df)
    df['month'] = pd.DatetimeIndex(df['due']).month
    df['year'] = pd.DatetimeIndex(df['due']).year
    df['day'] = pd.DatetimeIndex(df['due']).day
    df['dayofweek'] = pd.DatetimeIndex(df['due']).dayofweek
    # df['weekofyear'] = pd.DatetimeIndex(df['due']).isocalendar().week

    from_date = min(df["due"])
    to_date = max(df["due"])
    template = Template(weekly_agenda_template)
    x = template.render(tasks=df,
                        from_date=from_date,
                        to_date=to_date,
                        today=today)
    #print(x)
    html_report_file = None
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False) as tf:
        tf.write(x)
        html_report_file = 'file://' + tf.name
    webbrowser.open_new(html_report_file)


if __name__ == '__main__':
    test_tasks = []
    t = date.today()
    delta = timedelta(days=1)
    for i in range(3):
        td = t + (delta * i)
        test_tasks.append({ "task": "blah" + str(i), "due": td})
        test_tasks.append({ "task": "bluh" + str(i), "due": td})
    weekly_agenda(test_tasks)
