import pygame


# havent had the chance to fully fix this but yeah.

once = 0
fonts = {}

sounds = {
    "BUY" : "./game//soundfiles/buy2.wav",
    "CLICK" : "./game//soundfiles/click1.wav",
    "HARVEST" : "./game/soundfiles/harvest4.wav",
    "PLANT" : "./game//soundfiles/pick2.wav"
}

def playSound(sound):
    pygame.mixer.music.load(sound)
    pygame.mixer.music.set_volume(1)
    pygame.mixer.music.play()

def clearText():
    global fonts
    fonts.clear()
    screen.fill((234, 212, 200))
    createRectangle()
    pygame.display.update()

def createRectangle():
    rectangleheight = 100
    rectanglewidth = 100
    xpos = 20
    rect = pygame.draw.rect(screen, (255,5,5), pygame.Rect(xpos, screen.get_height()/2 - rectangleheight/2, rectanglewidth ,rectangleheight))
    return rect

def popup():

    font = pygame.font.Font(None, 36)

    screen_w = screen.get_width()
    screen_h = screen.get_height()

    fonts.clear()
    fonts.update({
        "Harvest": {
            "render": font.render("Harvest", True, (255,0,0)),
            "position": None
        },
        "Sell": {
            "render": font.render("Sell", True, (255,0,0)),
            "position": None
        },
        "Plant": {
            "render": font.render("Plant", True, (255,0,0)),
            "position": None
        },
        "Exit": {
            "render": font.render("Exit", True, (255,0,0)),
            "position": None
        }
    })

    initialx = screen_w/2
    initialy = screen_h/2 - 4*fonts["Exit"]["render"].get_height()
    space = 50

    fonts["Harvest"]["position"] = fonts["Harvest"]["render"].get_rect(topleft=(initialx, initialy))
    fonts["Sell"]["position"] = fonts["Sell"]["render"].get_rect(topleft=(initialx, initialy + space))
    fonts["Plant"]["position"] =  fonts["Plant"]["render"].get_rect(topleft=(initialx, initialy + 2*space))
    fonts["Exit"]["position"] = fonts["Exit"]["render"].get_rect(topleft=(initialx, initialy + 3*space))

    for key in fonts:
        screen.blit(fonts[key]["render"], fonts[key]["position"])
    
    pygame.display.update()

    return fonts

def HarvestFunctionality():
    playSound(sounds["HARVEST"])
    clearText()

def SellFunctionality():
    playSound(sounds["BUY"])
    clearText()

def PlantFunctionality():
    playSound(sounds["PLANT"])
    clearText()

def ExitFunctionality():
    playSound(sounds["CLICK"])
    screen.fill((255,0,0))
    clearText()

pygame.init()
pygame.mixer.init()
pygame.display.set_caption('Testing')
screen = pygame.display.set_mode((500,400))
screen.fill((234, 212, 200))
rect = createRectangle()
pygame.display.flip()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:

            mouse = pygame.mouse.get_pos()

            if rect.collidepoint(mouse):

                if once < 1:
                    popup()
                    once += 1
                else:
                    if not fonts:
                        print("error")
                        continue
            
            if once >= 1 :
                if "Exit" in fonts and fonts["Exit"]["position"].collidepoint(mouse):
                    ExitFunctionality()
                    once = 0
                elif "Plant" in fonts and fonts["Plant"]["position"].collidepoint(mouse):
                    PlantFunctionality()
                    once = 0
                elif "Sell" in fonts and fonts["Sell"]["position"].collidepoint(mouse):
                    SellFunctionality()
                    once = 0
                elif "Harvest" in fonts and fonts["Harvest"]["position"].collidepoint(mouse):
                    HarvestFunctionality()
                    once = 0
                    


pygame.quit()