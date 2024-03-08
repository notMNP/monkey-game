""" Name: Arjan, Shyam, Milan
Date: May 27, 2022
Description: create a custom game using pygame - MonkeyMan: 2D retro monkey game. Single leveled platoformer game, where you can throw bananas and jump.
"""

import pygame, sprites, csv, random

pygame.init()


def main():

    welcomeMenu = True

    # establish display size
    screenWidth = 800
    screenHeight = 500

    screen = pygame.display.set_mode((screenWidth, screenHeight))
    pygame.display.set_caption("MonkeyMan IV")

    # shuffle background music
    randomMusic = random.randint(1, 3)
    pygame.mixer.music.load(f"Sound/background/{randomMusic}.mp3")
    if randomMusic == 2:
        pygame.mixer.music.set_volume(0.1)
    else:
        pygame.mixer.music.set_volume(0.45)
    pygame.mixer.music.play(-1)

    # set frame rate
    clock = pygame.time.Clock()
    frameRate = 60

    # define game variables
    gravity = 0.9
    walkSpeed = 3
    runSpeed = 8
    jumpHeight = 16
    maxFallSpeed = 13
    health = 100
    scrollThreshold = 250
    rows = 16
    columns = 150
    tileSize = screenHeight // rows
    tileTypes = 21
    screenScroll = 0
    bgScroll = 0

    # define action variables
    movingLeft = False
    movingRight = False
    sprint = False
    throw = False
    bananaThrown = False

    # load background
    jungleIMG = pygame.image.load("background.png").convert_alpha()
    instructionTitle = pygame.image.load("welcome.png").convert_alpha()

    # load tiles + store in list
    tileList = []
    for x in range(tileTypes):
        img = pygame.image.load(f"Tile/{x}.png")
        img = pygame.transform.scale(img, (tileSize, tileSize))
        tileList.append(img)

    # load images
    bananaImage = pygame.image.load("Banana/one.png").convert_alpha()
    backpackImage = pygame.image.load("Backpack/backpack.png").convert_alpha()
    coinImage = pygame.image.load("Coin/coin.png").convert_alpha()
    bunchImage = pygame.image.load("Banana/bunch.png").convert_alpha()
    bananaImage = pygame.transform.scale(bananaImage, (bananaImage.get_width() * 0.2, bananaImage.get_height() * 0.2))
    backpackImage = pygame.transform.scale(backpackImage,
                                           (backpackImage.get_width() * 0.2, backpackImage.get_height() * 0.2))
    coinImage = pygame.transform.scale(coinImage, (coinImage.get_width() * 0.02, coinImage.get_height() * 0.02))
    bunchImage = pygame.transform.scale(bunchImage, (bunchImage.get_width() * 0.2, bunchImage.get_height() * 0.2))
    pickups = {"backpack": backpackImage, "bunch": bunchImage, "coin": coinImage}

    # define colours
    bgColour = (0, 0, 0)

    def background():
        screen.fill(bgColour)
        width = jungleIMG.get_width()
        for x in range(5):
            screen.blit(jungleIMG, ((x * width) - bgScroll, 0))

    # create sprite groups
    bananaGroup = pygame.sprite.Group()
    consumableGroup = pygame.sprite.Group()
    enemyGroup = pygame.sprite.Group()
    decorationGroup = pygame.sprite.Group()
    waterGroup = pygame.sprite.Group()
    exitGroup = pygame.sprite.Group()

    # create tile list
    worldData = []
    for row in range(rows):
        r = [-1] * columns
        worldData.append(r)
    # load in level data and create world
    with open(f"level0_data.csv", newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for x, row in enumerate(reader):
            for y, tile in enumerate(row):
                worldData[x][y] = int(tile)

    world = sprites.World(screenWidth, scrollThreshold, screenScroll)
    player = world.processData(worldData, tileSize, tileList, enemyGroup, pickups, consumableGroup, decorationGroup,
                               waterGroup, exitGroup)

    # add labels
    healthLabel = sprites.Label("Health: " + str(player.health), (98, 30), 34, (255, 255, 255))
    scoreLabel = sprites.Label("Coins: " + str(player.score), (screenWidth // 2, 30), 34, (255, 255, 255))
    bananaLabel = sprites.Label("Bananas: " + str(player.bananas), (screenWidth - 100, 30), 34, (255, 255, 255))
    labelGroup = pygame.sprite.Group(healthLabel, scoreLabel, bananaLabel)

    doubleClock = pygame.time.Clock()
    doubleClickTime = 250
    play = True
    while play:
        clock.tick(frameRate)
        background()

        # draw map
        world.draw(screen, player)
        player.changeAnimation(sprint, throw)
        player.update(screen, bananaGroup, enemyGroup)

        # update groups
        bananaGroup.update(sprint, gravity, screenWidth, player)
        bananaGroup.draw(screen)
        consumableGroup.update(player)
        consumableGroup.draw(screen)
        decorationGroup.update(player)
        decorationGroup.draw(screen)
        waterGroup.update(player)
        waterGroup.draw(screen)
        exitGroup.update(player, screen)
        exitGroup.draw(screen)

        healthLabel.set_text("Health: " + str(player.health))
        scoreLabel.set_text("Coins: " + str(player.score))
        bananaLabel.set_text("Bananas: " + str(player.bananas))
        labelGroup.update()
        labelGroup.draw(screen)

        for enemy in enemyGroup:
            # create ai crocodiles
            enemy.crocodile(player, tileSize)
            if enemy.bite:
                # establish damage delay
                enemy.thinking = True
                enemy.thinkCount = 50
                enemy.changeAction(4)  # biting animation
            enemy.changeAnimation(False, False)
            enemy.update(screen, bananaGroup, enemyGroup)
            enemy.bite = False

        if player.alive:
            # throw banana
            if throw and not bananaThrown and player.bananas > 0:
                projectile = sprites.Banana(player.rect.centerx, player.rect.centery - 0.6 * player.rect.size[1],
                                            player.direction, bananaImage, world.obstacleList)
                bananaGroup.add(projectile)
                # reduce banana and log throw
                player.bananas -= 1
                bananaThrown = True
            if player.win and not player.winSoundRepeat:
                player.winSoundRepeat = True
                winnerSound = pygame.mixer.Sound("Sound/winnerSound.mp3")
                winnerSound.play()
                bonusLabel = sprites.Label(str(player.score) + "/6 Coins Collected", (400, 130), 40, (251, 255, 81))
                winLabel = sprites.Label("YOU WIN!", (400, 230), 150, (251, 255, 81))
                repeatLabel = sprites.Label("Press Tab for Menu", (400, 320), 40, (251, 255, 81))
                labelGroup.add(bonusLabel, winLabel, repeatLabel)
            # update movement actions
            if player.inAir:
                # 3: jump
                player.changeAction(3)
            elif (movingLeft or movingRight) and sprint:
                # 2: run
                player.changeAction(2)
            elif movingLeft or movingRight:
                # 1: walk
                player.changeAction(1)
            else:
                if throw:
                    # 4: throw
                    player.changeAction(4)
                else:
                    # 0:  idle
                    player.changeAction(0)

        else:
            if not player.win and not player.alreadyDead:
                # 5: dead
                player.changeAction(5)
                player.selfHurting = True
                player.alreadyDead = True
                # display dead label
                deadLabel = sprites.Label("DEAD", (400, 230), 150, (251, 255, 81))
                repeatLabel = sprites.Label("Press Tab for Menu", (400, 320), 40, (251, 255, 81))
                labelGroup.add(deadLabel, repeatLabel)

        screenScroll = player.movement(movingLeft, movingRight, sprint, runSpeed, walkSpeed, jumpHeight, gravity,
                                       maxFallSpeed)
        # scroll the wallpaper
        bgScroll -= screenScroll

        for event in pygame.event.get():
            # terminate program
            if event.type == pygame.QUIT:
                play = False
            # keyboard press
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    play = False
                if event.key == pygame.K_LEFT and player.alive and not player.win:
                    movingLeft = True
                    # if arrows are pressed twice in a row
                    if doubleClock.tick() < doubleClickTime:
                        sprint = True
                    else:
                        sprint = False
                if event.key == pygame.K_RIGHT and player.alive and not player.win:
                    movingRight = True
                    if doubleClock.tick() < doubleClickTime:
                        sprint = True
                    else:
                        sprint = False
                if event.key == pygame.K_TAB and welcomeMenu:
                    # get out of menu and start game
                    welcomeMenu = False
                elif event.key == pygame.K_SPACE and player.alive and not welcomeMenu and not player.win:
                    player.jumping = True
                if event.key == pygame.K_TAB and (not player.alive or player.win):
                    # restart game
                    main()
                if event.key == pygame.K_q and player.alive and not player.win:
                    throw = True
                    randomThrow = random.randint(1,2)
                    # two different throw sounds
                    if randomThrow == 1:
                        throwSound = pygame.mixer.Sound("Sound/throwSound.mp3")
                    elif randomThrow == 2:
                        throwSound = pygame.mixer.Sound("Sound/throwSound2.mp3")
                    throwSound.play()
            # keyboard release
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    movingLeft = False
                if event.key == pygame.K_RIGHT:
                    movingRight = False
                if event.key == pygame.K_q:
                    throw = False
                    bananaThrown = False

        if welcomeMenu:
            # display menu instructions over game, prevent movement
            screen.blit(instructionTitle, (0, 0))
            movingLeft = False
            movingRight = False

        pygame.display.update()

    pygame.quit()


main()
