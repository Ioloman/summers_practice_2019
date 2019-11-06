import random
from math import sin, cos, radians, sqrt


class SimObject(object):
    def __init__(self):
        self._x_coord = random.randint(0, FIELD_WIDTH)
        self._y_coord = random.randint(0, FIELD_HEIGHT)
        self._size = 5

    def get_canvas_location(self):
        return self._x_coord - self._size, self._y_coord - self._size, \
               self._x_coord + self._size, self._y_coord + self._size

    def get_coords(self):
        return self._x_coord, self._y_coord


class Food(SimObject):
    def __init__(self, env):
        super().__init__()


FIELD_HEIGHT = 500
FIELD_WIDTH = 500
FRAMERATE = 1  # ms
FOOD_AMOUNT = 50
AMOUNT = 10
ANGLE_CHANGE = 17
MUTATION_CHANCE = 20
BREED_CHANCE = 50


def _get_coord_from_p(p):
    if p <= FIELD_WIDTH:
        return p, 0, 270
    elif FIELD_WIDTH < p <= FIELD_HEIGHT + FIELD_WIDTH:
        return FIELD_WIDTH, p - FIELD_WIDTH, 180
    elif FIELD_HEIGHT + FIELD_WIDTH < p <= FIELD_HEIGHT + FIELD_WIDTH + FIELD_HEIGHT:
        return FIELD_WIDTH - (p - FIELD_HEIGHT - FIELD_WIDTH), FIELD_HEIGHT, 90
    elif FIELD_HEIGHT + FIELD_WIDTH + FIELD_HEIGHT < p <= FIELD_HEIGHT * 2 + FIELD_WIDTH * 2:
        return 0, FIELD_HEIGHT * 2 + FIELD_WIDTH * 2 - p, 0


def _change_angle(angle, val, dir):
    if dir:
        val = val
    else:
        val = -val
    if angle + dir > 359:
        angle = angle + val - 360
    elif angle + dir < 0:
        angle = angle + val + 360
    else:
        angle = angle + val

    return angle


class Entity(SimObject):
    _food_list = []

    @staticmethod
    def set_food(food_list):
        Entity._food_list = food_list

    @staticmethod
    def get_food():
        return Entity._food_list

    def __init__(self, env, params=False, mutation=False):
        super().__init__()
        self._basic_speed = 5
        self._size = 10
        self._basic_distance = 500
        self._range = 35
        self._x_coord, self._y_coord, self._angle =\
            _get_coord_from_p(random.randint(0, FIELD_HEIGHT * 2 + FIELD_WIDTH * 2))
        self._angle_dir = True if random.randint(0, 1) == 1 else False
        self._count = 0
        self._x_change = 0
        self._y_change = 0
        self._target = False
        self._env = env
        self._action = env.process(self.move())
        self._wait = 0
        self.food_consumed = 0
        self.done = False
        self.mutation = mutation
        if params:
            self._basic_speed, self._range, self._basic_distance = params
        self._speed = self._basic_speed
        self._distance = self._basic_distance

    def copy(self, speed=0, range=0, distance=0):
        params = [self._basic_speed+speed, self._range+range, self._basic_distance+distance]
        return Entity(self._env, params, mutation=self.mutation)

    def move(self):
        while True:
            if self._distance <= 0:
                self._speed = 0
                self.done = True
            if self._wait > 0:  # eating
                self._wait -= 1
                self._x_change = 0
                self._y_change = 0
            else:
                if self.food_consumed >= 2:  # returning back
                    self._angle = self._closest_border()
                    self._x_change = cos(radians(self._angle)) * self._speed
                    self._y_change = - sin(radians(self._angle)) * self._speed
                    self._distance -= self._speed
                    if self._x_coord <= 0 or self._x_coord >= FIELD_WIDTH or \
                            self._y_coord <= 0 or self._y_coord >= FIELD_HEIGHT:
                        self._x_change = 0
                        self._y_change = 0
                        self.done = True
                else:  # moving
                    self._target = self._is_food_close() if self._speed else False
                    if self._target:  # going to eat food
                        self._x_change, self._y_change = self._target['change']
                        self._distance -= self._speed
                    else:  # moving around
                        if self._count > 10 and random.randint(0, 5) == 3:
                            self._angle_dir = False if self._angle_dir else True
                            self._count = 0
                        if self._y_coord - self._range < 0 and 0 < self._angle < 180 or \
                                self._y_coord + self._range > FIELD_HEIGHT and 180 < self._angle < 360 or \
                                self._x_coord - self._range < 0 and 90 < self._angle < 270 or \
                                self._x_coord + self._range > FIELD_WIDTH and (self._angle < 90 or 270 < self._angle):
                            self._angle = self._angle + 90
                        self._angle = _change_angle(self._angle, random.randint(0, ANGLE_CHANGE), self._angle_dir)
                        self._count += 1
                        self._x_change = cos(radians(self._angle)) * self._speed
                        self._y_change = - sin(radians(self._angle)) * self._speed
                self._x_coord = self._x_coord + self._x_change
                self._y_coord = self._y_coord + self._y_change
                self._distance -= self._speed
            yield self._env.timeout(FRAMERATE)

    def _closest_border(self):
        top, left, right, bottom = self._y_coord, self._x_coord, FIELD_WIDTH - self._x_coord, FIELD_HEIGHT - self._y_coord
        if min(top, bottom, right, left) == top:
            return 90
        elif min(top, bottom, right, left) == bottom:
            return 270
        elif min(top, bottom, right, left) == right:
            return 0
        elif min(top, bottom, right, left) == left:
            return 180

    def _is_food_close(self):
        for food_piece in Entity._food_list:
            x2, y2 = food_piece.get_coords()
            x = x2 - self._x_coord
            y = y2 - self._y_coord
            hyp = sqrt(x**2 + y ** 2)
            x_change = x / (hyp / self._speed)
            y_change = y / (hyp / self._speed)
            if hyp <= sqrt(2 * self._size**2):
                Entity._food_list.remove(food_piece)
                self._wait = 10
                self.food_consumed += 1
                self._distance += 500
                return False
            if hyp <= self._range:
                return {'object': food_piece, 'change': (x_change, y_change)}
        else:
            return False

    def reset(self):
        spawn_point = _get_coord_from_p(random.randint(0, FIELD_HEIGHT * 2 + FIELD_WIDTH * 2))
        try:
            self._x_coord, self._y_coord, self._angle = spawn_point
        except TypeError:
            print(type(spawn_point))
            exit(0)
        self._speed = self._basic_speed
        self._distance = self._basic_distance
        self._count = 0
        self._x_change = 0
        self._y_change = 0
        self._target = False
        self._wait = 0
        self.food_consumed = 0
        self.done = False

    def breed(self):
        if random.randint(1, 100) <= BREED_CHANCE:
            return None
        mutation = True if random.randint(1, 100) <= MUTATION_CHANCE else False
        if mutation:
            what_mutation = random.randint(1, 3)
            if what_mutation == 1:
                baby = self.copy(speed=1, distance=-50)
            elif what_mutation == 2:
                baby = self.copy(range=10, speed=-0.5)
            elif what_mutation == 3:
                baby = self.copy(distance=100, range=-5)
            baby.mutation = True
        else:
            baby = self.copy()
        return baby

    def params(self):
        return self._basic_speed, self._basic_distance, self._range

