# Task Tracker

Live and working micro-service showcasing the Endpoints standard from Byteplug
(equivalent of the Petstore service from OAS). It aims to be as simple as
possible, yet showing every features of the standard, and an example for other
developers.

## How to use

To start the server (the GCP JSON key is needed to access the Firestore
database).

```
export GOOGLE_APPLICATION_CREDENTIALS="gcp-key.json"
python task_manager.py
```

To clear users periodically (so the database doesn't grow in size too much),
the following script can be executed periodically.

```
python clean_tasks.py
```

To toy around with the micro-service and see if everything works well, the
`test_service.py` script can be used.

```
python test_service.py
```
```
In order to interact (and test) the Task Tracker service, this script will create a new user, create a few tasks and edit them. Before completing, it will probe the service status. Note that you are still able to interact with the service using the same username and password after the script has completed.

Generated username and password.

  username: adavis
  password: 8Q7Yp1xQbQ

Do you want to continue ?

Login successful.

Token: eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyLWtleSI6InVzZXJzL3hrWW5obnZoRlFZUDFMa1VPRkJFIn0.6ltKxbp9qN1-QH64pgQxxI1IR8JRqQmCH00P6V_RJeI

This token will be used in all subsequent requests.

Create task "My Task"...
...task created with ID dfxdr4qxX8C39CYhrBT7

Renaming "My Task" to "My Super Task" and give it a description...
...task successfully updated.

Marking "My Super Task" as 'in-progress'...
...task successfully updated.

Check current state of our task to see if it was updated correctly.

Name: My Super Task
Description: This is a super task. Very important.
Status: in-progress

All OK.

Creating 3 new tasks (task A, task B and task C)

Task A created with ID 7UHlMyTKLtUQAnVS3SgW
Task B created with ID eglyvG13fLMllJafcfho
Task C created with ID dxLqvMZNMH8XAfkQbCEH

Marking all tasks as done...
Tasks successfully updated.

List all existing tasks...
Task IDs are:  ['7UHlMyTKLtUQAnVS3SgW', 'dfxdr4qxX8C39CYhrBT7', 'dxLqvMZNMH8XAfkQbCEH', 'eglyvG13fLMllJafcfho']

Deleting task A, task B and task C...
Task A successfully deleted.
Task B successfully deleted.
Task C successfully deleted.

The only remaining task is "My Super Task" now.

Probing service status now...

Number of users: 10
Number of tasks: 27
Average number of tasks per user: 2.7
Session duration:  60 minutes (the time before data are wiped)
Maximum number of task per user: 100

Listing all existing users...
User IDs are:  ['6sttzmCA6iJyH7cplT12', 'COqdU2jfDbQX13Q8lHfm', 'HGGKut1JL7EeR0qrp2Vn', 'JPPapbOSYxsqgihrzerp', 'RmLeWLOns0IXe9VmnAuY', 'UJnibNnlqWY9JxatYTq6', 'hLoNByeg4MDSjyAWzI00', 'pq0G8AsQIkZp1Fv7sUeU', 'wsYFTkennouHRj5ryz9U', 'xkYnhnvhFQYP1LkUOFBE']

Picking 3 of the users and displaying their information...

User with ID pq0G8AsQIkZp1Fv7sUeU has 'schneiderglenda' as username and '0qQD1sfZSA' as password.
User with ID RmLeWLOns0IXe9VmnAuY has 'dfoster' as username and '6ocFXQBl5l' as password.
User with ID 6sttzmCA6iJyH7cplT12 has 'jrusso' as username and '4Wy3F3IZ7m' as password.

End of the script.
```
