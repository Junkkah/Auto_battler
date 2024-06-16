import pygame as pg
import sys
from config_ab import Config
from sprites_ab import Adventure
from data_ab import get_data, get_json_data, row_to_dict
import pandas as pd
import random
import math


class WorldMap(Config):
    def __init__(self):
        Config.__init__(self)
        self.next = 'path'
        self.error = False
        self.line_thickness = 10

    def cleanup(self):
        self.map_objects = []
        self.map_data = []
        self.map_sprites.empty()
    
    def generate_random_coordinates(self, adventure: str, num_layers: int, start_size: int):
        coords_file = adventure + '_coords'
        random_coords = get_json_data(coords_file)

        coords_dict = {} 
        start_layer = 1
        start_layer_size = start_size
        last_layer = num_layers
        last_layer_size = 1

        coords_dict[start_layer] = random.choice(random_coords[str(start_layer_size)])
        coords_dict[last_layer] = random.choice(random_coords[str(last_layer_size)])

        for layer in range(2, last_layer):
            num_nodes = len(coords_dict[layer - 1])

            if num_nodes == 3:
                num_nodes += 1
            elif num_nodes == 6:
                num_nodes -= 1
            else:
                num_nodes += random.choice([-1, 1])
            
            if layer == last_layer - 2:
                num_nodes = min(5, num_nodes)
            if layer == last_layer - 1:
                num_nodes = min(4, num_nodes)
            coords_dict[layer] = random.choice(random_coords[str(num_nodes)])
        return coords_dict
    
    def assign_node_type(self, layer: int, node_type_data: dict, fight_prob: float, final_layer: bool):
        #additional types: event, rest(town?), elite monsters
        if final_layer:
            node_type = 'boss'
            node_image = 'cave'
        elif layer == 1:
            node_type = 'fight'
        else:
            node_type = 'fight' if random.random() < fight_prob else 'shop'
            if layer %  2 == 0:
                if node_type == 'shop':
                    node_type = 'fight'

        if node_type == 'fight':
            image_options = node_type_data['fight']
            if isinstance(image_options, list):
                node_image = random.choice(image_options)
            else:
                node_image = image_options
        if node_type == 'shop':
            node_image = node_type_data['shop']

        return (node_type, node_image)
            
    def create_node_dicts(self, num_layers: int, coords_dict: dict, adventure: str, fight_prob: float):
        node_dicts = {}
        node_json = get_json_data('node_types')
        node_type_data = node_json[adventure]
        for layer in range(1, num_layers + 1):
            layer_data = []
            for node_idx, node_coords in enumerate(coords_dict[layer]):
                
                name = f'node{layer}_{node_idx + 1}'

                if layer == num_layers:
                    final_layer = True
                else:
                    final_layer = False
                node_type = self.assign_node_type(layer, node_type_data, fight_prob, final_layer)
                tier = math.ceil(layer / 4) + (len(Config.completed_adventures) * 3)

                node_dict = {
                    'name': name, #'node12_1'
                    'type': node_type[0],  #fight or shop, if layer == 13: boss
                    'y_coord': node_coords,
                    'size_scalar': 10, #based on adventure, set 8-9 for ruins
                    'tier': tier,  
                    'depth': layer,  # Depth
                    'desc': '',  # not used
                    'image_name': node_type[1],  
                    'parent1': None,
                    'parent2': None,  
                    'child1': None,  
                    'child2': None
                }
                layer_data.append(node_dict)
            node_dicts[layer] = layer_data
        return node_dicts
    
    def edge_count(self, num_nodes_current: int, num_nodes_next: int):
        min_edges = max(num_nodes_current, num_nodes_next)
        max_edges = 2 * (min(num_nodes_current, num_nodes_next))
        if num_nodes_current == num_nodes_next:
            max_edges -= 1

        if num_nodes_next == 1:
            num_edges = num_nodes_current
        else:
            num_edges = random.randint(min_edges, max_edges)

        return num_edges
    
    def check_parent(self, layer, index):
        if self.node_dicts[layer][index]['parent1'] == None:
            return 'parent1'
        return 'parent2'

    def assign_child_nodes(self, coords_dict: dict, num_layers: int):
        #not iterating over final layer
        #adding parent for boss node
        self.node_dicts[num_layers][0]['parent1'] = f'node{num_layers - 1}_1'

        for layer in range(1, num_layers):
            current_layer_coords = coords_dict[layer]
            next_layer_coords = coords_dict[layer + 1] if layer + 1 in coords_dict else None
            current_layer_nodes = len(current_layer_coords)
            next_layer_nodes = len(next_layer_coords)
            num_edges = self.edge_count(current_layer_nodes, next_layer_nodes)
            
            if current_layer_nodes == num_edges:
                #possible at layer 11 where node number is restricted
                if current_layer_nodes == next_layer_nodes:
                    for node_idx in range(current_layer_nodes):
                        self.node_dicts[layer][node_idx]['child1'] = f'node{layer + 1}_{node_idx + 1}'
                        self.node_dicts[layer + 1][node_idx]['parent1'] = f'node{layer}_{node_idx + 1}'
                
                elif next_layer_nodes == 1:
                    for node_idx in range(current_layer_nodes):
                        self.node_dicts[layer][node_idx]['child1'] = f'node{layer + 1}_{1}'

                else:
                    #each node has exactly one child, next layer smaller
                    #randomly choose 1 node in next that gets extra parent
                    extra_idx = random.randint(1, next_layer_nodes)
                    #at extra idx and after assign child name at node_idx
                    for node_idx in range(current_layer_nodes):
                        if node_idx >= extra_idx:
                            self.node_dicts[layer][node_idx]['child1'] = f'node{layer + 1}_{node_idx}'
                            parent = self.check_parent(layer + 1, node_idx - 1)
                            self.node_dicts[layer + 1][node_idx - 1][parent] = f'node{layer}_{node_idx + 1}'
                        #before extra idx assign child name at node_idx + 1
                        else:
                            self.node_dicts[layer][node_idx]['child1'] = f'node{layer + 1}_{node_idx + 1}'
                            parent = self.check_parent(layer + 1, node_idx)
                            self.node_dicts[layer + 1][node_idx]['parent1'] = f'node{layer}_{node_idx + 1}'
                    
            if current_layer_nodes < num_edges: #/ else:
                if current_layer_nodes > next_layer_nodes:
                    extra_child_count = num_edges - current_layer_nodes
                    #randomly choose indexes that have extra child
                    extra_idx = random.sample(range(1, next_layer_nodes), extra_child_count)
                    for node_idx in range(current_layer_nodes):
                        #we check if we are at the index that has extra child
                        extra_count = 0
                        if node_idx == extra_idx[extra_count]:
                            extra_count += 1
                            self.node_dicts[layer][node_idx]['child1'] = f'node{layer + 1}_{node_idx}'
                            parent = self.check_parent(layer + 1, node_idx - 1)
                            self.node_dicts[layer + 1][node_idx - 1][parent] = f'node{layer}_{node_idx + 1}'

                            self.node_dicts[layer][node_idx]['child2'] = f'node{layer + 1}_{node_idx + 1}'
                            parent = self.check_parent(layer + 1, node_idx)
                            self.node_dicts[layer + 1][node_idx][parent] = f'node{layer}_{node_idx + 1}'
                        
                        elif node_idx == (current_layer_nodes - 1):
                            self.node_dicts[layer][node_idx]['child1'] = f'node{layer + 1}_{node_idx}'
                            parent = self.check_parent(layer + 1, node_idx - 1)
                            self.node_dicts[layer + 1][node_idx - 1][parent] = f'node{layer}_{node_idx + 1}'
                        
                        else:
                            self.node_dicts[layer][node_idx]['child1'] = f'node{layer + 1}_{node_idx + 1}'
                            parent = self.check_parent(layer + 1, node_idx)
                            self.node_dicts[layer + 1][node_idx][parent] = f'node{layer}_{node_idx + 1}'

                if current_layer_nodes < next_layer_nodes: 
                    extra_child_count = num_edges - current_layer_nodes
                    #which current layer nodes have extra child
                    extra_idx = random.sample(range(0, current_layer_nodes), extra_child_count)
                    for node_idx in range(current_layer_nodes):
                        extra_count = 0
                        if node_idx == extra_idx[extra_count]:
                            extra_count += 1
                            self.node_dicts[layer][node_idx]['child1'] = f'node{layer + 1}_{node_idx + 1}'
                            parent = self.check_parent(layer + 1, node_idx)
                            self.node_dicts[layer + 1][node_idx][parent] = f'node{layer}_{node_idx + 1}'

                            self.node_dicts[layer][node_idx]['child2'] = f'node{layer + 1}_{node_idx + 2}'
                            parent = self.check_parent(layer + 1, node_idx + 1)
                            self.node_dicts[layer + 1][node_idx + 1][parent] = f'node{layer}_{node_idx + 1}'

                        else:
                            self.node_dicts[layer][node_idx]['child1'] = f'node{layer + 1}_{node_idx + 1}'
                            parent = self.check_parent(layer + 1, node_idx)
                            self.node_dicts[layer + 1][node_idx][parent] = f'node{layer}_{node_idx + 1}'

                            if node_idx == (current_layer_nodes - 1):
                                self.node_dicts[layer][node_idx]['child2'] = f'node{layer + 1}_{node_idx + 2}'
                                parent = self.check_parent(layer + 1, node_idx + 1)
                                self.node_dicts[layer + 1][node_idx + 1][parent] = f'node{layer}_{node_idx + 1}'
                
                if current_layer_nodes == next_layer_nodes:
                    extra_child_count = num_edges - current_layer_nodes
                    extra_idx = random.sample(range(0, next_layer_nodes - 1), extra_child_count)
                    for node_idx in range(current_layer_nodes):
                        extra_count = 0
                        if node_idx == extra_idx[extra_count]:
                            extra_count += 1
                            self.node_dicts[layer][node_idx]['child1'] = f'node{layer + 1}_{node_idx + 1}'
                            parent = self.check_parent(layer + 1, node_idx)
                            self.node_dicts[layer + 1][node_idx][parent] = f'node{layer}_{node_idx + 1}'

                            self.node_dicts[layer][node_idx]['child2'] = f'node{layer + 1}_{node_idx + 2}'
                            parent = self.check_parent(layer + 1, node_idx + 1)
                            self.node_dicts[layer + 1][node_idx + 1][parent] = f'node{layer}_{node_idx + 1}'

                        else:
                            self.node_dicts[layer][node_idx]['child1'] = f'node{layer + 1}_{node_idx + 1}'
                            parent = self.check_parent(layer + 1, node_idx)
                            self.node_dicts[layer + 1][node_idx][parent] = f'node{layer}_{node_idx + 1}'

    def write_path_df(self, num_layers: int):
        df = pd.DataFrame(columns=['name', 'type', 'y_coord', 'size_scalar', 'tier', 'depth', 'desc', 'image_name', 'parent1', 'parent2', 'child1', 'child2'])
        data = []
        for depth in range(1, num_layers + 1):
            for node_dict in self.node_dicts[depth]:
                data.append(node_dict)
        df = pd.DataFrame(data)
        return df

    def generate_random_path(self, adventure: str):
        #duplicate map_data needed for simulator
        self.map_data = get_data('adventures')
        adventure_df = self.map_data[self.map_data['name'] == adventure].reset_index(drop=True)
        num_layers = adventure_df.iloc[0]['layers']
        fight_prob = adventure_df.iloc[0]['fight_p']
        start_size = adventure_df.iloc[0]['start_size']

        coords = self.generate_random_coordinates(adventure, num_layers, start_size)
        self.node_dicts = self.create_node_dicts(num_layers, coords, adventure, fight_prob) 
        self.assign_child_nodes(coords, num_layers)
        random_path = self.write_path_df(num_layers)

        return random_path

    def startup(self):
        self.error = False
        self.line_thickness = 10
        self.rect_thickness = 2
        self.text_offset_y = 5

        self.map_data = get_data('adventures')
        self.map_objects = []
        for index, row in self.map_data.iterrows():
            name = row['name']
            coords = (row['pos_x'], row['pos_y'])
            desc = row['desc']
            child = row['child']
            adventure = Adventure(coords, self.map_sprites, desc, name, child)
            self.map_objects.append(adventure)


        def set_child(df):
            for obj in self.map_objects:
                obj_name = obj.name
                obj_child_name = df.loc[df['name'] == obj_name, 'child'].values[0]

                if pd.notna(obj_child_name):
                    obj.child = next((child_obj for child_obj in self.map_objects if child_obj.name == obj_child_name), None)
        set_child(self.map_data)

        hood = pg.image.load('./ab_images/hood.png').convert_alpha()
        self.coords_dialogue = ((self.screen_width * 0.12, self.screen_height * 0.72))
        COORDS_HOOD = (self.screen_width * 0.05, self.screen_height * 0.80)
        SCALAR_HOOD = ((hood.get_width() / self.npc_size_scalar), (hood.get_height() / self.npc_size_scalar))

        adventure_number = len(Config.completed_adventures)
        next_adventure = self.map_objects[adventure_number].desc
        self.overworld_dialogue = [f'"Choose {next_adventure} for', 'your next adventure"']

        self.hood_image = pg.transform.smoothscale(hood, SCALAR_HOOD)
        self.hood_rect = self.hood_image.get_rect(topleft=COORDS_HOOD)

    def get_event(self, event):
        mouse_pos = pg.mouse.get_pos()
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                exit()
        
        elif event.type == pg.MOUSEBUTTONDOWN:
            for adventure in self.map_objects:
                if adventure.rect.collidepoint(mouse_pos):
                    adventure_number = len(Config.completed_adventures)
                    if adventure.name == self.map_objects[adventure_number].name:
                        Config.current_adventure = adventure.name
                        Config.generated_path = self.generate_random_path(Config.current_adventure)
                        self.next = 'path'
                        self.done = True

                    else:
                        error = 'Inaccessible'
                        self.error_text = self.info_font.render((error), True, (self.red))
                        self.error_text_rect = self.error_text.get_rect(topleft=((adventure.pos_x), (adventure.pos_y))) 
                        self.error = True

    def update(self, screen, dt):
        self.draw(screen)

    def draw(self, screen):
        self.screen.blit(self.ground, (0,0))

        for node in self.map_objects:
            if node.child:
                pg.draw.line(self.screen, self.white, node.pos, node.child.pos, self.line_thickness)

        self.map_sprites.draw(self.screen)

        for i, dia_line in enumerate(self.overworld_dialogue):
            dia_line_text = self.dialogue_font.render(dia_line, True, self.black)
            dia_line_rect = dia_line_text.get_rect(center=(self.coords_dialogue[0], self.coords_dialogue[1] + i * self.medium_font_size))
            self.screen.blit(dia_line_text, dia_line_rect)

        self.screen.blit(self.hood_image, self.hood_rect)

        collided_objects = [obj for obj in self.map_objects if obj.rect.collidepoint(pg.mouse.get_pos())]
        if collided_objects:
            obj = collided_objects[0]
            info_text = self.info_font.render(obj.desc, True, self.black)
            info_text_rect = info_text.get_rect(bottomleft=(obj.pos_x + obj.width // 2, obj.pos_y + obj.height // 2 + self.text_offset_y))
            self.screen.blit(info_text, info_text_rect)
            #map_objects.name list 
            if obj.name == 'dark_forest':
                pg.draw.rect(self.screen, self.red, obj.rect, self.rect_thickness)
        
        if self.error == True:
            self.screen.blit(self.error_text, self.error_text_rect)