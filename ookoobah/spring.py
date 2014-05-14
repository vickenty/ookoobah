__all__ = [ 'Spring' ]

class Spring (object):
    def __init__(self, value, speed, snap):
        self.value = self.next_value = value
        self.speed = speed
        self.snap = snap
        self.static = True

    def tick(self):
        delta = self.next_value - self.value
        if abs(delta) < self.snap:
            self.value = self.next_value.copy()
            self.static = True
        else:
            self.value += delta * self.speed
            self.static = False
