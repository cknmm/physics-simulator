
import pygame
from pygame.locals import *
import threading as t
import time, sys
from random import randint

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
		
	def update_collisions(self):
		
		global INITIATEEXIT
		
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
						p1.net_force, p2.net_force = p2.net_force, p1.net_force
						p1.collision_data = id(p2)
						p2.collision_data = id(p1)
						lct[p1] = 0
						lct[p2] = 0
					#p1.net_force, p2.net_force = p2.net_force, p1.net_force
			
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
        self.is_pawn = self.kwargs["pawn"]

        self.net_force = Vector2()
        self.velocity = Vector2()
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
            self.kwargs["static"] = ""
        if "pawn" not in keys:
            self.kwargs["pawn"] = False
        if "collision_list" not in keys:
            self.kwargs["collision_list"] = []

    def apply_force(self, force=Vector2()):
        self.net_force += force

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
                    self.apply_force(Vector2(0, -0.2))
                if key_events[pygame.K_s]:
                    self.apply_force(Vector2(0, 0.2))
                if key_events[pygame.K_a]:
                    self.apply_force(Vector2(-0.2, 0))
                if key_events[pygame.K_d]:
                    self.apply_force(Vector2(0.2, 0))
                delta_time_input += 1/60
            if self.net_force:
                x_component = self.net_force.x
                y_component = self.net_force.y
                if x_component:
                    if previous_force.x != x_component:
                        velocity_x = x_component/self.mass
                        inertial_x = velocity_x
                        self.x += velocity_x
                    else:
                        self.x += inertial_x
                if y_component:
                    if previous_force.y != y_component:
                        velocity_y = y_component/self.mass
                        inertial_y = velocity_y
                        self.y += velocity_y
                    else:
                        self.y += inertial_y
                        
            self.velocity = Vector2(velocity_x, velocity_y)
            ends_at = time.time()
            net_time_taken = ends_at - starts_at
            if net_time_taken < 1/60:
                time.sleep((1/60) - net_time_taken)

    def update_physics_reactive(self):
        pass
    
    def draw(self, display):
        pygame.draw.rect(display, self.color, self.get_rect())

main = pygame.display.set_mode((600, 600))

physics_objects = [PhysicsParticle(pawn=True, pos=(500, 100), color=(255, 0, 0))]
for i in range(30):
    physics_objects.append(PhysicsParticle(pos=(i + i*20, 100), mass=randint(3, 5)))
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
            x, y = randint(-1, 1), randint(-1, 1)
            i.apply_force(Vector2(x, y))

    main.fill((0, 0, 0))

    for i in physics_objects:
        i.draw(main)
        """if i.x > 600:
            i.x = 0
        if i.y > 600:
            i.y = 0
        if i.x < 0:
            i.x = 600
        if i.y < 0:
            i.y = 600"""

    pygame.display.flip()

pygame.quit()