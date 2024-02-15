import pygame
import os
import csv
import json

class Component():
    def __init__(self, code="W", x=0 , y=0 , color=(255,0,0), width=0, height=0):
        self.code = code
        self.pins = data[code]["pins"]
        self.width = width
        self.height = height
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.color = color
        self.rotation = 0
        self.shadow_color = (100, 100, 150)
        self.dragging = False
        self.selected = False
        self.offset_x = 0
        self.offset_y = 0
    
    def draw(self, screen):
        # Draw component shadow if selected
        if self.selected:
            shadow_rect = pygame.Rect(self.rect.x-1, self.rect.y-1, self.width+2, self.height+2)
            pygame.draw.rect(screen, self.shadow_color, shadow_rect)
        try:
            current_dir = os.path.dirname(__file__)
            relative_path = os.path.join(current_dir, 'src', f'{self.code}.png')
            image = pygame.image.load(relative_path)
            rotated_image = pygame.transform.rotate(image, self.rotation * 90)
            screen.blit(rotated_image, self.rect)
        except:
            pygame.draw.rect(screen, self.color, self.rect)

    def Rotate(self):
        self.rotation += 1
        self.rotation %= 4
        self.width, self.height = self.height, self.width
        self.rect.w = self.width
        self.rect.h = self.height

    def update_position(self, pos):
        self.rect.topleft = pos


def serialize(obj):
    # Convert object to json format
    if not isinstance(obj.rect, pygame.Rect):
        raise TypeError("obj.rect must be a pygame.Rect object")
    return json.dumps({
        "code": obj.code,
        "width": obj.width,
        "height": obj.height,
        "x": obj.rect.x,
        "y": obj.rect.y,
        "rotation": obj.rotation
    })


def deserialize(js):
    DATA = json.loads(js)
    obj = Component()
    obj.code = DATA["code"]
    obj.pins = data[obj.code]["pins"]
    obj.width = DATA["width"]
    obj.height = DATA["height"]
    obj.rect = pygame.Rect(DATA["x"], DATA["y"], obj.width, obj.height)
    obj.rotation = DATA["rotation"]
    return obj


def load(str):
    global Connections, Circuit
    jsn = json.loads(str)
    lst = []
    Connections = jsn["Connections"]
    for C in jsn["Circuit"]:
        lst.append(deserialize(C))
    Circuit = lst

def save():
    lst = []
    for C in Circuit:
        lst.append(serialize(C))
    return (json.dumps({"Circuit" : lst, 
                        "Connections" : Connections}))

# Button Class
class Button():
    def __init__(self, x, y, width, height, text, action, d=(29, 120, 116),h=(19, 79, 76)):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.default = d
        self.hover = h
        self.color = self.default
        self.action = action

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        font = pygame.font.SysFont(None, 24)
        text = font.render(self.text, True, (0, 0, 0))
        text_rect = text.get_rect(center=self.rect.center)
        screen.blit(text, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            if self.rect.collidepoint(event.pos):
                # Change button color when hovered
                self.color = self.default
            else:
                self.color = self.hover
                
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if self.rect.collidepoint(event.pos):
                    self.action()


# Component Button Class
class ComponentButton(Button):
    def __init__(self, x, y, width, height, text, component_id):
        super().__init__(x, y, width, height, text, self.create_component)
        self.component_id = component_id

    def create_component(self):
        component_data = data[self.component_id]
        component = Component(self.component_id, 50, 60, component_data["color"], component_data["width"], component_data["height"])
        Circuit.append(component)

class DeleteButton(Button):
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "remove component" , self.delete_component, (255,0,0), (165,42,42))

    def delete_component(self):
        global Connections
        for component in Circuit:
            if component.selected:
                # If found record index and remove component
                index = Circuit.index(component)
                Circuit.remove(component)
                temp = {}
                for key, value in Connections.items():
                    t = key[:1]
                    key = int(key[1:])
                    if key != index:
                        if key > index:
                            key -= 1
                        nlist = []
                        for i in value:
                            if i > index:
                                nlist.append(i-1)
                            elif i < index:
                                nlist.append(i)
                        temp[t + str(key)] = nlist
                # Remove all instances of the component within the dictionary
                Connections = temp
                break

data = {}

Circuit = []
Connections = {}

def Open(sve=""):
    global Circuit, Connections, data
    
    Circuit = []
    Connections = {}

    with open('api/Classes/component.csv', 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # Extract the relevant information from each row
            code = row['Code']
            name = row['Name']
            Pins = int(row["Pins"])
            width = int(row['Width'])
            height = int(row['Height'])
            # Create a dictionary with the extracted information
            component_info = {
                'a': name,
                'pins' : Pins,
                'width': width,
                'height': height,
                'color' : (255,0,0)
            }
            # Add the component information to the data dictionary
            data[code] = component_info

    pygame.init()

    size = 5*4
    screen = pygame.display.set_mode((size*50, int(size*31.25)))
    pygame.display.set_caption("Editor")

    if sve:
        load(sve)

    Transform = [[(1,0.5),(0.5,1),(0,0.5),(0.5,0)],
                 [(0,0.5),(0.5,0),(1,0.5),(0.5,1)],
                 [(0.5,1),(1,0.5),(0.5,0),(0,0.5)]]

    # Define sidebar dimensions and button width
    sidebar_width = 200
    button_height = 40
    button_margin = 10
    button_width = sidebar_width - 2 * button_margin
    sidebar_rect = pygame.Rect(screen.get_width() - sidebar_width, 0, sidebar_width, screen.get_height())


    # Create buttons for each component
    component_buttons = [DeleteButton(screen.get_width() - sidebar_width + button_margin, 10, button_width, button_height)]
    y_pos = button_margin + 50
    for component_id, component_data in data.items():
        component_button = ComponentButton(screen.get_width() - sidebar_width + button_margin, y_pos, button_width, button_height, f"Create {component_data['a']}", component_id)
        component_buttons.append(component_button)
        y_pos += button_height + button_margin

    # Position buttons on the sidebar
    for i, button in enumerate(component_buttons):
        button.rect.topleft = (screen.get_width() - sidebar_width + button_margin, i * (button_height + button_margin) + button_margin)

    # Game loop
    running = True
    while running:
        screen.fill((255, 255, 255))  # Set background to white
        # Draw gray grid lines
        grid_spacing = 50  # Adjust as needed
        for x in range(0, screen.get_width(), grid_spacing):
            pygame.draw.line(screen, (200, 200, 200), (x, 0), (x, screen.get_height()))
        for y in range(0, screen.get_height(), grid_spacing):
            pygame.draw.line(screen, (200, 200, 200), (0, y), (screen.get_width(), y))

        # Draw components
        for component in Circuit:
            component.draw(screen)
        
        # Draw wires
        for wire in Connections:
            end = Connections[wire]
            for points in end:
                # Define wire color
                wire_color = (255, 0, 0)

                # Calculate starting position of the wire
                start_component = Circuit[int(wire[1:])]
                # Specifying which terminal
                if wire[:1] == 'a':
                    start_x = start_component.rect.x + start_component.width * Transform[0][start_component.rotation][0]
                    start_y = start_component.rect.y + start_component.height * Transform[0][start_component.rotation][1]
                elif wire[:1] == 'b':
                    start_x = start_component.rect.x + start_component.width * Transform[2][start_component.rotation][0]
                    start_y = start_component.rect.y + start_component.height * Transform[2][start_component.rotation][1]
                pos1 = (start_x, start_y)

                # Calculate ending position of the wire
                end_component = Circuit[points]
                end_x = end_component.rect.x + end_component.width * Transform[1][end_component.rotation][0]
                end_y = end_component.rect.y + end_component.height * Transform[1][end_component.rotation][1]
                pos2 = (end_x, end_y)

                # Draw the wire
                pygame.draw.line(screen, wire_color, pos1, pos2, 4)


        # Draw sidebar
        pygame.draw.rect(screen, (7, 30, 34), sidebar_rect)  # Draw sidebar
        for button in component_buttons:
            button.draw(screen)
            
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                
                running = False
            # Inside the event handling loop
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:  # Mouse wheel scrolled up
                    if sidebar_rect.collidepoint(event.pos) and component_buttons[0].rect.y < 10:
                        # Adjust the y positions of buttons to scroll up
                        for button in component_buttons:
                            button.rect.y += 10  # Increase the y position by 10 pixels
                elif event.button == 5:  # Mouse wheel scrolled down
                    if sidebar_rect.collidepoint(event.pos) and component_buttons[-1].rect.y > screen.get_height() - 50:
                        # Adjust the y positions of buttons to scroll down
                        for button in component_buttons:
                            button.rect.y -= 10  # Decrease the y position by 10 pixels

            for c1 in Circuit:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    # Check if the mouse click is on a component
                    if event.button == 1 and c1.rect.collidepoint(event.pos):
                        # Deselect all components
                        for c2 in Circuit:
                            c2.selected = False
                        # Select the clicked component
                        c1.selected = True
                        c1.dragging = True
                        # Calculate the offset for the selected component being dragged
                        c1.offset_x = c1.rect.x - event.pos[0]
                        c1.offset_y = c1.rect.y - event.pos[1]
                        
                    elif event.button == 3 and c1.rect.collidepoint(event.pos):
                        if not c1.selected:
                            selected_index = None
                            for index, component in enumerate(Circuit):
                                if component.selected:
                                    selected_index = index
                                    break
                            if selected_index is not None:
                                if "a" + str(selected_index) not in Connections:
                                    Connections["a" + str(selected_index)] = [Circuit.index(c1)]
                                else:
                                    if Circuit.index(c1) not in Connections["a" + str(selected_index)]:
                                        Connections["a" + str(selected_index)].append(Circuit.index(c1))
                                    else:
                                        Connections["a" + str(selected_index)].remove(Circuit.index(c1))
                        else:
                            c1.Rotate()
                        
                    elif event.button == 2 and c1.rect.collidepoint(event.pos) and not c1.selected:
                        # Connection for a 3rd terminal
                        selected_index = None
                        for index, component in enumerate(Circuit):
                            if component.selected:
                                selected_index = index
                                break
                        if selected_index is not None and Circuit[selected_index].pins > 2:
                            if "b" + str(selected_index) not in Connections:
                                Connections["b" + str(selected_index)] = [Circuit.index(c1)]
                            else:
                                if Circuit.index(c1) not in Connections["b" + str(selected_index)]:
                                    Connections["b" + str(selected_index)].append(Circuit.index(c1))
                                else:
                                    Connections["b" + str(selected_index)].remove(Circuit.index(c1))
                        
                elif event.type == pygame.MOUSEBUTTONUP:
                    # Deselect all components
                    if event.button == 1:
                        for c2 in Circuit:
                            c2.dragging = False
                elif event.type == pygame.MOUSEMOTION:
                    for c1 in Circuit:
                        if c1.selected and c1.dragging:
                            # Update the position of the selected component being dragged
                            c1.update_position((event.pos[0] + c1.offset_x, event.pos[1] + c1.offset_y))

            for button in component_buttons:
                button.handle_event(event)
        # Update the display
        pygame.display.flip()

    # Quit Pygame
    pygame.quit()
    return save()