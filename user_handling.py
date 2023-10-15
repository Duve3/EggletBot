from json_handling import ObjectEncoder, ObjectDecoder
import json

USER_DEFAULT_DATA = {"money": 0, "people": [], "xp": 0, "level": 0, "inv": [], "perms": [False, False, False]}


class User:
    def __init__(self, uid: int, new: bool = False):
        file_name = f"./db/users/{uid}.json"
        self._f = file_name
        self._d = {}
        if new:
            self.resetUser()
            self.reload()
        try:
            with open(file_name, 'r') as f:
                r = f.read()
                if r == "{}" or r == "":
                    self.resetUser()
                    self.reload()
                self._d = json.loads(r, cls=ObjectDecoder)
        except FileNotFoundError:
            self.resetUser()
            self.reload()

        # attrs
        self.money = float(self._d["money"])
        self.people = self._d["people"]
        self.xp = float(self._d["xp"])
        self.level = float(self._d["level"])
        self.inv = self._d["inv"]
        self.permissions = [False, False, False]
        self.getPermissions()

    def getPermissions(self):
        if "perms" in self._d:
            self.permissions = self._d["perms"]

        else:
            self.permissions = [False, False, False]

    def save(self):
        self._d["money"] = self.money
        self._d["people"] = self.people
        self._d["xp"] = self.xp
        self._d["level"] = self.level
        self._d["inv"] = self.inv
        self._d["perms"] = self.permissions
        with open(self._f, 'w') as f:
            f.write(json.dumps(self._d, cls=ObjectEncoder))
            f.truncate()

    def reload(self):
        with open(self._f, 'r') as f:
            self._d = json.loads(f.read(), cls=ObjectDecoder)

        self.money = float(self._d["money"])
        self.people = self._d["people"]
        self.xp = float(self._d["xp"])
        self.level = float(self._d["level"])
        self.inv = self._d["inv"]
        self.getPermissions()

    def resetUser(self):
        with open(self._f, 'w') as f:
            f.write(json.dumps(USER_DEFAULT_DATA, cls=ObjectEncoder))
            f.truncate()

        self._d = USER_DEFAULT_DATA

        self.money = float(self._d["money"])
        self.people = self._d["people"]
        self.xp = float(self._d["xp"])
        self.level = float(self._d["level"])
        self.inv = self._d["inv"]

        self.getPermissions()

    def __str__(self, t: bool = False):
        return prettify(self._d, t)

    def __eq__(self, other):
        if not isinstance(other, User):
            return False

        if other._f == self._f:
            return True

        return False


def prettify(d: dict, t: bool = False):
    rep = ""

    for k, v in d.items():
        if t:
            rep += f"{k}: {v} (type: '{type(v)}'), "
        else:
            rep += f"{k}: {v}, "

    return rep
