import pygame
from pygame.display import update
from pygame.locals import *
import threading as t
import time, sys, random
from random import randint

def init():

    pygame.mixer.pre_init(44100, -16, 2, 2048)
    pygame.mixer.init()
    pygame.init()
    

INITIATEEXIT = False


class Vector2:
    """A class used to represent vectors"""
    def __init__(self, x=0, y=0):
    
        self.x, self.y = round(x, 2), round(y, 2)
        
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
    
    def __init__(self, collision_list=[], fx_manager=None):
        
        self.collision_list = collision_list
        self.fx_manager = fx_manager
        
        self.assign_pairs()
        
        self.collision_ready = False
        
        t.Thread(target=self.update_collisions).start()
        
    def assign_pairs(self):
        
        pairs = []
        for i in self.collision_list:
            for j in self.collision_list:
                if i != j:
                    pairs.append([i, j])
        #removing duplicates
        to_remove = []
        for i in pairs:
            e1, e2 = i[0], i[1]
            if [e2, e1] in pairs and i not in pairs:
                to_remove.append(pairs[pairs.index([e2, e1])])
        
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

        self.collision_ready = True
        
        while not(INITIATEEXIT):
            
            s = time.time()
            
            for i in self.unique_pairs:
                p1 = i[0]
                p2 = i[1]
                
                r1 = p1.get_rect()
                r2 = p2.get_rect()
                
                if r1.colliderect(r2):
                    if p1.collision_data != id(p2) or lct[p1] >= 0.5:
                        if "physics object" in p1.type and "physics object" in p2.type:
                            #velocity exchange as per law of conservation of momentum
                            total_mass = p1.mass + p2.mass
                            v1 = p1.velocity*((p1.mass - p2.mass)/total_mass) + p2.velocity*(2*p2.mass/total_mass)
                            v2 = p2.velocity*((p2.mass - p1.mass)/total_mass) + p1.velocity*(2*p1.mass/total_mass)
                            p1.velocity, p2.velocity = v1, v2
                            
                            #fire on hit events
                            p1.on_hit(p2)
                            p2.on_hit(p1)
                            
                            #add a particle fx near to the collision site (center of the line segment joining the centers of colliding objects)
                            c1, c2 = r1.center, r2.center
                            xc = (c1[0] + c2[0])/2
                            yc = (c1[1] + c2[1])/2
                            center = (xc, yc)
                            self.fx_manager.add_fx(Rectangle_fx(center))
                            
                            #play a collision sound
                            #t.Thread(target=self.play_sound).start()
                            
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
        self.type = "physics object"

        self.net_force = Vector2()
        self.velocity = Vector2()
        self.acceleration = Vector2()
        self.collision_data = 0
        
        self.field_forces = {}
        
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
    
    def apply_field_force(self, force=Vector2(), name="field force 0"):
        if name in self.field_forces:
            self.remove_field_force(name)
        self.field_forces[name] = force
        self.net_force += force
        
    def on_hit(self, other):
        pass
    
    def on_end_overlap(self):
        pass
        
    def remove_field_force(self, name="field force 0"):
        try:
            force = self.field_forces[name]
            #print(name)
            self.net_force -= force
            del self.field_forces[name]
        except:
            pass

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def draw_force_velocity_arrows(self, dis):
        
        #force arrow
        if self.net_force:
        
            net_force_unit_vector = self.net_force * (1/self.net_force.get_magnitude()) * 50
            point1 = self.get_rect().center
            point2 = (point1[0] + net_force_unit_vector.x, point1[1] + net_force_unit_vector.y)
            
            pygame.draw.line(dis, (0, 255, 0), point1, point2, 2)
            
            #x, y = point2[0]-5, point2[1]-5
            #head_rect = pygame.Rect(x, y, 10, 10)
            pygame.draw.circle(dis, (0, 255, 0), point2, 5)
            
        #velocity arrow
        if self.velocity:
            
            velocity_unit_vector = self.velocity * (1/self.velocity.get_magnitude()) * 25
            
            point1 = self.get_rect().center
            point2_vel = (point1[0] + velocity_unit_vector.x, point1[1] + velocity_unit_vector.y)
            
            pygame.draw.line(dis, (255, 255, 102), point1, point2_vel, 2)
            
            pygame.draw.circle(dis, (255, 255, 102), point2_vel, 5)

    def update_physics(self):
        
        global INITIATEEXIT
        #loop variables
        velocity_x, velocity_y = 0, 0
        delta_time_input = 1
        while not(INITIATEEXIT):
            starts_at = time.time()
            
            #print(self.field_forces, self.net_force)

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
                    self.apply_impulse(Vector2(0, -10), 1)
                if key_events[pygame.K_s]:
                    self.apply_impulse(Vector2(0, 10), 1)
                if key_events[pygame.K_a]:
                    self.apply_impulse(Vector2(-10, 0), 1)
                if key_events[pygame.K_d]:
                    self.apply_impulse(Vector2(10, 0), 1)
                if key_events[pygame.K_c]:
                    self.net_force = Vector2()
                    self.velocity = Vector2()
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
        self.draw_force_velocity_arrows(display)


class Fx_Manager:
    
    def __init__(self):
        self.active_fx = []
        self.fx_surface = pygame.Surface((600, 600), pygame.SRCALPHA)
        
        t.Thread(target=self.update_fx).start()
        
    def add_fx(self, fx):
        self.active_fx.append(fx)
    
    def add_multiple_fx(self, fx=[]):
        self.active_fx += fx
    
    def update_fx(self):
        
        global INITIATEEXIT
        
        while not(INITIATEEXIT):
            
            s = time.time()
            
            self.fx_surface.fill((0, 0, 0, 0))
            
            to_remove_fx = []
            for i in self.active_fx:
                if i.ended:
                    to_remove_fx.append(i)
                else:
                    i.draw(self.fx_surface)
            for i in to_remove_fx:
                del_obj = self.active_fx.pop(self.active_fx.index(i))
                del del_obj
            
            e = time.time()
            
            if (e - s) < 1/60:
                time.sleep(1/60 - (e - s))
            
    def draw(self, dis):
        
        dis.blit(self.fx_surface, (0, 0))
        
        
class Finite_Uniform_Square_Field:
    
    def __init__(self, side=300, center=(300, 300), field_strength=100):
        
        self.side = side
        self.center = center
        self.field_strength = field_strength
        
        self.type = "force field object"
        
        self.collision_particles = []
        self.particles_under_field = []
        
    def get_rect(self):
        
        x = self.center[0] - (self.side//2)
        y = self.center[1] - (self.side//2)
        return pygame.Rect(x, y, self.side, self.side)
    
    def set_collision_objects(self, particles=[]):
        
        for i in particles:
            if "physics object" in i.type:
                self.collision_particles.append(i)
                
        t.Thread(target=self.update_field).start()
                
    def update_field(self):
        
        global INITIATEEXIT
        
        while not(INITIATEEXIT):
            
            s = time.time()
            
            for i in self.collision_particles:
                
                other = i.get_rect()
                this = self.get_rect()
                
                if this.colliderect(other):
                    
                    this_center = this.center
                    other_center = other.center
                    
                    this_poition_vec = Vector2(this_center[0], this_center[1])
                    other_position_vec = Vector2(other_center[0], other_center[1])
                    
                    force_direction = this_poition_vec - other_position_vec
                    try:
                        force_direction_unit_vector = force_direction * (1/force_direction.get_magnitude())
                        force_vector = force_direction_unit_vector * self.field_strength
                        
                        i.apply_field_force(force_vector, "finite square field")
                    except:
                        pass
                    
                else:
                    
                    i.remove_field_force("finite square field")
                    
            e = time.time()
            net_time = e - s
            
            if net_time < 1/120:
                time.sleep(1/120 - net_time)
        
    def draw(self, dis):
        
        pygame.draw.rect(dis, (255, 0, 0), self.get_rect(), width=2)


if __name__ == "__main__":
    
    init()
    
    main = pygame.display.set_mode((600, 600))

    ppo = PhysicsParticle(pawn=True, pos=(300, 200), color=(255, 0, 0))
    ppo.velocity += Vector2(80, 0)
    physics_objects = [ppo]
    for i in range(20):
        physics_objects.append(PhysicsParticle(pos=(i + i*20, i*20 + i + 100), mass=randint(3, 5)))
      
    fx_manager = Fx_Manager()

    collision_handler = CollisionHandler(physics_objects, fx_manager)
    collision_ready = collision_handler.collision_ready
    
    test_field = Finite_Uniform_Square_Field(side=300, center=(300, 300))
    test_field.set_collision_objects(physics_objects)

    #click message
    font = pygame.font.Font('freesansbold.ttf', 16)
    text_to_display = font.render('Click to apply random impulses to particles', True, (0, 255, 0, 128))
    tr = text_to_display.get_rect()
    tr.x, tr.y = 10, 10
    text_surface = pygame.Surface((500, 500), pygame.SRCALPHA)

    while True:

        if INITIATEEXIT:
            break
        
        for i in pygame.event.get():
            if i.type == QUIT:
                INITIATEEXIT = True

        keys = pygame.key.get_pressed()

        if collision_ready:
            if keys[pygame.K_r] or pygame.mouse.get_pressed()[0]:
                for i in physics_objects:
                    x, y = randint(-100, 100), randint(-100, 100)
                    i.apply_impulse(Vector2(x, y), 1)
            

        main.fill((0, 0, 0))
        text_surface.fill((0, 0, 0, 0))

        if collision_ready:
            text_surface.blit(text_to_display, tr)

        for i in physics_objects:
            i.draw(main)
            
        test_field.draw(main)
            
        fx_manager.draw(main)
        
        main.blit(text_surface, (0, 0))

        pygame.display.flip()

    pygame.quit()
