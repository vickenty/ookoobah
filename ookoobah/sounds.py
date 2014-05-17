import pyglet

sounds = {}

all_sounds = [
    'boom.wav',
    'charge.wav',
    'flip-off.wav',
    'flip-on.wav',
    'mirror.wav',
    'noway.wav',
    'portal.wav',
    'start.wav',
    'wall.wav',
]

def load():
    for name in all_sounds:
        try:
            sounds[name] = pyglet.resource.media(name, streaming=False)
        except Exception as e:
            print 'Failed to load %s: %s' % (name, e)

def play(name, volume=0.4):
    player = sounds[name].play()
    player.volume = volume
    return player
