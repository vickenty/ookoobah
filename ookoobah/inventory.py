from collections import defaultdict
class Inventory (object):
    class Error (Exception):
        pass

    def __init__(self):
        self.inventory = defaultdict(int)

    def use_block(self, block_class):
        if block_class not in self.inventory:
            raise Inventory.Error("Can't let you do that")
        
        if self.inventory[block_class] < 1:
            raise Inventory.Error("I'm all out of gum")

        self.inventory[block_class] -= 1

    def add_block(self, block_class):
        self.inventory[block_class] += 1

    def items(self):
        return self.inventory.items()

if __name__ == '__main__':
    inv = Inventory()
    inv.add_block(Inventory)
    inv.use_block(Inventory)
    try:
        inv.use_block(Inventory)
    except Exception as e:
        print e
    try:
        inv.use_block(Inventory.Error)
    except Exception as e:
        print e
