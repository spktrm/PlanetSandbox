import numpy as np
import random
import pygame as pg
import sys

from point import Point, gravity_constant
from pygame import gfxdraw
from copy import deepcopy

width = 1920
height = 1080

WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLACK = (0, 0, 0)

running = True


def render_points():

    global scale

    gridsize = 60
    lat_lines = [((int(i * gridsize), 0), (int(i * gridsize), height)) for i in range(1, int(width/gridsize))]
    lon_lines = [((0, int(i * gridsize)), (width, int(i * gridsize))) for i in range(1, int(height/gridsize))]
    for i in lat_lines:
        pg.draw.aaline(screen, (50, 50, 50), i[0], i[1])
    for i in lon_lines:
        pg.draw.aaline(screen, (50, 50, 50), i[0], i[1])

    for i in range(len(points)):
        pos = points[i].get_pos()
        color = points[i].get_color()
        r = int(points[i].radius) 

        gfxdraw.aacircle(screen, pos[0], pos[1], r, color)
        gfxdraw.filled_circle(screen, pos[0], pos[1], r, color)


def update_points(dt):
    global points

    for i in range(len(points)):
        points[i].update_velocity(points, dt)

    for i in range(len(points)):
        try:
            p1 = points[i]
            p1.update_position(dt)
        except IndexError:
            continue

        for j in range(len(points)):
            if i == j:
                continue
            try:
                p2 = points[j]
            except IndexError:
                continue
            pos1 = p1.get_pos()
            pos2 = p2.get_pos()
            r1 = p1.radius
            r2 = p2.radius

            distance = np.linalg.norm(pos1 - pos2)
            if distance < (r1 + r2):

                m1 = p1.mass
                m2 = p2.mass
                v1 = p1.velocity
                v2 = p2.velocity
                a1 = p1.acceleration
                a2 = p2.acceleration
                c1 = p1.color
                c2 = p2.color

                # impact_force = m1 * a1 + m2 * a2
                # p1_thresh = gravity_constant * m1 ** 2 / (0.75 * r1) ** 2
                # p2_thresh = gravity_constant * m2 ** 2 / (0.75 * r2) ** 2
                # total_mass = m1 + m2
                    
                new_pos = (m1 * pos1 + m2 * pos2) / (m1 + m2)
                new_pos = new_pos.astype(int)
                new_color = tuple([int((c1[i] + c2[i])/2) for i in range(3)])
                new_radius = ((4/3 * np.pi * (r1 ** 3 + r2 ** 3)) / (4/3 * np.pi)) ** (1/3)
                new_point = Point(pos=new_pos, radius=new_radius, bounds=(width, height), color=new_color)
                new_point.velocity = (m1 * v1 + m2 * v2)/new_point.mass
                new_point.acceleration = (m1 * a1 + m2 * a2)/new_point.mass

                points.append(new_point)

                try:
                    points.remove(p1)
                except ValueError:
                    pass
                try:
                    points.remove(p2)
                except ValueError:
                    pass


def draw_ghost():
    pos = pg.mouse.get_pos()
    gfxdraw.aacircle(screen, pos[0], pos[1], radius, WHITE)


def draw_LOS(start_pos):
    pos = pg.mouse.get_pos()
    pg.draw.aaline(screen, WHITE, start_pos, (pos[0], pos[1]))


def draw_trajectory(start_pos, dt):
    global points
    depth = 400

    trails = {}

    end_pos = np.array(pg.mouse.get_pos())
    d = np.linalg.norm(start_pos - end_pos)
    if d != 0:
        v = (end_pos - start_pos)/10
    else:
        v = np.array([0, 0])

    fake_point = Point(pos=start_pos, velocity=v, radius=radius, color=(255, 255, 255), bounds=(width, height))
    test_points = deepcopy(points)
    test_points.append(fake_point)

    for i in test_points:
        trails[i] = []

    for d in range(depth):
        
        for i in range(len(test_points)):
            test_points[i].update_velocity(test_points, dt)

        for i in range(len(test_points)):
            try:
                p1 = test_points[i]
                p1.update_position(dt)
            except IndexError:
                continue

            for j in range(len(test_points)):
                if i == j:
                    continue
                try:
                    p2 = test_points[j]
                except IndexError:
                    continue
                pos1 = p1.get_pos()
                pos2 = p2.get_pos()
                r1 = p1.radius
                r2 = p2.radius

                distance = np.linalg.norm(pos1 - pos2)
                if distance < (r1 + r2):

                    m1 = p1.mass
                    m2 = p2.mass
                    v1 = p1.velocity
                    v2 = p2.velocity
                    a1 = p1.acceleration
                    a2 = p2.acceleration
                    c1 = p1.color
                    c2 = p2.color

                    new_pos = (m1 * pos1 + m2 * pos2) / (m1 + m2)
                    new_pos = new_pos.astype(int)
                    new_color = tuple([int((c1[i] * m1 + c2[i] * m2)/(m1 + m2)) for i in range(3)])
                    new_radius = ((4/3 * np.pi * (r1 ** 3 + r2 ** 3)) / (4/3 * np.pi)) ** (1/3)
                    new_point = Point(pos=new_pos, radius=new_radius, bounds=(width, height), color=new_color)
                    new_point.velocity = (m1 * v1 + m2 * v2)/new_point.mass
                    new_point.acceleration = (m1 * a1 + m2 * a2)/new_point.mass

                    test_points.append(new_point)
                    trails[new_point] = []
                    try:
                        test_points.remove(p1)
                    except ValueError:
                        pass
                    try:
                        test_points.remove(p2)
                    except ValueError:
                        pass

        for i in trails: 
            trails[i].append(i.get_pos())

    for i in trails:
        if len(trails[i]) > 2:
            pg.draw.aalines(screen, i.color, False, np.array(trails[i]).astype('int'))

def display_fps():
    text_to_show = pg.font.SysFont("Arial", 18).render(str(int(clock.get_fps())), 0, pg.Color(255, 255, 255))
    screen.blit(text_to_show, (0, 0))

def display_paused():
    if update == False:
        text_to_show = pg.font.SysFont("Arial", 18).render(str("paused"), 0, pg.Color(255, 255, 255))
        screen.blit(text_to_show, (width - 50, 0))
    elif update == True:
        text_to_show = pg.font.SysFont("Arial", 18).render(str("playing"), 0, pg.Color(255, 255, 255))
        screen.blit(text_to_show, (width - 50, 0))

def main():
    global running, screen, clock, points, radius, update, new_color, scale

    fps = 60
    scale = 1

    radius = 5
    points = []

    pg.init()
    screen = pg.display.set_mode((width, height), pg.FULLSCREEN)
    # screen = pg.display.set_mode((width, height))
    pg.display.set_caption("Gravity Sim")
    screen.fill((0, 0, 0))
    pg.display.update()
    clock = pg.time.Clock()

    mode = 0
    scale_mode = 0
    update = True
    trajectories = True

    while running:
        dt = fps/50

        screen.fill((0, 0, 0))

        display_fps()
        display_paused()
        render_points()
        draw_ghost()

        if update:
            update_points(dt)
        
        if mode == 1:
            draw_LOS(start_pos)
            if trajectories:
                draw_trajectory(start_pos, dt)

        for event in pg.event.get():
            if event.type == pg.KEYDOWN:
                
                if event.key == pg.K_r:
                    points = []

                if event.key == pg.K_a:
                    # print("aim")
                    start_pos = np.array(pg.mouse.get_pos())
                    mode = 1

                if event.key == pg.K_d:
                    if mode == 1:
                        end_pos = np.array(pg.mouse.get_pos())
                        d = np.linalg.norm(start_pos - end_pos)
                        if d != 0:
                            v = (end_pos - start_pos)/10
                        else:
                            v = np.array([0, 0])
                        new_color = tuple(random.randint(0, 255) for i in range(3))
                        points.append(Point(pos=start_pos, radius=radius, velocity=v, color=new_color, bounds=(width, height)))

                if event.key == pg.K_SPACE:
                    if update == True:
                        update = False
                    elif update == False:
                        update = True

                if event.key == pg.K_t:
                    if trajectories == True:
                        trajectories = False
                    elif trajectories == False:
                        trajectories = True

                if event.key == pg.K_LCTRL:
                    scale_mode = 1
                
                if event.key == pg.K_ESCAPE:
                    pg.quit()
                    sys.exit()

            if event.type == pg.KEYUP:
                if event.key == pg.K_a:
                    mode = 0

                if event.key == pg.K_LCTRL:
                    scale_mode = 0

            if event.type == pg.MOUSEBUTTONDOWN:
                if scale_mode == 0:
                    if event.button == 4:
                        radius += 1

                    elif event.button == 5:
                        radius -= 1
                        if radius < 1:
                            radius = 1
                else:
                    if event.button == 4:
                        scale += 0.01 * screen.get_width()

                    elif event.button == 5:
                        scale -= 0.01 * screen.get_width()
                        if scale < 0.01:
                            scale = 0.01 * screen.get_width()

                    for i in range(len(points)):
                        points[i].scale_vals(scale)

        clock.tick(fps)
        pg.display.update()

if __name__ == '__main__':
    main()
