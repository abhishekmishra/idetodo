import PySimpleGUI as sg
from config import read_config
from todotxt import parse_todo_line, get_todo_lines
from pathlib import Path
import os

cfg = read_config()
sg.theme(cfg["theme"])

HOME_DIR = str(Path.home())
TODO_DIR = os.path.join(HOME_DIR, cfg["todo_dir"])
TODO_TXT_PATH = os.path.join(TODO_DIR, cfg["todo_file"])

# ------ Menu Definition ------ #
menu_def = [
    ['File', ['New', 'Open', 'Print', 'Print Preview', 'Archive Completed Tasks', 'Reload File', 'Options', 'Exit',
              'Properties']],
    ['Edit', ['Cut', 'Copy', 'Copy Task to New Task', 'Paste', 'Undo'], ],
    ['Task'],
    ['Sort'],
    ['Filter'],
    ['Help', 'About...'], ]

if __name__ == '__main__':
    tl = get_todo_lines(TODO_TXT_PATH)
    todo_list = []
    for t in tl:
        todo_list.append(parse_todo_line(t.strip()))
    selected_todo = None
    if todo_list is not None and len(todo_list) > 0:
        selected_todo = todo_list[0]

    # TODO: some of the tests below should be moved to a unit test.
    # print(todo_list)
    # print(selected_todo)
    # parse_todo_line(selected_todo.strip())
    # parse_todo_line("x (N) 2021-01-06 2021-01-05 create")
    # parse_todo_line("x 2021-01-06 2021-01-05 create")
    # parse_todo_line("x 2021-01-05 create")
    # parse_todo_line("2021-01-05 create")

    LAYOUT_WIDTH = 100

    layout = [
        [sg.Menu(menu_def)],
        [sg.Input(default_text=selected_todo.text, key="-TODOTEXT-", size=(LAYOUT_WIDTH, None))],
        [sg.Listbox(key="-TODOLIST-", values=todo_list,
                    default_values=[selected_todo], size=(LAYOUT_WIDTH, 20), enable_events=True)],
        # [sg.Button("Quit")],
        [sg.StatusBar("Filter", key="-STATUSBAR_FILTER-"), sg.StatusBar("Sort", key="-STATUSBAR_SORT-"),
         sg.StatusBar("Tasks", key="-STATUSBAR_TASKS-"), sg.StatusBar("Incomplete", key="-STATUSBAR_INCOMPLETE-"),
         sg.StatusBar("Due Today", key="-STATUSBAR_DUE_TODAY-"), sg.StatusBar("Overdue", key="-STATUSBAR_OVERDUE-")]
    ]

    window = sg.Window('IDETODO', layout)

    # see docs - persistent window - multiple reads using an event loop
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == 'Quit':
            break
        if len(values['-TODOLIST-']) > 0:
            selected_todo = values['-TODOLIST-'][0]
            window['-TODOTEXT-'].update(selected_todo.text)
        print(event, values)

    window.close()
