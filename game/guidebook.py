import pygame

class BookScene():

    BOOK_COLOURS = { 
        "PLANT": (255,0,0),
        "FERTILISER": (0,255,0),
        "SOIL": (0,0,255),
        "DEFAULT": (255,0,0)
    }

    def __init__(self, scene):
        self.scene = scene
        self.scene_width = scene.get_width()
        self.scene_height = scene.get_height()

        self.setup_book()

    def setup_book(self):
        self.draw_layout(self.BOOK_COLOURS.get("DEFAULT")) # needs colour
    
    #Add new item
    #Update stroke of main when selected a button and ui?

    def draw_layout(self, colour):
        self.main_Page_Inner()

    # Main Page Layout
    def main_Page_Inner(self):
        RECTANGLE_WIDTH = 600
        RECTANGLE_HEIGHT = 400
        SCREEN_WIDTH = self.scene_width/2 - RECTANGLE_WIDTH/2
        SCREEN_HEIGHT = self.scene_height/2 - RECTANGLE_HEIGHT/2
       # self.rectangle_pos = (SCREEN_WIDTH)
        rectangle = pygame.draw.rect(self.scene, self.BOOK_COLOURS.get("DEFAULT"), pygame.Rect(SCREEN_WIDTH,SCREEN_HEIGHT,RECTANGLE_WIDTH,RECTANGLE_HEIGHT))
        
        # new buttons
        buttons = createButtons(rectangle)

        buttons.newButton("Plant",(0,0,125))
        buttons.newButton("Fertiliser", (0,0,125))
        buttons.newButton("Soil", (0,0,125))

class createButtons():

    button_spacing = 0

    def __init__(self, rectangle):
        self.book = rectangle

    def colourDictionary(self, string):
        BUTTON_COLOURS = { # Add button colours here!
            "Fertiliser": (207, 217, 180),
            "Plant":(42, 245, 140),
            "Soil": (68, 241, 218)
        }

        for key in BUTTON_COLOURS:
            if string.upper() == key.upper():
                return BUTTON_COLOURS[key]

        return "not found"

    def newButton(self, string, colour): # add colours and text

        # variables
        topleftx = self.book.x + 20
        toplefty = self.book.y

        width_of_buttons = 100
        height_of_buttons = 50

        text_font_size = 36

        # creating box
        #parameters: screen, colour, Rect(xpos,ypos,width,height)
        rect = pygame.draw.rect(screen, self.colourDictionary(string) , pygame.Rect(topleftx + self.button_spacing, toplefty - height_of_buttons/2, width_of_buttons, height_of_buttons))
        
        # creating text
        font = pygame.font.Font(None, text_font_size)
        text_width, text_height = font.size(string)
        # adjust size of text if the length exceeds boundaries

        while (text_width >= rect.width):
            text_font_size = text_font_size - 5
            font = pygame.font.Font(None, text_font_size)
            text_width2, text_height = font.size(string)

            if (text_width2 < rect.width):
                break
        
        text = font.render(string, True, (0,0,0))
        pos = text.get_rect(center=(rect.centerx,rect.centery))
        #parameters: x, y

        screen.blit(text, pos)
        
        self.button_spacing = self.button_spacing + width_of_buttons + 15

"""
STAGES
- Buttons

"""

pygame.init()

pygame.display.set_caption('Testing')
screen = pygame.display.set_mode((800,600))
screen.fill((234, 212, 200))
BookScene(screen)
pygame.display.flip()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

pygame.quit()