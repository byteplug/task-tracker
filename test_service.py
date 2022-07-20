import random
import json
import requests
from faker import Faker

BASE_URL = "https://tasks.byteplug.io"

def print_and_exit(response):
    print(response.status_code)
    print(response.text)
    exit(1)

fake = Faker()

# Generate a username and password that (hopefully) should be unique.
username = fake.user_name()
password = fake.password(special_chars=False)

MESSAGE = f"""\
In order to interact (and test) the Task Tracker service, this script will \
create a new user, create a few tasks and edit them. Before completing, it \
will probe the service status. Note that you are still able to interact with \
the service using the same username and password after the script has completed.

Generated username and password.

  username: {username}
  password: {password}

Do you want to continue ?
"""

input(MESSAGE)

document = {
    'username': username,
    'password': password
}
url = BASE_URL + "/login"
response = requests.post(url, json=json.dumps(document))

if response.status_code == 200:
    token = response.json()

    print("Login successful. ", end="\n\n")
    print(f"Token: {token}", end="\n\n")
    print("This token will be used in all subsequent requests.", end="\n\n")
else:
    print("Login failed.")
    print_and_exit(response)

# Prepare the common request headers for the subsequent requests.
headers = {"Authorization": f"Bearer {token}"}

# Create "My Task" task.
print("Create task \"My Task\"...")

url = BASE_URL + "/tasks/create"
document = {
    'name': "My Task",
    'description': None,
    'status': None
}
response = requests.post(url, headers=headers, json=json.dumps(document))
if response.status_code == 200:
    task_id = response.json()
    print(f"...task created with ID {task_id}")
else:
    print("Failed to create the task.")
    print_and_exit(response)
print("")

# Edit "My Task" to rename it to "My Super Task" and give it a description.
print("Renaming \"My Task\" to \"My Super Task\" and give it a description...")

url = BASE_URL + f"/tasks/{task_id}/update"
document = {
    'name': "My Super Task",
    'description': "This is a super task. Very important.",
    'status': None
}
response = requests.post(url, headers=headers, json=json.dumps(document))
if response.status_code == 204:
    print(f"...task successfully updated.")
else:
    print("Failed to update the task.")
    print_and_exit(response)
print("")

# Update "My Super Task" to mark it as 'in-progress'.
print("Marking \"My Super Task\" as 'in-progress'...")

url = BASE_URL + f"/tasks/{task_id}/update"
document = {
    'name': None,
    'description': None,
    'status': 'in-progress'
}
response = requests.post(url, headers=headers, json=json.dumps(document))
if response.status_code == 204:
    print(f"...task successfully updated.")
else:
    print("Failed to update the task.")
    print_and_exit(response)
print("")

# Checking the current state of the task.
print("Check current state of our task to see if it was updated correctly.", end="\n\n")
url = BASE_URL + f"/tasks/{task_id}/get"
response = requests.post(url, headers=headers)

document = response.json()
print("Name:", document['name'])
if document['description']:
    print("Description:", document['description'])
else:
    print("Description: No description.")
print("Status:", document['status'])

print("")
print("All OK.", end="\n\n")

# Create three tasks (A, B and C)
print("Creating 3 new tasks (task A, task B and task C)", end="\n\n")

letter_tasks_map = {}

url = BASE_URL + "/tasks/create"
for letter in ('A', 'B', 'C'):
    document = {
        'name': f"Task {letter}",
        'description': None,
        'status': None
    }
    response = requests.post(url, headers=headers, json=json.dumps(document))
    if response.status_code == 200:
        task_id = response.json()
        print(f"Task {letter} created with ID {task_id}")

        letter_tasks_map[letter] = task_id
    else:
        print(f"Failed to create task {letter}.")
        print_and_exit(response)
print("")

# Mark all tasks as done
print("Marking all tasks as done...")

url = BASE_URL + f"/tasks/mark-all-as"
response = requests.post(url, headers=headers, json='"done"')
if response.status_code == 204:
    print("Tasks successfully updated.")
else:
    print("Failed to update the tasks.")
    print_and_exit(response)
print("")

# List all tasks
print("List all existing tasks...")

url = BASE_URL + f"/tasks/list"
response = requests.post(url, headers=headers)
if response.status_code == 200:
    all_tasks = response.json()
    print("Task IDs are: ", all_tasks)

else:
    print("Failed to list the tasks.")
    print_and_exit(response)
print("")

# Delete task A, B and C.
print("Deleting task A, task B and task C...")

for letter, task_id in letter_tasks_map.items():
    url = BASE_URL + f"/tasks/{task_id}/delete"
    response = requests.post(url, headers=headers)
    if response.status_code == 204:
        print(f"Task {letter} successfully deleted.")
    else:
        print(f"Failed to delete task {letter}.")
        print_and_exit(response)

print("")
print("The only remaining task is \"My Super Task\" now.", end="\n\n")

# Get the status of the service and display it.
print("Probing service status now...", end="\n\n")

url = BASE_URL + "/status"
response = requests.post(url)
if response.status_code == 200:
    document = response.json()

    print("Number of users:", document['user-count'])
    print("Number of tasks:", document['task-count'])
    print("Average number of tasks per user:", document['average-task-per-user'])
    print("Session duration: ", document['session-duration'], "(the time before data are wiped)")
    print("Maximum number of task per user:", document['max-task-per-user'])
else:
    print("Failed to probe service status.")
    print_and_exit(response)
print("")

# List users.
print("Listing all existing users...")

url = BASE_URL + "/users/list"
response = requests.post(url)
if response.status_code == 200:
    all_users = response.json()
    print("User IDs are: ", all_users)

else:
    print("Failed to list the users.")
    print_and_exit(response)
print("")

# Pick 3 of the users and display their infos.
k = min(3, len(all_users))
print(f"Picking {k} of the users and displaying their information...", end="\n\n")
users_to_display = random.sample(all_users, k=k)

for user_id in users_to_display:
    url = BASE_URL + f"/users/{user_id}/get"
    response = requests.post(url)
    if response.status_code == 200:
        document = response.json()
        print(f"User with ID {user_id} has '{document['username']}' as username and '{document['password']}' as password.")
    else:
        print(f"Failed to retrieve information of user {user_id}.")
        print_and_exit(response)

print("")
print("End of the script.")
