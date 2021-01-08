from pathlib import Path
import os
import PySimpleGUI as sg
from parsimonious.grammar import Grammar
from parsimonious.nodes import NodeVisitor
from datetime import datetime


def date_to_string(date_obj):
    return date_obj.strftime("%Y-%m-%d")


class Todo:
    def __init__(self, text=None, task=None, done=False, priority=None, completion_date=None, creation_date=None,
                 due_date=None,
                 projects=None, contexts=None):
        self.text = text
        self.task = task
        self.done = done
        self.priority = priority
        self.completion_date = completion_date
        self.creation_date = creation_date,
        self.due_date = due_date
        self.projects = projects
        self.contexts = contexts

    def update_parts_from_text(self):
        #TODO:call the parser here
        pass

    def update_text_from_parts(self):
        self.text = ""
        if self.done:
            self.text += "x "
        if self.priority:
            self.text += "(" + self.priority + ") "
        if self.completion_date:
            self.text += date_to_string(self.completion_date) + " "
        if self.creation_date:
            self.text += date_to_string(self.creation_date) + " "
        if self.task:
            self.text = self.task
        return self.text

    def __str__(self):
        return self.text


todo_txt_grammar = Grammar(r"""
    todo        = done? priority? date? date? task
    done        = ("x" / "X") ws
    priority    = "(" ~"[A-Z]" ")" ws
    date        = y "-" m  "-" d ws
    task        = ~".*"
    d           = digit digit
    m           = digit digit
    y           = digit digit digit digit
    digit       = ~r"[0-9]"
    ws          = ~"\s*"
    """)


class TodoVisitor(NodeVisitor):
    def visit_todo(self, node, visited_children):
        "gets todo"
        todo = Todo(
            done=visited_children[0][0] if visited_children[0] else False,
            priority=visited_children[1][0] if visited_children[1] else None,
            completion_date=visited_children[2][0] if visited_children[2] else None,
            creation_date=visited_children[3][0] if visited_children[3] else None,
            task=visited_children[4],
            text=node.text
        )

        return todo

    def visit_priority(self, node, visited_children):
        "gets priority"
        _, p, _, _ = node.children
        return p.text

    def visit_date(self, node, visited_children):
        "gets date"
        return datetime.strptime(node.text.strip(), '%Y-%m-%d')

    def visit_done(self, node, visited_children):
        "gets date"
        return True

    def visit_task(self, node, visited_children):
        "gets date"
        return node.text

    def visit_ws(self, node, visited_children):
        return "space"

    def generic_visit(self, node, visited_children):
        """ The generic visit method. """
        # changed this from returning node, so as to return only matched items
        return visited_children or None


def parse_todo_line(line):
    # print(line)
    tree = todo_txt_grammar.parse(line.rstrip())
    iv = TodoVisitor()
    output = iv.visit(tree)
    # print(output)
    return output


HOME_DIR = str(Path.home())
DOCS_DIR = os.path.join(HOME_DIR, "Documents")
TODO_DIR = os.path.join(DOCS_DIR, "notes", "TODO")

TODO_TXT_PATH = os.path.join(TODO_DIR, "todo.txt")

print(TODO_TXT_PATH)


def get_todo_lines():
    f = open(TODO_TXT_PATH, "r")
    todos = f.readlines()
    todo_ls = []
    for todo in todos:
        # print(todo.strip())
        todo_ls.append(todo.strip())
    return todo_ls


if __name__ == '__main__':
    tl = get_todo_lines()
    todo_list = []
    for t in tl:
        todo_list.append(parse_todo_line(t.strip()))
    selected_todo = None
    if todo_list is not None and len(todo_list) > 0:
        selected_todo = todo_list[0]

    print(todo_list)
    print(selected_todo)
    # parse_todo_line(selected_todo.strip())
    # parse_todo_line("x (N) 2021-01-06 2021-01-05 create")
    # parse_todo_line("x 2021-01-06 2021-01-05 create")
    # parse_todo_line("x 2021-01-05 create")
    # parse_todo_line("2021-01-05 create")

    LAYOUT_WIDTH = 100

    layout = [
        [sg.Input(default_text=selected_todo.text, key="-TODOTEXT-", size=(LAYOUT_WIDTH, None))],
        [sg.Listbox(key="-TODOLIST-", values=todo_list,
                    default_values=[selected_todo], size=(LAYOUT_WIDTH, 20), enable_events=True)],
        [sg.Button("New Thread"), sg.Button("Quit")]
    ]

    window = sg.Window('todotxt ide', layout)

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
