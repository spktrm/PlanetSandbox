import numpy as np
import random

gravity_constant = 0.1

class Point(object):

    def __init__(self, pos=None, velocity=None, acceleration=None, radius=None, color=None, bounds=None):

        if pos is None:
            self.pos = np.array([0, 0], dtype='float64')
        else:
            self.pos = np.array(pos, dtype='float64')

        if velocity is None:
            self.velocity = np.array([0, 0], dtype='float64')
        else:
            self.velocity = np.array(velocity, dtype='float64')

        if acceleration is None:
            self.acceleration = np.array([0, 0], dtype='float64')
        else:
            self.acceleration = np.array(acceleration, dtype='float64')

        self.radius = radius

        self.mass = (4*np.pi/3*(self.radius)**3)

        self.bounds = bounds
        
        if color is None:
            self.color = tuple(random.randint(0, 255) for i in range(3))
        else:
            self.color = color

        self.id = random.randint(0, 2**32 - 1)

    def __eq__(self, other):
        if self.id == other.id:
            return True
        else:
            return False

    def __hash__(self):
        return hash(self.id)

    def get_pos(self):
        return self.pos.astype('int')

    def get_color(self):
        return self.color

    def get_mass(self):
        return self.mass

    def get_force(self, other_point):

        self_pos = self.get_pos()
        other_pos = other_point.get_pos()

        distance = np.linalg.norm(other_pos - self_pos)

        if distance < (self.radius + other_point.radius):
            force = np.array([0, 0], dtype='float64')
        else:
            force_direction = (self_pos - other_pos)/distance
            force = force_direction * gravity_constant * (self.get_mass() * other_point.get_mass()) / (distance ** 2)

        return -1 * force

    def update_velocity(self, points, dt):
        total_force = np.array([0, 0], 'float64')

        for i in range(len(points)):
            if self.__eq__(points[i]):
                continue
            force = self.get_force(points[i])
            total_force += force

        self.acceleration = total_force / self.mass
        self.velocity += self.acceleration * dt
    
    def update_position(self, dt):

        self.pos += self.velocity * dt
        if self.bounds is not None:
            if self.pos[0] < 0:
                self.pos[0] = 0
                self.velocity[0] *= -.8
                self.acceleration[0] = 0
            elif self.pos[0] > self.bounds[0]:
                self.pos[0] = self.bounds[0]
                self.velocity[0] *= -.8
                self.acceleration[0] = 0
            if self.pos[1] < 0:
                self.pos[1] = 0
                self.velocity[1] *= -.8
                self.acceleration[1] = 0
            elif self.pos[1] > self.bounds[1]:
                self.pos[1] = self.bounds[1]
                self.velocity[1] *= -.8
                self.acceleration[1] = 0
        
        