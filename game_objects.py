import pygame
from game_state import GameState
SCALE = 3
screen = pygame.display.set_mode((800, 600))
screen_rect=screen.get_rect()

incremento = 0.3
limite_maximo = 2
limite_minimo = 0.3  # definir um limite mínimo para a velocidade



class StaticObject:
    def __init__(self, x, y, image, z=0):
        self.is_dead  = False
        self.x = x
        self.y = y
        self.z = z if z is not None else 0  # Garanta que z nunca seja None

      
        self.image = image
        self.change_direction = True
        self.image = pygame.transform.scale(self.image, (self.image.get_width() * SCALE, self.image.get_height() * SCALE))
        self.image.set_colorkey(GameState.WATER_COLOR) 
        self.size = (self.image.get_width(), self.image.get_height())
        
        self.rect = pygame.Rect(self.x, self.y, self.image.get_width(), self.image.get_height())

    def update_rect(self):
        self.rect.topleft = (self.x, self.y)

    def to_dict(self):
        return {
            'type': class_to_char[type(self)],
            'x': self.rect.x,
            'y': self.rect.y,
            'z': self.z
        }
    
    
    def scroll(self):
        self.y += GameState.speed
        self.rect.x = self.x
        self.rect.y = self.y       
        self.update_rect()  # Update the Rect after scrolling           

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))  
    
    def move_to(self, x, y):
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y    

    def update(self, dt):
        pass        

class MovingObject:
    def __init__(self, x, y, image, z=0):
        self.x = x
        self.y = y
        self.z = z 
        self.is_dead  = False
        self.image = image
        self.image = pygame.transform.scale(self.image, (self.image.get_width() * SCALE, self.image.get_height() * SCALE))
        self.explode_image1 = pygame.transform.scale(self.explode_image1, (self.image.get_width() * SCALE, self.explode_image1.get_height() * SCALE))        
        self.explode_image2 = pygame.transform.scale(self.explode_image1, (self.image.get_width() * SCALE, self.explode_image1.get_height() * SCALE))                
        self.size = (self.image.get_width(), self.image.get_height())
        self.rect = pygame.Rect(self.x, self.y, self.image.get_width(), self.image.get_height())
        self.direction = -3
    def update_rect(self):
        self.rect.topleft = (self.x, self.y)

    def to_dict(self):
        return {
            'type': class_to_char[type(self)],
            'x': self.rect.x,
            'y': self.rect.y,
            'z': self.z
        }
    
    def move(self):
        self.x += self.direction
        self.rect.x = self.x
        self.rect.y = self.y

    def move_to(self, x, y):
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y        

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

    def change_direction(self):
        self.image = pygame.transform.flip(self.image, True, False)
        self.direction = -self.direction

    def trata_colisao(self, objeto_rect):
        if self.rect.colliderect(objeto_rect):
            self.change_direction()

    def scroll(self):
        self.y += GameState.speed
        self.rect.x = self.x
        self.rect.y = self.y        
        self.update_rect()  # Update the Rect after scrolling        

    def update(self, dt):
        if self.is_dead:
            self.image = self.explode_image

    def explode(self):
        self.is_dead = True
        self.image = self.explode_image1
    

class Player:
    def __init__(self, x, y, sheet_image):
        self.x = x
        self.y = y
        self.gasolina = 100
        self.blinking = False
        self.is_dead  = False
      
        # Recorte do avião voando para a esquerda
        self.player_left_image = sheet_image.subsurface(pygame.Rect(10, 17, 13, 16))
        self.player_left_image = pygame.transform.scale(self.player_left_image, (self.player_left_image.get_width() * SCALE, self.player_left_image.get_height() * SCALE))
        self.player_left_image.set_colorkey(GameState.WATER_COLOR)  # Torna a cor da água transparente

        # Recorte do avião voando para o centro
        self.player_center_image = sheet_image.subsurface(pygame.Rect(24, 16, 16, 16))
        self.player_center_image = pygame.transform.scale(self.player_center_image, (self.player_center_image.get_width() * SCALE, self.player_center_image.get_height() * SCALE))
        self.player_center_image.set_colorkey(GameState.WATER_COLOR)  # Torna a cor da água transparente


        # Recorte do avião voando para a direita
        self.player_right_image = sheet_image.subsurface(pygame.Rect(43, 17, 16, 16))
        self.player_right_image = pygame.transform.scale(self.player_right_image, (self.player_right_image.get_width() * SCALE, self.player_right_image.get_height() * SCALE))
        self.player_right_image.set_colorkey(GameState.WATER_COLOR)  # Torna a cor da água transparente

        # Recorte do avião explodindo
        self.player_explode_image = sheet_image.subsurface(pygame.Rect(6, 76, 18, 15))
        self.player_explode_image = pygame.transform.scale(self.player_explode_image, (self.player_explode_image.get_width() * SCALE, self.player_explode_image.get_height() * SCALE))
        self.player_explode_image.set_colorkey(GameState.WATER_COLOR)  # Torna a cor da água transparente

        # Começa com a imagem do avião voando para a direita
        self.player_image = self.player_right_image
        self.rect = pygame.Rect(self.x, self.y, self.player_image.get_width(), self.player_image.get_height())

        # Inicializa o timer para o jogador ficar parado
        self.idle_timer = 0

    def update(self, dt):
        keys = pygame.key.get_pressed()

        if not keys[pygame.K_LEFT]  and not keys[pygame.K_RIGHT]:

            self.idle_timer += dt
        else:
            self.idle_timer = 0

        if self.idle_timer >= 30 and not self.is_dead:
            self.player_image = self.player_center_image
    def refuel(self):
        if not self.is_dead:
            self.gasolina += 7
            if self.gasolina > 100:
                self.gasolina = 100

    def decrease_gasolina(self, base_amount, speed):

        if not self.is_dead:
            self.gasolina -= base_amount 
            if self.gasolina <= 0:
                self.gasolina = 0
                return True
            return False


    def move_left(self):
        if not self.is_dead:
            self.x -= 5
            self.rect.x = self.x
            self.player_image = self.player_right_image

    def move_right(self):
        if not self.is_dead:
            self.x += 5
            self.rect.x = self.x        
            self.player_image = self.player_left_image


    def move_up(self):
 
        if not self.is_dead:
            self.player_image = self.player_center_image
            GameState.speed += incremento if GameState.speed < limite_maximo else 0

    def move_down(self):
       
        if not self.is_dead:
            self.player_image = self.player_center_image
            GameState.speed -= incremento if GameState.speed - incremento >= limite_minimo else 0

    def explode(self):
        self.is_dead =True
        self.player_image = self.player_explode_image


    def draw(self, screen):
        screen.blit(self.player_image, (self.x, self.y))


class Casa(StaticObject):
    def __init__(self, x, y, sheet_image ,z=0):
        image  = sheet_image.subsurface(pygame.Rect(117, 15, 32, 24))
        super().__init__(x, y, image,z)

class Gramaupright(StaticObject):  # azul\verde  
    def __init__(self, x, y, sheet_image, z=0):
        image = sheet_image.subsurface(pygame.Rect(84, 40, 32, 8))
        super().__init__(x, y, image,z)


class Gramaupleft(StaticObject): # verde/azul
    def __init__(self, x, y, sheet_image, z=0):
        image = sheet_image.subsurface(pygame.Rect(117, 40, 32, 8))
        super().__init__(x, y, image,z)

class Gramadownleft(StaticObject):    #azul/verde -erro
    def __init__(self, x, y, sheet_image, z=0):
        image = sheet_image.subsurface(pygame.Rect(84, 5, 31, 8))
        super().__init__(x, y, image,z)
 
class Gramadownright(StaticObject):  #verde\azul
    def __init__(self, x, y, sheet_image, z=0):
        image = sheet_image.subsurface(pygame.Rect(117, 5, 31, 8))
        super().__init__(x, y, image,z)

class Grama(StaticObject):
    def __init__(self, x, y, sheet_image, z=0):
        image = sheet_image.subsurface(pygame.Rect(84, 15, 32, 13))
        super().__init__(x, y, image,z)



class Bullet(StaticObject):
    def __init__(self, x, y, sheet_image, z=0):
        image = sheet_image.subsurface(pygame.Rect(6, 21, 2, 7))
        super().__init__(x, y, image, z)
        self.speed = -10  # A velocidade a que a bala se move (negativo para subir)

    def scroll(self):
        self.y += self.speed
        self.rect.x = self.x
        self.rect.y = self.y        
        self.update_rect()  # Update the Rect after scrolling



class Fuel(StaticObject):
    def __init__(self, x, y, sheet_image, z=0):
        self.x = x
        self.y = y
        self.z = z
        self.is_dead  = False
        self.rect = pygame.Rect(153, 15, 15, 24)
        image = sheet_image.subsurface(self.rect)
        #gauge_image = sheet_image.subsurface(pygame.Rect(74, 66, 78, 15))
        #self.gauge_image = pygame.transform.scale(gauge_image, (gauge_image.get_width() * SCALE, gauge_image.get_height() * SCALE))
        self.image = pygame.transform.scale(image, (image.get_width() * SCALE, image.get_height() * SCALE))
 
        explode_image1 = sheet_image.subsurface(pygame.Rect(1, 112, 23, 15))
        explode_image1 = pygame.transform.scale(explode_image1, (explode_image1.get_width() * SCALE, explode_image1.get_height() * SCALE))
        explode_image2 = sheet_image.subsurface(pygame.Rect(24, 110, 41, 16))
        explode_image2 = pygame.transform.scale(explode_image2, (explode_image2.get_width() * SCALE, explode_image2.get_height() * SCALE))

        self.explode_images = [explode_image1, explode_image2]
        self.is_exploding = False
        self.explode_timer = 0
        self.explode_index = 0


        self.size = (self.image.get_width(), self.image.get_height())
        self.rect = pygame.Rect(self.x, self.y, self.image.get_width(), self.image.get_height())
    #to do   make gauge slide from empty to full with the distance and refueling
 

    def explode(self):
        self.is_exploding = True
        self.image = self.explode_images[0]

    def update(self, dt):
        if self.is_exploding:
            self.explode_timer += dt
            if self.explode_timer >= 200:
                self.explode_timer = 0
                self.explode_index = (self.explode_index + 1) % len(self.explode_images)
                self.image = self.explode_images[self.explode_index]
                if self.explode_index == len(self.explode_images) - 1:
                    self.is_dead = True


    def scroll(self):
        self.y += GameState.speed
        self.rect.x = self.x
        self.rect.y = self.y
        self.update_rect()  # Update the Rect after scrolling          
     
    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

class Ponte(StaticObject):
    def __init__(self, x, y, sheet_image, z=0):
        image = sheet_image.subsurface(pygame.Rect(172, 15, 63, 23))
        self.original_width = image.get_width()
        self.original_height = image.get_height()
        self.original_x = x
        self.original_y = y

        explode_image1 = sheet_image.subsurface(pygame.Rect(1, 112, 23, 15))
        explode_image1 = pygame.transform.scale(explode_image1, (explode_image1.get_width() * SCALE, explode_image1.get_height() * SCALE))
        explode_image2 = sheet_image.subsurface(pygame.Rect(24, 110, 41, 16))
        explode_image2 = pygame.transform.scale(explode_image2, (explode_image2.get_width() * SCALE, explode_image2.get_height() * SCALE))

        self.explode_images = [explode_image1, explode_image2]
        self.is_exploding = False
        self.explode_timer = 0
        self.explode_index = 0

        super().__init__(x, y, image, z)

    def explode(self):
        self.is_exploding = True
        self.image = self.explode_images[0]

    def update(self, dt):
        if self.is_exploding:
            self.explode_timer += dt
            if self.explode_timer >= 200:
                self.explode_timer = 0
                self.explode_index = (self.explode_index + 1) % len(self.explode_images)
                self.image = self.explode_images[self.explode_index]
                if self.explode_index == len(self.explode_images) - 1:
                    self.is_dead = True

    def draw(self, screen):
        if self.is_exploding:
            offset_x = self.original_width 
            offset_y = self.original_height 
            x = self.original_x +  offset_x
            y = self.original_y + offset_y
            screen.blit(self.image, (x, y))
        else:
            screen.blit(self.image, (self.x, self.y))


class Asfalto(StaticObject):
    def __init__(self, x, y, sheet_image, z=0):
        image = sheet_image.subsurface(pygame.Rect(67, 14, 16, 26))
        super().__init__(x, y, image,z)
 

class Gauge:
    def __init__(self, x, y, sheet_image):
        self.x = x
        self.y = y

        self.image = sheet_image.subsurface(pygame.Rect(74, 66, 78, 15))
        self.image = pygame.transform.scale(self.image, (self.image.get_width() * 2, self.image.get_height() * 2))  # Aumenta o tamanho em 2x
        self.size = (self.image.get_width(), self.image.get_height())
        self.rect = pygame.Rect(self.x, self.y, self.image.get_width(), self.image.get_height())        

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))


class GaugeMeter:
    def __init__(self, x, y, gauge, sheet_image):
        self.x = x
        self.y = y
        self.gauge = gauge

        self.image = sheet_image.subsurface(pygame.Rect(154, 70, 4, 10))
        self.image = pygame.transform.scale(self.image, (self.image.get_width() * 2, self.image.get_height() * 2))  # Aumenta o tamanho em 2x
        self.start_x = self.x + self.image.get_width() 
        self.size = (self.image.get_width(), self.image.get_height())
        self.rect = pygame.Rect(self.x, self.y, self.image.get_width(), self.image.get_height())

    def update(self, fuel):
        self.x = self.start_x + (fuel / 100.0) * (self.gauge.image.get_width() - 2 * self.image.get_width())



    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

class Boat(MovingObject):
    def __init__(self, x, y, sheet_image, z=0):
        boat_image  = sheet_image.subsurface(pygame.Rect(4, 57, 33, 9))
        self.explode_image1 = sheet_image.subsurface(pygame.Rect(6, 98, 15, 10))
        self.explode_image1 = pygame.transform.scale(self.explode_image1, (self.explode_image1.get_width() * SCALE, self.explode_image1.get_height() * SCALE))
        self.explode_image2 = sheet_image.subsurface(pygame.Rect(28, 97, 29, 12))
        self.explode_image2 = pygame.transform.scale(self.explode_image2, (self.explode_image2.get_width() * SCALE, self.explode_image2.get_height() * SCALE))        
        self.explode_images = [self.explode_image1,
                               self.explode_image2]
        self.is_exploding = False
        self.explode_timer = 0
        self.explode_index = 0


        super().__init__(x, y, boat_image,z)
    def explode(self):
        self.is_exploding = True
        self.image = self.explode_images[0]

    def update(self, dt):
        if self.is_exploding:
            self.explode_timer += dt
            if self.explode_timer >= 100:
                self.explode_timer = 0
                self.explode_index = (self.explode_index + 1) % len(self.explode_images)
                self.image = self.explode_images[self.explode_index]
                # Quando a animação da explosão estiver completa
                if self.explode_index == len(self.explode_images) - 1:
                    self.is_dead = True
class Score:
    DIGIT_RECTS = [
        pygame.Rect(196, 96, 12, 8),  # Dígito 0
        pygame.Rect(74, 96, 8, 8),   # Dígito 1
        pygame.Rect(84, 96, 12, 8),  # Dígito 2
        pygame.Rect(98, 96, 12, 8),  # Dígito 3
        pygame.Rect(112, 96, 12, 9),  # Dígito 4
        pygame.Rect(126, 96, 12, 8),  # Dígito 5
        pygame.Rect(140, 96, 12, 8),  # Dígito 6
        pygame.Rect(154, 96, 12, 8),  # Dígito 7
        pygame.Rect(168, 96, 12, 8),  # Dígito 8
        pygame.Rect(192, 96, 12, 8),  # Dígito 9
    ]

    def __init__(self, x, y, score, sheet_image, gauge_width, scale):
        self.x = x  # Posição x passada na inicialização
        self.y = y
        self.score = score
        self.sheet_image = sheet_image
        self.scale = scale
        self.gauge_width = gauge_width
        self.digits_images = self.get_digits_images(score)
        self.score_width = sum(image.get_width() for image in self.digits_images)
        self.digits = [Digit(self.x + self.digit_width(i), self.y, self.digits_images[i]) for i in range(len(self.digits_images))]

    def digit_width(self, index):
        return sum(self.digits_images[i].get_width() for i in range(index))


    def get_digits_images(self, score):
       
        digit_images = [pygame.transform.scale(self.sheet_image.subsurface(self.DIGIT_RECTS[int(digit)]), (self.DIGIT_RECTS[int(digit)].width * self.scale, self.DIGIT_RECTS[int(digit)].height * self.scale)) for digit in str(score)]
        for image in digit_images:
            image.set_colorkey(GameState.WATER_COLOR)
        return digit_images 
    
    def update(self, new_score):
        self.score = new_score
        self.digits_images = self.get_digits_images(self.score)
        self.score_width = sum(image.get_width() for image in self.digits_images)
        self.x = self.gauge_width - self.score_width - 10  # Alinhamento à direita do gauge
        self.digits = [Digit(self.x + self.digit_width(i), self.y, self.digits_images[i]) for i in range(len(self.digits_images))]

    def draw(self, screen):
        x_offset = self.x
        for digit_image in self.digits_images:
            screen.blit(digit_image, (x_offset, self.y))
            x_offset += digit_image.get_width()  # Atualiza a posição x para o próximo dígito


class Digit:
    def __init__(self, x, y, image):
        self.x = x
        self.y = y
        self.image = image
        self.rect = pygame.Rect(self.x, self.y, self.image.get_width(), self.image.get_height())        

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))



class Helicopter(MovingObject):
    def __init__(self, x, y, sheet_image, z=0):
        self.x = x
        self.y = y
        self.y = z
        
        self.image1 = sheet_image.subsurface(pygame.Rect(2, 44, 19, 12))
        self.image2 = sheet_image.subsurface(pygame.Rect(21, 44, 19, 12))

        self.explode_image1 = sheet_image.subsurface(pygame.Rect(5, 95, 17, 14))
        self.explode_image2 = sheet_image.subsurface(pygame.Rect(28, 95, 31, 12))

        self.imagefront1 = pygame.transform.scale(self.image1, (self.image1.get_width() * SCALE, self.image1.get_height() * SCALE))
        self.imagefront2 = pygame.transform.scale(self.image2, (self.image2.get_width() * SCALE, self.image2.get_height() * SCALE))
        self.imageback1 = pygame.transform.flip(self.imagefront1, True, False)
        self.imageback2 = pygame.transform.flip(self.imagefront2, True, False)
        self.image = self.image1
        self.size = (self.image.get_width(), self.image.get_height())
        self.rect = pygame.Rect(self.x, self.y, self.image.get_width(), self.image.get_height())
        self.direction = 3
        self.image_index = 0

        self.timer = 0

    def update_rect(self):
        self.rect.topleft = (self.x, self.y)

    def change_direction(self):

        self.direction = -self.direction 
        if self.direction > 0:
            self.image = self.imagefront1
        else:
            self.x += self.direction
            self.image = self.imageback1
        self.rect = pygame.Rect(self.x, self.y, self.image.get_width(), self.image.get_height())            

   
        
    def update(self, dt):
        self.timer += dt
        if self.timer >= 100:
            self.timer = 0
            self.image_index = (self.image_index + 1) % 2
            if self.image_index == 0:
                if self.direction > 0:
                    self.image = self.imagefront1
                else:
                    self.image = self.imageback1
            else:
                if self.direction > 0:
                    self.image = self.imagefront2
                else:
                    self.image = self.imageback2
        if self.is_dead:
            self.image = self.explode_image

    def draw(self, screen):
        super().draw(screen)


class Airplane:
    def __init__(self, x, y, sheet_image):
        self.x = x
        self.y = y
        self.direction = -3
        self.image = sheet_image.subsurface(pygame.Rect(38, 46, 21, 11))
        self.image = pygame.transform.scale(self.image, (self.image.get_width() * SCALE, self.image.get_height() * SCALE))
        self.size = (self.airplane_image.get_width(), self.airplane_image.get_height())
        self.rect = pygame.Rect(self.x, self.y, self.image.get_width(), self.image.get_height())
    
    def update_rect(self):
        self.rect.topleft = (self.x, self.y)        
    def move(self):
        self.x += self.direction
        self.rect.x = self.x
        self.rect.y = self.y
    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

char_to_class = {
    "g": Grama,
    "a": Asfalto,
    "H": Helicopter,
    "N": Boat,
    "f": Fuel,
    "p": Ponte,
    "\\": Gramaupright,
    "/": Gramaupleft,
    "]": Gramadownleft,
    "[": Gramadownright,
    "^": Casa
}

class_to_char = {v: k for k, v in char_to_class.items()}