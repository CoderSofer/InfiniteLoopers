import pygame

once = 0
fonts = {}

sounds = {
    "BUY" : "./game//soundfiles/buy2.wav",
    "CLICK" : "./game//soundfiles/click1.wav",
    "PICK" : "./game//soundfiles/pick2.wav",
    "HARVEST" : "./game/soundfiles/harvest4.wav",
    "PLANT" : 0
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

def popup(rect, mousex, mousey):
    global once
    global fonts

    if not (rect.collidepoint(mousex,mousey)):
        return fonts

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
    once = 1

    print("works")
    return fonts

def HarvestFunctionality(mousex, mousey):
    global once
    global fonts
    
    if fonts["Harvest"]["position"].collidepoint(mousex, mousey):
        playSound(sounds["HARVEST"])
        clearText()
        once = 0

def SellFunctionality(mousex, mousey):
    global once
    global fonts

    if fonts["Sell"]["position"].collidepoint(mousex, mousey):
        playSound(sounds["BUY"])
        clearText()
        once = 0

def PlantFunctionality(mousex, mousey):
    global once
    global fonts

    if fonts["Plant"]["position"].collidepoint(mousex, mousey):
        playSound(sounds["PICK"])
        clearText()
        once = 0

def ExitFunctionality(mousex, mousey):
    global once
    global fonts
    
    if fonts["Exit"]["position"].collidepoint(mousex, mousey):
        playSound(sounds["CLICK"])
        clearText()
        once = 0

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

            mousex, mousey = pygame.mouse.get_pos()

            if once == 0:
                fonts = popup(rect, mousex,mousey)

                print("Exit position:", type(fonts["Exit"]["position"]))


            else:
                if not fonts:
                    continue

                if "Exit" in fonts and fonts["Exit"]["position"].collidepoint(mousex, mousey):
                    ExitFunctionality(mousex, mousey)
                    continue
                elif "Plant" in fonts and fonts["Plant"]["position"].collidepoint(mousex, mousey):
                    PlantFunctionality(mousex, mousey)
                    continue
                elif "Sell" in fonts and fonts["Sell"]["position"].collidepoint(mousex, mousey):
                    SellFunctionality(mousex, mousey)
                    continue
                elif "Harvest" in fonts and fonts["Harvest"]["position"].collidepoint(mousex, mousey):
                    HarvestFunctionality(mousex, mousey)
                    continue


pygame.quit()