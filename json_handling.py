import json
from shop_handling import Item


class ObjectEncoder(json.JSONEncoder):
    def default(self, o):
        """
        A recursive function for easily handling complex objects.
        :param o: Object
        :return: dict
        """
        try:
            d: dict = o.__dict__
        except AttributeError:
            return o
        for key, obj in d.items():
            if not self.isDecode(obj):
                r = self.default(obj)
                r["_type"] = type(obj)
                d[key] = r

        return d

    def isDecode(self, o):
        try:
            self.default(o)
            return True
        except json.JSONDecodeError:
            return False


class ObjectDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        super().__init__(object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, obj):
        if "_type" not in obj:
            return obj
        t = obj["_type"]

        if t.lower() == "item":
            i = Item(obj)

            for k, o in i.__dict__.items():
                if not self.isEncode(o):
                    i.__dict__[k] = self.object_hook(o)

    def isEncode(self, o):
        try:
            a = o["_type"]
            return False
        except KeyError:
            return True

