
import pygame
import os
import sys
import copy
import json
from game_objects import *
from game_state import GameState

pygame.init()
screen = pygame.display.set_mode((1200, 600))  # Aumenta a largura da tela
object_area_width = 800  # Largura da área em que os objetos podem ser colocados

screen_rect = screen.get_rect()

sheet_image = pygame.image.load('Atari - River Raid Atari 2600 - River Raid.png')
tile_size = 38  # Tamanho de cada bloco no mapa

game_objects = []  # Inicializando game_objects como uma lista vazia


clock = pygame.time.Clock()  # Adicionando esta linha

image = pygame.image.load('Atari - River Raid Atari 2600 - River Raid.png')
center_pos = screen_rect.center



def draw_dashed_rect(surface, rect, color, dash_length):
    x, y, w, h = rect
    pygame.draw.lines(surface, color, False, [(x, y), (x+w, y), (x+w, y+h), (x, y+h)], dash_length)

def load_game_state():
    try:
        with open('game_state.json', 'r') as f:
            game_objects_dicts = json.load(f)
    except FileNotFoundError:
        return []  # Retorna uma lista vazia se o arquivo não existir

    game_objects = []
    for obj_dict in game_objects_dicts:
        cls = char_to_class[obj_dict['type']]
        x = obj_dict['x']
        y = obj_dict['y']
        z = obj_dict['z']  # Get the z value from the dictionary
        if z is None:  # Se z for None, atribua 0 a z
            z = 0
        game_object = cls(x, y, sheet_image, z)  # Pass the z value to the constructor
        game_objects.append(game_object)

    return game_objects

def draw_coordinates(screen, obj):
    if obj is not None:
        font = pygame.font.Font(None, 24)  # Use a fonte padrão do pygame, tamanho 24
        text = f'x: {obj.x}, y: {obj.y}, z: {obj.z}'
        text_surface = font.render(text, True, (255, 255, 255))  # Cria uma superfície com o texto
        screen.blit(text_surface, (object_area_width + 20, 120))  # Desenha o texto na tela


def draw_object_count(screen, objs):
    if objs:
        font = pygame.font.Font(None, 24)  # Use a fonte padrão do pygame, tamanho 24
        text = f'{len(objs)} objects selected'  # Obtem o número de objetos selecionados
        text_surface = font.render(text, True, (255, 255, 255))  # Cria uma superfície com o texto
        screen.blit(text_surface, (object_area_width + 20, 80))  # Desenha o texto na tela

def draw_object_name(screen, obj):
    if obj is not None:
        font = pygame.font.Font(None, 24)  # Use a fonte padrão do pygame, tamanho 24
        text = obj.__class__.__name__  # Get the class name of the object
        text_surface = font.render(text, True, (255, 255, 255))  # Cria uma superfície com o texto
        screen.blit(text_surface, (object_area_width + 20, 150))  # Desenha o texto na tela

def draw_menu(game):
    border_width = 2  # Largura da borda do retângulo
    padding = 15  # Espaço extra para evitar que a imagem toque a borda
    for i, (char, cls) in enumerate(char_to_class.items()):
        # Cria um retângulo para a opção
        rect = pygame.Rect(game.menu_start_x + (i % game.menu_items_per_row) * game.menu_item_width, 
                           game.menu_start_y + (i // game.menu_items_per_row) * game.menu_item_height, 
                           game.menu_item_width, game.menu_item_height)
        pygame.draw.rect(screen, (255, 255, 255), rect, border_width)  # Desenha o retângulo

        # Cria uma instância temporária do objeto e desenha uma pré-visualização
        obj = cls(0, 0, sheet_image)

        # Calcula a proporção para a nova altura e largura, considerando a largura da borda e o padding
        ratio = min((game.menu_item_width - border_width * 2 - padding) / obj.image.get_width(), 
                    (game.menu_item_height - border_width * 2 - padding) / obj.image.get_height())
        new_width = int(obj.image.get_width() * ratio)
        new_height = int(obj.image.get_height() * ratio)

        # Redimensiona a imagem mantendo a proporção
        image = pygame.transform.scale(obj.image, (new_width, new_height))

        # Calcula as coordenadas x e y para centralizar a imagem no retângulo, considerando a largura da borda
        x = game.menu_start_x + (i % game.menu_items_per_row) * game.menu_item_width + (game.menu_item_width - new_width) // 2
        y = game.menu_start_y + (i // game.menu_items_per_row) * game.menu_item_height + (game.menu_item_height - new_height) // 2

        # Desenha a imagem na tela
        screen.blit(image, (x + border_width, y + border_width))  # Adiciona a largura da borda à posição

        # Verifica se o usuário clicou na opção
        if pygame.mouse.get_pressed()[0]:  # Se o botão esquerdo do mouse está pressionado
            x, y = pygame.mouse.get_pos()
    if game.selection_rectangle_start is not None:
        x, y = pygame.mouse.get_pos()
        start_x, start_y = game.selection_rectangle_start
        width = x - start_x
        height = y - start_y
        pygame.draw.rect(screen, (255, 255, 255), (start_x, start_y, width, height), 1)  # Desenha um retângulo branco



class Game:
    def __init__(self, scroll_speed, object_area_width, menu_start_x, menu_start_y, menu_item_width, menu_item_height, menu_items_per_row):
        """
        Inicialize uma nova instância do jogo.

        Parâmetros:
        scroll_speed (int): A velocidade de rolagem em pixels por quadro.
        object_area_width (int): A largura da área de objetos em pixels.
        menu_start_x (int): A coordenada x inicial para o menu.
        menu_start_y (int): A coordenada y inicial para o menu.
        menu_item_width (int): A largura de um item de menu em pixels.
        menu_item_height (int): A altura de um item de menu em pixels.
        menu_items_per_row (int): O número de itens de menu por linha.
        """



        # Inicialize todas as suas variáveis aqui
        self.dragging_start_pos = []
        self.original_objects = []
        self.copy_started = False
        self.scroll_speed = scroll_speed
        self.object_area_width = object_area_width
        self.menu_start_x = menu_start_x
        self.menu_start_y = menu_start_y
        self.menu_item_width = menu_item_width
        self.menu_item_height = menu_item_height
        self.menu_items_per_row = menu_items_per_row
        self.dragging_objects = None
        self.dragging_group_objects = None
        self.cloned_objects  = []
        self.original_z = None
        self.mouse_offset_x = 0
        self.mouse_offset_y = 0
        self.game_objects = load_game_state()
        self.adding_new_object = False
        self.selected_group_objects = []
        self.selection_rectangle_start = None
        self.mouse_is_down = None

        # outras variáveis
    def handle_quit_event(self,event):
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    def handle_key_down_event(self,event):
        # process key down event here...
        if event.key == pygame.K_UP:
            for game_object in self.game_objects:
                game_object.y += self.scroll_speed  # Scroll up
                game_object.update_rect()  # Update the object's Rect
        elif event.key == pygame.K_DOWN:
            for game_object in self.game_objects:
                game_object.y -= self.scroll_speed  # Scroll down
                game_object.update_rect()  # Update the object's Rect    
        elif event.key == pygame.K_s:  # A tecla 's' foi pressionada
            game_objects_dicts = [obj.to_dict() for obj in self.game_objects]
            with open('game_state.json', 'w') as f:
                json.dump(game_objects_dicts, f)
        if event.key == pygame.K_DELETE:

            if self.selected_group_objects:  # Verifica se a lista de objetos selecionados não está vazia
                for game_object in self.selected_group_objects:
                     self.game_objects.remove(game_object)

                
        elif event.key == pygame.K_PAGEDOWN:
            if self.selected_group_objects:  # Verifica se a lista de objetos selecionados não está vazia
                for game_object in self.selected_group_objects:
                     game_object.z -= 1
                self.game_objects.sort(key=lambda obj: obj.z)  # Reordena a lista de objetos com base na profundidade z
        elif event.key == pygame.K_PAGEUP:
            if self.selected_group_objects:  # Verifica se a lista de objetos selecionados não está vazia
                for game_object in self.selected_group_objects:
                     game_object.z += 1
                self.game_objects.sort(key=lambda obj: obj.z)  # Reordena a lista de objetos com base na profundidade z

      


    def handle_mouse_motion_event(self, event):
        # Se estiver arrastando um grupo de objetos e a posição inicial do arrasto foi registrada
        if self.mouse_is_down and self.dragging_objects is not None:
            x, y = event.pos  # Correção aqui
            self.handle_object_drag(x, y)
            for obj, start_pos in zip(self.dragging_group_objects, self.dragging_start_pos):
                x, y = pygame.mouse.get_pos()
                dx = x - start_pos[0]
                dy = y - start_pos[1]
                obj.move_to(obj.rect.x + dx, obj.rect.y + dy)
                start_pos = (x, y)  # Adicione esta linha





    def handle_mouse_button_down_event(self, event):
        self.mouse_is_down = True
        x, y = pygame.mouse.get_pos()  # Pega a posição do mouse
        mods = pygame.key.get_mods()  # Verifica se as teclas especiais estão pressionadas

        if mods & pygame.KMOD_SHIFT:
            self.handle_multi_select_event(x, y)
        if mods & pygame.KMOD_CTRL:
            object_clicked = False
            for game_object in reversed(self.game_objects): 
                if game_object.rect.collidepoint(x, y):
                    object_clicked = True
                    if game_object in self.original_objects:
                        if game_object in self.selected_group_objects:
                            self.selected_group_objects.remove(game_object)
                        else:
                            self.selected_group_objects.append(game_object)
                    else:
                        # Ao clonar o objeto, registre a posição do mouse em relação ao objeto original.
                        mouse_offset_x = game_object.rect.x - x
                        mouse_offset_y = game_object.rect.y - y                        
                        if game_object in self.selected_group_objects:
                            self.selected_group_objects.remove(game_object)
                        else:
                            self.selected_group_objects.append(game_object)
                            clone = self.copy_object(game_object)
                            self.game_objects.append(clone)
                            self.cloned_objects.append(clone)
                            self.original_objects.append(game_object)
                        clone.move_to(clone.rect.x + mouse_offset_x, clone.rect.y + mouse_offset_y)      
                        if self.dragging_start_pos is None:
                                    self.dragging_start_pos = []                        
                        self.dragging_start_pos.append((x, y))  # Adicione esta linha                                              
                    break

            if not object_clicked:
                self.selected_group_objects = []
                self.selection_rectangle_start = (x, y)
        else:
            # Seleciona apenas um objeto ou limpa a seleção se clicado fora
            object_clicked = False
            for game_object in reversed(self.game_objects):  # Itera de trás para frente para pegar os objetos no topo primeiro
                if game_object.rect.collidepoint(x, y):
                    object_clicked = True
                    self.selected_group_objects = [game_object]  # seleciona apenas este objeto
                    break  # Sai do loop assim que um objeto é selecionado
            if not object_clicked:
                self.selected_group_objects = []  # Limpa a seleção se clicado fora de qualquer objeto

        self.check_menu_click(x, y)

        if self.selected_group_objects:
            self.dragging_group_objects = self.selected_group_objects  # Não é necessário copiar os objetos, pois estamos usando o move_to
            self.dragging_start_pos = [(obj.rect.x, obj.rect.y) for obj in self.dragging_group_objects]  # Registra a posição inicial de cada objeto



    def handle_mouse_button_up_event(self, event):
        self.dragging_objects = None
        self.dragging_group_objects = None
        self.dragging_start_pos = None           
        self.mouse_is_down = False
        self.copy_started = False  
        x, y = pygame.mouse.get_pos()  
        if self.selection_rectangle_start is not None:  

            selection_rectangle = pygame.Rect(self.selection_rectangle_start, (x - self.selection_rectangle_start[0], y - self.selection_rectangle_start[1]))  
            self.selection_rectangle_start = None  
            self.cloned_objects = []
            for game_object in self.game_objects:
                if selection_rectangle.colliderect(game_object.rect):
                    if game_object not in self.selected_group_objects and game_object not in self.cloned_objects:  
                        self.selected_group_objects.append(game_object)        
                        if pygame.key.get_mods() & pygame.KMOD_CTRL and not self.copy_started:
                            clone = self.copy_object(game_object) 
                            self.game_objects.append(clone)
                            self.cloned_objects.append(clone)
                            self.original_objects.append(game_object)
        if self.dragging_objects is not None:
                x, y = pygame.mouse.get_pos()  
                for obj, start_pos in zip(self.dragging_objects, self.dragging_start_pos):  # Vamos iterar tanto os objetos quanto suas posições iniciais
                    dx = x - start_pos[0]
                    dy = y - start_pos[1]
                    obj.move_to(obj.rect.x + dx, obj.rect.y + dy)

                self.dragging_objects = None
                self.dragging_start_pos = None
        # Deseleciona objetos se clicarmos fora deles
        object_clicked = False
        for game_object in reversed(self.game_objects):  # Itera de trás para frente para pegar os objetos no topo primeiro
            if game_object.rect.collidepoint(x, y):
                object_clicked = True
                
                break  # Sai do loop assim que um objeto é selecionado
        if not object_clicked:
            #self.selected_group_objects = []  # Limpa a seleção se clicado fora de qualquer objeto
            self.dragging_objects = None  # Limpa o objeto arrastado no fina        
      
    

    def copy_object(self, game_object):
        # Usa o método to_dict do objeto para criar um dicionário com seus atributos
        obj_dict = game_object.to_dict()

        # Crie uma nova instância do objeto usando o dicionário
        cls = char_to_class[obj_dict['type']]
        x = obj_dict['x']
        y = obj_dict['y']
        z = obj_dict['z']  
        if z is None:  # Se z for None, atribua 0 a z
            z = 0
        clone = cls(x, y, sheet_image, z)  # Pass the z value to the constructor

        return clone

    
    def handle_copy_event(self, x, y):
  
        object_clicked = False
        clones = []  # Lista para guardar os objetos clonados

        if self.selected_group_objects:  # Verifica se a lista de objetos selecionados não está vazia
            for game_object in self.selected_group_objects:
                clone = self.copy_object(game_object)
                clones.append(clone)  # Adiciona o clone à lista de clones
                self.game_objects.append(clone)
                print("clonando group")
            self.set_dragging_objects(clones, x, y)  # Passa a lista de clones em vez de um único clone
       
        if not object_clicked:
            self.selected_group_objects = []
            self.selection_rectangle_start = (x, y)





    
    def handle_multi_select_event(self, x, y):

        object_clicked = False
        for game_object in self.game_objects:
            if game_object.rect.collidepoint(x, y):
                object_clicked = True
                if game_object not in self.selected_group_objects:
                    self.selected_group_objects.append(game_object)
                    self.set_dragging_objects(game_object, x, y)
                  
                break
        if not object_clicked:
            self.selected_group_objects = []
            self.selection_rectangle_start = (x, y)

    
    def handle_object_drag(self, x, y):
        if self.dragging_objects is not None and self.dragging_start_pos is not None:
            for obj, start_pos in zip(self.dragging_objects, self.dragging_start_pos):
                dx = x - start_pos[0]  # Correção aqui
                dy = y - start_pos[1]
                obj.move_to(start_pos[0] + dx, start_pos[1] + dy)
            self.dragging_start_pos = [(obj.rect.x, obj.rect.y) for obj in self.dragging_objects]


    def check_menu_click(self, x, y):
        if self.dragging_objects is None:
            menu_rect = pygame.Rect(self.menu_start_x, self.menu_start_y, self.menu_item_width * self.menu_items_per_row,
                                    self.menu_item_height * (len(char_to_class) // self.menu_items_per_row + 1))
            if menu_rect.collidepoint(x, y):
                self.handle_menu_click(x, y)

    def handle_menu_click(self, x, y):
        mouse_x, mouse_y = x, y
        for i, (char, cls) in enumerate(char_to_class.items()):
            row = i // self.menu_items_per_row
            col = i % self.menu_items_per_row

            x = self.menu_start_x + col * self.menu_item_width
            y = self.menu_start_y + row * self.menu_item_height

            rect = pygame.Rect(x, y, self.menu_item_width, self.menu_item_height)
            if rect.collidepoint(mouse_x, mouse_y):
                if self.game_objects:
                    z = max(obj.z for obj in self.game_objects) + 1  # New line
                else:
                    z = 1
                clone = self.copy_object(cls(x, y, sheet_image, z))
                self.set_dragging_objects([clone], x, y)  # Passa uma lista com o clone
                self.mouse_offset_x = mouse_x - clone.rect.x
                self.mouse_offset_y = mouse_y - clone.rect.y
                self.adding_new_object = True
                self.set_dragging_object_depth()
                break


    def set_dragging_objects(self, clones, x, y):
        print("set_dragging_objects foi chamado")
        self.dragging_objects = clones
        self.dragging_start_pos = [(x, y) for _ in clones]     
        print(self.dragging_objects)  # Adicione esta linha    


    def set_dragging_object_depth(self):
        if self.dragging_objects is not None:  # Verifica se self.dragging_objects não é None
            for obj in self.dragging_objects:  # Precisamos fazer a verificação e a mudança para cada objeto na lista
                if self.game_objects:
                    self.original_z = obj.z
                    obj.z = max(o.z for o in self.game_objects) + 1
                else:
                    self.original_z = obj.z
                    obj.z = 1



    


    def run(self):
        while True:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.handle_quit_event(event)
                    elif event.type == pygame.KEYDOWN:
                        self.handle_key_down_event(event)
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        self.handle_mouse_button_down_event(event)
                    elif event.type == pygame.MOUSEBUTTONUP:
                        self.handle_mouse_button_up_event(event)
                    elif event.type == pygame.MOUSEMOTION:
                        self.handle_mouse_motion_event(event)                        

                # Limpa a tela antes de desenhar
                screen.fill((45, 50, 184))

                # Desenha todos os objetos, exceto o que está sendo arrastado
                for game_object in sorted(self.game_objects, key=lambda obj: obj.z):
                    if game_object != self.dragging_objects:
                        game_object.draw(screen)

 
              
                if self.dragging_group_objects is not None and self.dragging_start_pos is not None:
                        x, y = pygame.mouse.get_pos()
                        for obj, start_pos in zip(self.dragging_group_objects, self.dragging_start_pos):  # Vamos iterar tanto os objetos quanto suas posições iniciais
                            dx = x - start_pos[0]
                            dy = y - start_pos[1]
                            obj.move_to(obj.rect.x + dx, obj.rect.y + dy)
                        self.dragging_start_pos = [(obj.rect.x, obj.rect.y) for obj in self.dragging_group_objects]  # Atualiza a posição inicial de cada objeto


                for obj in self.selected_group_objects:
                    draw_dashed_rect(screen, obj.rect, (255, 0, 0), 3)


                # Desenha o menu
                draw_menu(game)
                # Desenha a área do jogo
                pygame.draw.rect(screen, (255, 255, 255), pygame.Rect(0, 0, self.object_area_width, screen.get_height()), 2)

                pygame.display.update()    
                # Verifica se há pelo menos um objeto na lista
                if self.selected_group_objects:
                # Desenha as coordenadas do objeto selecionado
                    draw_coordinates(screen, self.selected_group_objects[0])    
                    draw_object_name(screen, self.selected_group_objects[0])    
                    draw_object_count(screen,self.selected_group_objects)
                    pygame.display.flip()

                # Limita a taxa de quadros
                clock.tick(60)             

game = Game(tile_size, object_area_width, object_area_width + 20, 180, 110, 110, 3)
game.run()







game.scroll_speed = tile_size  # Velocidade de rolagem (pixels por quadro)
game.object_area_width = object_area_width





