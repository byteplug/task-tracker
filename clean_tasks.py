
# Copyright (c) 2022 - Byteplug Inc.
#
# This source file is part of the Byteplug toolkit for the Python programming
# language which is released under the OSL-3.0 license. Please refer to the
# LICENSE file that can be found at the root of the project directory.
#
# Written by Jonathan De Wachter <jonathan.dewachter@byteplug.io>, July 2022

from datetime import datetime, timedelta
from fireo.models import Model
from fireo.fields import TextField, DateTime

# Dirty copy-pasted from task_tracker.py; to be kept in sync!!
class User(Model):
    username = TextField(required=True)
    password = TextField(required=True)
    last_updated = DateTime(required=True)

    class Meta:
        collection_name = "users"

for user_document in User.collection.fetch():
    elapsed_time = datetime.now() - user_document.last_updated.replace(tzinfo=None)
    if elapsed_time > timedelta(minutes=60):
        print(f"Deleting user {user_document.id}")
        User.collection.delete(user_document.key)
