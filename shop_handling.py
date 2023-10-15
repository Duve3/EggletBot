import random


class Item:
    def __init__(self, data):
        self.name = data["name"]
        self.weight = data["weight"]
        self.info = data["info"]
        self.price = data["price"]


class Shop:
    def __init__(self, items: list):
        self.items: list[Item] = []
        for i in items:
            self.items.append(Item(i))

    def randomItem(self) -> Item:
        return random.choice(self.items)
