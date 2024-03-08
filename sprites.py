""" Name: Arjan, Shyam, Milan
Date: May 27, 2022
Description: create a custom game using pygame - MonkeyMan: 2D retro monkey game. Single leveled platoformer game, where you can throw bananas and jump.
"""

import pygame, os, random

pygame.init()


class Animal(pygame.sprite.Sprite):
    """ establish movement of animal(monkey or croc) as well as changes animations"""
    def __init__(self, species, position, size, health, bananas, obstacleList,
                 screenWidth, scrollThreshold):
        pygame.sprite.Sprite.__init__(self)
        self.screenWidth = screenWidth
        self.scrollThreshold = scrollThreshold
        self.alive = True
        self.alreadyDead = False
        self.win = False
        self.score = 0
        self.winSoundRepeat = False
        self.health = health
        self.bananas = bananas
        self.species = species
        self.size = size
        self.direction = 1
        self.jumping = False
        self.updownVelocity = 0
        self.inAir = True
        self.flipImage = False
        self.animationList = []
        self.frameIndex = 0
        self.action = 0
        self.updateTime = pygame.time.get_ticks()
        self.hurting = False
        self.hurtingTime = 0
        self.obstacleList = obstacleList
        self.screenScroll = 0
        # croc specific variable
        self.moveCount = 0
        self.thinking = False
        self.thinkCount = 0
        self.bite = False

        # load all player animation images
        animationTypes = [
            "idle", "slowMove", "fastMove", "jump", "throw", "dead"
        ]
        for movementType in animationTypes:
            try:
                # count the number of files in a given folder
                numFiles = len(
                    os.listdir(f"Animations/{self.species}/{movementType}"))
                tempList = []
                for animations in range(numFiles - 1):
                    monkey = pygame.image.load(
                        f"Animations/{self.species}/{movementType}/{animations + 1}.png"
                    ).convert_alpha()
                    monkey = pygame.transform.scale(
                        monkey, (monkey.get_width() * size,
                                 monkey.get_height() * size))
                    tempList.append(monkey)
                self.animationList.append(tempList)
            except FileNotFoundError:
                pass
        self.animal = self.animationList[self.action][self.frameIndex]
        self.rect = self.animal.get_rect()
        self.rect.center = position
        self.width = self.animal.get_width()
        self.height = self.animal.get_height()

    def movement(self, movingLeft, movingRight, sprint, runSpeed, walkSpeed,
                 jumpHeight, gravity, maxFallSpeed):
        self.screenScroll = 0
        dx = 0
        dy = 0
        # check if sprint is active
        if sprint:
            speed = runSpeed
        else:
            speed = walkSpeed
        # assign movement variables from user input
        if movingLeft:
            dx = -speed
            self.flipImage = True
            self.direction = -1
        if movingRight:
            dx = speed
            self.flipImage = False
            self.direction = 1
        if self.jumping and not self.inAir:
            self.updownVelocity = -jumpHeight
            self.jumping = False
            self.inAir = True

        # gravity effect
        self.updownVelocity += gravity
        if self.updownVelocity > maxFallSpeed:
            self.updownVelocity = maxFallSpeed
        dy += self.updownVelocity
        # check for collision
        for tile in self.obstacleList:
            # check x direction collision
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width,
                                   self.height):
                dx = 0
            # check y direction collision
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width,
                                   self.height):
                # check if below ground
                if self.updownVelocity < 0:
                    self.updownVelocity = 0
                    dy = tile[1].bottom - self.rect.top
                # check if above ground
                elif self.updownVelocity >= 0:
                    self.updownVelocity = 0
                    self.inAir = False
                    dy = tile[1].top - self.rect.bottom

        # update rect position
        self.rect.x += dx
        self.rect.y += dy

        # update scroll based on player position
        if self.species == "monkey":
            if self.rect.right > self.screenWidth - self.scrollThreshold or self.rect.left < self.scrollThreshold:
                self.rect.x -= dx
                self.screenScroll = -dx

        return self.screenScroll

    def changeAnimation(self, sprint, throw):
        # update animation
        if sprint or throw or self.bite:
            animationCooldown = 50
        else:
            animationCooldown = 100
        # update image depending on frame
        self.animal = self.animationList[self.action][self.frameIndex]
        # check if sufficient time has passed since last update
        if pygame.time.get_ticks() - self.updateTime > animationCooldown:
            self.updateTime = pygame.time.get_ticks()
            # does not loop idle or jumping animations
            if self.frameIndex != (len(self.animationList[self.action]) -
                                   1) or self.action == 1 or self.action == 2:
                self.frameIndex += 1
        # if animation list has run out, reset list
        if self.frameIndex >= len(self.animationList[self.action]):
            self.frameIndex = 0

    def changeAction(self, newAction):
        # check if new action is different from previous
        if newAction != self.action:
            self.action = newAction
            # update the animation settings
            self.frameIndex = 0
            self.updateTime = pygame.time.get_ticks()

    def crocodile(self, player, tileSize):
        sprint = False
        walkSpeed = 2
        runSpeed = walkSpeed
        jumpHeight = 15
        gravity = 0.9
        maxFallSpeed = 13
        if self.alive and player.alive:
            if not self.thinking and random.randint(1, 300) == 50:
                self.thinking = True
                self.changeAction(0)  # idle
                self.thinkCount = 50
            if not self.thinking:
                if self.direction == 1:
                    crocMovingRight = True
                else:
                    crocMovingRight = False
                crocMovingLeft = not crocMovingRight
                self.movement(crocMovingLeft, crocMovingRight, sprint,
                              runSpeed, walkSpeed, jumpHeight, gravity,
                              maxFallSpeed)
                self.changeAction(1)  # slowMove
                self.moveCount += 1
                if self.moveCount > tileSize:
                    self.direction *= -1
                    self.moveCount *= -1
            else:
                self.thinkCount -= 1
                if self.thinkCount == 0:
                    self.thinking = False

        # scroll
        self.rect.x += player.screenScroll

    def update(self, screen, bananaGroup, enemyGroup):
        if self.species == "croc":
            for banana in bananaGroup:
                if pygame.sprite.collide_rect(self, banana) and banana.inAir:
                    crocSound = pygame.mixer.Sound("Sound/crocSound.mp3")
                    crocSound.set_volume(0.5)
                    crocSound.play()
                    self.kill()
                    banana.kill()
        else:
            for enemy in enemyGroup:
                if pygame.sprite.collide_rect(self, enemy) and not self.hurting and self.alive:
                    enemy.bite = True
                    self.hurting = True
                    self.health -= 25
                    self.hurtingTime = 800
                    soundNum = random.randint(1, 3)
                    if soundNum == 1:
                        monkeySound = pygame.mixer.Sound("Sound/monkeySound1.mp3")
                    elif soundNum == 2:
                        monkeySound = pygame.mixer.Sound("Sound/monkeySound2.mp3")
                        monkeySound.set_volume(0.5)
                    elif soundNum == 3:
                        monkeySound = pygame.mixer.Sound("Sound/monkeySound3.mp3")
                        monkeySound.set_volume(0.5)
                    monkeySound.play()
                    if self.health <= 0:
                        self.health = 0
                        self.alive = False

                else:
                    self.hurtingTime -= 1
                    if self.hurtingTime == 0:
                        self.hurting = False

        screen.blit(pygame.transform.flip(self.animal, self.flipImage, False),
                    self.rect)


class Banana(pygame.sprite.Sprite):
    """establish gravity and throwing physics for banana"""
    def __init__(self, x, y, direction, bananaImage, obstacleList):
        pygame.sprite.Sprite.__init__(self)
        self.timer = 100
        self.velocity = -9
        self.image = bananaImage
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.direction = direction
        self.inAir = True
        self.obstacleList = obstacleList
        self.speed = 10

    def update(self, sprint, gravity, screenWidth, player):
        self.velocity += gravity
        dx = self.direction * self.speed
        dy = self.velocity
        for tile in self.obstacleList:
            # check collision with walls
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width,
                                   self.height):
                self.direction *= -1
                dx = self.direction * self.speed
            # check y direction collision
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width,
                                   self.height):
                self.speed = 0
                # check if below ground
                if self.velocity < 0:
                    self.velocity = 0
                    dy = tile[1].bottom - self.rect.top
                # check if above ground
                elif self.velocity >= 0:
                    self.velocity = 0
                    self.inAir = False
                    dy = tile[1].top - self.rect.bottom

        # update banana position
        self.rect.x += dx + player.screenScroll
        self.rect.y += dy
        if pygame.sprite.collide_rect(self, player):
            player.bananas += 1
            self.kill()


class Consumable(pygame.sprite.Sprite):
    """establish position, image and function of pickups"""
    def __init__(self, list, itemType, x, y, tileSize):
        pygame.sprite.Sprite.__init__(self)
        self.itemType = itemType
        self.image = list[self.itemType]
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + tileSize // 2,
                            y + (tileSize - self.image.get_height()) - 6)

    def update(self, player):
        self.rect.x += player.screenScroll
        # check if player has picked up box
        if pygame.sprite.collide_rect(self, player):
            if self.itemType == "backpack":
                for i in range(25):
                    if player.health < 100:
                        player.health += 1
            elif self.itemType == "bunch":
                player.bananas += 3
                bananaSound = pygame.mixer.Sound("Sound/eatingSound.mp3")
                bananaSound.play()
            elif self.itemType == "coin":
                coinSound = pygame.mixer.Sound("Sound/coinSound.mp3")
                coinSound.play()
                player.score += 1
            self.kill()


class Decoration(pygame.sprite.Sprite):
    """define objects that are not collision driven (in background)"""
    def __init__(self, img, x, y, tileSize):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + tileSize // 2,
                            y + (tileSize - self.image.get_height()))

    def update(self, player):
        self.rect.x += player.screenScroll


class Water(pygame.sprite.Sprite):
    """establish water with collision detection that kills user"""
    def __init__(self, img, x, y, tileSize):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + tileSize // 2,
                            y + (tileSize - self.image.get_height()))

    def update(self, player):
        self.rect.x += player.screenScroll
        if pygame.sprite.collide_rect(self, player) and player.alive:
            waterSound = pygame.mixer.Sound("Sound/waterSound.mp3")
            waterSound.play()
            player.health = 0
            player.alive = False


class Exit(pygame.sprite.Sprite):
    """establish exit block that wins game when collided with"""
    def __init__(self, img, x, y, tileSize):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + tileSize // 2,
                            y + (tileSize - self.image.get_height()))

    def update(self, player, screen):
        self.rect.x += player.screenScroll
        if pygame.sprite.collide_rect(self, player):
            player.win = True


class Label(pygame.sprite.Sprite):
    """establishes larger text on screen"""
    def __init__(self, message, x_y_center, size, colour):
        pygame.sprite.Sprite.__init__(self)
        self.__font = pygame.font.Font("River Adventurer.ttf", size)
        self.__text = message
        self.__center = x_y_center
        self.__colour = colour

    def set_text(self, message):
        self.__text = message

    def update(self):
        self.image = self.__font.render(self.__text, 1, self.__colour)
        self.rect = self.image.get_rect()
        self.rect.center = self.__center


class World():
    """establish the world tile system that allows for player to advance in game"""
    def __init__(self, screenWidth, scrollThreshold, screenScroll):
        self.obstacleList = []
        self.screenWidth = screenWidth
        self.scrollThreshold = scrollThreshold
        self.screenScroll = screenScroll

    def processData(self, data, tileSize, tileList, enemyGroup, pickups,
                    consumableGroup, decorationGroup, waterGroup, exitGroup):
        # iterate through each value in data file
        for y, row in enumerate(data):
            for x, tile in enumerate(row):
                if tile >= 0:
                    img = tileList[tile]
                    imgRect = img.get_rect()
                    imgRect.x = x * tileSize
                    imgRect.y = y * tileSize
                    tileData = (img, imgRect)
                    if tile == 0 or tile == 4 or tile == 5 or tile == 16:
                        self.obstacleList.append(tileData)
                    elif tile == 18 or tile == 19:
                        water = Water(img, x * tileSize, y * tileSize,
                                      tileSize)
                        waterGroup.add(water)
                    elif tile == 12 or tile == 3:
                        decoration = Decoration(img, x * tileSize,
                                                y * tileSize, tileSize)
                        decorationGroup.add(decoration)
                    elif tile == 7:  # create player
                        player = Animal("monkey", (x * tileSize, y * tileSize),
                                        0.45, 100, 1, self.obstacleList,
                                        self.screenWidth, self.scrollThreshold)
                    elif tile == 15:  # create enemy
                        enemy = Animal("croc", (x * tileSize, y * tileSize),
                                       0.35, 100, 0, self.obstacleList,
                                       self.screenWidth, self.scrollThreshold)
                        enemyGroup.add(enemy)
                    elif tile == 2:  # create banana bunch
                        groceries = Consumable(pickups, "bunch", x * tileSize,
                                               y * tileSize, tileSize)
                        consumableGroup.add(groceries)
                    elif tile == 10:  # create backpack
                        luggage = Consumable(pickups, "backpack", x * tileSize,
                                             y * tileSize, tileSize)
                        consumableGroup.add(luggage)
                    elif tile == 14:  # coin
                        rupee = Consumable(pickups, "coin", x * tileSize,
                                             y * tileSize, tileSize)
                        consumableGroup.add(rupee)
                    elif tile == 11:  # exit
                        exit = Exit(img, x * tileSize, y * tileSize, tileSize)
                        exitGroup.add(exit)
        return player

    def draw(self, screen, player):
        for tile in self.obstacleList:
            tile[1][0] += player.screenScroll
            screen.blit(tile[0], tile[1])
