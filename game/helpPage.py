import pygame

def show_help(screen, pixel_font, sfx):
    #load image
    help_image = pygame.image.load("./images/help_page.png").convert_alpha()
    help_image = pygame.transform.scale(help_image, (100,500))

    #position to the left side
    image_rect=help_image.get_rect()
    image_rect.bottomleft=(0,screen.get_height()-10)
    
    #Load and position truck
    truck_image = pygame.image.load("./images/truck.png").convert_alpha()
    truck_image = pygame.transform.scale(truck_image, (200,90))

    truck_rect = truck_image.get_rect()
    truck_rect.bottomright = (screen.get_width() - 10, screen.get_height()-10)

    #Load and scale back arrow icon
    arrow_image=pygame.image.load("./images/arrow.png").convert_alpha()
    arrow_image = pygame.transform.scale(arrow_image, (75, 75))

    arrow_rect=arrow_image.get_rect()
    arrow_rect.midtop=(35,35)

    #load font for help instrcutions
    instruction_font = pygame.font.Font("./pixel_Font.ttf", 35)

    
    running=True
    quit_game=False
    while running:
        screen.fill('#f5e49c')

        #Draw all visual elements
        screen.blit(help_image,image_rect)
        screen.blit(truck_image, truck_rect)
        screen.blit(arrow_image, arrow_rect)

        #Render and enter "Help" title
        help_text=pixel_font.render("Help", True, (53,94,59))
        help_rect=help_text.get_rect()
        help_rect.midtop = (screen.get_width()//2,10)
        screen.blit(help_text,help_rect)

        #Display help instructions
        instructions = [
            ("To Play the game press Play", (100,120)),
            ("To earn coins harvest some veggies!", (100,200)),
            ("Go to Book of Knowledge to learn", (100, 290)),
            ("Go to Shop to buy/sell veggies", (100,380))

        ]

        
        for line, pos in instructions:
            line_surface = instruction_font.render(line, True, (53,94,59))
            screen.blit(line_surface,pos)

    
        #Handles user input 
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                quit_game=True
                running=False
            elif event.type==pygame.MOUSEBUTTONDOWN:
                if arrow_rect.collidepoint(event.pos):
                    if sfx: sfx.play("CLICK")
                    running= False    
        

        pygame.display.update()

    return quit_game # Tells main_page whether to quit or return