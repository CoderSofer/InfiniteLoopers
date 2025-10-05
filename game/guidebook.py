import pygame

array_of_menus = {}
array_of_items = {}

BOOKMENU_COLOURS = { # Add button colours here!
    "Fertiliser": (207, 217, 180),
    "Plant":(42, 245, 140),
    "Soil": (68, 241, 218),
    "DEFAULT": (163, 204, 198)
}

def colourDictionary(string):

    for key in BOOKMENU_COLOURS:
        if string.upper() == key.upper():
            return BOOKMENU_COLOURS[key]

    return "not found"

"""
elif event.type == pygame.MOUSEBUTTONDOWN:
    mouse_pos = pygame.mouse.get_pos()
    
    if current_tab != "Main":
        if back_button_rect.collidepoint(mouse_pos):
            current_tab = "Main"
            book_scene = BookScene(screen)
            pygame.display.flip()
            continue

    #check if any button was clicked
    for rect, label in book_scene.buttons.buttons:
        if rect.collidepoint(mouse_pos):
        print(f"{label} tab clicked")
        switch_tab(label)
"""
def addToArrayOfItems(name, item, category):
    array_of_items.setdefault(category, {})[name] = item

def addToArrayOfMenus(item, category):
    array_of_menus[category] = item

class BookScene():

    def __init__(self, scene):
        self.scene = scene
        self.setup_book()

    def setup_book(self):
        self.create_foundation()
        self.create_buttons()
        self.create_Items()

    # Main Page Layout
    def create_foundation(self):
        BOOK_WIDTH = 600
        BOOK_HEIGHT = 400
        SCREEN_WIDTH = self.scene.get_width()/2 - BOOK_WIDTH/2
        SCREEN_HEIGHT = self.scene.get_height()/2 - BOOK_HEIGHT/2

        self.rectangle = pygame.draw.rect(self.scene, BOOKMENU_COLOURS.get("DEFAULT"), pygame.Rect(SCREEN_WIDTH,SCREEN_HEIGHT,BOOK_WIDTH,BOOK_HEIGHT))

    def create_Items(self):
        self.item = Items(self.rectangle)

        #names have to be unique otherwise it will not display items correctly
        self.item.addItemToGuideBook("name2", 4, "image.png", "new plant", "Plant")
        self.item.addItemToGuideBook("name", 8, "image.png", "new bush", "Fertiliser")

    def create_buttons(self):
        buttons = createButtons(self.rectangle)

        button1 = buttons.newButton("Plant")
        button2 = buttons.newButton("Fertiliser")
        button3 = buttons.newButton("Soil")

        # be able to click these

    def display_items(self, category):
        self.item.displayItems(category)
    
class Items():
    
    """
    Aim: Create new item

    Requirements:
    - Name
    - Value
    - Image (for now.. rectangle)
    - Same dimensions for card (different for card in guidebook and outside of it)
    - Colour
    - Descriptions

    Add new item
    - Add card to guidebook DONE
    - Retrieve everything except descriptions? DONE
    (Consider: Let filter change what is displayed, or add hover over to reveal description)

    When interact with item
    - Create new card to the left of screen (movable?)
    - Retrieve all the requirement list

    Need to track position
    - if it exceeds to the right, skip to next line
    - add scroll if it exceeds downwards (later feature)
    """

    SPACING = 0

    def __init__(self, foundation):
        self.item_list = {}
        self.foundation = foundation

    def addItemToGuideBook(self, name, value, image, description, category):
        self.item_list[name] = {
            "value": value,
            "image": image,
            "colour": (217,217,217),
            "descriptions": description,
            "category": category
        }

        # create rectangle
        # check if it exceeds boundaries to the right of rectangle
    
    def produceText(self, text_font_size, rect, string):
        rectx, recty = rect.bottomleft

        font = pygame.font.Font(None, text_font_size)
        text_width, text_height = font.size(string)

        while (text_width >= rect.width):
            text_font_size = text_font_size - 1
            font = pygame.font.Font(None, text_font_size)
            text_width, text_height = font.size(string)
                
        text = font.render((string), True, (0,0,0))
        center_position = text.get_rect(topleft=(rectx + rect.width/2 - text_width/2 ,recty - text_height))
        screen.blit(text, center_position)
    
    def displayItems(self, category):

        screen.fill((234, 212, 200))
        book.create_foundation()
        book.create_buttons()
        
        WIDTH = 125
        HEIGHT = 125
        posx = self.foundation.x + 20
        posy = self.foundation.y + 50
        text_font_size = 36

        for key in self.item_list:

            if not (self.item_list[key]["category"] == category):
                continue

            self.item_list[key]["rect"] = pygame.draw.rect(screen, self.item_list[key]["colour"], pygame.Rect(posx + self.SPACING, posy, WIDTH, HEIGHT))
            addToArrayOfItems(key, self.item_list[key], self.item_list[key]["category"])

            self.SPACING = self.SPACING + WIDTH + 15

            # add value to rectangle

            self.produceText(text_font_size, self.item_list[key]["rect"], "value: " + str(self.item_list[key]["value"]))

            pygame.display.update()

        self.SPACING = 0

class createButtons():

    button_spacing = 0
    WIDTH_OF_BUTTONS = 100
    HEIGHT_OF_BUTTONS = 50
    
    def __init__(self, rectangle):
        self.TOPLEFTX = rectangle.x + 20
        self.TOPLEFTY = rectangle.y

    def produceText(self, text_font_size, rect, string):
        font = pygame.font.Font(None, text_font_size)
        text_width, text_height = font.size(string)
        
        while (text_width >= rect.width):
            text_font_size = text_font_size - 1
            font = pygame.font.Font(None, text_font_size)
            text_width, text_height = font.size(string)
        
        text = font.render(string, True, (0,0,0))
        center_position = text.get_rect(center=(rect.centerx,rect.centery))
        screen.blit(text, center_position)
        self.button_spacing = self.button_spacing + self.WIDTH_OF_BUTTONS + 15


    def newButton(self, string):
        text_font_size = 36

        rect = pygame.draw.rect(screen, colourDictionary(string) , pygame.Rect(self.TOPLEFTX + self.button_spacing, self.TOPLEFTY - self.HEIGHT_OF_BUTTONS/2, self.WIDTH_OF_BUTTONS, self.HEIGHT_OF_BUTTONS))
        
        self.produceText(text_font_size, rect, string)

        addToArrayOfMenus(rect, string)
        

pygame.init()

pygame.display.set_caption('Testing')
screen = pygame.display.set_mode((800,600))
screen.fill((234, 212, 200))
book = BookScene(screen)
pygame.display.flip()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:

            mouse_pos = pygame.mouse.get_pos()

            for category, items in array_of_items.items():
                for name, item in items.items():
                    if "rect" in item and item["rect"].collidepoint(mouse_pos):
                        print(" clicked!")

            for category, rect in array_of_menus.items():
                if rect.collidepoint(mouse_pos):
                    book.display_items(category)

pygame.quit()