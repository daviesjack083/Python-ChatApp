import random

# Username change
def set_username(name_list):
    name_list = name_list.split(' ')
    name_list.pop(0)

    username = ""
    for name in name_list:
        username = username + " " + name.capitalize()

    return username.strip()
