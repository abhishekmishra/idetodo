import PySimpleGUI as sg
from config import read_config
from todotxt import TodoList, Todo
from pathlib import Path
import os
import sys
from view_calendar import weekly_agenda
from lupa import LuaRuntime, LuaSyntaxError, LuaError
from datetime import date, timedelta

win_values = None
win_event = None
todos = None


def todo_ask():
    todo_text = sg.PopupGetText("Add todo:", "Add todo")
    if todo_text:
        lualine_eval_print("todo('" + todo_text + "')")
        return todo_text
    else:
        return "cancelled"


def _refresh_todos(select=None):
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


def done(t):
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


def update_ask(todo_row):
    if todo_row is None:
        todo_row = selected()
    idx = todos.ls.index(todo_row)
    todo_text = sg.PopupGetText("Update todo:", "Update todo", todo_row.text)
    todo_new = Todo(text=todo_text)
    todos.replace(idx, todo_new)
    _refresh_todos(todo_new)
    return todo_new


def selected():
    s = None
    if len(win_values['-TODOLIST-']) == 1:
        s = win_values['-TODOLIST-'][0]
    return s


def agenda():
    weekly_agenda(todos)


lua = LuaRuntime(unpack_returned_tuples=True)
lua.execute("""
function pyfunc(name)
    return python.eval(name)
end

todo = pyfunc("todo")
done = pyfunc("done")
daily_todo=pyfunc("daily_todo")
todo_ask = pyfunc("todo_ask")
update_ask = pyfunc("update_ask")
save = pyfunc("save")
reload = pyfunc("reload")
selected = pyfunc("selected")
debug = pyfunc("sg.Print")
popup_ok = pyfunc("sg.popup_ok")
agenda = pyfunc("agenda")

""")


def update_lua_py_globals():
    lua.execute("""
    -- python variables
    todos = python.eval("todos")
    win_event = python.eval("win_event")
    win_values = python.eval("win_values")
    """)


cfg = read_config(lua)
sg.theme(cfg["theme"])

HOME_DIR = str(Path.home())
TODO_DIR = os.path.join(HOME_DIR, cfg["todo_dir"])
TODO_TXT_PATH = os.path.join(TODO_DIR, cfg["todo_file"])


# ------ Menu Definition ------ #
def get_menu_key(menu_item_str):
    return menu_item_str.replace('&', '')


task_new = '&New    (Ctrl-N)::task_new'
task_update = '&Update (Ctrl-U)::task_update'
task_done = '&Done (Ctrl-X)::task_done'

file_reload = '&Reload File  (Ctrl-.)::file_reload'
menu_def = [
    ['&File', ['New', 'Open', 'Print', 'Print Preview', 'Archive Completed Tasks', file_reload, 'Options', 'Exit',
               'Properties']],
    ['Edit', ['Cut', 'Copy', 'Copy Task to New Task', 'Paste', 'Undo'], ],
    ['&Task', [task_new, task_update, task_done]],
    ['Sort'],
    ['Filter'],
    ['Report', ['Daily']],
    ['Help', 'About'], ]

lualine_history = []
lualine_count = 0


def lualine_eval_print(lua_input):
    # print read value
    window['-LUAOUTPUT-'].print('> ', lua_input)
    global lualine_count
    lualine_count = lualine_count + 1
    lualine_history.append(lua_input)
    # eval
    lua_output = None
    error = True
    try:
        lua_output = lua.eval(lua_input)
        error = False
    except LuaSyntaxError as syntax_error:
        try:
            lua_output = lua.execute(lua_input)
            error = False
        except LuaSyntaxError as syntax_error_2:
            lua_output = syntax_error
        except LuaError as lua_error:
            lua_output = lua_error
    except LuaError as lua_error:
        lua_output = lua_error
    except:
        lua_output = "Unexpected error:", sys.exc_info()[0]
    # print
    window['-LUAOUTPUT-'].print(str(lua_output), text_color='red' if error else 'green')


if __name__ == '__main__':
    todos = TodoList(TODO_TXT_PATH)

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

    LAYOUT_WIDTH = 100

    layout = [
        [sg.Menu(menu_def)],
        [sg.Listbox(key="-TODOLIST-", values=todos.ls,
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

    window = sg.Window('IDETODO', layout, return_keyboard_events=True, margins=(0, 0))

    # see docs - persistent window - multiple reads using an event loop
    while True:
        win_event, win_values = window.read()
        update_lua_py_globals()

        if win_event == sg.WIN_CLOSED or win_event == 'Quit':
            break

        if win_event == 'Up:38':
            lualine_count -= 1
            if -1 < lualine_count < len(lualine_history):
                window['-LUALINE-'].update(lualine_history[lualine_count])

        if win_event == 'Down:40':
            lualine_count += 1
            if -1 < lualine_count < len(lualine_history):
                window['-LUALINE-'].update(lualine_history[lualine_count])

        if win_event in (get_menu_key(task_new), 'n:78'):
            lualine_eval_print("todo_ask()")

        if win_event in (get_menu_key(task_update), 'u:85'):
            lualine_eval_print("update_ask(nil)")

        if win_event in (get_menu_key(file_reload), 'period:190'):
            lualine_eval_print("reload()")

        if win_event in (get_menu_key(task_done), 'x:88'):
            lualine_eval_print("done(nil)")

        if win_event == '-SUBMIT_LUALINE-':
            # read
            lua_line = win_values['-LUALINE-']
            lualine_eval_print(lua_line)
            # loop
            window['-LUALINE-'].update("")

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
