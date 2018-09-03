from collections import OrderedDict
from .models import GameObject
from .world import GameWorld, DIRECTIONS

# There are three phases to mapping:
# 1. walking rooms
# 2. generating the mapfile
# 3. calling out to Graph::Easy and passing the mapfile.
#
# a mapfile looks like this:
#
# [ Room Name 0 ] -- direction --> [ Room Name 1 ]
# [ Room Name 1 ] -- direction --> [ Room Name 2]
# ...

def mapfile_for_room(mapped, room):
    return [
        '[ {from_room} ] -- {direction} --> [ {to_room} ]'.format(
            from_room=room.name,
            direction=d,
            to_room=r.name)
        for d,r in adjacent(room)
        if r.shortname not in mapped]

def adjacent(room):
    out = []
    for d in DIRECTIONS:
        e = GameWorld.resolve_exit(room, d)
        if e is None: continue
        route = e.get_data('exit').get(room.shortname)
        target_room = GameObject.get_or_none(GameObject.shortname==route[1])
        out.append((d,target_room))

    return out

def build_queue(queue, room):
    if queue[room.shortname] == 0:
        return
    else:
        for d,r in adjacent(room):
            if r.shortname in queue: continue
            queue[r.shortname] = queue[room.shortname] - 1
            build_queue(queue, r)

def from_room(room, distance=3):
    if distance < 0:
        raise ValueError('distance must be greater than 0')

    queue = OrderedDict()
    queue[room.shortname] = distance
    build_queue(queue, room)
    mapped = set()
    mapfile = []
    for room_name in queue.keys():
        room = GameObject.get(GameObject.shortname==room_name)
        mapfile.extend(mapfile_for_room(mapped, room))
        mapped.add(room_name)

    return '\n'.join(mapfile)