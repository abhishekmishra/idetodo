import uuid

from parsimonious.grammar import Grammar
from parsimonious.nodes import NodeVisitor
from datetime import datetime, date
import re


class TodoList:
    """
    Manages a list of todos read from a source.
    Allows CRUD function, as well as filter/sort
    """

    def __init__(self, todo_txt_path):
        self.todo_txt_path = todo_txt_path
        self._todos = None
        self.ls = None
        self.get_todos()

    def get_todos(self):
        with open(self.todo_txt_path, "r") as f:
            todos = f.readlines()
            self._todos = []
            for todo in todos:
                self._todos.append(Todo(text=todo.strip()))
            self.update_view()

    def update_view(self):
        self.ls = sorted(self._todos, key=lambda x: x.text)

    def add_todos(self, todo_item):
        self._todos.insert(0, todo_item)
        self.update_view()

    def replace(self, todo_row, todo_item):
        i = self._todos.index(todo_row)
        self._todos[i] = todo_item
        self.update_view()

    def save_todos(self):
        todo_ls_str = ""
        i = 0
        for todo in self._todos:
            todo_ls_str += todo.text
            if i < (len(self._todos) - 1):
                todo_ls_str += '\n'
        with open(self.todo_txt_path, 'w') as f:
            f.write(todo_ls_str)
        return todo_ls_str


def date_to_string(date_obj):
    return date_obj.strftime("%Y-%m-%d")


class Todo:
    def __init__(self, text=None, task=None, done=False, priority=None,
                 completion_date=None, creation_date=None,
                 due=None,
                 projects=None, contexts=None):
        self.text = text.strip()
        self.task = task
        self.done = done
        self.priority = priority
        self.completion_date = completion_date
        self.creation_date = creation_date
        self.projects = projects
        self.contexts = contexts
        self.properties = {}
        if self.text:
            self.update_parts_from_text()
        else:
            self.update_text_from_parts()

        # if the task does not have a due date set it
        if due is not None:
            self.set_due(due)

        # if the task does not have an id, generate it
        if self.get_id() is None:
            self.set_id()

    def mark_done(self):
        if not self.done:
            self.done = True
            self.completion_date = date.today()
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
            for p in props:
                x = p.split(':', 1)
                self.properties[x[0]] = x[1]
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

    def set_property(self, name, value):
        new_prop = False
        if name in self.properties:
            re.replace(rf'{re.escape(name)}:[\w-]+', name + ':' + value, self.task)
        else:
            new_prop = True
            self.task += " " + name + ":" + value
        self.properties[name] = value
        if new_prop:
            self.update_text_from_parts()

    def get_due(self):
        if 'due' in self.properties:
            return datetime.strptime(self.properties['due'], '%Y-%m-%d').date()
        else:
            return None

    def set_due(self, dt):
        self.set_property('due', dt.strftime('%Y-%m-%d'))

    def get_id(self):
        if 'id' in self.properties:
            return self.properties['id']
        else:
            return None

    def set_id(self):
        self.set_property('id', str(uuid.uuid4()))

    def __str__(self):
        return self.text

    def as_dict(self):
        return {
            "text": self.text,
            "task": self.task,
            "done": self.done,
            "priority": self.priority,
            "completion_date": self.completion_date,
            "creation_date": self.creation_date,
            "due": self.get_due(),
            "properties": self.properties
        }


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
