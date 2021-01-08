from parsimonious.grammar import Grammar
from parsimonious.nodes import NodeVisitor
from datetime import datetime
import re


def get_todos(todo_txt_path):
    with open(todo_txt_path, "r") as f:
        todos = f.readlines()
        todo_ls = []
        for todo in todos:
            # print(todo.strip())
            todo_ls.append(Todo(text=todo.strip()))
        todo_ls.sort(key=lambda x: x.text)
        return todo_ls


def add_todos(todo_ls, todo_item):
    todo_ls.append(todo_item)
    todo_ls.sort(key=lambda x: x.text)


def date_to_string(date_obj):
    return date_obj.strftime("%Y-%m-%d")


class Todo:
    def __init__(self, text=None, task=None, done=False, priority=None, completion_date=None, creation_date=None,
                 due_date=None,
                 projects=None, contexts=None):
        self.text = text.strip()
        self.task = task
        self.done = done
        self.priority = priority
        self.completion_date = completion_date
        self.creation_date = creation_date
        self.due_date = due_date
        self.projects = projects
        self.contexts = contexts
        self.properties = None
        if self.text:
            self.update_parts_from_text()
        else:
            self.update_text_from_parts()

    def update_parts_from_text(self):
        dirty = False
        self.text = self.text.strip()
        tree = todo_txt_grammar.parse(self.text)
        iv = TodoVisitor()
        output = iv.visit(tree)
        self.task = output["task"]
        if self.task:
            self.projects = [x[1:] for x in re.findall(r'\+\w+', self.task)]
            self.contexts = [x[1:] for x in re.findall(r'@\w+', self.task)]
            props = re.findall(r'\w+:[\w-]+', self.task)
            self.properties = {}
            for p in props:
                x = p.split(':', 1)
                self.properties[x[0]] = x[1]
            if 'due' in self.properties:
                self.due_date = datetime.strptime(self.properties['due'], '%Y-%m-%d')
            print(self.projects)
            print(self.contexts)
            print(self.properties)
            print(self.due_date)
        self.done = output["done"]
        self.priority = output["priority"]

        if output["date1"] is None:
            self.creation_date = datetime.today()
            dirty = True
        elif output["date2"] is None:
            self.creation_date = output["date1"]
        else:
            self.completion_date = output["date1"]
            self.creation_date = output["date2"]

        if dirty:
            self.update_text_from_parts()

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
            self.text += self.task
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
        todo = {"done": visited_children[0][0] if visited_children[0] else False,
                "priority": visited_children[1][0] if visited_children[1] else None,
                "date1": visited_children[2][0] if visited_children[2] else None,
                "date2": visited_children[3][0] if visited_children[3] else None, "task": visited_children[4],
                "text": node.text}
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


if __name__ == '__main__':
    Todo(text="2021-01-05 create @blah +bluh a:b due:2007-01-02")
    # t = todo_txt_grammar.parse("2021-01-05 create @blah +bluh")
    # v = TodoVisitor()
    # o = v.visit(t)
    # print(t)
    # print(o)
