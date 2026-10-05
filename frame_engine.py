class Frame:

    def __init__(self, name, parent=None):
        self.name = name
        self.parent = parent
        self.slots = {}

    def set_slot(self, slot, value):
        self.slots[slot] = value

    def get_slot(self, slot):

        if slot in self.slots:
            return self.slots[slot]

        if self.parent is not None:
            return self.parent.get_slot(slot)

        return None

    def all_slots(self):

        result = {}

        if self.parent is not None:
            result.update(
                self.parent.all_slots()
            )

        result.update(self.slots)

        return result