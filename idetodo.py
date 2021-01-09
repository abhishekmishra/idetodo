import PySimpleGUI as sg
from config import read_config
from todotxt import get_todos, Todo, add_todos
from pathlib import Path
import os
from view_calendar import weekly_agenda
from lupa import LuaRuntime

lua = LuaRuntime(unpack_returned_tuples=True)
cfg = read_config(lua)
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
    ['Report', ['Daily']],
    ['Help', 'About'], ]

if __name__ == '__main__':
    todo_list = get_todos(TODO_TXT_PATH)
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
        # [sg.Input(default_text="", key="-TODOTEXT-", size=(LAYOUT_WIDTH, None), enable_events=True),
        #  sg.Button('-SUBMIT_TODOTEXT-', visible=False, bind_return_key=True)],
        [sg.Listbox(key="-TODOLIST-", values=todo_list,
                    default_values=[selected_todo], size=(LAYOUT_WIDTH, 20), enable_events=True, auto_size_text=True)],
        # [sg.Button("Quit")],
        [sg.Multiline(default_text="", key="-LUAOUTPUT-", size=(LAYOUT_WIDTH, 5),
                      disabled=True, autoscroll=True)],
        [sg.T(text="IDETODO >>", size=(10, None)),
         sg.Input(default_text="", key="-LUALINE-", size=(LAYOUT_WIDTH - 11, None), enable_events=True, focus=True),
         sg.Button('-SUBMIT_LUALINE-', visible=False, bind_return_key=True)],
        [sg.StatusBar("Filter", key="-STATUSBAR_FILTER-"), sg.StatusBar("Sort", key="-STATUSBAR_SORT-"),
         sg.StatusBar("Tasks", key="-STATUSBAR_TASKS-"), sg.StatusBar("Incomplete", key="-STATUSBAR_INCOMPLETE-"),
         sg.StatusBar("Due Today", key="-STATUSBAR_DUE_TODAY-"), sg.StatusBar("Overdue", key="-STATUSBAR_OVERDUE-")]
    ]

    window = sg.Window('IDETODO', layout, resizable=True)

    # see docs - persistent window - multiple reads using an event loop
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == 'Quit':
            break
        if event == '-SUBMIT_TODOTEXT-':
            todo_added = values['-TODOTEXT-']
            add_todos(todo_list, Todo(text=todo_added))
            window['-TODOLIST-'].update(todo_list)
            window['-TODOTEXT-'].update("")
        if event == '-SUBMIT_LUALINE-':
            # read
            lua_input = values['-LUALINE-']
            # eval
            x = lua.eval(lua_input)
            # print
            print(lua_input)
            window['-LUAOUTPUT-'].update(values['-LUAOUTPUT-'] + '\n> ' + lua_input + '\n' + str(x))
            # loop
            window['-LUALINE-'].update("")
        if event == 'Daily':
            weekly_agenda(todo_list)
        if event == 'About':
            sg.popup_ok("IDETODO v0.01:\nA productivity IDE based on the todo.txt file format. "
                        "UX heavily inspired from todotxt.net", title="About IDETODO v0.01", non_blocking=True,
                        no_titlebar=True,
                        keep_on_top=True, modal=True)
        if len(values['-TODOLIST-']) > 0:
            selected_todo = values['-TODOLIST-'][0]

        print(event)
        # print(event, values)

    window.close()
