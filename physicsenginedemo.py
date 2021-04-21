import pygame
from pygame.locals import *
import threading as t
import time, sys, random
from random import randint

pygame.mixer.pre_init(44100, -16, 2, 2048)
pygame.mixer.init()
pygame.init()

INITIATEEXIT = False

class Vector2:
    """A class used to represent vectors"""
    def __init__(self, x=0, y=0):
    
        self.x, self.y = x, y
        
    def get_magnitude(self):
        
        return (self.x**2 + self.y**2)**(0.5)
    
    #vector algebra
    def __add__(self, other): 
        return Vector2(self.x+other.x, self.y+other.y)
    def __sub__(self, other):
        return Vector2(self.x-other.x, self.y-other.y)
    def __mul__(self, other):
        #scalar multiplication
        if isinstance(other, int) or isinstance(other, float):
            return Vector2(self.x*other, self.y*other)
        #dot product
        if isinstance(other, Vector2):
            return self.x*other.x + self.y*other.y
    def __nonzero__(self):
        #for boolean calculations (truth values)
        return (self.x != 0 or self.y != 0)
    __bool__ = __nonzero__
    def __eq__(self, other):
        #check if 2 vectors are equal
        return (self.x == other.x and self.y == other.y)
    def __str__(self):
        return "Vector2(x={}, y={})".format(self.x, self.y)
    def __neg__(self):
        return Vector2(-self.x, -self.y)
    

class Rectangle_fx:
    
    def __init__(self, emerge_from=(0, 0)):
        
        self.emerge_from = emerge_from
        
        self.particles = []
        
        self.ended = False
        
        self.create_particles()
        
        t.Thread(target=self.animate_particles).start()
        
    def create_particles(self):
        
        ex, ey = self.emerge_from
        
        for i in range(1, 11):
            
            while True:
                
                r = pygame.Rect(ex + random.randint(0, 15), ey + random.choice([-1, 1])*random.randint(0, 15), 4, 4)
                
                for i in self.particles:
                    if i.colliderect(r):
                        break
                else:
                    self.particles.append(r)
                    break
                
        for i in range(11, 21):
            
            while True:
                
                r = pygame.Rect(ex - random.randint(0, 15), ey - random.choice([-1, 1])*random.randint(0, 15), 4, 4)
                
                for i in self.particles:
                    if i.colliderect(r):
                        break
                else:
                    self.particles.append(r)
                    break
                
        for i in range(1, 11):
            
            while True:
                
                r = pygame.Rect(ex + random.choice([-1, 1])*random.randint(0, 15), ey + random.randint(0, 15), 4, 4)
                
                for i in self.particles[21:]:
                    if i.colliderect(r):
                        break
                else:
                    self.particles.append(r)
                    break
                
        for i in range(11, 21):
            
            while True:
                
                r = pygame.Rect(ex + random.choice([-1, 1])*random.randint(0, 15), ey - random.randint(0, 15), 4, 4)
                
                for i in self.particles[21:]:
                    if i.colliderect(r):
                        break
                else:
                    self.particles.append(r)
                    break
        
    def animate_particles(self):
        
        global INITIATEEXIT
        
        ref = 0
        ex, ey = self.emerge_from
        
        while ref < 6 and not(INITIATEEXIT):
            
            for i in self.particles[0:21]:
                if i.x < ex:
                    i.x -= 1
                else:
                    i.x += 1
            for i in self.particles[21:41]:
                if i.y < ey:
                    i.y -= 1
                else:
                    i.y += 1
                    
            ref += 1
            time.sleep(1/60)
        
        else:
            self.ended = True
            
    def draw(self, dis):
        
        for i in self.particles:
                pygame.draw.rect(dis, (0, random.randint(0, 255), random.randint(128, 255), 255), i)
                
        
class CollisionHandler:
    
    def __init__(self, collision_list=[]):
        
        self.collision_list = collision_list
        pairs = []
        
        self.assign_pairs()
        
        t.Thread(target=self.update_collisions).start()
        
    def assign_pairs(self):
        
        assigned_pairs = []
        pairs = []
        for i in self.collision_list:
            for j in self.collision_list:
                if i != j:
                    pairs.append([i, j])
        #removing duplicates
        to_remove = []
        for i in pairs:
            for j in pairs:
                if i != j:
                    if j[0] in i and j[1] in i:
                        if i not in to_remove:
                            to_remove.append(j)
                            break
                        else:
                            break
        for i in to_remove:
            pairs.remove(i)
        
        self.unique_pairs = list(pairs)
        
    def play_sound(self):
        
        pygame.mixer.Sound.play(pygame.mixer.Sound("./soundoncollide.OGG"))
        
    def update_collisions(self):
        
        global INITIATEEXIT, active_fx
        
        lct = {}
        for i in self.collision_list:
            lct[i] = 0
        
        while not(INITIATEEXIT):
            
            s = time.time()
            
            for i in self.unique_pairs:
                p1 = i[0]
                p2 = i[1]
                
                r1 = p1.get_rect()
                r2 = p2.get_rect()
                
                if r1.colliderect(r2):
                    if p1.collision_data != id(p2) or lct[p1] >= 0.2:
                        #velocity exchange as per law of conservation of momentum
                        total_mass = p1.mass + p2.mass
                        v1 = p1.velocity*((p1.mass - p2.mass)/total_mass) + p2.velocity*(2*p2.mass/total_mass)
                        v2 = p2.velocity*((p2.mass - p1.mass)/total_mass) + p1.velocity*(2*p1.mass/total_mass)
                        p1.velocity, p2.velocity = v1, v2
                        
                        #add a particle fx near to the collision site (center of the line segment joining the centers of colliding objects)
                        c1, c2 = r1.center, r2.center
                        xc = (c1[0] + c2[0])/2
                        yc = (c1[1] + c2[1])/2
                        center = (xc, yc)
                        active_fx.append(Rectangle_fx(center))
                        
                        #play a collision sound
                        t.Thread(target=self.play_sound).start()
                        
                        p1.collision_data = id(p2)
                        p2.collision_data = id(p1)
                        lct[p1] = 0
                        lct[p2] = 0
            
            for i in lct:
                lct[i] += 1/120
                
            e = time.time()
            
            if e-s < 1/120:
                time.sleep(1/120 - (e-s))

class PhysicsParticle:

    def __init__(self, **kwargs):

        self.kwargs = kwargs

        self.set_defaults()

        self.x, self.y = self.kwargs["pos"]
        self.width, self.height = self.kwargs["dimensions"]
        self.color = self.kwargs["color"]
        self.mass = self.kwargs["mass"]
        self.static = self.kwargs["static"]
        if self.static:
            self.mass = float("inf")
        self.is_pawn = self.kwargs["pawn"]

        self.net_force = Vector2()
        self.velocity = Vector2()
        self.acceleration = Vector2()
        self.collision_data = 0
        
        t.Thread(target=self.update_physics).start()


    def set_defaults(self):

        keys = self.kwargs.keys()

        if "pos" not in keys:
            self.kwargs["pos"] = (0, 0)
        if "dimensions" not in keys:
            self.kwargs["dimensions"] = (20, 20)
        if "color" not in keys:
            self.kwargs["color"] = (255, 255, 255)
        if "mass" not in keys:
            self.kwargs["mass"] = 1
        if "static" not in keys:
            self.kwargs["static"] = False
        if "pawn" not in keys:
            self.kwargs["pawn"] = False
        if "collision_list" not in keys:
            self.kwargs["collision_list"] = []

    def apply_force(self, force=Vector2(), act_time=0.1):
        self.net_force += force
        time.sleep(act_time)
        self.net_force -= force
        
    def apply_impulse(self, force=Vector2(), for_time=0.1):
        t.Thread(target=self.apply_force, args=(force, for_time)).start()

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def update_physics(self):
        
        global INITIATEEXIT
        #loop variables
        inertial_x, inertial_y = 0, 0
        velocity_x, velocity_y = 0, 0
        previous_force = Vector2()
        delta_time_input = 1
        time_since_last_collision = 0
        while not(INITIATEEXIT):
            starts_at = time.time()

            if self.x > 600:
                self.x = 0
            if self.y > 600:
                self.y = 0
            if self.x < 0:
                self.x = 600
            if self.y < 0:
                self.y = 600

            if self.is_pawn:
                key_events = pygame.key.get_pressed()
                if key_events[pygame.K_w]:
                    self.apply_impulse(Vector2(0, -0.2), 1)
                if key_events[pygame.K_s]:
                    self.apply_impulse(Vector2(0, 0.2), 1)
                if key_events[pygame.K_a]:
                    self.apply_impulse(Vector2(-0.2, 0), 1)
                if key_events[pygame.K_d]:
                    self.apply_impulse(Vector2(0.2, 0), 1)
                delta_time_input += 1/60
                
            self.acceleration = self.net_force*(1/self.mass)
                
            if self.net_force:                
                
                if self.acceleration.x:
                    velocity_x = self.acceleration.x*(1/60)
                    
                if self.net_force.y:
                    velocity_y = self.acceleration.y*(1/60)
                    
            else:
                velocity_x, velocity_y = 0, 0
                
            if self.velocity:
                
                if self.velocity.x:
                    self.x += self.velocity.x*(1/60)
                    
                if self.velocity.y:
                    self.y += self.velocity.y*(1/60)
                        
            self.velocity += Vector2(velocity_x, velocity_y)
            ends_at = time.time()
            net_time_taken = ends_at - starts_at
            if net_time_taken < 1/60:
                time.sleep((1/60) - net_time_taken)

    def update_physics_reactive(self):
        pass
    
    def draw(self, display):
        pygame.draw.rect(display, self.color, self.get_rect())

main = pygame.display.set_mode((600, 600))
fx_surf = pygame.Surface((600, 600), pygame.SRCALPHA)

active_fx = []

physics_objects = [PhysicsParticle(pawn=True, pos=(500, 540), color=(255, 0, 0))]
for i in range(20):
    physics_objects.append(PhysicsParticle(pos=(i + i*20, i*20 + i + 100), mass=randint(3, 5)))
for i in physics_objects:
    i.collision_list = physics_objects
    
CollisionHandler(physics_objects)

while True:

    if INITIATEEXIT:
        break
    
    for i in pygame.event.get():
        if i.type == QUIT:
            INITIATEEXIT = True

    keys = pygame.key.get_pressed()

    if keys[pygame.K_r] or pygame.mouse.get_pressed()[0]:
        for i in physics_objects:
            x, y = randint(-100, 100), randint(-100, 100)
            i.apply_impulse(Vector2(x, y), 1)

    main.fill((0, 0, 0))
    fx_surf.fill((0, 0, 0, 0))

    for i in physics_objects:
        i.draw(main)
        
    to_remove_fx = []
    for i in active_fx:
        if i.ended:
            to_remove_fx.append(i)
        else:
            i.draw(fx_surf)
    for i in to_remove_fx:
        del_obj = active_fx.pop(active_fx.index(i))
        del del_obj
    
    main.blit(fx_surf, (0, 0))

    pygame.display.flip()

pygame.quit()