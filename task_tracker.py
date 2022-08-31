
# Copyright (c) 2022 - Byteplug Inc.
#
# This source file is part of the Byteplug toolkit for the Python programming
# language which is released under the OSL-3.0 license. Please refer to the
# LICENSE file that can be found at the root of the project directory.
#
# Written by Jonathan De Wachter <jonathan.dewachter@byteplug.io>, July 2022

# Few notes:
# - Refer to Firestore / Fireo documentation to understand the difference
#   between key and ID (ID is something like abcd1234 and key is something like
#   foo/abcd1234).
# - TODO; Most endpoint could define a 'invalid-user-id' error, which will
#         happen when a token is too old and the server has already wiped the
#         database.

# TODO; Improve last-updated field to be either a record (restricting to
#       date time in ISO format) or to be of the 'datetime' field later when
#       it's implemented (and if) in the Document Validator standard.
from datetime import datetime
import re
import jwt
from fireo.models import Model
from fireo.fields import TextField, DateTime
from flask_cors import CORS
from byteplug.document import Node
from byteplug.endpoints import Endpoints
from byteplug.endpoints import request, response, error
from byteplug.endpoints import endpoint, collection_endpoint
from byteplug.endpoints import adaptor
from byteplug.endpoints import EndpointError

JWT_ALGORITHM = "HS256"
JWT_SECRET = "CVuyY1Se"

SESSION_DURATION = "60 minutes"
MAX_TASK_PER_USER = 100

TASK_STATUS = ('not-done', 'in-progress', 'done')

# TODO; Update regex to allow more characters.
USERNAME_PATTERN = "^[a-zA-Z0-9_.-]*$"
USERNAME_LENGTH = (2, 16)
# Minimum eight characters, at least one letter and one number.
PASSWORD_PATTERN = "^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$"
PASSWORD_LENGTH = (8, 16)

TASK_NAME_LENGTH = (2, 40)
TASK_DESCRIPTION_LENGTH = (0, 120)

class User(Model):
    username = TextField(required=True)
    password = TextField(required=True)
    last_updated = DateTime(required=True)

    class Meta:
        collection_name = "users"

class Task(Model):
    name = TextField(required=True)
    description = TextField()
    status = TextField(required=True)

    class Meta:
        collection_name = "tasks"

endpoints = Endpoints('task-tracker')
flask_cors = CORS(endpoints.flask)

endpoints.title = "Task Tracker"
endpoints.summary = """\
Live and working micro-service showcasing the Easy Endpoint standard.\
Equivalent of the Pet Store from OAS. It aims to be as simple as possible, yet\
showing every features of the standard, and an example for other developers.
"""

endpoints.contact = {
    'name' : "Byteplug",
    'url'  : "https://www.byteplug.io/",
    'email': "contact@byteplug.io"
}
endpoints.license = {
    'name': "The Open Software License 3.0",
    'url' : "https://opensource.org/licenses/OSL-3.0"
}
endpoints.version = "1.0.0"

# This is a generic endpoint adaptor that can be copy-pasted.
def endpoint_adaptor(token=None, item=None, document=None):
    args = []

    if token:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        args.append(payload['user-key'])

    if item:
        args.append(item)

    if document:
        if type(document) is dict:
            args.extend(list(document.values()))
        else:
            args.append(document)

    return args

@request(Node('map', fields={
    'username': Node('string', pattern=USERNAME_PATTERN, length=USERNAME_LENGTH),
    'password': Node('string', pattern=PASSWORD_PATTERN, length=PASSWORD_LENGTH)
}))
@response(Node('string'))
@error('invalid-password')
@adaptor(endpoint_adaptor)
@endpoint("login")
def login(username, password):
    """ Authenticate a user and returns a token.

    If the user doesn't exist, the user is created. If the user already exists,
    the password is checked and it returns 'invalid-password' error if it
    doesn't match.
    """

    user_document = User.collection.filter('username', '==', username).get()

    if user_document is None:
        print("User does not exist, creating it...")

        user_document = User()
        user_document.username = username
        user_document.password = password
        user_document.last_updated = datetime.now()
        user_document.save()

        user_key = user_document.key
    else:
        print("User exists, checking password...")
        if user_document.password != password:
            raise EndpointError('invalid-password', None)

        user_key = user_document.key

    print("Logging successful, generating token...")
    token = jwt.encode({"user-key": user_key}, JWT_SECRET, algorithm=JWT_ALGORITHM)
    print(f"Token {token} was generated")

    return token

@response(Node('map', fields={
    'username': Node('string', pattern=USERNAME_PATTERN, length=USERNAME_LENGTH),
    'password': Node('string', pattern=PASSWORD_PATTERN, length=PASSWORD_LENGTH),
    'last-updated': Node('number', decimal=False)
}))
@error('invalid-user-id')
@adaptor(endpoint_adaptor)
@collection_endpoint("users", "get", operate_on_item=True)
def get_user(user_id):
    """ Retrieve the information of a given user.

    It returns the username and password of a particular user (you need its ID).
    Use the list users endpoints in order to retrieve their IDs.
    """

    user_document = User.collection.get('users/' + user_id)

    if user_document is None:
        raise EndpointError('invalid-user-id')

    return {
        'username': user_document.username,
        'password': user_document.password,
        'last-updated': int(user_document.last_updated.timestamp())
    }

@response(Node('array', value=Node('string')))
@adaptor(endpoint_adaptor)
@collection_endpoint("users", "list")
def list_users():
    """ List all existing users.

    It returns a list of user IDs. Use the get user endpoint in order to
    retrieve their information.
    """
    users = []
    for user_document in User.collection.fetch():
        users.append(user_document.id)

    return users

@request(Node('map', fields={
    'name':        Node('string', length=TASK_NAME_LENGTH),
    'description': Node('string', length=TASK_DESCRIPTION_LENGTH, option=True),
    'status':      Node('enum', values=TASK_STATUS, option=True)
}))
@response(Node('string'))
@adaptor(endpoint_adaptor)
@collection_endpoint("tasks", "create", authentication=True)
def create_task(user_key, name, description, status):
    """ Create a new task.

    The newly created task has status 'not-done' unless a specific status is
    specified. It return the task ID.
    """

    task_document = Task(parent=user_key)
    task_document.name = name
    task_document.description = description

    if not status:
        status = 'not-done'
    task_document.status = status

    task_document.save()

    return task_document.id

@response(Node('map', fields={
    'name':        Node('string', length=TASK_NAME_LENGTH),
    'description': Node('string', length=TASK_DESCRIPTION_LENGTH, option=True),
    'status':      Node('enum', values=TASK_STATUS)
}))
@error('invalid-task-id')
@adaptor(endpoint_adaptor)
@collection_endpoint("tasks", "get", operate_on_item=True, authentication=True)
def get_task(user_key, task_id):
    """ Retrieve the information of a given task.

    It returns the name, description and status of a particular task (you need
    its ID). Use the list tasks endpoints in order to retrieve their IDs.
    """

    task_document = Task.collection.get(user_key + '/tasks/' + task_id)

    if task_document is None:
        raise EndpointError('invalid-task-id')

    return {
        'name':        task_document.name,
        'description': task_document.description,
        'status':      task_document.status
    }

@request(Node('map', fields={
    'name':        Node('string', length=TASK_NAME_LENGTH, option=True),
    'description': Node('string', length=TASK_DESCRIPTION_LENGTH, option=True),
    'status':      Node('enum', values=TASK_STATUS, option=True)
}))
@error('invalid-task-id')
@adaptor(endpoint_adaptor)
@collection_endpoint("tasks", "update", operate_on_item=True, authentication=True)
def update_task(user_key, task_id, name, description, status):
    """ Update the information of task.

    It updates the name, description and status of a task. If you don't want to
    change a piece of information, use null.
    """

    task_document = Task.collection.get(user_key + '/tasks/' + task_id)

    if task_document is None:
        raise EndpointError('invalid-task-id')

    if name:
        task_document.name = name

    if description:
        task_document.description = description

    if status:
        task_document.status = status

    task_document.save()

@error('invalid-task-id') # TODO; This one is probably to be removed.
@adaptor(endpoint_adaptor)
@collection_endpoint("tasks", "delete", operate_on_item=True, authentication=True)
def delete_task(user_id, task_id):
    """ Delete a task.

    It simply deletes a given task.
    """

    # TODO; Rework implemention (perhaps to detect invalid task ID ?)
    Task.collection.delete(user_id + '/tasks/' + task_id)

@response(Node('array', value=Node('string')))
@adaptor(endpoint_adaptor)
@collection_endpoint("tasks", "list", authentication=True)
def list_tasks(user_key):
    """ List all existing tasks.

    It returns a list of IDs of all the tasks for the user.
    """

    tasks = []

    for task_document in Task.collection.parent(user_key).fetch():
        tasks.append(task_document.id)

    return tasks

@request(Node('enum', values=TASK_STATUS))
@adaptor(endpoint_adaptor)
@collection_endpoint("tasks", "mark-all-as", authentication=True)
def mark_all_tasks_as(user_key, status):
    """ Change the status of all tasks.

    It changes the status of all tasks for the user.
    """

    for task_document in Task.collection.parent(user_key).fetch():
        task_document.status = status
        task_document.save()

@response(Node('map', fields={
    'user-count':            Node('number', decimal=False),
    'task-count':            Node('number', decimal=False),
    # Should be a decimal but it's not implemented yet; work around is to use String()
    'average-task-per-user': Node('string'),
    'session-duration':      Node('string'),
    'max-task-per-user':     Node('number', decimal=False)
}))
@adaptor(endpoint_adaptor)
@endpoint("status")
def status():
    """ Get the service status.

    It returns information about the service such as the number of users, tasks, etc.
    """

    user_count = 0
    task_count = 0
    all_task_counts = []

    for user_document in User.collection.fetch():
        print(user_document)

        user_task_count = 0
        for task_document in Task.collection.parent(user_document.key).fetch():

            user_task_count += 1

        all_task_counts.append(user_task_count)
        task_count += user_task_count
        user_count += 1

    return {
        'user-count': user_count,
        'task-count': task_count,
        'average-task-per-user': str(sum(all_task_counts) / len(all_task_counts)),
        'session-duration': SESSION_DURATION,
        'max-task-per-user': MAX_TASK_PER_USER
    }

endpoints.add_endpoint(login)
endpoints.add_endpoint(status)

endpoints.add_collection("users", name="User", description="Represents a user having tasks associated to it.")
endpoints.add_endpoint(get_user)
endpoints.add_endpoint(list_users)

endpoints.add_collection("tasks", name="Task", description="Task represents something that you need to do.")
endpoints.add_endpoint(create_task)
endpoints.add_endpoint(get_task)
endpoints.add_endpoint(update_task)
endpoints.add_endpoint(delete_task)
endpoints.add_endpoint(list_tasks)
endpoints.add_endpoint(mark_all_tasks_as)

# Extra endpoint to toy around with different kind of errors.
@endpoint("simulate-error")
def simulate_error():
    # TODO; To be implemented.
    pass

endpoints.add_endpoint(simulate_error)

# Start the endpoints server.
if __name__ == "__main__":
    endpoints.add_shutdown_endpoint()
    endpoints.add_expose_specs_endpoint()
    endpoints.run()

# Extra code to start the server with Gunicorn
def with_unicorn():
    endpoints.add_shutdown_endpoint()
    endpoints.add_expose_specs_endpoint()
    return endpoints.flask
