import calendar
import webbrowser
import tempfile
from datetime import date, timedelta
from jinja2 import Template

weekly_agenda_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <title>Daily Agenda for {{ from_date }} to {{ to_date }}</title>
</head>
<body>

    <ul id="tasks">
    {% for dt, day_ls in tasks.items() %}
        <li id="day_{{ loop.index0 }}">
            <div>Date: {{ dt }}</div>
            <ul>
            {% for agenda in day_ls %}
                <li>{{ agenda }}</li>
            {% endfor %}
            </ul>
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

    from_date = min(tasks.keys())
    to_date = max(tasks.keys())
    template = Template(weekly_agenda_template)
    x = template.render(tasks=tasks,
                        from_date=from_date,
                        to_date=to_date,
                        today=today)
    print(x)
    # html_report_file = None
    # with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False) as tf:
    #     tf.write(x)
    #     html_report_file = 'file://' + tf.name
    # webbrowser.open_new(html_report_file)


if __name__ == '__main__':
    test_tasks = {}
    t = date.today()
    delta = timedelta(days=1)
    for i in range(3):
        td = t + (delta * i)
        test_tasks[td] = []
        test_tasks[td].append("blah" + str(i))
        test_tasks[td].append("bluh" + str(i))
    weekly_agenda(test_tasks)
