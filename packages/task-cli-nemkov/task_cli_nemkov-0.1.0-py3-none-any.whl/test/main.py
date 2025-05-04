"""
The application should run from the command line, 
accept user actions and inputs as arguments,
and store the tasks in a JSON file.
The user should be able to:

    Add, Update, and Delete tasks
    Mark a task as in progress or done
    List all tasks
    List all tasks that are done
    List all tasks that are not done
    List all tasks that are in progress

    # Adding a new task
    task-cli add "Buy groceries"
    # Output: Task added successfully (ID: 1)

    # Updating and deleting tasks
    task-cli update 1 "Buy groceries and cook dinner"
    task-cli delete 1

    # Marking a task as in progress or done
    task-cli mark-in-progress 1
    task-cli mark-done 1

    # Listing all tasks
    task-cli list

    # Listing tasks by status
    task-cli list done
    task-cli list todo
    task-cli list in-progress
"""
import argparse, json, os, datetime

def debug(func):
    def wrapper(*args, **kwargs):
        print(Data().read())
        func(*args, **kwargs)
        print(Data().read())
    return wrapper

class Task:
    def __init__(self, args):
        self.args = args
        self.data = Data()
        self.action_map = {
        'add': self.add,
        'update': self.update,
        'delete': self.delete,
        'mark-in-progress': self.mip,
        'mark-done': self.md,
        'list': self.list
        }
        self._analyse()
    
    @staticmethod
    def _get_id():
        maxId = 0
        tasks = Data().read()
        for id in tasks.keys():
            maxId = max(maxId, int(id))
        return str(maxId+1)
    
    @staticmethod
    def _print_task(task_id, task):
        print(f"{task_id}: {task["title"]} [{task['status']}]")

    def _analyse(self):
        data = self.args._get_kwargs()
        if data[0][1] in self.action_map:
            self.action_map[data[0][1]](data[1:])

    def add(self, *args):
        tasks = self.data.read()
        title = args[0][0][1]
        id = self._get_id()
        new_task = {
                "title": title,
                "status": "todo",
                "time": datetime.datetime.now().isoformat()
                }
        tasks[id] = new_task
        self.data.write(tasks)
        self._print_task(id, new_task)
        

    def update(self, *args):
        tasks = self.data.read()
        try:
            tasks[str(args[0][0][1])]["title"] = args[0][1][1]
            self.data.write(tasks)
            self._print_task(str(args[0][0][1]), tasks[str(args[0][0][1])])
            print("Succesfully updated")
        except KeyError as e:
            print(f"Error: wrong key {e}")


    def delete(self, *args):
        tasks = self.data.read()
        try:
            del tasks[str(args[0][0][1])]
            self.data.write(tasks)
        except KeyError as e:
            print(f"Error: wrong key {e}")


    def mip(self, *args):
        tasks = self.data.read()
        tasks[str(args[0][0][1])]["status"] = "in-progress"
        self.data.write(tasks)

    def md(self, *args):
        tasks = self.data.read()
        tasks[str(args[0][0][1])]["status"] = "done"
        self.data.write(tasks)

    def list(self, *args):
        tasks = self.data.read()
        mode = args[0][0][1] if args[0][0][1] else None
        for task_id, task in tasks.items():
            if not mode or task['status'] == mode:
                print(f"{task_id}: {task["title"]}, {task["status"]}")

class Data:
    def __init__(self):
        self.path = "../../data/data.json"
    
    def read(self):
        if not os.path.exists(self.path): return {}
        with open(self.path, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    
    def write(self, data):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Tasks CLI")
    subparcers = parser.add_subparsers(dest="command", required=True)

    parser_add = subparcers.add_parser("add")
    parser_add.add_argument("title", help="Task name/title")

    parser_update = subparcers.add_parser("update")
    parser_update.add_argument("id", type=int, help="Task id")
    parser_update.add_argument("new value", help="New value of a task")

    parser_delete = subparcers.add_parser("delete")
    parser_delete.add_argument("id", type=int, help="Task id")

    parser_status = subparcers.add_parser("list")
    parser_status.add_argument("status", nargs="?", choices=["done", "todo", "in progress"], default=None, help="Filter by status")

    parser_mip = subparcers.add_parser("mark-in-progress")
    parser_mip.add_argument("id", type=int, help="Task id")

    parser_md = subparcers.add_parser("mark-done")
    parser_md.add_argument("id", type=int, help="Task id")
    
    args = parser.parse_args()
    action = Task(args)
    # print(Task._get_id())
