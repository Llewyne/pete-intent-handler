import difflib
import json
import subprocess

from rhasspyhermes.nlu import NluIntent
from rhasspyhermes_app import EndSession

from app import app, _LOGGER

@app.on_intent("PietAddTask")
async def handle_intent(intent: NluIntent):

    # Only handle intents using whisper
    if intent.custom_data != "rasa-whisper":
        return
    _LOGGER.info("PietAddTask")
    # Parse the raw text
    [task,project] = sentence_splitter(intent.input)
    if task == "":
        return EndSession("No task given")
    # Create task
    output = taskwarrior_command("add", task, project)

    return EndSession("Task " + task + " added")

@app.on_intent("PietCompleteTask")
async def handle_intent(intent: NluIntent):
    _LOGGER.info("PietCompleteTask")
    _LOGGER.info(intent)
    task = next((x for x in intent.slots if x.slot_name =="task"), None)
    if task is None:
        return EndSession("No task given")
    task = task.value["value"]
    # Convert task to string
    task = str(task)
    # Complete task
    output = taskwarrior_command("done", task_id = task)
    return EndSession("Task " + task + " completed")


def sentence_splitter(text):
    # extract task and project because rasa does it wrong
    if "tasks " in text:
        text = text.split("tasks ")[1]
    elif "task " in text:
        text = text.split("task ")[1]
    elif "task" in text:
        text = text.split("task")[1]
    project = None
    task = text
    if "to project" in text:
        [task,project] = text.split(" to project ")
    if "for project" in text:
        [task,project] = text.split(" for project ")
    return [task,project]

def taskwarrior_command(type: str, description: str = None, project: str = None, tags=None, confirm = False, task_id = None):
    if tags is None:
        tags = []
    command = []
    if confirm:
        command.extend(["echo","'all'","|"])

    if type != "done":
        command.extend(["task", type])
        if project:
            command.append("project:" + project)
        for tag in tags:
            command.append("+" + tag)
        command.append(description)

    else:
        command.extend(["task", task_id, "done"])

    _LOGGER.info(command)
    return subprocess.check_output(command)

def find_task(description: str, project = None, tags = None):
    listParams = {}
    if project:
        listParams["project"] = project
    if tags:
        listParams["tags"] = tags

    tasks = json.loads(list_tasks(listParams))
    taskDescriptions = [x["description"] for x in tasks]
    matches = difflib.get_close_matches(description, taskDescriptions)
    matchingTasks = [x for x in tasks if x["description"] in matches]
    return [x["id"] for x in tasks]

def list_tasks(params = {}):
    command = ["task"]
    filter = []
    if "project" in params:
        filter.append("(project~"+params["project"] + " or " + "project~"+params["project"].lower() + ")")
    if "tags" in params:
        tagfilter = []
        for i in range(0,len(params["tags"])):
            tagfilter.append("+" + params["tags"][i])
        filter.append("(" +" or ".join(tagfilter) + ") ")
    filter.append("status!~deleted")
    command.append("'" + " and ".join(filter)+ "'")
    command.append("export")
    print(" ".join(command))
    return subprocess.check_output(command)