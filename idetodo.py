import PySimpleGUI as sg
from config import read_config
from todotxt import TodoList, Todo
from pathlib import Path
import os
import sys
from view_calendar import weekly_agenda
from datetime import date, timedelta

win_values = None
win_event = None
todos = None
window = None


def todo_ask():
    todo_text = sg.PopupGetText("Add todo:", "Add todo")
    if todo_text:
        pyline_eval_print("todo('" + todo_text + "')")
        return todo_text
    else:
        return "cancelled"


def _refresh_todos(select=None):
    if window:
        window['-TODOLIST-'].update(todos.ls)
        window['-TODOLIST-'].SetValue([select])
        idx = 0
        if select is not None:
            for t in todos.ls:
                if t == select:
                    break
                idx += 1
        window['-TODOLIST-'].set_vscroll_position(idx * 1.0 / len(todos.ls))


def todo(todo_txt):
    todo_new = Todo(text=todo_txt)
    todos.add_todos(todo_new)
    _refresh_todos(todo_new)
    return todo_new


def done(t=None):
    if t is None:
        t = selected()
    t.mark_done()
    todos.update_view()
    _refresh_todos(t)


def daily_todo(todo_txt, num_days=7):
    """
    Create a number of tasks for the coming days
    starting today, and up to num_days.
    All have the same text except the due date.
    """
    today = date.today()
    d = timedelta(days=1)
    for i in range(num_days):
        todo_new = Todo(text=todo_txt)
        todo_new.set_due(today + (i * d))
        todo_new.update_text_from_parts()
        todos.add_todos(todo_new)
        _refresh_todos(todo_new)


def save():
    todos.save_todos()


def reload():
    sel = selected()
    idx = 0 if sel is None else todos.ls.index(sel)
    todos.get_todos()
    _refresh_todos(todos.ls[idx])


def update_ask(todo_row=None):
    if todo_row is None:
        todo_row = selected()
    todo_text = sg.PopupGetText("Update todo:", "Update todo", todo_row.text)
    if todo_text:
        todo_new = Todo(text=todo_text)
        todos.replace(todo_row, todo_new)
        _refresh_todos(todo_new)
        return todo_new
    else:
        return "cancelled"


def selected():
    s = None
    if len(win_values['-TODOLIST-']) == 1:
        s = win_values['-TODOLIST-'][0]
    return s


def agenda():
    weekly_agenda(todos)


cfg = read_config()
sg.theme(cfg["ui"]["theme"])

HOME_DIR = str(Path.home())
TODO_DIR = os.path.join(HOME_DIR, cfg["todotxt"]["todo_dir"])
TODO_TXT_PATH = os.path.join(TODO_DIR, cfg["todotxt"]["todo_file"])

todos = TodoList(TODO_TXT_PATH)


# ------ Menu Definition ------ #
def get_menu_key(menu_item_str):
    return menu_item_str.replace('&', '')


task_new = '&New    (Ctrl-N)::task_new'
task_update = '&Update (Ctrl-U)::task_update'
task_done = '&Done (Ctrl-X)::task_done'

file_reload = '&Reload File  (Ctrl-.)::file_reload'
file_save = '&Save      (Ctrl-S)::file_save'
menu_def = [
    ['&File',
     ['New', 'Open', 'Print', 'Print Preview', 'Archive Completed Tasks', file_reload, file_save, 'Options', 'Exit',
      'Properties']],
    ['Edit', ['Cut', 'Copy', 'Copy Task to New Task', 'Paste', 'Undo'], ],
    ['&Task', [task_new, task_update, task_done]],
    ['Sort'],
    ['Filter'],
    ['Report', ['Daily']],
    ['Help', 'About'], ]

pyline_history = []
pyline_count = 0


def pyline_eval_print(py_input):
    # print read value
    window['-PYOUTPUT-'].print('> ', py_input)
    global pyline_count
    pyline_count = pyline_count + 1
    pyline_history.append(py_input)
    # eval
    py_output = None
    error = True
    try:
        py_output = eval(py_input)
        error = False
    except:
        py_output = "Unexpected error:", sys.exc_info()[0]
    # print
    window['-PYOUTPUT-'].print(str(py_output), text_color='red' if error else 'green')


if __name__ == '__main__':
    selected_todo = None
    if todos is not None and len(todos.ls) > 0:
        selected_todo = todos.ls[0]

    # TODO: some of the tests below should be moved to a unit test.
    # print(todo_list)
    # print(selected_todo)
    # parse_todo_line(selected_todo.strip())
    # parse_todo_line("x (N) 2021-01-06 2021-01-05 create")
    # parse_todo_line("x 2021-01-06 2021-01-05 create")
    # parse_todo_line("x 2021-01-05 create")
    # parse_todo_line("2021-01-05 create")

    LAYOUT_WIDTH = 150

    layout = [
        [sg.Menu(menu_def)],
        [sg.Listbox(key="-TODOLIST-", values=todos.ls,
                    default_values=[selected_todo], size=(LAYOUT_WIDTH, 30), enable_events=True, auto_size_text=True)],
        # [sg.Button("Quit")],
        [sg.Multiline(default_text="", key="-PYOUTPUT-", size=(LAYOUT_WIDTH, 5),
                      disabled=True, autoscroll=True)],
        [sg.T(text="IDETODO >>", size=(10, None)),
         sg.Input(default_text="", key="-PYLINE-", size=(LAYOUT_WIDTH - 11, None), enable_events=True, focus=True),
         sg.Button('-SUBMIT_PYLINE-', visible=False, bind_return_key=True)],
        [sg.StatusBar("Filter", key="-STATUSBAR_FILTER-"), sg.StatusBar("Sort", key="-STATUSBAR_SORT-"),
         sg.StatusBar("Tasks", key="-STATUSBAR_TASKS-"), sg.StatusBar("Incomplete", key="-STATUSBAR_INCOMPLETE-"),
         sg.StatusBar("Due Today", key="-STATUSBAR_DUE_TODAY-"), sg.StatusBar("Overdue", key="-STATUSBAR_OVERDUE-")]
    ]

    window = sg.Window('IDETODO', layout, return_keyboard_events=True, margins=(0, 0))

    # see docs - persistent window - multiple reads using an event loop
    while True:
        win_event, win_values = window.read()

        if win_event == sg.WIN_CLOSED or win_event == 'Quit':
            break

        if win_event == 'Up:38':
            pyline_count -= 1
            if -1 < pyline_count < len(pyline_history):
                window['-PYLINE-'].update(pyline_history[pyline_count])

        if win_event == 'Down:40':
            pyline_count += 1
            if -1 < pyline_count < len(pyline_history):
                window['-PYLINE-'].update(pyline_history[pyline_count])

        if win_event in (get_menu_key(task_new), 'n:78', 'n:57'):
            pyline_eval_print("todo_ask()")

        if win_event in (get_menu_key(task_update), 'u:85'):
            pyline_eval_print("update_ask()")

        if win_event in (get_menu_key(file_reload), 'period:190'):
            pyline_eval_print("reload()")

        if win_event in (get_menu_key(file_save), 's:83'):
            pyline_eval_print("save()")

        if win_event in (get_menu_key(task_done), 'x:88', 'x:53'):
            pyline_eval_print("done()")

        if win_event == '-SUBMIT_PYLINE-':
            # read
            lua_line = win_values['-PYLINE-']
            pyline_eval_print(lua_line)
            # loop
            window['-PYLINE-'].update("")

        if win_event == 'Daily':
            agenda()

        if win_event == 'About':
            sg.popup_ok("IDETODO v0.01:\nA productivity IDE based on the todo.txt file format. "
                        "UX heavily inspired from todotxt.net", title="About IDETODO v0.01", non_blocking=True,
                        no_titlebar=True,
                        keep_on_top=True, modal=True)
        if len(win_values['-TODOLIST-']) > 0:
            selected_todo = win_values['-TODOLIST-'][0]

        print(win_event)

    window.close()
