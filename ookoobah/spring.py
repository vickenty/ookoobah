__all__ = [ 'Spring' ]

class Spring (object):
    def __init__(self, value, speed, snap):
        self.value = self.next_value = value
        self.speed = speed
        self.snap = snap

    def tick(self):
        delta = self.next_value - self.value
        if abs(delta) < self.snap:
            self.value = self.next_value.copy()
        else:
            self.value += delta * self.speed

