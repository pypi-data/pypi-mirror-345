from .Item import Item

class Inventory:
    def __init__(self):
        self.inventory = []

    def get_inventory(self):
        return self.inventory
    
    def add_item(self, item_name, amount = 1):
        item_index = self.where(item_name)

        if item_index == -1:
            item = Item(item_name, amount)
            self.inventory.append(item)
        else:
            self.inventory[item_index].add_amount(amount)
    
    def get_item_at_index(self, index):
        return self.inventory[index].get_name()

    def get_item_amount_at_index(self, index):
        return self.inventory[index].get_amount()
    
    def get_item_amount(self, item_name):
        item_index = self.where(item_name)
        if item_index != -1:
            return self.inventory[item_index].get_amount()
        return -1
    
    def remove_item(self, item_name, amount = 1):
        item_index = self.where(item_name)
        if item_index != -1:
            self.inventory[item_index].subtract_amount(amount)
            if self.inventory[item_index].get_amount() < 1:
                del self.inventory[item_index]

    def remove_item_at_index(self, index, amount = 1):
        self.inventory[index].subtract_amount(amount)
        if self.inventory[index].get_amount() < 1:
            del self.inventory[index]

    def where(self, item_name):
        for i, object in enumerate(self.inventory):
            if object.name == item_name:
                return i
        return -1
    
    def list_inventory(self, symbol = ")"):
        for i, item in enumerate(self.inventory):
            print(f"{i}{symbol} {item.get_name()}")
    
    def display_inventory(self):
        for item in self.inventory:
            print(item.get_amount())
