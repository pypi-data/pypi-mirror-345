# Description

This package is used if you want a simple inventory for a text based game or just in general. This package is in development and in a testing stage.

# Basic Usage


```python
from gameinventory import Inventory
inventory = Inventory()
inventory.add_item("YOUR ITEM")
print(inventory.get_inventory()) # Output: [Item(name: "Your item", amount: 1)]
```

# Functions

These are the current functions


| Functions                                            | Description                                                  |
| ---------------------------------------------------- | ------------------------------------------------------------ |
| add_item(item: str, amount: int = 1) -> None         | Adds a item to the inventory                                 |
| remove_item(item_name: str, amount: int = 1) -> None | Removes a item in the inventory                              |
| get_item_at_index(index: int) -> str                 | Returns the item in the inventory at index                   |
| get_item_amount(item_name: str) -> int               | Returns the item amount at a index                           |
| get_inventory() -> list                              | returns list inventory                                       |
| where(item_name: str) -> int                         | returns the index of an item                                 |
| list_inventory() -> None                             | Prints all the items with a number besides them indicating them |
| display_inventory() -> None                          | Prints all the items in the inventory                        |

