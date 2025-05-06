class Item:
    def __init__(self, name, amount):
        self.name = name
        self.amount = amount

    def get_name(self):
        return self.name

    def get_amount(self):
        return self.amount
    
    def add_amount(self, amount):
        self.amount += amount

    def subtract_amount(self, amount):
        self.amount -= amount
    
    def __repr__(self):
        return f"Item(name: {self.name}, amount: {self.amount})"

    def __eq__(self, value):
        if isinstance(value, Item):
            raise(TypeError)
        if self.name == value.name:
            return True
        return False