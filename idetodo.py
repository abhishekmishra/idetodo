import PySimpleGUI as sg
from config import read_config
from todotxt import get_todos, Todo, add_todos, save_todos
from pathlib import Path
import os
from view_calendar import weekly_agenda
from lupa import LuaRuntime

win_values = None
win_event = None


def todo(todo_txt):
    todo_new = Todo(text=todo_txt)
    add_todos(todo_list, todo_new)
    window['-TODOLIST-'].update(todo_list)
    idx = 0
    for t in todo_list:
        if t == todo_new:
            break
        idx += 1
    window['-TODOLIST-'].SetValue([todo_new])
    window['-TODOLIST-'].set_vscroll_position(idx * 1.0 / len(todo_list))


def save():
    save_todos(todo_list, TODO_TXT_PATH)


def update(todo_row):
    pass


def selected():
    if len(win_values['-TODOLIST-']) == 1:
        return win_values['-TODOLIST-'][0]
    return None


lua = LuaRuntime(unpack_returned_tuples=True)
lua.execute("""
function pyfunc(name)
    return python.eval(name)
end

todo = pyfunc("todo")
save = pyfunc("save")
selected = pyfunc("selected")
debug = pyfunc("sg.Print")
popup_ok = pyfunc("sg.popup_ok")

""")

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

    window = sg.Window('IDETODO', layout)

    # see docs - persistent window - multiple reads using an event loop
    while True:
        win_event, win_values = window.read()
        if win_event == sg.WIN_CLOSED or win_event == 'Quit':
            break
        if win_event == '-SUBMIT_LUALINE-':
            # read
            lua_input = win_values['-LUALINE-']
            # eval
            x = lua.eval(lua_input)
            # print
            print(lua_input)
            window['-LUAOUTPUT-'].update(win_values['-LUAOUTPUT-'] + '\n> ' + lua_input + '\n' + str(x))
            # loop
            window['-LUALINE-'].update("")
        if win_event == 'Daily':
            weekly_agenda(todo_list)
        if win_event == 'About':
            sg.popup_ok("IDETODO v0.01:\nA productivity IDE based on the todo.txt file format. "
                        "UX heavily inspired from todotxt.net", title="About IDETODO v0.01", non_blocking=True,
                        no_titlebar=True,
                        keep_on_top=True, modal=True)
        if len(win_values['-TODOLIST-']) > 0:
            selected_todo = win_values['-TODOLIST-'][0]

        print(win_event)
        # print(event, values)

    window.close()
