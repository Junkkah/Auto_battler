import pygame as pg
import sys
from config_ab import Config
from sprites_ab import Adventure
from data_ab import get_data, get_json_data, row_to_dict
import pandas as pd
import random


class WorldMap(Config):
    def __init__(self):
        Config.__init__(self)
        self.next = 'path'
        self.error = False
        self.line_thickness = 10

    def cleanup(self):
        self.map_objects = []
        self.map_sprites.empty()
    
    def generate_random_coordinates(self, adventure: str):
        coords_file = adventure + '_coords'
        random_coords = get_json_data(coords_file)

        coords_dict = {} 
        start_layer = 1
        start_layer_size = 3
        last_layer = 13
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
    
    def assign_node_type(self, layer):
        #assign probabilities based on Adventure
        #map location names based on Adventure
        fight_probability = 0.8
        if layer == 1:
            node_type = 'fight'
        elif layer == 13:
            node_type = 'boss'
            node_image = 'cave'
        else:
            node_type = 'fight' if random.random() < fight_probability else 'shop'

        if node_type == 'fight':
            node_image = random.choice(['tree', 'bush'])
        if node_type == 'shop':
            node_image = 'town'
        return (node_type, node_image)
            
    def create_node_dicts(self, num_layers, coords_dict):
        node_dicts = {}
        for layer in range(1, num_layers + 1):
            layer_data = []
            for node_idx, node_coords in enumerate(coords_dict[layer]):
                
                name = f'node{layer}_{node_idx + 1}'
                node_type = self.assign_node_type(layer)
                #assign node type after assign children. if parent == town: node_type = fight
                tier  = (layer + 2) // 3
                
                node_dict = {
                    'name': name, #'node12_1'
                    'type': node_type[0],  #fight or shop, assign later if layer == 13: boss
                    'y_coord': node_coords,
                    'size_scalar': 10, #based on adventure
                    'tier': tier,  # depth 4: 2, depth 7: 3, depth 10: 4, depth 13: 5 
                    'depth': layer,  # Depth
                    'desc': '',  # not used
                    'image_name': node_type[1],  
                    'parent1': None, #assing children next
                    'parent2': None,  
                    'child1': None,  
                    'child2': None
                }
                layer_data.append(node_dict)
            node_dicts[layer] = layer_data
        return node_dicts
    
    def edge_count(self, num_nodes_current, num_nodes_next):
        min_edges = max(num_nodes_current, num_nodes_next)
        max_edges = 2 * (min(num_nodes_current, num_nodes_next))

        if num_nodes_next == 1:
            num_edges = num_nodes_current
        else:
            num_edges = random.randint(min_edges, max_edges)

        return num_edges
    
    def check_parent(self, layer, index):
        if self.node_dicts[layer][index]['parent1'] == None:
            return 'parent1'
        return 'parent2'


    def assign_child_nodes(self, coords_dict):
        self.node_dicts[13][0]['parent1'] = 'node12_1'
        num_layers = len(coords_dict)
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
                
                #all child1 does not working, set_children works how?
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
                            parent = self.check_parent(layer + 1, node_idx - 1) #are we chaking correct node?
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

    def write_path_df(self, num_layers):
        df = pd.DataFrame(columns=['name', 'type', 'y_coord', 'size_scalar', 'tier', 'depth', 'desc', 'image_name', 'parent1', 'parent2', 'child1', 'child2'])
        data = []
        for depth in range(1, num_layers + 1):
            for node_dict in self.node_dicts[depth]:
                data.append(node_dict)
        df = pd.DataFrame(data)
        return df

    def generate_random_path(self, adventure: str):
        #procedurally generated directed acylic graph for adventure path
        #adventure determines: image_names, shop probabilities, starting tier
        #ramp up tier from starting, forest: 1-3, ruins 3-6, swamp, 7-9, give bosses tier bonus
        
        num_layers = 13
        starting_tier = 1 #for dark forest
        coords = self.generate_random_coordinates(adventure)
        self.node_dicts = self.create_node_dicts(num_layers, coords) 
        #returns dictionary where key is layer and valus is list of node_dicts for that layer 
        self.assign_child_nodes(coords)
        random_path = self.write_path_df(num_layers)

        return random_path

    def startup(self):
        self.error = False
        self.line_thickness = 10
        self.rect_thickness = 2
        self.text_offset_y = 5

        map_data = get_data('adventures')
        self.map_objects = []
        for index, row in map_data.iterrows():
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
        set_child(map_data)

        hood = pg.image.load('./ab_images/hood.png').convert_alpha()
        self.coords_dialogue = ((self.screen_width * 0.12, self.screen_height * 0.72))
        COORDS_HOOD = (self.screen_width * 0.05, self.screen_height * 0.80)
        SCALAR_HOOD = ((hood.get_width() / self.npc_size_scalar), (hood.get_height() / self.npc_size_scalar))

        self.overworld_dialogue = ['"Choose Dark Forest for', 'your first adventure"']

        self.hood_image = pg.transform.smoothscale(hood, SCALAR_HOOD)
        self.hood_rect = self.hood_image.get_rect(topleft=COORDS_HOOD)

    def get_event(self, event):
        mouse_pos = pg.mouse.get_pos()
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                exit()
        
        elif event.type == pg.MOUSEBUTTONDOWN:
            for obj in self.map_objects:
                if obj.rect.collidepoint(mouse_pos):
                    if obj.name == 'dark_forest':
                        Config.current_adventure = obj.name
                        Config.generated_path = self.generate_random_path(Config.current_adventure)
                        self.next = 'path'
                        self.done = True

                    else:
                        error = 'Inaccessible'
                        self.error_text = self.info_font.render((error), True, (self.red))
                        self.error_text_rect = self.error_text.get_rect(topleft=((obj.pos_x), (obj.pos_y))) 
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
            #create adv list, if obj.name == next item on list
            if obj.name == 'dark_forest':
                pg.draw.rect(self.screen, self.red, obj.rect, self.rect_thickness)
        
        if self.error == True:
            self.screen.blit(self.error_text, self.error_text_rect)