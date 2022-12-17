import json
import random

from config import JSON_PATH


class JsonHandler:

    def __init__(self):
        self.secret_Santa_list = []
        self.users_list = []
        self.path_to_json = JSON_PATH

    def write_json(self, new_data):
        with open(self.path_to_json, 'r+') as file:
            file_data = json.load(file)
            file_data["users"].append(new_data)
            file.seek(0)
            json.dump(file_data, file, indent=4)

    def get_users_list(self):
        with open(self.path_to_json, 'r') as f:
            users_list = json.load(f)["users"]
            return users_list

    def get_id_list(self):
        users_list = self.get_users_list()
        return [user['chat_id'] for user in users_list]

    def secret_Santa(self, to_whom):
        who = random.choice(self.users_list)
        if to_whom["chat_id"] == who["chat_id"]:
            self.secret_Santa(to_whom)
        else:
            self.users_list.remove(who)
            self.secret_Santa_list.append({to_whom["chat_id"]: who["full_name"]})
