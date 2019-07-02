# enemy.py
import pygame
import math
from random import *

# note: pygame.transform.flip() is non-destructive
# -------------------------------------------------
# This function is used to check whether subject collides with any object in the list:
# if yes, invoke hitted() of the collided object.
def cldList( subject, objList ):
    for each in objList:
        if ( pygame.sprite.collide_mask( subject, each ) ):
            each.hitted( subject.damage, subject.push )
            return True   # 返回True表示发生碰撞，否则函数最后返回默认值None

# ----------------------------------------------------
def rot_center(image, angle):
    """rotate an image while keeping its center and size"""
    orig_rect = image.get_rect()
    rot_image = pygame.transform.rotate(image, angle)
    rot_rect = orig_rect.copy()
    rot_rect.center = rot_image.get_rect().center
    rot_image = rot_image.subsurface(rot_rect).copy()
    return rot_image

# ----------------------------------------------------
# 辅助函数：sprite是要处理的sprite对象，参数x和y都应是[0，1]的数，分别是横坐标和纵坐标相对于整个rect的比例
def getPos(sprite, x, y):
    posX = round( sprite.rect.left + sprite.rect.width*x )
    posY = round( sprite.rect.top + sprite.rect.height*y )
    return [posX, posY]

# ----------------------------------------------------
# 辅助函数：为调用者生成一个画布对象。接受参数为画布尺寸和透明色信息（RGB无A），返回画布的surface及其rect。
def createCanvas(size, colorKey):
    canvas = pygame.Surface( size ).convert()
    canvas.set_colorkey( colorKey )  # set black as transparent color, generally make the canvas transparent
    cRect = canvas.get_rect()
    cRect.left = 0
    cRect.top = 0
    return (canvas, cRect)

# ----------------------------------------------------
# 辅助函数：为调用者生成一个含左右图片列表的字典并返回。接受参数为左向的图片列表。
# 注意，必须要把所有图片按顺序装在列表中传入，即使只有一个图片也须为列表形式。
# 但是如果实际只有一个图片传入，在返回时，字典中的元素将会是单个对象，而非列表。
def createImgList(imgList):
    if len(imgList)>1:       # 多张图片。
        imgDic = { "left":[], "right":[] }
        imgDic["left"] = imgList
        for each in imgDic["left"]:
            imgDic["right"].append( pygame.transform.flip(each, True, False) )
    else:                     # 一张图片。
        imgDic = { "left":None, "right":None }
        imgDic["left"] = imgList[0]
        imgDic["right"]= pygame.transform.flip(imgList[0], True, False)
    return imgDic

# ========================================================================
#   DIY一个enemy类，此类将提供所有enemy应有的方法和属性，子类可在此基础上扩展
# 初始化需要的参数有：游戏内类别名，血的颜色，体力值，击退位移，价值得分，所在层数。
# ========================================================================
class Monster(pygame.sprite.Sprite):
    
    # 所有monster类都应有的几个属性
    category = ""
    bldColor = None
    health = 0
    full = 0
    push = 0
    hitBack = 0

    score = 0
    exp = 0
    onlayer = 0
    direction = "left"
    gravity = 0

    # 以下是monster类共享的一个真正的静态变量。在冒险模式初始化时，由adventure model对象来对这个值进行初始化。（1表示原生命）
    healthBonus = 1

    def __init__(self, cate, bldColor, health, push, weight, onlayer, score, exp):
        pygame.sprite.Sprite.__init__(self) # 首先它应该是一个pygame.sprite
        self.category = cate
        self.bldColor = bldColor
        self.health = round( health * self.healthBonus )
        self.full = self.health

        self.pushList = (-push, push)
        self.push = push
        self.weight = weight
        self.hitBack = 0
        
        self.score = score
        self.exp = exp
        self.onlayer = int(onlayer)
        self.direction = "left"             # 默认的初始朝向为left。若需要自定义，可以在monster子类的构造函数中再修改本值。
        self.gravity = 0

    def alterSpeed(self, speed):
        self.speed = speed
        if speed > 0:
            self.direction = "right"
            self.push = self.pushList[1]
        elif speed < 0:
            self.direction = "left"
            self.push = self.pushList[0]

    def checkHitBack(self):
        if abs(self.hitBack)>0:
            self.rect.left += self.hitBack
            if self.hitBack>0:
                self.hitBack -= 1
            else:
                self.hitBack += 1
    
    def fall(self, keyLine, groupList):
        if self.gravity<5:
            self.gravity += 1
        self.rect.bottom += self.gravity
        while ( pygame.sprite.spritecollide(self, self.wallList, False, pygame.sprite.collide_mask) ):  # 如果和参数中的物体相撞，则尝试纵坐标-1
            self.rect.bottom -= 1
            self.gravity = 0
        if self.rect.top >= keyLine:
            self.onlayer -= 2
            if self.onlayer<-1:
                self.erase()
            else:
                self.initLayer( groupList[str(self.onlayer)] )
    
    # 此函数用于确定新一行中的位置及scope
    def initLayer(self, line):
        self.wallList = []          # 存储本行的所有砖块; # 每次初始化一个新实例时，清空此类的wallList（否则会在上一个实例的基础上再加！）
        posList = []                # 辅助列表，用于暂时存储本行砖块的位置（左边线）
        wall = None         # 此刻monster正下方的wall
        for aWall in line:  # 由于spriteGroup不好进行索引/随机选择操作，因此将其中的sprite逐个存入列表中存储
            if aWall.category=="lineWall" or aWall.category=="specialWall" or aWall.category=="baseWall":
                self.wallList.append(aWall)
                posList.append(aWall.rect.left)
                if aWall.rect.left<getPos(self,0.5,0)[0]<aWall.rect.right:  # 可以落到下一行上，有砖接着
                    wall = aWall
        if not wall:        # 没wall接着，直接返回，继续下落吧！
            return
        # 到了这一步，已经得到了wall，好，可以开始计算scope了。
        leftMax = wall.rect.left
        rightMax = wall.rect.right  # note：此处砖块的右坐标即下一砖块的左坐标
        while True:
            if leftMax in posList:  # warmachine比较宽，可以占两格行进
                leftMax -= wall.rect.width
            else:
                leftMax += wall.rect.width  # 将多减的加回来
                break
        while True:
            if rightMax in posList:
                rightMax += wall.rect.width
            else:
                break
        self.scope = (leftMax, rightMax)
        return wall
    
    def paint(self, surface):               # 所有monster都应有paint()函数，供外界调用，将自身画在传来的surface上。
        surface.blit( self.image, self.rect )

    def lift(self, dist):                   # 所有monster都应可以响应model主函数的调用而竖直方向上移动。
        self.rect.bottom += dist
    
    def level(self, dist):
        self.rect.left += dist

    def hitted(self, damage, pushed):
        self.health -= damage
        if self.health <= 0:                # dead。
            self.health = 0
            self.erase()
            return True
        if pushed>0:   # 向右击退
            self.hitBack = max( pushed-self.weight, 0 )
        elif pushed<0: # 向左击退
            self.hitBack = min( pushed+self.weight, 0 )

    def erase(self):                        # 所有monster都应有erase()函数。
        self.kill()
        del self
        return

# ============================= stg0 ==================================
# -----------------------------------
class Strawman(Monster):  

    def __init__(self, wallGroup, blockSize, onlayer):
        # calculate its position
        Monster.__init__(self, "strawman", (250,160,120), 30, 4, 1, onlayer, 2, 0)
        self.wallList = []       # 存储本行的所有brick; # 每次初始化一个新实例时，清空此类的wallList（否则会在上一个实例的基础上再加！）
        posList = []             # 辅助列表，用于暂时存储本行brick的位置（左边线）
        for aWall in wallGroup:  # 由于spriteGroup不好进行索引/随机选择操作，因此将其中的sprite逐个存入列表中存储
            self.wallList.append(aWall)
            posList.append(aWall.rect.left)
        wall = choice(self.wallList)
        leftMax = wall.rect.left
        rightMax = wall.rect.right # note：此处砖块的右坐标即下一砖块的左坐标
        while True:
            if leftMax in posList:
                leftMax -= blockSize
            else:
                leftMax += blockSize  # 将多减的加回来
                break
        while True:
            if rightMax in posList:
                rightMax += blockSize
            else:
                break
        self.scope = (leftMax, rightMax)
        # initialize the sprite
        self.imgLeftList = [ pygame.image.load("image/stg0/strawman0.png").convert_alpha(), pygame.image.load("image/stg0/strawman1.png").convert_alpha(), 
            pygame.image.load("image/stg0/strawman1.png").convert_alpha(), pygame.image.load("image/stg0/strawman1.png").convert_alpha(), 
            pygame.image.load("image/stg0/strawman0.png").convert_alpha(), pygame.image.load("image/stg0/strawman0.png").convert_alpha(),
            pygame.image.load("image/stg0/strawman0.png").convert_alpha() ]
        self.imgRightList = [ pygame.transform.flip(self.imgLeftList[0], True, False), pygame.transform.flip(self.imgLeftList[1], True, False), 
            pygame.transform.flip(self.imgLeftList[2], True, False), pygame.transform.flip(self.imgLeftList[3], True, False),
            pygame.transform.flip(self.imgLeftList[4], True, False), pygame.transform.flip(self.imgLeftList[5], True, False),
            pygame.transform.flip(self.imgLeftList[6], True, False) ]

        self.imgIndx = 0
        self.attIndx = 0
        self.image = self.imgLeftList[0]
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.left = wall.rect.left
        self.rect.bottom = wall.rect.top
        self.damage = 6
        self.coolDown = 0          
        self.speed = choice( [-1, 1] )
        if self.speed<0:
            self.push = -self.push
        self.rise = ( 0, -6, -12, -16, -12, -6, 0 )

    def move(self, delay, sprites):
        self.checkHitBack()
        if not (delay % 2 ):
            self.rect.left += self.speed
            if (getPos(self,0.75,0)[0] >= self.scope[1] and self.speed > 0) or (getPos(self,0.25,0)[0] <= self.scope[0] and self.speed < 0):
                self.alterSpeed( -self.speed )
        if not (delay % 5 ):
            trPos = [ self.rect.left + self.rect.width//2, self.rect.bottom-self.rise[self.imgIndx] ]  # 为保证图片位置正确，临时存储之前的位置信息
            self.imgIndx = (self.imgIndx+1) % len(self.imgLeftList)
            self.image = self.imgLeftList[self.imgIndx] if ( self.speed<0 ) else self.imgRightList[self.imgIndx]
            self.mask = pygame.mask.from_surface(self.image)
            self.rect = self.image.get_rect()
            self.rect.left = trPos[0]-self.rect.width//2
            self.rect.bottom = trPos[1] + self.rise[self.imgIndx]
        if ( self.coolDown==0 ):
            for each in sprites:
                if pygame.sprite.collide_mask(self, each):
                    self.coolDown = 36
        if (self.coolDown > 0):
            self.coolDown -= 1
            if ( self.coolDown == 20 ):
                cldList( self, sprites )

    def level(self, dist):
        self.rect.left += dist
        self.scope = (self.scope[0]+dist, self.scope[1]+dist)

class Pool():

    bg_size = 0    # 屏幕尺寸
    canvas = None
    canvasRect = None
    surfH = 0      # 液面的高度
    bubbles = []
    stream = 1

    def __init__(self, bg_size, initH):  # initH 是游戏开始时ooze已有的初始高度，相对于bg_size[1]而言。
        # initialize the sprite
        self.canvas, self.canvasRect = createCanvas( bg_size, (0,0,0) )
        self.canvas.set_alpha(60)
        # green ooze 部分，整个屏幕的大小，只是在渲染时只渲染surfH以下的部分。
        self.blueCv = pygame.Surface( (bg_size[0], bg_size[1]) )
        self.blueCv.fill( (120,120,180) )

        self.bg_size = bg_size
        self.surfH = bg_size[1]-initH
        self.category = "pool"
        self.bubbles = []

    def flow(self, delay, screen, sprites, spurtCanvas):
        if not (delay % 4):
            # 重画软泥
            if (0 <= self.surfH < self.bg_size[1]):
                self.canvas.fill((0,0,0))
                oozeRect = pygame.Rect( 0, self.surfH, self.bg_size[0], self.bg_size[1] )
                self.canvas.blit(self.blueCv, oozeRect)
                pygame.draw.line( self.canvas, (60,60,100), (0,self.surfH), (self.bg_size[0],self.surfH), randint(3,6) ) # 液面的深色线
            if random()<0.1:
                #生成新气泡（列表形式：[横坐标，纵坐标，半径]）。同时生成两个，左侧右侧各一个，总有一个是顺流，另一个逆流即时删除，这样避免了分支。
                self.bubbles.append( [0, randint(self.surfH,self.bg_size[1]), randint(1,8)] )
                self.bubbles.append( [self.bg_size[0], randint(self.surfH,self.bg_size[1]),  randint(1,8)] )
                if random()<0.02:
                    self.stream = -self.stream  # 改变流动方向
        for each in sprites:
            if each.rect.bottom>self.surfH:
                # Draw visual effect.
                if each.rect.top<self.surfH:
                    posX = getPos(each, random(), 0)[0]
                    spurtCanvas.addSpatters( 5, (2,3,4), (4,5,6), (60,60,100,210), (posX, self.surfH)) # 溅射效果
                else:
                    spurtCanvas.addTrails([3,4,5], [12, 16, 20], (60,60,100,180), getPos(each, 0.5, random()))
        # 处理气泡.
        for each in self.bubbles:
            pygame.draw.circle( self.canvas, (60,60,100), (each[0],each[1]), each[2] )
            each[0] += self.stream
            if each[0]<=0 or each[0]>=self.bg_size[0]:
                self.bubbles.remove(each)
        screen.blit(self.canvas, self.canvasRect)

    def lift(self, dist):
        self.surfH += dist

    def level(self, dist):
        pass

# ============================================================================
# --------------------------------- Stage1 -----------------------------------
# ============================================================================
class InfernoFire(pygame.sprite.Sprite):
    def __init__(self, bg_size):
        pygame.sprite.Sprite.__init__(self)

        self.imgList = [pygame.image.load("image/stg1/infernoFire0.png").convert_alpha(), pygame.image.load("image/stg1/infernoFire1.png").convert_alpha(), pygame.image.load("image/stg1/infernoFire2.png").convert_alpha()]
        self.image = self.imgList[0]
        self.imgIndx = 0
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.width = bg_size[0]
        self.height = bg_size[1]
        self.damage = 0.6
        self.push = 0
        self.speed = 5
        self.category = "infernoFire"
        self.snd = pygame.mixer.Sound("audio/infernoFire.wav")
        # randomize the position
        self.rect.left = randint(100, 640)
        self.rect.top = randint(self.height+100, self.height*2.1)

    def move(self, delay, sprites, canvas):
        if self.rect.bottom > 0:
            self.rect.top -= self.speed
            canvas.addTrails( [4,5,6], [18,21,24], (240,180,0,240), getPos(self, 0.4+random()*0.2, 0.6+random()*0.2) )
        else:
            self.reset()
            return
        if self.rect.top == self.height: # 限制在出现屏幕下方的一瞬间触发音效
            self.snd.play(0)
        cldList( self, sprites )
        if not (delay % 6):              # 若delay整除8，则切换图片
            self.imgIndx = ( self.imgIndx+1 ) % len(self.imgList)
            self.image = self.imgList[self.imgIndx]
            self.mask = pygame.mask.from_surface(self.image)
    
    def reset(self):
        self.snd.play(0)
        self.rect.left = randint(100, 640)
        self.rect.top = randint(self.height+10, self.height*2.1)

    def lift(self, dist):
        self.rect.bottom += dist
    
    def level(self, dist):
        self.rect.left += dist
    
# -----------------------------------
class Gozilla(Monster):

    def __init__(self, wallGroup, blockSize, onlayer):
        # calculate its position
        if int(onlayer)>10 and random()<0.4:
            Monster.__init__(self, "megaGozilla", (255,0,0,240), 44, 6, 2, onlayer, 3, 2)
            self.t = 2
        else:
            Monster.__init__(self, "gozilla", (255,0,0,240), 30, 6, 1, onlayer, 2, 1)
            self.t = 1
        self.wallList = []       # 存储本行的所有砖块; # 每次初始化一个新实例时，清空此类的wallList（否则会在上一个实例的基础上再加！）
        posList = []             # 辅助列表，用于暂时存储本行砖块的位置（左边线）
        for aWall in wallGroup:  # 由于spriteGroup不好进行索引/随机选择操作，因此将其中的sprite逐个存入列表中存储
            self.wallList.append(aWall)
            posList.append(aWall.rect.left)
        wall = choice(self.wallList)
        leftMax = wall.rect.left
        rightMax = wall.rect.right # note：此处砖块的右坐标即下一砖块的左坐标
        while True:
            if leftMax in posList:
                leftMax -= blockSize
            else:
                leftMax += blockSize  # 将多减的加回来
                break
        while True:
            if rightMax in posList:
                rightMax += blockSize
            else:
                break
        self.scope = (leftMax, rightMax)
        # initialize the sprite
        self.imgLeftList = [ pygame.image.load("image/stg1/"+self.category+"0.png").convert_alpha(), pygame.image.load("image/stg1/"+self.category+"1.png").convert_alpha(), \
            pygame.image.load("image/stg1/"+self.category+"0.png").convert_alpha(), pygame.image.load("image/stg1/"+self.category+"2.png").convert_alpha() ]
        self.imgRightList = [ pygame.transform.flip(self.imgLeftList[0], True, False), pygame.transform.flip(self.imgLeftList[1], True, False), \
            pygame.transform.flip(self.imgLeftList[2], True, False), pygame.transform.flip(self.imgLeftList[3], True, False) ]

        self.attLList = [ pygame.image.load("image/stg1/"+self.category+"Att0.png").convert_alpha(), pygame.image.load("image/stg1/"+self.category+"Att1.png").convert_alpha(), \
            pygame.image.load("image/stg1/"+self.category+"Att2.png").convert_alpha(), pygame.image.load("image/stg1/"+self.category+"Att3.png").convert_alpha(), \
            pygame.image.load("image/stg1/"+self.category+"Att4.png").convert_alpha() ]
        self.attRList = [ pygame.transform.flip(self.attLList[0], True, False), pygame.transform.flip(self.attLList[1], True, False), \
            pygame.transform.flip(self.attLList[2], True, False), pygame.transform.flip(self.attLList[3], True, False), \
            pygame.transform.flip(self.attLList[4], True, False) ]

        self.imgIndx = 0
        self.attIndx = 0
        self.image = self.imgLeftList[0]
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.left = wall.rect.left
        self.rect.bottom = wall.rect.top
        self.damage = 6
        self.coolDown = 0
        self.alterSpeed( choice([1,-1]) )

    def move(self, delay, sprites):
        self.checkHitBack()
        if not (delay%self.t):
            self.rect.left += self.speed
            if (getPos(self,0.75,0)[0] >= self.scope[1] and self.speed > 0) or (getPos(self,0.25,0)[0] <= self.scope[0] and self.speed < 0):
                self.alterSpeed(-self.speed)
            if not (delay % (8*self.t) ):
                self.imgIndx = (self.imgIndx+1) % len(self.imgLeftList)
                self.image = self.imgLeftList[self.imgIndx] if ( self.speed<0 ) else self.imgRightList[self.imgIndx]
        if ( self.coolDown==0 ):
            for each in sprites:
                if pygame.sprite.collide_mask(self, each):
                    self.coolDown = 40
        if (self.coolDown > 0):
            self.coolDown -= 1
            self.cratch( sprites )
    
    def cratch(self, sprites):
        if (self.coolDown <= 22):
            return
        if (self.coolDown >= 37):
            self.attIndx = 0
        elif (self.coolDown >= 34):
            self.attIndx = 1
        elif (self.coolDown >= 31):
            self.attIndx = 2
        elif (self.coolDown >= 28):
            self.attIndx = 3
        elif (self.coolDown >= 25):
            self.attIndx = 4
            if ( self.coolDown == 25 ):
                cldList( self, sprites )
        trPos = [ self.rect.left + self.rect.width//2, self.rect.bottom ]
        self.image = self.attLList[self.attIndx] if ( self.speed<0 ) else self.attRList[self.attIndx]
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.left = trPos[0]-self.rect.width//2
        self.rect.bottom = trPos[1]

    def level(self, dist):
        self.rect.left += dist
        self.scope = (self.scope[0]+dist, self.scope[1]+dist)

# -----------------------------------
# 有一个衍生物，是吐出的攻击物，fire类，保存在self.fireList中
class Dragon(Monster):  

    def __init__(self, wallGroup, onlayer, boundaries):
        # calculate its position
        Monster.__init__(self, "dragon", (255,0,0,240), 40, 0, 1, onlayer, 3, 2)
        self.wallList = []         # 存储本行的所有砖块;
        for aWall in wallGroup:    # 由于spriteGroup不好进行索引/随机选择操作，因此将其中的sprite逐个存入列表中存储
            self.wallList.append(aWall)
        wall = choice(self.wallList)
        self.boundaries = boundaries
        # initialize the sprite
        self.imgLeftList = [ pygame.image.load("image/stg1/dragonLeft0.png").convert_alpha(), pygame.image.load("image/stg1/dragonLeft1.png").convert_alpha(), 
            pygame.image.load("image/stg1/dragonLeft2.png").convert_alpha(), pygame.image.load("image/stg1/dragonLeft3.png").convert_alpha(), 
            pygame.image.load("image/stg1/dragonLeft2.png").convert_alpha(), pygame.image.load("image/stg1/dragonLeft1.png").convert_alpha() ]
        self.imgRightList = [ pygame.transform.flip(self.imgLeftList[0], True, False), pygame.transform.flip(self.imgLeftList[1], True, False), 
            pygame.transform.flip(self.imgLeftList[2], True, False), pygame.transform.flip(self.imgLeftList[3], True, False), 
            pygame.transform.flip(self.imgLeftList[4], True, False), pygame.transform.flip(self.imgLeftList[5], True, False) ]
        
        self.imgIndx = 0
        self.image = self.imgLeftList[0]
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.left = wall.rect.left
        if self.rect.right > self.boundaries[1]:
            self.rect.right = self.boundaries[1]
        self.rect.top = wall.rect.bottom
        self.alterSpeed( choice([-1, 1]) )
        self.upDown = 2
        self.fireList = pygame.sprite.Group()

    def move(self, delay):
        self.checkHitBack()
        if not (delay % 20):
            self.rect.top += self.upDown
            self.upDown = - self.upDown
        if not (delay % 6 ):
            self.imgIndx = (self.imgIndx+1) % len(self.imgLeftList)
            self.image = self.imgLeftList[self.imgIndx] if ( self.direction=="left" ) else self.imgRightList[self.imgIndx] 
        self.rect.left += self.speed
        if (self.rect.left<=self.boundaries[0] and self.speed < 0) or (self.rect.right>=self.boundaries[1] and self.speed > 0):
            self.alterSpeed(-self.speed)
        # randomly fire
        if not (delay % 120) and (random() > 0.2):  # 控制喷火频率
            fire = Fire(getPos(self, 0, 1), self.onlayer, -2, 0) if (self.direction=="left") else Fire(getPos(self,0.95,1), self.onlayer, 2, 0)
            self.fireList.add(fire)
            return fire

    def level(self, dist):
        self.rect.left += dist
        self.boundaries = (self.boundaries[0]+dist, self.boundaries[1]+dist)
    
class Fire(pygame.sprite.Sprite):
    def __init__(self, pos, layer, speed, iniG):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("image/stg1/fire.png").convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.left = pos[0]
        self.rect.bottom = pos[1]
        self.mask = pygame.mask.from_surface(self.image)
        self.damage = 6.5
        self.category = "fire"
        self.onlayer = int(layer)
        self.gravity = iniG
        self.speed = speed
        if speed>0:
            self.push = 6
        else:
            self.push = -6

    def move(self, delay, sideWalls, downWalls, keyLine, sprites, canvas, bg_size):
        self.rect.left += self.speed
        self.rect.bottom += self.gravity
        canvas.addTrails( [1, 2, 3], [8, 9, 10], (240,220,0,240), getPos(self, 0.4+random()*0.3, 0.4+random()*0.3) )
        if cldList( self, sprites ):      # 命中英雄
            self.explode(canvas)
            return
        if ( pygame.sprite.spritecollide(self, downWalls, False, pygame.sprite.collide_mask) ) or ( pygame.sprite.spritecollide(self, sideWalls, False, pygame.sprite.collide_mask) ) or self.rect.top>=bg_size[1] or self.rect.right<=0 or self.rect.left>=bg_size[1]:
            self.explode(canvas)
            return
        if not (delay % 6):
            self.image = rot_center(self.image, 40) if self.speed <= 0 else rot_center(self.image, -40)
            if (self.gravity < 5):
                self.gravity += 1
        if ( self.rect.top >= keyLine ):  # 因为只有大于检查，因此只有初始行之下的砖块会与之碰撞
            self.onlayer -= 2
            if self.onlayer<-1:
                self.explode(canvas)

    def explode(self, canvas):
        canvas.addSpatters( 5, [3, 4], [8, 9, 10], (1,1,1,255), getPos(self, 0.5, 0.5) )
        self.kill()
        del self
    
    def lift(self, dist):
        self.rect.bottom += dist

    def level(self, dist):
        self.rect.left += dist

# -----------------------------------
class RedDragon(Monster):

    def __init__(self, x, y, onlayer):
        # initialize the sprite
        Monster.__init__(self, "RedDragon", (255, 0, 0, 240), 200, 0, 3, onlayer, 40, 20)
        # ----- body part (the core of the RedDragon) ------
        self.bodyLeft = pygame.image.load("image/stg1/DragonBody.png").convert_alpha()
        self.bodyRight = pygame.transform.flip(self.bodyLeft, True, False)
        self.imgIndx = 0
        self.image = self.bodyLeft
        self.mask = pygame.mask.from_surface(self.image)
        # calculate its position
        self.rect = self.image.get_rect()
        self.rect.left = x
        self.rect.top = y
        # ------------- head part --------------
        self.headLeft = [ pygame.image.load("image/stg1/DragonHead0.png").convert_alpha(), pygame.image.load("image/stg1/DragonHead1.png").convert_alpha(), 
            pygame.image.load("image/stg1/DragonHead2.png").convert_alpha() ]
        self.headRight = [ pygame.transform.flip(self.headLeft[0], True, False), pygame.transform.flip(self.headLeft[1], True, False), 
            pygame.transform.flip(self.headLeft[2], True, False) ]
        self.headR = { "left":[ (0,0.6), (0,0.61), (0,0.62) ], "right":[ (1,0.6), (1,0.61), (1,0.62) ] }    # 分别为左和右时的位置信息
        self.head = Ajunction( self.headLeft[2], getPos(self, self.headR[self.direction][0][0], self.headR[self.direction][0][1]) )
        self.headIndx = 0
        # ------------- wing part ----------------
        self.wingLeft = [ pygame.image.load("image/stg1/wing0.png").convert_alpha(), pygame.image.load("image/stg1/wing1.png").convert_alpha(), pygame.image.load("image/stg1/wing2.png").convert_alpha(), pygame.image.load("image/stg1/wing3.png").convert_alpha(), \
            pygame.image.load("image/stg1/wing2.png").convert_alpha(), pygame.image.load("image/stg1/wing1.png").convert_alpha(), pygame.image.load("image/stg1/wing0.png").convert_alpha() ]
        self.wingRight = [ pygame.transform.flip(self.wingLeft[0], True, False), pygame.transform.flip(self.wingLeft[1], True, False), pygame.transform.flip(self.wingLeft[2], True, False), pygame.transform.flip(self.wingLeft[3], True, False), \
            pygame.transform.flip(self.wingLeft[4], True, False), pygame.transform.flip(self.wingLeft[5], True, False), pygame.transform.flip(self.wingLeft[6], True, False) ]
        self.wingR = { "left":[ (0.5,-0.3), (0.5,-0.21), (0.5,0.1), (0.5,0.3), (0.5,0.1), (0.5,-0.21), (0.5,-0.3) ], "right":[ (0.5,-0.3), (0.5,-0.21), (0.5,0.1), (0.5,0.3), (0.5,0.1), (0.5,-0.21), (0.5,-0.3) ] }
        self.wing = Ajunction( self.wingLeft[0], getPos(self, self.wingR[self.direction][0][0], self.wingR[self.direction][0][1]) )
        self.wingIndx = 0
        # -------------- tail part ---------------
        self.tailLeft = [ pygame.image.load("image/stg1/tail0.png").convert_alpha(), pygame.image.load("image/stg1/tail1.png").convert_alpha(), pygame.image.load("image/stg1/tail2.png").convert_alpha(), 
            pygame.image.load("image/stg1/tail3.png").convert_alpha(), pygame.image.load("image/stg1/tail2.png").convert_alpha(), pygame.image.load("image/stg1/tail1.png").convert_alpha() ]
        self.tailRight = [ pygame.transform.flip(self.tailLeft[0], True, False), pygame.transform.flip(self.tailLeft[1], True, False), pygame.transform.flip(self.tailLeft[2], True, False), 
            pygame.transform.flip(self.tailLeft[3], True, False), pygame.transform.flip(self.tailLeft[4], True, False), pygame.transform.flip(self.tailLeft[5], True, False) ]
        self.tailR = { "left":[ (0.76,0.84), (0.76,0.84), (0.72,0.84), (0.68,0.84), (0.72,0.84), (0.76,0.84) ], "right":[ (0.24,0.84), (0.24,0.84), (0.28,0.84), (0.32,0.84), (0.28,0.84), (0.24,0.84) ] }
        self.tail = Ajunction( self.tailLeft[0], getPos(self, self.tailR[self.direction][0][0], self.tailR[self.direction][0][1]) )
        self.tailIndx = 0
        # ------------- fire part -----------------
        self.fireList = pygame.sprite.Group()
        self.fireSpd = 6
        # ----------- other attributes -------------------------
        self.cnt = 1600      # count for the loop of shift position
        self.coolDown = 0    # count for attack coolDown
        self.nxt = (0, 0)
        self.growlSnd = pygame.mixer.Sound("audio/redDragonGrowl.wav")
        self.moanSnd = pygame.mixer.Sound("audio/redDragonMoan.wav")
        self.upDown = 3      # 悬停状态身体上下振幅
        self.activated = False

    def move(self, sprites, canvas):
        self.checkHitBack()
        self.cnt -= 1
        if self.cnt<=0:
            self.cnt = 1800
        elif self.cnt>=240:
            if not self.cnt%60:
                self.nxt = ( randint(100,640), randint(80,520) )   # randomize a new position
                self.direction = "left" if ( self.nxt[0] < getPos(self, 0.5, 0.5)[0] ) else "right"
        else:
            self.nxt = ( 540, 80 )
            self.direction = "left"
            if not self.cnt%8:
                self.makeFire( sprites )
        # charging motion
        if not (self.cnt % 3):
            if self.shift( self.nxt[0], self.nxt[1] ):
                # 如果处于悬停状态，则随着扇翅上下摆动，且晃动尾巴。
                if not (self.cnt % 18):
                    self.rect.top += self.upDown
                    self.upDown = - self.upDown
                    self.tailIndx = (self.tailIndx+1)%len(self.tailLeft)
            self.wingIndx = (self.wingIndx+1) % len(self.wingLeft)
            if self.direction == "left":
                self.image = self.bodyLeft
                self.head.updateImg( self.headLeft[self.headIndx] )
                self.wing.updateImg( self.wingLeft[self.wingIndx] )
                self.tail.updateImg( self.tailLeft[self.tailIndx] )
            elif self.direction == "right":
                self.image = self.bodyRight
                self.head.updateImg( self.headRight[self.headIndx] )
                self.wing.updateImg( self.wingRight[self.wingIndx] )
                self.tail.updateImg( self.tailRight[self.tailIndx] )
            self.mask = pygame.mask.from_surface(self.image)
            self.head.updatePos( getPos(self, self.headR[self.direction][self.headIndx][0], self.headR[self.direction][self.headIndx][1]) )
            self.wing.updatePos( getPos(self, self.wingR[self.direction][self.wingIndx][0], self.wingR[self.direction][self.wingIndx][1]) )
            self.tail.updatePos( getPos(self, self.tailR[self.direction][self.tailIndx][0], self.tailR[self.direction][self.tailIndx][1]) )
        # deal fire attack:
        self.headIndx = 0
        if not (self.cnt % 12) and self.coolDown<=0 and random()<0.26:    # 喷火
            self.growlSnd.play(0)
            self.coolDown = 90
            self.makeFire( sprites )
        elif self.coolDown > 0:
            self.coolDown -= 1
            if self.coolDown >= 84:
                self.headIndx = 1
            elif self.coolDown >= 78:
                self.headIndx = 2
            elif self.coolDown >= 72:
                self.headIndx = 1
        for each in self.fireList:
            vib = each.move( sprites, canvas )
            if vib=="vib":
                return "vib"
    
    def makeFire(self, sprites):
        aim = getPos( choice( sprites ), 0.5, 0.5 )
        deltaX = aim[0] - getPos( self.head, 0.5, 0.5 )[0]
        deltaY = aim[1] - getPos( self.head, 0.5, 0.5 )[1]
        time = round( ( deltaX**2 + deltaY**2 )**0.5 / self.fireSpd )
        spdX = round( deltaX/time )
        spdY = round( deltaY/time )
        degree = math.degrees( math.atan2(spdY, spdX) )      #两点线段的弧度值，并弧度转角度
        fire = RedDragonFire( getPos( self.head, 0.2, 0.6), (spdX, spdY), time, degree ) if self.direction=="left" else RedDragonFire( getPos( self.head, 0.8, 0.6), (spdX, spdY), time, degree )
        self.fireList.add( fire )

    # 鉴于本对象的构造非常复杂，因此提供一个专门的绘制接口
    # 给此函数传递一个surface参数，即可在该surface上绘制（blit）完整的本对象
    def paint(self, screen):
        screen.blit( self.tail.image, self.tail.rect )
        screen.blit( self.image, self.rect )
        screen.blit( self.head.image, self.head.rect )
        screen.blit( self.wing.image, self.wing.rect )
        for each in self.fireList:
            screen.blit( each.image, each.rect )
    
    def erase(self):
        self.moanSnd.play(0)
        self.head.kill()
        del self.head
        self.wing.kill()
        del self.wing
        self.kill()
        del self
        return True   # dead

    def lift(self, dist):
        self.rect.bottom += dist
        for each in self.fireList:
            each.rect.bottom += dist

    def level(self, dist):
        self.rect.left += dist
        for each in self.fireList:
            each.rect.left += dist

    def shift(self, final_x, final_y):
        x = self.rect.left + self.rect.width/2
        y = self.rect.top + self.rect.height/2
        if (x == final_x) or (y == final_y):
            return True   # 表示已到目标
        maxSpan = 8
        spd = 4
        dist = 0
        if (x < final_x):
            dist = math.ceil( (final_x - x)/spd )
            if dist > maxSpan:
                dist = maxSpan
            self.rect.left += dist
        elif (x > final_x):
            dist = math.ceil( (x - final_x)/spd )
            if dist > maxSpan:
                dist = maxSpan
            self.rect.left -= dist
        if (y < final_y):
            dist = math.ceil( (final_y - y)/spd )
            if dist > maxSpan:
                dist = maxSpan
            self.rect.top += dist
        elif (y > final_y):
            dist = math.ceil( (y - final_y)/spd )
            if dist > maxSpan:
                dist = maxSpan
            self.rect.top -= dist
        return False    # 表示未到目标

# ------------------------------------------------
# 此类应附属于某个monster主体而存在。由于是附属物，此类只提供供主物移动位置、替换image的函数接口，需要主物来执行相应的删除工作。
class Ajunction(pygame.sprite.Sprite):
    def __init__(self, img, pos):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.left = pos[0] - self.rect.width//2
        self.rect.bottom = pos[1] - self.rect.height//2
        self.mask = pygame.mask.from_surface(self.image)

    def updatePos(self, pos):
        self.rect.left = pos[0] - self.rect.width//2
        self.rect.top = pos[1] - self.rect.height//2
    
    def updateImg(self, img):
        trPos = [ self.rect.left + self.rect.width//2, self.rect.top + self.rect.height//2 ]
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.left = trPos[0]-self.rect.width//2
        self.rect.bottom = trPos[1]
        self.mask = pygame.mask.from_surface(self.image)

class RedDragonFire(pygame.sprite.Sprite):
    def __init__(self, pos, spd, time, degree):   # 参数pos为本对象初始的位置，aim为目标坐标
        pygame.sprite.Sprite.__init__(self)
        self.imageList = [ pygame.transform.rotate( pygame.image.load("image/stg1/RedFire0.png").convert_alpha(), -degree ), 
            pygame.transform.rotate( pygame.image.load("image/stg1/RedFire1.png").convert_alpha(), -degree ) ]
        self.explodeList = [ pygame.image.load("image/stg1/Explode0.png").convert_alpha(), pygame.image.load("image/stg1/Explode1.png").convert_alpha(),
            pygame.image.load("image/stg1/Explode2.png").convert_alpha(), pygame.image.load("image/stg1/Explode3.png").convert_alpha() ]
        self.imgIndx = 0
        self.image = self.imageList[0]
        self.rect = self.image.get_rect()
        self.rect.left = pos[0]-self.rect.width//2
        self.rect.top = pos[1]-self.rect.height//2
        self.mask = pygame.mask.from_surface(self.image)
        self.speed = spd
        if spd[0]>0:
            self.push = 8
        else:
            self.push = -8
        self.damage = 12
        self.blastSnd = pygame.mixer.Sound("audio/blast.wav")
        self.cnt = time
        self.doom = 0

    def move(self, sprites, canvas):
        if self.doom<=0:
            if self.cnt<0:
                self.explode(canvas)
                return "vib"
            self.cnt -= 1
            # generate some sparks
            canvas.addTrails( [6, 7, 8], [16, 17, 18], (255,200,40,210), getPos(self, 0.4+random()*0.2, 0.4+random()*0.2) )
            if not self.cnt%4:
                self.imgIndx = (self.imgIndx+1) % len(self.imageList)
                self.image = self.imageList[self.imgIndx]
                self.mask = pygame.mask.from_surface(self.image)
            if cldList(self, sprites):
                self.explode(canvas)
                return "vib"
        else:
            if self.doom>=24:
                self.kill()
                del self
                return
            if not self.doom%6:
                formerPos = [self.rect.right-self.rect.width//2, self.rect.top+self.rect.height//2]
                self.imgIndx = (self.imgIndx+1) % len(self.imageList)
                self.image = self.imageList[self.imgIndx]
                self.rect = self.image.get_rect()
                self.rect.left = formerPos[0]-self.rect.width//2
                self.rect.top = formerPos[1]-self.rect.height//2
            self.doom += 1
        # move the object
        self.rect.left += self.speed[0]
        self.rect.top += self.speed[1]

    def explode(self, canvas):
        self.blastSnd.play(0)
        canvas.addSmoke( 4, (4, 6, 8), 2, [0,-1], (2,2,2,240), getPos(self,0.5,0.5), 2 )
        self.imageList = self.explodeList
        self.doom = 1
        self.imgIndx = 0
        self.speed = ( self.speed[0]//4, self.speed[1]//4 )

# ===========================================================================
# -------------------------------- Stage 2 ----------------------------------
# ===========================================================================
class Column(pygame.sprite.Sprite):
    def __init__(self, bg_size, groupList):
        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.image.load("image/stg2/column.png").convert_alpha()
        self.alarmList = [pygame.image.load("image/stg2/alarm0.png").convert_alpha(), pygame.image.load("image/stg2/alarm1.png").convert_alpha(), \
        pygame.image.load("image/stg2/alarm2.png").convert_alpha(), pygame.image.load("image/stg2/alarm3.png").convert_alpha(), \
        pygame.image.load("image/stg2/alarm4.png").convert_alpha(), pygame.image.load("image/stg2/alarm5.png").convert_alpha(), \
        pygame.image.load("image/stg2/alarm6.png").convert_alpha(), pygame.image.load("image/stg2/alarm7.png").convert_alpha(), \
        pygame.image.load("image/stg2/alarm8.png").convert_alpha(), pygame.image.load("image/stg2/alarm9.png").convert_alpha(), \
        pygame.image.load("image/stg2/alarm10.png").convert_alpha()]

        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.width = bg_size[0]
        self.height = bg_size[1]
        self.damage = 1
        self.speed = 8
        self.category = "column"
        self.aim = [0, 0]   # 当delay重置为0时就获取并更新hero的中心坐标
        self.rect.left = self.aim[0]
        self.rect.top = -self.rect.height    # 初始位置于屏幕左上角
        self.delay = 0      # an index that controll the fall and wait
        self.t = 260        # 循环时间周期，可在main中动态调整以改变游戏难度
        self.falling = False
        self.dustCnt = -1
        self.push = 0

        self.hitSnd = pygame.mixer.Sound("audio/crush.wav")
        # 生成一个自管理的透明画布
        self.canvas, self.canvasRect = createCanvas( bg_size, (0,0,0) )

    def move(self, sprites, frnLayer, groupList):
        if self.delay > 0:
            self.delay = ( self.delay + 1 ) % self.t
        # 确认目的地 (0为等待目的地的状态)
        if ( self.delay == 0 ):
            tgt = choice(sprites)
            if tgt.aground:
                # 英雄在落地状态，可以进行攻击。但首先需要判断自己的真正落点（必须落在linewall上，不能悬空）。
                self.aim[0] = tgt.rect.left + tgt.rect.width // 2
                self.aim[1] = tgt.rect.bottom
                aimLayer = tgt.onlayer-1   # 这里采用砖块的行数系统（奇数），以方便查找最终落点
                flag = False
                while not flag:
                    #遍历该层所有行砖，检查是否可以落在该行上
                    for wall in groupList[str(aimLayer)]:
                        if wall.rect.left <= self.aim[0] <= wall.rect.right:
                            self.aim[1] = wall.rect.top
                            flag = True
                            break
                    aimLayer -= 2
                self.delay += 1
            else:
                return
        # 警告阶段 (1~33)
        if ( 1 <= self.delay < 34 ):
            self.canvas.fill((0,0,0))  # fill the canvas with black (transparent): clear former lines
            pygame.draw.line( self.canvas, (80,80,255), (self.aim[0],0), (self.aim[0],self.aim[1]), 2)
            return "alarm"
        # 开始下落
        elif ( self.delay == 34 ):
            self.reset(frnLayer)
            return
        # 下落中
        elif ( self.delay > 34 ) and ( self.falling == True):
            self.rect.bottom += self.speed
            cldList( self, sprites )
        if ( self.rect.bottom >= self.aim[1] ):
            if self.falling:
                self.hitSnd.play(0)
                self.falling = False
                self.dustCnt = 0
                return "vib"
            else:
                if (self.dustCnt >= 0) and (self.dustCnt < 44):
                    self.dustCnt += 1
                    self.alarmRect = self.alarmList[ (self.dustCnt-1)//4 ].get_rect()  # 获取新的图片的rect
                    self.alarmRect.left = self.aim[0] - self.alarmRect.width // 2  # 设定x位置
                    self.alarmRect.bottom = self.aim[1]  # 设定y位置
                    return ( self.alarmList[ (self.dustCnt-1)//4 ], self.alarmRect )
                if self.dustCnt == 44:
                    self.dustCnt = -1
    
    def reset(self, frnLayer):
        self.falling = True
        if ( frnLayer >= 30 and self.t >= 260 ) or ( frnLayer >= 60 and self.t >= 240 ) or ( frnLayer >= 90 and self.t >= 220 ):
            self.t -= 20
        self.rect.left = self.aim[0] - self.rect.width//2
        self.rect.bottom = 0
    
    def lift(self, dist):
        self.rect.bottom += dist
        self.aim[1] += dist

    def level(self, dist):
        self.rect.left += dist
        self.aim[0] += dist

# -----------------------------------
class Golem(Monster):
    def __init__(self, wallGroup, blockSize, onlayer):
        # calculate its position
        Monster.__init__(self, "golem", (10,60,80,240), 42, 8, 4, onlayer, 3, 2)
        self.wallList = []       # 存储本行的所有砖块; # 每次初始化一个新实例时，清空此类的wallList（否则会在上一个实例的基础上再加！）
        posList = []             # 辅助列表，用于暂时存储本行砖块的位置（左边线）
        for aWall in wallGroup:  # 由于spriteGroup不好进行索引/随机选择操作，因此将其中的sprite逐个存入列表中存储
            self.wallList.append(aWall)
            posList.append(aWall.rect.left)
        wall = choice(self.wallList)
        leftMax = wall.rect.left
        rightMax = wall.rect.right    # note：此处砖块的右坐标即下一砖块的左坐标
        while True:
            if leftMax in posList:
                leftMax -= blockSize
            else:
                leftMax += blockSize  # 将多减的加回来
                break
        while True:
            if rightMax in posList:
                rightMax += blockSize
            else:
                break
        self.scope = (leftMax, rightMax)
        # initialize the sprite
        self.imgLeftList = [ pygame.image.load("image/stg2/golemLeft0.png").convert_alpha(), pygame.image.load("image/stg2/golemLeft1.png").convert_alpha(), pygame.image.load("image/stg2/golemLeft2.png").convert_alpha() ]
        self.imgRightList = [ pygame.transform.flip(self.imgLeftList[0], True, False), pygame.transform.flip(self.imgLeftList[1], True, False), pygame.transform.flip(self.imgLeftList[2], True, False) ]

        self.attLList = [ pygame.image.load("image/stg2/golemLAtt0.png").convert_alpha(), pygame.image.load("image/stg2/golemLAtt1.png").convert_alpha(), \
            pygame.image.load("image/stg2/golemLAtt2.png").convert_alpha() ]
        self.attRList = [ pygame.transform.flip(self.attLList[0], True, False), pygame.transform.flip(self.attLList[1], True, False), \
            pygame.transform.flip(self.attLList[2], True, False) ]

        self.imgIndx = 0
        self.attIndx = 0
        self.image = self.imgLeftList[0]
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.left = wall.rect.left
        self.rect.bottom = wall.rect.top
        self.damage = 8
        self.coolDown = 0
        self.doom = 0
        if self.rect.left > leftMax:           
            self.alterSpeed(-1)
        elif self.rect.right < rightMax:
            self.alterSpeed(1)
        else:
            self.alterSpeed(0)

    def move(self, delay, sprites):
        if self.health>0:
            self.checkHitBack()
            if (self.speed):   # 排除self.speed = 0的情况
                self.rect.left += self.speed
                if (getPos(self,0.75,0)[0] >= self.scope[1] and self.speed > 0) or (getPos(self,0.25,0)[0] <= self.scope[0] and self.speed < 0):
                    self.alterSpeed(-self.speed)
            if not ( delay % 10 ):
                self.imgIndx = (self.imgIndx+1) % len(self.imgLeftList)
                self.image = self.imgLeftList[self.imgIndx] if ( self.speed<0 ) else self.imgRightList[self.imgIndx]
            if self.coolDown == 0:
                for each in sprites:
                    if ( pygame.sprite.collide_mask(self, each) ):
                        self.coolDown = 60
            if (self.coolDown > 0):
                self.coolDown -= 1
                self.cratch(sprites)
        else:
            self.doom += 1
            if self.doom == 22:
                mite1 = Golemite( self.rect, self.scope, "left", self.onlayer )
                mite2 = Golemite( self.rect, self.scope, "right", self.onlayer )
                self.erase()
                return ( mite1, mite2 )
            elif self.doom >= 15:
                self.image = pygame.image.load("image/stg2/crush2.png")
            elif self.doom >= 8:
                self.image = pygame.image.load("image/stg2/crush1.png")
            elif self.doom >= 1:
                self.image = pygame.image.load("image/stg2/crush0.png")
    
    def cratch(self, sprites):
        if (self.coolDown <= 40):
            return
        if (self.coolDown >= 55):
            self.attIndx = 0
        elif (self.coolDown >= 50):
            self.attIndx = 1
        elif (self.coolDown >= 45):
            self.attIndx = 2
            if ( self.coolDown == 45 ):
                cldList( self, sprites )
        self.image = self.attLList[self.attIndx] if ( self.speed<0 ) else self.attRList[self.attIndx]
    
    def hitted(self, damage, pushed):
        if pushed>0:   # 向右击退
            self.hitBack = max( pushed-self.weight, 0 )
        elif pushed<0: # 向左击退
            self.hitBack = min( pushed+self.weight, 0 )
        self.health -= damage
        if self.health <= 0:
            self.health = 0
            return True

    def level(self, dist):
        self.rect.left += dist
        self.scope = (self.scope[0]+dist, self.scope[1]+dist)

class Golemite(Monster):
    def __init__(self, rect, scope, direct, onlayer):
        Monster.__init__(self, "golem", (10,60,80,240), 21, 4, 2, onlayer, 2, 1)
        self.scope = scope
        self.imgLeftList = [ pygame.image.load("image/stg2/golemiteLeft0.png"), pygame.image.load("image/stg2/golemiteLeft1.png"), pygame.image.load("image/stg2/golemiteLeft0.png"), pygame.image.load("image/stg2/golemiteLeft2.png") ]
        self.imgRightList = [ pygame.transform.flip(self.imgLeftList[0], True, False), pygame.transform.flip(self.imgLeftList[1], True, False), pygame.transform.flip(self.imgLeftList[2], True, False), pygame.transform.flip(self.imgLeftList[3], True, False) ]
        self.imgIndx = 0

        self.image = self.imgLeftList[0] if direct=="left" else self.imgRightList[0]
        if direct == "left":
            self.alterSpeed(-1)
        else:
            self.alterSpeed(1)
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.left = rect.left+ rect.width//2 - self.rect.width//2
        self.rect.bottom = rect.bottom
        self.coolDown = 0
        self.damage = 4
        self.doom = 0
    
    def move(self, delay, sprites):
        self.checkHitBack()
        # deal move
        if not delay % 2:
            self.rect.left += self.speed
            if (getPos(self,0.75,0)[0] >= self.scope[1] and self.speed > 0) or (getPos(self,0.25,0)[0] <= self.scope[0] and self.speed < 0):
                self.alterSpeed(-self.speed)
        if not delay % 8:
            self.imgIndx = (self.imgIndx+1) % len(self.imgLeftList)
            self.image = self.imgLeftList[self.imgIndx] if self.speed<0 else self.imgRightList[self.imgIndx]
        # deal attack
        if self.coolDown == 0:
            for each in sprites:
                if ( pygame.sprite.collide_mask(self, each) ):
                    self.coolDown = 60
        if (self.coolDown > 0):
            self.coolDown -= 1
            if ( self.coolDown == 45 ):
                cldList( self, sprites )
            
    def level(self, dist):
        self.rect.left += dist
        self.scope = (self.scope[0]+dist, self.scope[1]+dist)

# -----------------------------------
class Bowler(Monster):

    def __init__(self, wallGroup, onlayer):
        # calculate its position
        Monster.__init__(self, "bowler", (10,60,80,240), 45, 0, 4, onlayer, 3, 2)
        # note： 这里bowler的onlayer，以及其stone的onlayer值均为砖的行数，并非自身的行数，使用时不需要-1操作
        self.wallList = []       # 存储本行的所有砖块;
        for aWall in wallGroup:  # 由于spriteGroup不好进行索引/随机选择操作，因此将其中的sprite逐个存入列表中存储
            self.wallList.append(aWall)
        wall = choice(self.wallList)
        # initialize the sprite
        self.imgLeftList = [ pygame.image.load("image/stg2/bowler0.png").convert_alpha(), pygame.image.load("image/stg2/bowler0.png").convert_alpha(), \
        pygame.image.load("image/stg2/bowler0.png").convert_alpha(), pygame.image.load("image/stg2/bowler1.png").convert_alpha() ]
        self.imgRightList = [ pygame.transform.flip(self.imgLeftList[0], True, False), pygame.transform.flip(self.imgLeftList[1], True, False), \
            pygame.transform.flip(self.imgLeftList[2], True, False), pygame.transform.flip(self.imgLeftList[3], True, False) ]
        
        self.throwLeft = pygame.image.load("image/stg2/bowlerThrow.png").convert_alpha()
        self.throwRight = pygame.transform.flip(self.throwLeft, True, False)
        
        self.imgIndx = 0
        self.image = self.imgLeftList[0]
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.left = wall.rect.left
        self.rect.bottom = wall.rect.top
        self.stoneList = []

    def move(self, delay, sprites):
        self.checkHitBack()
        if not (delay % 20 ):
            heroX = choice(sprites).rect.left
            self.imgIndx = (self.imgIndx+1) % len(self.imgLeftList)
            trPos = [ self.rect.left + self.rect.width//2, self.rect.bottom ]
            if self.rect.left > heroX:
                self.image = self.imgLeftList[self.imgIndx]
                self.direction = "left"
            else:
                self.image = self.imgRightList[self.imgIndx]
                self.direction = "right"
            self.rect = self.image.get_rect()
            self.rect.left = trPos[0]-self.rect.width//2
            self.rect.bottom = trPos[1]

    def throw(self, delay):
        if not (delay % 120) and (random() > 0.5):  # 控制投石频率
            trPos = [ self.rect.left + self.rect.width//2, self.rect.bottom ]
            self.image = self.throwLeft if self.direction=="left" else self.throwRight
            self.rect = self.image.get_rect()
            self.rect.left = trPos[0]-self.rect.width//2
            self.rect.bottom = trPos[1]
            stone = Stone((self.rect.left, self.rect.bottom), self.onlayer, self.direction)
            self.stoneList.append(stone)
            return stone

class Stone(pygame.sprite.Sprite):
    def __init__(self, pos, onlayer, direction):
        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.image.load("image/stg2/stone.png").convert_alpha()
        self.oriImage = self.image
        self.deg = 0

        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.damage = 0.5
        #self.speed = 5
        self.category = "stone"
        self.rect.left = pos[0]
        self.rect.bottom = pos[1]
        self.onlayer = int(onlayer)
        self.gravity = 1
        self.speed = -2 if direction == "left" else 2   # 负数表示向左，正数向右
        self.duration = 3  # 可横向撞击次数
        self.doom = 0

    def move(self, delay, sideWalls, downWalls, keyLine, sprites, canvas):
        self.rect.left += self.speed
        if self.doom > 0:  # 如果石球要碎裂：
            trPos = [ self.rect.left + self.rect.width//2, self.rect.bottom ]
            if self.doom == 21:
                self.kill()
                del self
                return
            elif self.doom >= 16:
                self.image = pygame.image.load("image/stg2/crack3.png")
            elif self.doom >= 11:
                self.image = pygame.image.load("image/stg2/crack2.png")
            elif self.doom >= 6:
                self.image = pygame.image.load("image/stg2/crack1.png")
            elif self.doom >= 1:
                self.image = pygame.image.load("image/stg2/crack0.png")
            self.rect = self.image.get_rect()
            self.rect.left = trPos[0]-self.rect.width//2
            self.rect.bottom = trPos[1]
            self.doom += 1
        else:
            if not (delay % 4):
                self.deg = (self.deg+20) % 360
                self.image = rot_center(self.oriImage, self.deg) if self.speed <= 0 else rot_center(self.oriImage, -self.deg)
            # 水平
            for each in sprites:
                if ( pygame.sprite.collide_mask(self, each) ):
                    pos = getPos(self, 0, 0.6) if self.speed<0 else getPos(self, 1, 0.6)
                    canvas.addSpatters(2, (2,3,4), (6,7,8), (40,40,40,255), pos)
                    push = -6 if (self.speed<0) else 6
                    each.hitted(self.damage, push)
            if ( pygame.sprite.spritecollide(self, sideWalls, False, pygame.sprite.collide_mask) ) or ( pygame.sprite.spritecollide(self, downWalls, False, pygame.sprite.collide_mask) ):
                # 和英雄的处理方法一样，尝试纵坐标-4，再看是否还会碰撞。4以内的高度都可以自动滚上去
                self.rect.top -= 4
                if getCld(self, downWalls, ["lineWall","specialWall"]) or getCld(self, sideWalls, ["baseWall","sideWall"]):
                    pos = getPos(self, 0, 0.6) if self.speed<0 else getPos(self, 1, 0.6)
                    canvas.addSpatters(4, (2,4,6), (6,7,8), (40,40,40,255), pos)
                    self.rect.top += 4
                    self.rect.left -= self.speed
                    self.speed = - self.speed
                    self.duration -= 1
                    if ( self.duration <= 0 ):
                        self.doom += 1
        # 下落
        self.rect.bottom += self.gravity
        while ( pygame.sprite.spritecollide(self, downWalls, False, pygame.sprite.collide_mask) ):
            self.rect.bottom -= 1
            if not ( pygame.sprite.spritecollide(self, downWalls, False, pygame.sprite.collide_mask) ): # 如果不再和wall有重合
                canvas.addSpatters(1, (2,3,4), (5,6,7), (40,40,40,255), getPos(self,0.5,1))
                self.gravity = 1
                return False
        if (self.gravity <= 6):
            self.gravity += 1
        if ( self.rect.top >= keyLine ):
            self.onlayer -= 2
            if self.onlayer<-1:   # 防止切换area或删除底层时，onlayer减到-3
                self.kill()
                del self
    
    def lift(self, dist):
        self.rect.bottom += dist

    def level(self, dist):
        self.rect.left += dist

# -----------------------------------------------Assistant function for stone.fall
def getCld(core, group, cateList):
    spriteList = []
    cldList = pygame.sprite.spritecollide(core, group, False, pygame.sprite.collide_mask)
    for item in cldList:
        if item.category in cateList:
            spriteList.append(item)
    return spriteList

# ================================================
class GiantSpider(Monster):

    def __init__(self, wallGroup, blockSize, onlayer, boundaries):
        # initialize the sprite
        Monster.__init__(self, "GiantSpider", (255, 0, 0, 240), 200, 8, 3, onlayer, 40, 20)
        self.boundaries = boundaries
        self.wallList = []       # 存储本行的所有砖块; # 每次初始化一个新实例时，清空此类的wallList（否则会在上一个实例的基础上再加！）
        posList = []             # 辅助列表，用于暂时存储本行砖块的位置（左边线）
        for aWall in wallGroup:  # 由于spriteGroup不好进行索引/随机选择操作，因此将其中的sprite逐个存入列表中存储
            self.wallList.append(aWall)
            posList.append(aWall.rect.left)
        wall = choice(self.wallList)

        self.scope = self.boundaries
        # ----- body part (the core of the RedDragon) ------
        self.bodyLeft = pygame.image.load("image/stg2/spiderBody.png").convert_alpha()
        self.bodyRight = pygame.transform.flip(self.bodyLeft, True, False)
        self.imgIndx = 0
        self.image = self.bodyLeft
        self.mask = pygame.mask.from_surface(self.image)
        # calculate its position
        self.rect = self.image.get_rect()
        self.rect.left = wall.rect.left
        self.rect.bottom = wall.rect.top-20
        # --------------- head part ------------------
        self.headLeft = [ pygame.image.load("image/stg2/spiderHead.png").convert_alpha(), rot_center(pygame.image.load("image/stg2/spiderHeadAtt.png").convert_alpha(), 20), 
            rot_center(pygame.image.load("image/stg2/spiderHeadAtt.png").convert_alpha(), 10), rot_center(pygame.image.load("image/stg2/spiderHeadAtt.png").convert_alpha(), 40) ]
        self.headRight = [ pygame.transform.flip(self.headLeft[0], True, False), pygame.transform.flip(self.headLeft[1], True, False), 
            pygame.transform.flip(self.headLeft[2], True, False), pygame.transform.flip(self.headLeft[3], True, False) ]
        self.headR = { "left":[ (0.12,0.6), (0.2,0.7), (0.2,0.7), (0.2,0.7) ], "right":[ (0.88,0.6), (0.8,0.7), (0.8,0.7), (0.8,0.7) ] }
        self.head = Ajunction( self.headLeft[0], getPos(self, self.headR[self.direction][0][0], self.headR[self.direction][0][1]) )
        # ------------- front Legs part --------------
        self.frontLeft = [ pygame.image.load("image/stg2/frontLeg0.png").convert_alpha(), pygame.image.load("image/stg2/frontLeg1.png").convert_alpha(), \
            pygame.image.load("image/stg2/frontLeg0.png").convert_alpha(), pygame.image.load("image/stg2/frontLeg2.png").convert_alpha() ]
        self.frontRight = [ pygame.transform.flip(self.frontLeft[0], True, False), pygame.transform.flip(self.frontLeft[1], True, False), \
            pygame.transform.flip(self.frontLeft[2], True, False), pygame.transform.flip(self.frontLeft[3], True, False) ]
        self.frontR = { "left":[ (0.84,0.5), (0.82,0.5), (0.84,0.5), (0.82,0.5) ], "right":[ (0.14,0.5), (0.16,0.5), (0.14,0.5), (0.16,0.5) ] }    # 分别为左和右时的位置信息
        self.front = Ajunction( self.frontLeft[2], getPos(self, self.frontR[self.direction][0][0], self.frontR[self.direction][0][1]) )

        #self.frontJmpLeft = [ pygame.image.load("image/stg2/frontJmp0.png").convert_alpha(), pygame.image.load("image/stg2/frontJmp1.png").convert_alpha() ]
        #self.frontJmpRight = [ pygame.transform.flip(self.frontJmpLeft[0], True, False), pygame.transform.flip(self.frontJmpLeft[1], True, False) ]
        # ------------- rear legs part ----------------
        self.rearLeft = [ pygame.image.load("image/stg2/rearLeg0.png").convert_alpha(), pygame.image.load("image/stg2/rearLeg1.png").convert_alpha(), 
            pygame.image.load("image/stg2/rearLeg0.png").convert_alpha(), pygame.image.load("image/stg2/rearLeg2.png").convert_alpha() ]
        self.rearRight = [ pygame.transform.flip(self.rearLeft[0], True, False), pygame.transform.flip(self.rearLeft[1], True, False), 
            pygame.transform.flip(self.rearLeft[2], True, False), pygame.transform.flip(self.rearLeft[3], True, False) ]
        self.rearR = { "left":[ (0.5,0.5), (0.5,0.5), (0.5,0.5), (0.5,0.5) ], "right":[ (0.5,0.5), (0.5,0.5), (0.5,0.5), (0.5,0.5) ] }
        self.rear = Ajunction( self.rearLeft[0], getPos(self, self.rearR[self.direction][0][0], self.rearR[self.direction][0][1]) )
        # ------------------- 本boss比较特殊的一点：前后腿的图片数量相同，动画顺序相同 ------------------
        self.legIndx = 0
        self.headIndx = 0
        # ----------- other attributes -------------------------
        self.damage = 8
        self.coolDown = 0
        self.doom = 0
        self.alterSpeed( choice( [-1,1] ) )
        self.cnt = 0         # count for the loop of shift position
        self.coolDown = 0    # count for attack coolDown
        self.growlSnd = pygame.mixer.Sound("audio/redDragonGrowl.wav")
        self.moanSnd = pygame.mixer.Sound("audio/redDragonMoan.wav")
        self.upDown = 3

    def move(self, delay, sprites, canvas):
        self.checkHitBack()
        if (self.speed):     # 排除self.speed = 0的情况
            self.rect.left += self.speed
            if (self.rect.right >= self.scope[1] and self.speed > 0) or (self.rect.left <= self.scope[0] and self.speed < 0):
                self.alterSpeed( -self.speed )
        if not delay % 2:
            if not delay%20:
                self.rect.top += self.upDown
                self.upDown = -self.upDown
            # Decide whether to Jump
            #if not self.onlayer==
            # move horizent
            if not ( delay % 12 ):
                if self.direction == "left":
                    self.image = self.bodyLeft
                    self.mask = pygame.mask.from_surface(self.image)
                    # deal legs:
                    self.legIndx = (self.legIndx+1) % len(self.frontLeft)
                    self.front.updateImg( self.frontLeft[self.legIndx] )
                    self.rear.updateImg( self.rearLeft[self.legIndx] )
                    self.head.updateImg( self.headLeft[self.headIndx] )
                elif self.direction == "right":
                    self.image = self.bodyRight
                    self.mask = pygame.mask.from_surface(self.image)
                    # deal legs:
                    self.legIndx = (self.legIndx+1) % len(self.frontLeft)
                    self.front.updateImg( self.frontRight[self.legIndx] )
                    self.rear.updateImg( self.rearRight[self.legIndx] )
                    self.head.updateImg( self.headRight[self.headIndx] )
        self.front.updatePos( getPos(self, self.frontR[self.direction][self.legIndx][0], self.frontR[self.direction][self.legIndx][1]) )
        self.rear.updatePos( getPos(self, self.rearR[self.direction][self.legIndx][0], self.rearR[self.direction][self.legIndx][1]) )
        self.head.updatePos( getPos(self, self.headR[self.direction][self.headIndx][0], self.headR[self.direction][self.headIndx][1]) )
        if self.coolDown == 0:
            for each in sprites:
                if ( pygame.sprite.collide_mask(self, each) ):
                    self.coolDown = 60
        if (self.coolDown > 0):
            self.coolDown -= 1
            self.cratch(sprites)

    def cratch(self, sprites):
        if (self.coolDown <= 40):
            self.headIndx = 0
            return
        if (self.coolDown >= 54):
            self.headIndx = 1
        elif (self.coolDown >= 48):
            self.headIndx = 2
        elif (self.coolDown >= 42):
            self.headIndx = 3
            if ( self.coolDown == 42 ):
                for each in sprites:
                    if pygame.sprite.collide_mask( self.head, each ):
                        each.hitted( self.damage, self.push )
    
    # 鉴于本对象的构造非常复杂，因此提供一个专门的绘制接口
    # 给此函数传递一个surface参数，即可在该surface上绘制（blit）完整的本对象
    def paint(self, screen):
        screen.blit( self.rear.image, self.rear.rect )
        screen.blit( self.image, self.rect )
        screen.blit( self.head.image, self.head.rect )
        screen.blit( self.front.image, self.front.rect )
    
    def erase(self):
        self.moanSnd.play(0)
        self.front.kill()
        del self.front
        self.rear.kill()
        del self.rear
        self.kill()
        del self
        return True   # dead
# ===========================================================================
# -------------------------------- stage3 -----------------------------------
# ===========================================================================
class Mist():

    canvas = None
    canvasRect = None

    def __init__(self, bg_size):
        self.canvas = pygame.Surface(bg_size).convert_alpha()
        self.canvasRect = self.canvas.get_rect()
        self.canvasRect.left = 0
        self.canvasRect.top = 0
        self.category = "mist"
        self.alpha = 0
        self.range = 144
        self.pervade = False
    
    def renew(self, delay, sprites):
        if self.pervade and (delay % 240) and (self.alpha<240):
            self.alpha += 1  # highest: 240
        if delay % 2 == 0:   # 营造视野圆圈摇曳效果
            self.range = 140
        else:
            self.range = 144
        
        self.canvas.fill((0,0,0, self.alpha))
        for each in sprites:
            ctr = (each.rect.left + each.rect.width//2, each.rect.top + each.rect.height//2)
            pygame.draw.circle( self.canvas, (0,0,0,self.alpha*0.75), ctr, self.range+each.lumi+60, 0 )

        for each in sprites:
            ctr = (each.rect.left + each.rect.width//2, each.rect.top + each.rect.height//2)
            pygame.draw.circle( self.canvas, (0,0,0,self.alpha*0.5), ctr, self.range+each.lumi+40, 0 )

        for each in sprites:
            ctr = (each.rect.left + each.rect.width//2, each.rect.top + each.rect.height//2)
            pygame.draw.circle( self.canvas, (0,0,0,self.alpha*0.25), ctr, self.range+each.lumi+20, 0 )

        for each in sprites:
            ctr = (each.rect.left + each.rect.width//2, each.rect.top + each.rect.height//2)
            pygame.draw.circle( self.canvas, (0,0,0,0), ctr, self.range+each.lumi, 0 )

# -----------------------------------
class Bat(Monster):

    def __init__(self, wallGroup, onlayer):
        # calculate its position
        Monster.__init__(self, "bat", (80,10,80,240), 10, 3, 1, onlayer, 1, 1)
        self.wallList = []       # 存储本行的所有砖块; # 每次初始化一个新实例时，清空此类的wallList（否则会在上一个实例的基础上再加！）
        posList = []             # 辅助列表，用于暂时存储本行砖块的位置（左边线）
        for aWall in wallGroup:  # 由于spriteGroup不好进行索引/随机选择操作，因此将其中的sprite逐个存入列表中存储
            if not aWall.category == "specialWall":
                self.wallList.append(aWall)
                posList.append(aWall.rect.left)
        if len(self.wallList)==0:
            self.erase()
            return
        wall = choice(self.wallList)
        self.onlayer = int(onlayer)
        self.foot = wall.rect.bottom - 10
        # initialize the sprite ---------------
        self.hangImg = pygame.image.load("image/stg3/batHang.png").convert_alpha()
        self.flyList = [ pygame.image.load("image/stg3/bat0.png").convert_alpha(), pygame.image.load("image/stg3/bat1.png").convert_alpha() ]

        self.imgIndx = 0
        self.image = self.hangImg
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.left = wall.rect.left + (wall.rect.width-self.rect.width) // 2
        self.rect.top = self.foot
        self.damage = 2
        self.coolDown = 0
        self.speed = [0, 0]
        self.vib = 2
        self.tgt = None      # tgt将取三类值：None表示休息中；hero对象表示追击敌人；lineWall对象表示从飞行状态转入休息的短暂动作。
    
    def move(self, delay, sprites):
        self.checkHitBack()
        # 睡眠状态。若有hero接近，则将之唤醒。
        if not self.tgt:
            for each in sprites:
                if math.pow( getPos(each,0.5,0.5)[0]-getPos(self,0.5,0.5)[0], 2 ) + math.pow( getPos(each,0.5,0.5)[1]-getPos(self,0.5,0.5)[1], 2 )<100**2:
                    self.tgt = each
                    self.imgIndx = 0
                    break
        # 有tgt的飞行状态，又分为两类：
        else:
            # tgt引用的是砖块，表示目标丢失，则寻找最近的砖块，并悬停在下面。
            if self.tgt.category=="lineWall":
                if ( self.tgt.rect.left < getPos(self, 0.5, 0.5)[0] < self.tgt.rect.right ) and ( self.rect.top <= self.foot ):
                    self.tgt = None
                    self.rect.top = self.foot
                    trPos = [ self.rect.left + self.rect.width//2, self.rect.bottom ]
                    self.image = self.hangImg
                    self.rect = self.image.get_rect()
                    self.rect.left = trPos[0]-self.rect.width//2
                    self.rect.bottom = trPos[1]
                    self.imgIndx = 0
                    return
                elif getPos(self, 0.5, 0.5)[0] < getPos(self.tgt, 0.5, 0.5)[0]:
                    self.speed[0] = 1
                elif getPos(self, 0.5, 0.5)[0] > getPos(self.tgt, 0.5, 0.5)[0]:
                    self.speed[0] = -1
            # tgt引用的是hero，则为追击模式！
            elif self.tgt.category=="hero":
                if math.pow( getPos(self.tgt,0.5,0.5)[0]-getPos(self,0.5,0.5)[0], 2 ) + math.pow( getPos(self.tgt,0.5,0.5)[1]-getPos(self,0.5,0.5)[1], 2 )>160**2:
                    if len(self.wallList)==0:
                        self.erase()
                    dist = float("inf")     # 找最近的砖块。初始化为无穷大。
                    for each in self.wallList:
                        newDist = abs( getPos(self,0.5,0.5)[0]-getPos(each,0.5,0.5)[0] )
                        if newDist < dist:
                            dist = newDist
                            self.tgt = each
                    return
                if not delay%2:
                    if getPos(self, 0.5, 0.5)[0] < getPos(self.tgt, 0.5, 0.5)[0]:
                        self.speed[0] = 1
                    elif getPos(self, 0.5, 0.5)[0] > getPos(self.tgt, 0.5, 0.5)[0]:
                        self.speed[0] = -1
                    else:
                        self.speed[0] = 0
            # Move the bat.
            if not delay%2:
                if abs(self.speed[1]) > 5:
                    self.vib = -self.vib
                self.speed[1] += self.vib
                self.rect.left += self.speed[0]
                self.rect.top += self.speed[1]
                # Change image.
                if not (delay % 8):
                    trPos = [ self.rect.left + self.rect.width//2, self.rect.bottom ]
                    self.image = self.flyList[self.imgIndx]
                    self.rect = self.image.get_rect()
                    self.rect.left = trPos[0]-self.rect.width//2
                    self.rect.bottom = trPos[1]
                    self.mask = pygame.mask.from_surface(self.image)    # 更新mask，使得与hero重合的判断更加精确
                    self.imgIndx = (self.imgIndx+1) % len(self.flyList)
            # deal damage.
            if self.coolDown==0:
                for each in sprites:
                    if ( pygame.sprite.collide_mask(self, each) ):
                        self.coolDown = 16
            else:
                if self.coolDown == 12:
                    cldList( self, sprites )
                self.coolDown -= 1

    def lift(self, dist):
        self.rect.bottom += dist
        self.foot += dist
        
# -----------------------------------
class Skeleton(Monster):  

    def __init__(self, wallGroup, blockSize, onlayer):
        # calculate its position
        Monster.__init__(self, "skeleton", (255,255,255,240), 20, 3, 1, onlayer, 2, 1)
        self.wallList = []       # 存储本行的所有砖块; # 每次初始化一个新实例时，清空此类的wallList（否则会在上一个实例的基础上再加！）
        posList = []             # 辅助列表，用于暂时存储本行砖块的位置（左边线）
        for aWall in wallGroup:  # 由于spriteGroup不好进行索引/随机选择操作，因此将其中的sprite逐个存入列表中存储
            if not aWall.category == "specialWall":  # 排除特殊砖块上生成，造成空的popping操作
                self.wallList.append(aWall)
                posList.append(aWall.rect.left)
        if len(self.wallList) == 0:
            self.erase()
            return
        wall = choice(self.wallList)
        leftMax = wall.rect.left
        rightMax = wall.rect.right   # note：此处砖块的右坐标即下一砖块的左坐标
        while True:
            if leftMax in posList:
                leftMax -= blockSize
            else:
                leftMax += blockSize # 将多减的加回来
                break
        while True:
            if rightMax in posList:
                rightMax += blockSize
            else:
                break
        self.scope = (leftMax, rightMax)
        # initialize the sprite
        self.popList = [ pygame.image.load("image/stg3/pop0.png"), pygame.image.load("image/stg3/pop1.png"), pygame.image.load("image/stg3/pop2.png"), \
            pygame.image.load("image/stg3/pop3.png"), pygame.image.load("image/stg3/pop4.png"), pygame.image.load("image/stg3/pop5.png"), pygame.image.load("image/stg3/pop6.png"), \
            pygame.image.load("image/stg3/pop7.png") ]

        self.imgLeftList = [ pygame.image.load("image/stg3/skeletonLeft0.png").convert_alpha(), pygame.image.load("image/stg3/skeletonLeft1.png").convert_alpha(), \
            pygame.image.load("image/stg3/skeletonLeft2.png").convert_alpha(), pygame.image.load("image/stg3/skeletonLeft1.png").convert_alpha() ]
        self.imgRightList = [ pygame.transform.flip(self.imgLeftList[0], True, False), pygame.transform.flip(self.imgLeftList[1], True, False), \
            pygame.transform.flip(self.imgLeftList[2], True, False), pygame.transform.flip(self.imgLeftList[3], True, False) ]
        self.attLImg = pygame.image.load("image/stg3/attLeft.png").convert_alpha()
        self.attRImg = pygame.transform.flip(self.attLImg, True, False)

        self.imgIndx = 0
        self.image = self.popList[0]
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.left = wall.rect.left
        self.rect.bottom = wall.rect.top
        self.damage = 3
        self.coolDown = 0
        self.birth = [wall.rect.left+wall.rect.width//2, wall.rect.top]
        if random()<=0.5:
            self.alterSpeed(-3)
        else:
            self.alterSpeed(3)
        self.popping = True                    # 出生阶段为True

    def move(self, delay, sprites):
        self.checkHitBack()
        if not (delay % 4): 
            if not self.popping:
                self.rect.left += self.speed   # pop阶段的最后一张图片和移动阶段的第一张图片大小刚好是相等的，完美对接
                if (getPos(self,0.75,0)[0] >= self.scope[1] and self.speed > 0) or (getPos(self,0.25,0)[0] <= self.scope[0] and self.speed < 0):
                        self.alterSpeed(-self.speed)
                if not (delay % 8):
                    self.image = self.imgLeftList[self.imgIndx] if self.speed < 0 else self.imgRightList[self.imgIndx]
                    self.mask = pygame.mask.from_surface(self.image)  # 更新rect，使得与hero重合的判断更加精确
                    self.imgIndx = (self.imgIndx+1) % len(self.imgLeftList)
                if self.coolDown==0:
                    for each in sprites:
                        if ( pygame.sprite.collide_mask(self, each) ):
                            self.coolDown = 8  # 归在delay整除4的条件下，故实际间隔为8*4 = 32
                else:
                    self.cratch(sprites)
                    self.coolDown -= 1
            elif self.popping:
                self.image = self.popList[self.imgIndx]
                self.rect = self.image.get_rect()
                self.rect.bottom = self.birth[1]
                self.rect.left = self.birth[0]- self.rect.width//2
                self.imgIndx = (self.imgIndx+1) % len(self.popList)
                if self.imgIndx == 0:
                    self.popping = False      # 若imgIndx 第一次变为零，则表示完成了一次pop的过程

    def cratch(self, sprites):
        if (self.coolDown >= 4):
            self.image = self.attLImg if self.speed<0 else self.attRImg
            if ( self.coolDown == 5 ):
                cldList( self, sprites )
    
    def lift(self, dist):
        self.rect.bottom += dist
        self.birth[1] += dist

    def level(self, dist):
        self.rect.left += dist
        self.birth[0] += dist
        self.scope = (self.scope[0]+dist, self.scope[1]+dist)

# -----------------------------------
class Dead(Monster):
    
    def __init__(self, wallGroup, blockSize, onlayer):
        # calculate its position
        Monster.__init__(self, "dead", (10,10,10,240), 30, 0, 2, onlayer, 2, 2)
        self.wallList = []       # 存储本行的所有砖块; # 每次初始化一个新实例时，清空此类的wallList（否则会在上一个实例的基础上再加！）
        posList = []             # 辅助列表，用于暂时存储本行砖块的位置（左边线）
        for aWall in wallGroup:  # 由于spriteGroup不好进行索引/随机选择操作，因此将其中的sprite逐个存入列表中存储
            #if not aWall.category == "specialWall":
            self.wallList.append(aWall)
            posList.append(aWall.rect.left)
        if len(self.wallList)==0:
            self.erase()
            return
        wall = choice(self.wallList)
        leftMax = wall.rect.left
        rightMax = wall.rect.right   # note：此处砖块的右坐标即下一砖块的左坐标
        while True:
            if leftMax in posList:
                leftMax -= blockSize
            else:
                leftMax += blockSize # 将多减的加回来
                break
        while True:
            if rightMax in posList:
                rightMax += blockSize
            else:
                break
        self.scope = (leftMax, rightMax)
        self.onlayer = int(onlayer)
        # initialize the sprite
        gender = "Left" if random()<0.5 else "Right"
        self.imgLeftList = [ pygame.image.load("image/stg3/dead"+gender+"0.png").convert_alpha(), pygame.image.load("image/stg3/dead"+gender+"1.png").convert_alpha(), \
            pygame.image.load("image/stg3/dead"+gender+"2.png").convert_alpha(), pygame.image.load("image/stg3/dead"+gender+"1.png").convert_alpha() ]
        self.imgRightList = [ pygame.transform.flip(self.imgLeftList[0], True, False), pygame.transform.flip(self.imgLeftList[1], True, False),\
            pygame.transform.flip(self.imgLeftList[2], True, False), pygame.transform.flip(self.imgLeftList[1], True, False) ]
        self.attLeft = pygame.image.load("image/stg3/vomit"+gender+".png").convert_alpha()
        self.attRight = pygame.transform.flip(self.attLeft, True, False)

        self.imgIndx = 0
        self.image = self.imgLeftList[0]
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.left = wall.rect.left + (wall.rect.width-self.rect.width) // 2
        self.rect.bottom = wall.rect.top
        self.coolDown = 0
        
        if random()<=0.5:
            self.alterSpeed(-2)
        else:
            self.alterSpeed(2)
        self.snd = pygame.mixer.Sound("audio/vomiSplash.wav")
        self.vomiList = pygame.sprite.Group()
        self.voming = 0

    def move(self, delay, sprites, canvas):
        self.checkHitBack()
        if not (delay % 6) and not self.voming: 
            self.rect.left += self.speed
            if (self.rect.right >= self.scope[1] and self.speed > 0) or (self.rect.left <= self.scope[0] and self.speed < 0):
                self.alterSpeed(-self.speed)
            if not (delay % 12):
                self.image = self.imgLeftList[self.imgIndx] if self.speed < 0 else self.imgRightList[self.imgIndx]
                self.mask = pygame.mask.from_surface(self.image)  # 更新rect，使得与hero重合的判断更加精确
                self.imgIndx = (self.imgIndx+1) % len(self.imgLeftList)
            if random()<0.04:
                for hero in sprites:
                    if -2 < hero.onlayer-self.onlayer+1 < 2:
                        self.snd.play(0)
                        break
                self.voming = 54
        if (self.voming > 0):
            self.image = self.attLeft if (self.speed<0) else self.attRight
            self.voming -= 1
            if self.voming < 48:  # 警告:
                # 每次刷新均吐出1个气团
                spdX = 6-self.voming//8
                if self.speed <= 0:
                    spd = [ -spdX, 0 ]
                    startX = 0
                elif self.speed > 0:
                    spd = [ spdX, 0 ]
                    startX = 1
                vomi = Vomitus( getPos(self, startX, 0.35), spd, sprites, canvas )
                self.vomiList.add( vomi )

    def paint(self, screen):
        screen.blit(self.image, self.rect)
        for vomi in self.vomiList:
            vomi.move( self.rect.bottom )
            pygame.draw.circle(screen, vomi.color, vomi.pos, vomi.r)

    def lift(self, dist):
        self.rect.bottom += dist
        for vomi in self.vomiList:
            vomi.pos[1] += dist

    def level(self, dist):
        self.rect.left += dist
        self.scope = (self.scope[0]+dist, self.scope[1]+dist)
        for vomi in self.vomiList:
            vomi.pos[0] += dist

    def erase(self):                        # 所有monster都应有erase()函数。
        for vomi in self.vomiList:
            vomi.erase()
        self.kill()
        del self
        return

class Vomitus(pygame.sprite.Sprite):

    def __init__(self, pos, spd, sprites, canvas): # 参数color:推荐带上透明度RGBA；参数speed:为一个二元组
        pygame.sprite.Sprite.__init__(self)
        self.r = choice( [3, 4, 5] )
        self.color = choice( [(60,60,80,255),(100,100,120,255)] )
        self.initPos = [ randint(pos[0]-2, pos[0]+2), randint(pos[1]-2, pos[1]+2) ]
        self.pos = self.initPos
        self.speed = spd
        self.cnt = 0
        self.tgts = sprites
        self.canvas = canvas
    
    def move(self, btLine):
        if self.pos[1]<btLine:
            self.cnt += 1
            if not self.cnt%2:
                for hero in self.tgts:
                    if hero.rect.left < self.pos[0] < hero.rect.right and hero.rect.top < self.pos[1] < hero.rect.bottom:
                        if hero.affected<0:
                            hero.affect()
                        hero.hitted( 0.4, 0 )
                        if self.speed[0]>0:
                            hero.hitBack = 1
                        else:
                            hero.hitBack = -1
                        self.erase()
                        return
                self.pos[0] += self.speed[0]
                self.pos[1] += self.speed[1]
                if self.speed[1]<6 and not self.cnt%4:
                    self.speed[1] += 1
        else:
            self.erase()
    
    def erase(self):
        self.canvas.addSpatters(2, (1,2), (3,4), self.color, self.pos)
        self.kill()
        del self

# ------------------------------------
class Vampire(Monster):

    sycthe = None
    
    def __init__(self, groupList, onlayer, boundaries):
        # initialize the sprite
        Monster.__init__(self, "Vampire", (10, 30, 10, 240), 200, 8, 1, onlayer, 40, 20)
        self.activated = False
        self.onlayer = int(onlayer)
        self.boundaries = boundaries
        self.initLayer(groupList)
        # initialize the sprite
        self.imgList = createImgList( [ pygame.image.load("image/stg3/Vampire0.png").convert_alpha(), pygame.image.load("image/stg3/Vampire1.png").convert_alpha() ] )
        self.attList = createImgList( [ pygame.image.load("image/stg3/VampireAtt0.png").convert_alpha(), pygame.image.load("image/stg3/VampireAtt1.png").convert_alpha(), 
            pygame.image.load("image/stg3/VampireAtt2.png").convert_alpha() ] )
        self.summonImg = createImgList( [pygame.image.load("image/stg3/VampireSummon.png").convert_alpha()] )
        self.imgIndx = 0
        self.image = self.imgList["left"][0]
        self.mask = pygame.mask.from_surface(self.image)
        # calculate its position
        self.rect = self.image.get_rect()
        self.rect.left = self.initPos[0]-self.rect.width//2  # 位于砖块居中
        self.rect.bottom = self.initPos[1]
        # Define scythe. ----------------------------------------
        self.scytheR = { "left":(0.15,0.7, 0), "right":(0.85,0.7, 0) }
        self.scytheAttR = { "left":[ (0.6,0.5, 0), (0.25, 0.69, 1), (0.4,0.87, 1) ], "right":[ (0.4,0.5, 0), (0.75, 0.69, 1), (0.6,0.87, 1) ] }
        self.scytheImg = createImgList( [pygame.image.load("image/stg3/scythe.png").convert_alpha()] )
        self.scytheAttImg = createImgList( [pygame.image.load("image/stg3/scytheAtt0.png").convert_alpha(), pygame.image.load("image/stg3/scytheAtt1.png").convert_alpha(), 
            pygame.image.load("image/stg3/scytheAtt2.png").convert_alpha()] )
        self.scythe = Ajunction( self.scytheImg["left"], getPos(self, self.scytheR["left"][0], self.scytheR["left"][1]) )
        # ----------- other attributes -------------------------
        self.damage = 6
        self.coolDown = 0
        self.maxHealth = self.health
        self.snd = pygame.mixer.Sound("audio/vampireAtt.wav")
        self.alterSpeed( choice([-1,0,1]) )
        self.status = "wandering"          # wandering表示闲逛的状态，alarming表示发现英雄的状态
        self.wpPos = (0, 0, 0)
        self.tgt = None                    # 指示要攻击的英雄
        self.flying = False
        self.summonCD = 1100               # 召唤冷却
        self.upDown = 2
            
    # 这个move()函数是供外界调动的接口，这里仅起根据传入的英雄参数判断状态的作用。判断完成后，修改自身的状态，然后执行相应的函数。
    def move(self, delay, sprites, groupList):
        self.checkHitBack()
        # change layer
        if not (delay%20) and not self.flying and self.status=="wandering" and random()<0.1:
            self.flying = True
            hero = choice( sprites )
            # 向hero所在的层数进逼。由于hero能在的层数一定是合法的，故这里不需要检测层数的合法性（不需边界测试）
            if self.onlayer > 1 and self.onlayer > hero.onlayer-1:   # 注意，这里由于层数体系不一样，要检查self.layer为1时不能减为-1（那就成了sideWall！）
                self.onlayer -= 2
            elif self.onlayer < hero.onlayer-1:
                self.onlayer += 2
            self.initLayer(groupList)           # 计算其在新一行的水平scope        
        # 优先处理 flying $$$$
        if self.flying:
            self.rect.bottom += ( (self.initPos[1]-getPos(self, 0.5, 1)[1]) // 20 )
            self.rect.left += ( (self.initPos[0]-getPos(self, 0.5, 1)[0]) // 20 )
            #以竖直方向为标准，若已抵达(等于或略高于)目标行，则将flying标记为False
            if 0<= (self.initPos[1]-self.rect.bottom) < 20:
                self.rect.bottom = self.initPos[1]
                self.flying = False
        else:
            if not (delay % 20):
                self.rect.top += self.upDown
                self.upDown = - self.upDown
            for hero in sprites:
                # 如果有英雄在同一层，则将速度改为朝英雄方向。(这里的两套体系，英雄的层数为偶数，而怪物用的层数都是奇数)
                if ( (hero.onlayer-1)==self.onlayer and abs( getPos(hero,0.5,0.5)[0]-getPos(self,0.5,0.5)[0] )<=360 ) or self.coolDown>0:
                    self.status = "alarming"
                    self.tgt = hero
                    break     # 这里碰到第一个英雄符合条件就退出了。因此，如果两个英雄同时在一层中，P1总是会被针对，而P2永远不会被选中为目标。问题留着以后修正。
                else:
                    self.status = "wandering"
            if self.status == "wandering":
                # wander 部分
                if (self.speed):                        # speed!=0，在运动。
                    self.rect.left += self.speed
                    if (getPos(self, 0.7, 1)[0] >= self.scope[1] and self.speed > 0) or (getPos(self, 0.3, 1)[0] <= self.scope[0] and self.speed < 0):
                        self.alterSpeed(-self.speed)
                    if not delay % 20 and random()<0.08:# 随机进入休息状态。
                        self.alterSpeed(0)
                elif not delay % 20 and random()<0.08:  # 否则，在休息。此时若随机数满足条件，进入巡逻状态
                    self.alterSpeed( choice( [1,-1] ) )
                # wander时还会召唤小型生物。
                self.summonCD -= 1
                if self.summonCD <= 24:
                    trPos = [ self.rect.left + self.rect.width//2, self.rect.bottom ]
                    self.image = self.summonImg[self.direction]
                    self.rect = self.image.get_rect()
                    self.rect.left = trPos[0]-self.rect.width//2
                    self.rect.bottom = trPos[1]
                    if self.summonCD == 0:
                        self.summonCD = 1100
                        if random()<0.5:
                            babe = "skeleton"
                            pos1 = getPos(self, 0.3, 1)
                            pos2 = getPos(self, 0.7, 1)
                        else:
                            babe = "bat"
                            pos1 = getPos(self, 0.3, 0)
                            pos2 = getPos(self, 0.7, 0)
                        return ( (babe,pos1), (babe,pos2) )
                    return
            elif self.status == "alarming":
                if not self.coolDown:
                    if getPos( self.tgt, 0.5, 0.5 )[0]>getPos( self, 0.5, 0.5 )[0]:
                        self.alterSpeed(1)
                    else:
                        self.alterSpeed(-1)
                #attack部分
                self.rect.left += self.speed*2
                if self.coolDown==0:
                    for each in sprites:
                        if abs(getPos(self, 0.5, 0.5)[0]-getPos(each, 0.5, 0.5)[0])<60:
                            self.snd.play(0)    # 攻击英雄，咆哮
                            self.speed = 0
                            self.coolDown = 46
                else:
                    self.coolDown -= 1
        # checkImg部分
        trPos = [ self.rect.left + self.rect.width//2, self.rect.bottom ]
        if self.coolDown <= 0:
            self.wpPos = self.scytheR[self.direction]
            if not (delay % 14 ):
                self.imgIndx = (self.imgIndx+1) % len(self.imgList)
            self.image = self.imgList[self.direction][self.imgIndx]
            self.scythe.updateImg( self.scytheImg[self.direction] )
            self.scythe.updatePos( getPos(self, self.wpPos[0], self.wpPos[1]) )
        else:
            if self.coolDown >= 16:
                attIndx = 0
            elif self.coolDown >= 8:
                attIndx = 1
                for each in sprites:
                    if pygame.sprite.collide_mask(self.scythe, each):
                        each.hitted( self.damage, self.push )
                        self.health += self.damage*0.5
                        if self.health > self.maxHealth:
                            self.health = self.maxHealth
            else:
                attIndx = 2
            self.wpPos = self.scytheAttR[self.direction][attIndx]
            self.image = self.attList[self.direction][attIndx]
            self.scythe.updateImg( self.scytheAttImg[self.direction][attIndx] )
            self.scythe.updatePos( getPos(self, self.wpPos[0], self.wpPos[1]) )
                
        self.rect = self.image.get_rect()
        self.rect.left = trPos[0]-self.rect.width//2
        self.rect.bottom = trPos[1]

    # 此函数用于确定新一行中的位置及scope
    def initLayer(self, groupList):
        self.wallList = []          # 存储本行的所有砖块; # 每次初始化一个新实例时，清空此类的wallList（否则会在上一个实例的基础上再加！）
        posList = []                # 辅助列表，用于暂时存储本行砖块的位置（左边线）
        for aWall in groupList[str(self.onlayer)]:  # 由于spriteGroup不好进行索引/随机选择操作，因此将其中的sprite逐个存入列表中存储
            self.wallList.append(aWall)
            posList.append(aWall.rect.left)
        if len(self.wallList)==0:
            self.erase()
            return
        if self.activated:          # 找新层过程的调用，找最近的砖块。
            dist = float("inf")
            for each in self.wallList:
                newDist = abs( getPos(self,0.5,0.5)[0]-getPos(each,0.5,0.5)[0] )
                if newDist < dist:
                    dist = newDist
                    wall = each
        else:                       # 初始化过程的调用
            wall = choice(self.wallList)
        self.initPos = getPos(wall, 0.5, -0.1)   # 新点，居中，漂浮
        leftMax = wall.rect.left
        rightMax = wall.rect.right  # note：此处砖块的右坐标即下一砖块的左坐标
        while True:
            if leftMax in posList: # warmachine比较宽，可以占两格行进
                leftMax -= wall.rect.width
            else:
                leftMax += wall.rect.width  # 将多减的加回来
                break
        while True:
            if rightMax in posList:
                rightMax += wall.rect.width
            else:
                break
        self.scope = (leftMax, rightMax)
        return wall

    def lift(self, dist):
        self.rect.bottom += dist
        self.initPos[1] += dist

    def level(self, dist):
        self.rect.left += dist
        self.initPos[0] += dist
        self.boundaries = (self.boundaries[0]+dist, self.boundaries[1]+dist)

    # 鉴于本对象的构造非常复杂，因此提供一个专门的绘制接口
    # 给此函数传递一个surface参数，即可在该surface上绘制（blit）完整的本对象
    def paint(self, screen, canvas):
        canvas.addSmoke( 1, (2,4,5), 4, [-self.speed,-1], (210,10,190,200), getPos(self,0.5,1), 20 )
        #按层级顺序画weapon和self
        if self.wpPos[2]==0:
            screen.blit( self.scythe.image, self.scythe.rect )
            screen.blit( self.image, self.rect )
        elif self.wpPos[2]==1:
            screen.blit( self.image, self.rect )
            screen.blit( self.scythe.image, self.scythe.rect )
        
    
    def erase(self):
        #self.moanSnd.play(0)
        self.scythe.kill()
        del self.scythe
        self.kill()
        del self
        return True   # dead

# ===========================================================================
# --------------------------------- stage4 ----------------------------------
# ===========================================================================
class Ooze():

    bg_size = 0    # 屏幕尺寸
    canvas = None
    canvasRect = None
    surfH = 0      # 液面的高度
    bubbles = []   # 存储气泡的列表

    def __init__(self, bg_size, initH, font):  # initH 是游戏开始时ooze已有的初始高度，相对于bg_size[1]而言。
        # initialize.
        self.canvas, self.canvasRect = createCanvas( bg_size, (0,0,0) )
        self.canvas.set_alpha(128)
        self.bg_size = bg_size
        self.surfH = bg_size[1]-initH
        self.damage = 0.6
        self.speed = 1
        self.push = 0
        self.category = "ooze"
        self.font = font   # 用于在屏幕上显示高度数字。由于涉及到全角符号"▼/⬇"，故一律使用中文font。
        self.bubbles = []

        # green ooze 部分，整个屏幕的大小，只是在渲染时只渲染surfH以下的部分。
        self.greenCv = pygame.Surface( (bg_size[0], bg_size[1]) ).convert_alpha()
        self.greenCv.fill( (60,140,60,128) )
        self.oozeRect = self.greenCv.get_rect()
        self.oozeRect.left = 0
        self.oozeRect.top = self.surfH
        
    def rise(self, delay, screen, sprites, spurtCanvas): # 本函数是直接在传进来的screen上绘制。
        if not (delay % 4):
            self.surfH -= self.speed    # 上涨
            for each in sprites:
                if each.rect.bottom>self.surfH:
                    # Deal damage.
                    if not each.category=="slime":
                        if each.category in ("hero", "artiHero"):
                            each.hitted(self.damage, 0)
                        else:
                            each.hitted(self.damage, 0)
                    # Draw visual effect.
                    if each.rect.top<self.surfH:
                        posX = getPos(each, random(), 0)[0]
                        spurtCanvas.addSpatters( 5, (2,3,4), (4,5,6), (50,100,50,240), (posX, self.surfH)) # 腐蚀效果
                    else:
                        spurtCanvas.addTrails( [3,4,5], [16, 20, 24], (40,120,40,220), getPos(each, 0.5, random()) )
            if random()<0.5:
                self.bubbles.append( [randint(0,self.bg_size[0]), self.bg_size[1], randint(1,8)] )  #生成新气泡（列表形式：[横坐标，纵坐标，半径]）
        # 重画软泥.若液面在屏幕之外，则在下方显示其距离.
        if (self.surfH < self.bg_size[1]):
            self.canvas.fill((0,0,0))
            self.oozeRect.top = max(self.surfH, 0)
            screen.blit(self.greenCv, self.oozeRect)
            pygame.draw.line( self.canvas, (20,60,20), (0,self.surfH), (self.bg_size[0],self.surfH), randint(3,7) ) # 液面的深色线
        else:
            txt = self.font.render( "▼ "+str(self.surfH-self.bg_size[1]), True, (255,255,255) )
            rect = txt.get_rect()
            rect.left = self.bg_size[0]//2
            rect.top = self.bg_size[1]-30
            screen.blit( txt, rect )
            pass
        # 处理气泡.
        for each in self.bubbles:
            pygame.draw.circle( self.canvas, (20,60,20), (each[0],each[1]), each[2] )
            each[1] -= 1
            if each[1]<=self.surfH:
                self.bubbles.remove(each)
        screen.blit(self.canvas, self.canvasRect)

    def lift(self, dist):
        self.surfH += dist
        for each in self.bubbles:
            each[1] += dist

    def level(self, dist):
        pass

# -----------------------------------
class Slime(Monster):  

    def __init__(self, wallGroup, blockSize, onlayer):
        # calculate its position
        Monster.__init__(self, "slime", (0,255,0,240), 28, 4, 1, onlayer, 2, 2)
        self.wallList = []       # 存储本行的所有brick; # 每次初始化一个新实例时，清空此类的wallList（否则会在上一个实例的基础上再加！）
        posList = []             # 辅助列表，用于暂时存储本行brick的位置（左边线）
        for aWall in wallGroup:  # 由于spriteGroup不好进行索引/随机选择操作，因此将其中的sprite逐个存入列表中存储
            self.wallList.append(aWall)
            posList.append(aWall.rect.left)
        wall = choice(self.wallList)
        leftMax = wall.rect.left
        rightMax = wall.rect.right # note：此处砖块的右坐标即下一砖块的左坐标
        while True:
            if leftMax in posList:
                leftMax -= blockSize
            else:
                leftMax += blockSize  # 将多减的加回来
                break
        while True:
            if rightMax in posList:
                rightMax += blockSize
            else:
                break
        self.scope = (leftMax, rightMax)
        # initialize the sprite
        self.imgLeftList = [ pygame.image.load("image/stg4/slime0.png").convert_alpha(), pygame.image.load("image/stg4/slime1.png").convert_alpha(), 
            pygame.image.load("image/stg4/slime2.png").convert_alpha(), pygame.image.load("image/stg4/slime3.png").convert_alpha(), 
            pygame.image.load("image/stg4/slime4.png").convert_alpha(), pygame.image.load("image/stg4/slime5.png").convert_alpha(), 
            pygame.image.load("image/stg4/slime6.png").convert_alpha() ]
        self.imgRightList = [ pygame.transform.flip(self.imgLeftList[0], True, False), pygame.transform.flip(self.imgLeftList[1], True, False), 
            pygame.transform.flip(self.imgLeftList[2], True, False), pygame.transform.flip(self.imgLeftList[3], True, False), 
            pygame.transform.flip(self.imgLeftList[4], True, False), pygame.transform.flip(self.imgLeftList[5], True, False),
            pygame.transform.flip(self.imgLeftList[6], True, False) ]

        self.imgIndx = 0
        self.attIndx = 0
        self.image = self.imgLeftList[0]
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.left = wall.rect.left
        self.rect.bottom = wall.rect.top
        self.damage = 6
        self.coolDown = 0          
        self.alterSpeed( choice( [-1, 1] ) )
        self.rise = ( 0, -8, -16, -20, -16, -8, 0 )
        self.newSlime = None

    def move(self, delay, sprites):
        self.checkHitBack()
        self.rect.left += self.speed
        if (getPos(self,0.75,0)[0] >= self.scope[1] and self.speed > 0) or (getPos(self,0.25,0)[0] <= self.scope[0] and self.speed < 0):
            self.alterSpeed(-self.speed)
        if not (delay % 6 ):
            trPos = [ self.rect.left + self.rect.width//2, self.rect.bottom-self.rise[self.imgIndx] ]  # 为保证图片位置正确，临时存储之前的位置信息
            self.imgIndx = (self.imgIndx+1) % len(self.imgLeftList)
            self.image = self.imgLeftList[self.imgIndx] if ( self.speed<0 ) else self.imgRightList[self.imgIndx]
            self.mask = pygame.mask.from_surface(self.image)
            self.rect = self.image.get_rect()
            self.rect.left = trPos[0]-self.rect.width//2
            self.rect.bottom = trPos[1] + self.rise[self.imgIndx]
        if ( self.coolDown==0 ):
            for each in sprites:
                if pygame.sprite.collide_mask(self, each):
                    self.coolDown = 30
        if (self.coolDown > 0):
            self.coolDown -= 1
            if ( self.coolDown == 20 ):
                cldList( self, sprites )
        # If there is a newly generated slime, return it.
        if (self.newSlime):
            newS = self.newSlime
            self.newSlime = None
            return newS
        
    def hitted(self, damage, pushed):
        if pushed>0:   # 向右击退
            self.hitBack = max( pushed-self.weight, 0 )
        elif pushed<0: # 向左击退
            self.hitBack = min( pushed+self.weight, 0 )
        self.health -= damage
        if self.health <= 0:   # dead
            self.health = 0
            self.erase()
            return True
        else:                  # hitted but alive, check whether split another slime.
            if ( pushed>0 and self.speed<0 ) or ( pushed<0 and self.speed>0 ):
                slime = Slime( self.wallList, 1, self.onlayer )  # 前两项参数都是不需要的，但为了完整执行init函数，第一项参数传入，第二项设为1.
                # Set the properties of the generated slime.
                slime.scope = self.scope
                slime.speed = -self.speed     # 速度相反
                slime.imgIndx = self.imgIndx  # 图像相同
                slime.image = slime.imgLeftList[0] if ( slime.speed<0 ) else slime.imgRightList[slime.imgIndx]
                slime.rect = slime.image.get_rect()
                slime.rect.left = getPos(self, 0.5, 0.5)[0] - slime.rect.width//2
                slime.rect.bottom = self.rect.bottom  # 位置相同
                self.newSlime = slime         # 挂到本对象的newSlime变量上，等待下一次刷新调用move的时候上报给model。

    def level(self, dist):
        self.rect.left += dist
        self.scope = (self.scope[0]+dist, self.scope[1]+dist)
# -----------------------------------
class Fly(Monster):  

    def __init__(self, XRange, y, onlayer):
        # initialize the sprite
        Monster.__init__(self, "fly", (0,255,10,240), 38, 6, 1, onlayer, 4, 3)
        self.imgLeftList = [ pygame.image.load("image/stg4/flyLeft0.png").convert_alpha(), pygame.image.load("image/stg4/flyLeft1.png").convert_alpha(), \
            pygame.image.load("image/stg4/flyLeft0.png").convert_alpha(), pygame.image.load("image/stg4/flyLeft2.png").convert_alpha() ]
        self.imgRightList = [ pygame.transform.flip(self.imgLeftList[0], True, False), pygame.transform.flip(self.imgLeftList[1], True, False), \
            pygame.transform.flip(self.imgLeftList[2], True, False), pygame.transform.flip(self.imgLeftList[3], True, False) ]
        self.attLeftImg = pygame.image.load("image/stg4/flyAtt.png").convert_alpha()
        self.attRightImg = pygame.transform.flip(self.attLeftImg, True, False)
        self.imgIndx = 0
        self.image = self.imgLeftList[0]
        self.mask = pygame.mask.from_surface(self.image)
        # calculate its position
        self.rect = self.image.get_rect()
        self.leftBd = XRange[0]
        self.rightBd = XRange[1]
        self.rect.left = randint( XRange[0], XRange[1] )
        self.rect.top = y

        self.damage = 5.5
        self.alterSpeed(-1)
        self.cnt = 0       # count for the loop of shift position
        self.coolDown = 0    # count for attack coolDown
        self.nxt = [0, 0]
        self.snd = pygame.mixer.Sound("audio/flapper.wav")

    def move(self, delay, sprites):
        self.checkHitBack()
        if not (delay % 4 ):
            self.imgIndx = (self.imgIndx+1) % len(self.imgLeftList)
            self.image = self.imgLeftList[self.imgIndx] if ( self.direction=="left" ) else self.imgRightList[self.imgIndx]
        # find new position
        if self.cnt == 0:
            self.cnt = 60
            self.nxt = [ randint(self.leftBd, self.rightBd), randint(20, 580) ]  # randomize a new position
            self.direction = "left" if ( self.nxt[0] < self.rect.left + self.rect.width/2 ) else "right"
        # charging motion
        if not (delay % 3):
            self.shift( self.nxt[0], self.nxt[1] )
            self.cnt -= 1
            if random()<0.02:
                self.snd.play(0)
        if (self.coolDown == 0):
            for each in sprites:
                if pygame.sprite.collide_mask(self, each):
                    self.coolDown = 42
        elif self.coolDown > 0:
            self.coolDown -= 1
            if self.coolDown >= 32:
                if self.direction=="left":
                    self.image = self.attLeftImg
                    self.push = self.pushList[0]
                else:
                    self.image = self.attRightImg
                    self.push = self.pushList[1]
                if self.coolDown == 34:
                    cldList( self, sprites )

    def shift(self, final_x, final_y):
        maxSpan = 8
        spd = 4
        dist = 0
        x = self.rect.left + self.rect.width/2
        y = self.rect.top + self.rect.height/2
        if (x == final_x) or (y == final_y):
            return True
        if (x < final_x):
            dist = math.ceil( (final_x - x)/spd )
            if dist > maxSpan:
                dist = maxSpan
            self.rect.left += dist
        elif (x > final_x):
            dist = math.ceil( (x - final_x)/spd )
            if dist > maxSpan:
                dist = maxSpan
            self.rect.left -= dist
        if (y < final_y):
            dist = math.ceil( (final_y - y)/spd )
            if dist > maxSpan:
                dist = maxSpan
            self.rect.top += dist
        elif (y > final_y):
            dist = math.ceil( (y - final_y)/spd )
            if dist > maxSpan:
                dist = maxSpan
            self.rect.top -= dist
    
    def erase(self):
        self.snd.stop()
        self.kill()
        del self

    def level(self, dist):
        self.rect.left += dist
        self.nxt[0] += dist
        self.leftBd += dist
        self.rightBd += dist
        
# -----------------------------------
class Nest(Monster):

    def __init__(self, wallGroup, onlayer):
        # calculate its position
        Monster.__init__(self, "nest", (255,255,80,240), 55, 0, 0, onlayer, 3, 2)
        self.wallList = []       # 存储本行的所有砖块; # 每次初始化一个新实例时，清空此类的wallList（否则会在上一个实例的基础上再加！）
        posList = []             # 辅助列表，用于暂时存储本行砖块的位置（左边线）
        for aWall in wallGroup:  # 由于spriteGroup不好进行索引/随机选择操作，因此将其中的sprite逐个存入列表中存储
            self.wallList.append(aWall)
            posList.append(aWall.rect.left)
        wall = choice(self.wallList)
        # initialize the sprite
        self.imgList = [ pygame.image.load("image/stg4/nest0.png").convert_alpha(), pygame.image.load("image/stg4/nest1.png").convert_alpha() ]
        self.attLList = [  ]
        self.imgIndx = 0
        self.image = self.imgList[0]
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.left = wall.rect.left
        self.rect.top = wall.rect.bottom - 4  # link more tight with the block (block bottom is not even)

    def move(self, delay, allElem, mons):
        if self.health > 0:
            if not (delay % 24 ):
                self.imgIndx = (self.imgIndx+1) % len(self.imgList)
                self.image = self.imgList[self.imgIndx]
                if random() < 0.1:
                    worm = Worm( self.rect.left+self.rect.width//2, self.rect.bottom, self.onlayer )
                    allElem.add( worm )
                    mons.add( worm )
        else:
            pos1 = getPos(self, 0.3, 0.3)
            worm1 = Worm( pos1[0], pos1[1], self.onlayer )
            pos2 = getPos(self, 0.5, 0.6)
            worm2 = Worm( pos2[0], pos2[1], self.onlayer )
            pos3 = getPos(self, 0.7, 0.3)
            worm3 = Worm( pos3[0], pos3[1], self.onlayer )
            self.erase()
            return ( worm1, worm2, worm3 )

    def hitted(self, damage, pushed):
        self.health -= damage
        if self.health <= 0:
            self.health = 0
            return True
    
    def level(self, dist):
        self.rect.left += dist

class Worm(Monster):  

    def __init__(self, x, y, onlayer):   
        Monster.__init__(self, "worm", (255,255,10,240), 5, 1, 0, onlayer-2, 1, 1)# 由于掉落下来一定要减一层，所以传入onlayer-2。
        # initialize the sprite
        self.imgLeftList = [ pygame.image.load("image/stg4/worm0.png").convert_alpha(), pygame.image.load("image/stg4/worm1.png").convert_alpha(), \
            pygame.image.load("image/stg4/worm2.png").convert_alpha(), pygame.image.load("image/stg4/worm3.png").convert_alpha(), pygame.image.load("image/stg4/worm4.png").convert_alpha() ]
        self.imgRightList = [ pygame.transform.flip(self.imgLeftList[0], True, False), pygame.transform.flip(self.imgLeftList[1], True, False), \
            pygame.transform.flip(self.imgLeftList[2], True, False), pygame.transform.flip(self.imgLeftList[3], True, False), pygame.transform.flip(self.imgLeftList[4], True, False) ]
        self.imgIndx = 0
        self.attIndx = 0
        self.image = self.imgLeftList[0]
        self.mask = pygame.mask.from_surface( self.image )
        self.rect = self.image.get_rect()
        self.rect.left = x-self.rect.width//2
        self.rect.top = y
        self.damage = 4.5
        if random()<= 0.5:   # 随即决定向左或向右
            self.alterSpeed(-1)
        else:
            self.alterSpeed(1)
        self.aground = False
        self.doom = 0
        self.lifeSpan = 300

    def move(self, delay, lineWall, keyLine, sideWall, sprites):
        self.checkHitBack()
        # 无论health和lifespan是否有，都要检查下落
        self.fall(lineWall, keyLine)
        # 若健康的话，检查与英雄的碰撞
        if (self.health>0) and (self.lifeSpan > 0):
            self.lifeSpan -= 1
            # 如果着地，则可进行水平运动
            if self.aground and not (delay % 5):
                self.rect.left += self.speed
                self.imgIndx = (self.imgIndx+1) % len(self.imgLeftList)
                self.image = self.imgLeftList[self.imgIndx] if ( self.speed<0 ) else self.imgRightList[self.imgIndx]
                if ( pygame.sprite.spritecollide(self, sideWall, False, pygame.sprite.collide_mask) ):
                    self.alterSpeed(-self.speed)
            for each in sprites:
                if ( pygame.sprite.collide_mask(self, each) ):
                    self.health = 0
        else:
            self.doom += 1
            if self.doom == 19:
                self.erase()
            elif self.doom >= 13:
                self.image = pygame.image.load("image/stg4/boom2.png")
            elif self.doom >= 7:
                self.image = pygame.image.load("image/stg4/boom1.png") # 检查溅射到英雄，造成伤害
                if self.doom == 7:
                    cldList( self, sprites )
            elif self.doom >= 1:
                self.image = pygame.image.load("image/stg4/boom0.png")

    def fall(self, lineWall, keyLine):
        self.rect.bottom += 5
        while ( pygame.sprite.spritecollide(self, lineWall, False, pygame.sprite.collide_mask) ):      # 如果和参数中的物体重合，则尝试纵坐标-1
            self.rect.bottom -= 1
            if not ( pygame.sprite.spritecollide(self, lineWall, False, pygame.sprite.collide_mask) ): # 循环-1，直到不再和任何物体重合为止，进入这个if语句跳出循环
                self.aground = True
        if self.rect.top >= keyLine:
            self.onlayer -= 2
            if self.onlayer<-1:
                self.erase()
        
    def hitted(self, damage, pushed):
        self.health -= damage
        if self.health <= 0:
            self.health = 0
            return True    # dead

    def level(self, dist):
        self.rect.left += dist

# -----------------------------------
class Python(Monster):
    
    # 构造方式：本体为head，其余部分均用Ajunction实现。
    # onlayer是该python所在的行高；xLine是Python缠绕状态下head的竖直方向中点；boundaries是左右sideWall的内侧边界，用于确定当python head抵达时转换为twine状态。
    def __init__(self, onlayer, xLine, boundaries, blockSize):
        # initialize the sprite
        Monster.__init__(self, "Python", (10, 30, 10, 240), 100, 0, 0, onlayer, 40, 20)
        self.onlayer = int(onlayer)
        self.xLine = xLine
        self.boundaries = boundaries
        #self.coolDown = 0           
        #self.speed = 4                # attacking时的横向速度绝对值
        self.status = "await"         # status可取三种情况：await（初始）, twine, attack。初始情况下默认为left，方向决定了位置
        # ----- head part (the core of the Python) ------
        self.imgLeft = [ pygame.image.load("image/stg4/twine0.png").convert_alpha(), pygame.image.load("image/stg4/twine1.png").convert_alpha(),
            pygame.image.load("image/stg4/twine2.png").convert_alpha(), pygame.image.load("image/stg4/twine3.png").convert_alpha(),
            pygame.image.load("image/stg4/twine4.png").convert_alpha() ]
        self.imgRight = [ pygame.transform.flip(self.imgLeft[0], True, False), pygame.transform.flip(self.imgLeft[1], True, False),
            pygame.transform.flip(self.imgLeft[2], True, False), pygame.transform.flip(self.imgLeft[3], True, False),
            pygame.transform.flip(self.imgLeft[4], True, False) ]
        self.imgR = { "left":[ () ] }
        #self.headLeftList = [ pygame.image.load("image/stg6/WarMachine0.png").convert_alpha(), pygame.image.load("image/stg6/WarMachine1.png").convert_alpha() ]
        #self.headRightList = [ pygame.transform.flip(self.bodyLeftList[0], True, False), pygame.transform.flip(self.bodyLeftList[1], True, False) ]
        self.imgIndx = 0
        self.image = self.imgLeft[0]
        #self.image = self.headLeftList[0]
        self.mask = pygame.mask.from_surface(self.image)
        # calculate its position
        self.rect = self.image.get_rect()
        self.rect.left = self.boundaries[1]-self.rect.width  # 位于右侧边界向左
        self.rect.bottom = self.xLine+self.rect.height//2
        # ------------- segment part --------------
        #self.segLeft = [ pygame.image.load("image/stg6/arm.png").convert_alpha(), pygame.image.load("image/stg6/armFire.png").convert_alpha() ]
        #self.segRight = [ pygame.transform.flip(self.armLeft[0], True, False), pygame.transform.flip(self.armLeft[1], True, False) ]
        #self.segR = { "left":[ (0.5,0.4), (0.5,0.4) ], "right":[ (0.5,0.4), (0.5,0.4) ] }     # 分别为左和右时的位置信息
        #self.segment = Ajunction( self.armLeft[0], getPos(self, self.armR[self.status][0][0], self.armR[self.status][0][1]) )
        #self.segIndx = 0
        # ------------- tail part ----------------
        #self.tailLeft = [ pygame.image.load("image/stg6/packet.png").convert_alpha(), pygame.image.load("image/stg6/packetBroken.png").convert_alpha() ]
        #self.tailRight = [ pygame.transform.flip(self.pktLeft[0], True, False), pygame.transform.flip(self.pktLeft[1], True, False) ]
        #self.tailR = { "left":[ (0.75,0.4), (0.75,0.4) ], "right":[ (0.25,0.4), (0.25,0.4) ] }
        #self.tail = Ajunction( self.pktLeft[0], getPos(self, self.pktR[self.status][0][0], self.pktR[self.status][0][1]) )
        #self.tailIndx = 0
        # ----------- other attributes -------------------------
        self.cnt = 0         # count for the loop of shift position
        self.coolDown = 0    # count for attack coolDown
        #self.fireSnd = pygame.mixer.Sound("audio/MachineGrenade.wav")
        #self.moanSnd = pygame.mixer.Sound("audio/MachineCollapse.wav")
        #self.sparkySnd = pygame.mixer.Sound("audio/sparky.wav")
        self.fireList = pygame.sprite.Group()
        #self.jetting = False
        #self.jetImg = [ pygame.image.load("image/stg6/jet0.png").convert_alpha(), pygame.image.load("image/stg6/jet1.png").convert_alpha() ]
        #self.jetIndx = 0
        # 生成一个自管理的透明画布
        self.canvas, self.canvasRect = createCanvas( (800, 620), (0,0,0) )
        #self.sparkyCnt = 0
        self.chargeList = []   # 用于存放attack时与地面摩擦扬起的灰尘信息

    def move(self, delay):
        self.checkHitBack()    
        if not ( delay % 8 ):
            self.imgIndx = (self.imgIndx + 1) % len(self.imgLeft)
            self.image = self.imgLeft[self.imgIndx]
            #    if not delay%6:
            #        self.imgIndx = (self.imgIndx+1) % len(self.bodyLeftList) #自由移动，主体图像变动
            # 更新各组件的图像
            '''if self.status == "left":
                self.image = self.bodyLeftList[self.imgIndx]
                self.mask = pygame.mask.from_surface(self.image)
                self.packet.updateImg( self.pktLeft[self.pktIndx] )
                self.arm.updateImg( self.armLeft[self.armIndx] )
            elif self.status == "right":
                self.image = self.bodyRightList[self.imgIndx]
                self.mask = pygame.mask.from_surface(self.image)
                self.packet.updateImg( self.pktRight[self.pktIndx] )
                self.arm.updateImg( self.armRight[self.armIndx] )'''
        # 不管是什么时候，都应该及时更新ajunction的位置（还会有英雄击退）
        #self.packet.updatePos( getPos(self, self.pktR[self.status][self.pktIndx][0], self.pktR[self.status][self.pktIndx][1]) )
        #self.arm.updatePos( getPos(self, self.armR[self.status][self.armIndx][0], self.armR[self.status][self.armIndx][1]) )    

# ==========================================================================
# ---------------------------------- stage5 --------------------------------
# ==========================================================================
class blizzardGenerator():

    def __init__(self, bg_size):
        self.cntDown = 1600
        self.bg_size = bg_size
    
    def storm(self, sprites, wind, spurtCanvas):
        self.cntDown -= 1
        if self.cntDown <= 60:
            i = 0
            while i<4:
                r = choice( [6,8,10,12] )
                if wind>0:  # 向右
                    posX = randint(-180, self.bg_size[0]-120)
                    speed = (2,7)
                else:
                    posX = randint(120, self.bg_size[0]+180)
                    speed = (-2,7)
                posY = randint(-self.bg_size[1],0)
                flake = Flake(r, [posX, posY], speed, (250,250,250,250), self.bg_size)
                spurtCanvas.spatters.add(flake)
                i += 1
            
            if self.cntDown <= 0:
                for each in sprites:
                    each.freeze(2)
                self.cntDown = choice( range(1500, 2000, 50) )

class Flake(pygame.sprite.Sprite):
    def __init__(self, radius, startPos, speed, color, range):  # 参数：雪花的半径；雪花的起始位置
        pygame.sprite.Sprite.__init__(self)
        self.r = radius
        self.speed = speed
        self.pos = startPos
        self.color = color
        self.range = range

    def move(self):
        if (self.pos[1] < self.range[1]) and (0 < self.pos[0] < self.range[0]):  # 尚在屏幕内，继续下落
            self.pos[1] += self.speed[1]
            self.pos[0] += self.speed[0]
        else:
            self.kill()
            del self
            return True

# ----------------------------
class Wolf(Monster):  

    scopeList = []
    jumping = False

    def __init__(self, wallGroup, blockSize, onlayer):
        # calculate its position
        Monster.__init__(self, "wolf", (255,0,0,240), 32, 8, 1, onlayer, 3, 2)
        self.wallList = []       # 存储本行的所有砖块; # 每次初始化一个新实例时，清空此类的wallList（否则会在上一个实例的基础上再加！）
        posList = []             # 辅助列表，用于暂时存储本行砖块的位置（左边线）
        for aWall in wallGroup:  # 由于spriteGroup不好进行索引/随机选择操作，因此将其中的sprite逐个存入列表中存储
            self.wallList.append(aWall)
            posList.append(aWall.rect.left)
        wall = choice(self.wallList)
        leftMax = wall.rect.left
        rightMax = wall.rect.right       # note：此处砖块的右坐标即下一砖块的左坐标
        tList1 = [ [leftMax,rightMax] ]
        tList2 = [ [leftMax,rightMax] ]
        i1 = 0       # 辅助变量，用于在循环过程中指示当前正在处理列表中的哪一项scope。每当新加一个scope项时，i应+1
        while True:
            if (leftMax-blockSize) in posList:
                leftMax -= blockSize
                tList1[i1][0] = leftMax
            elif (leftMax-2*blockSize) in posList:
                leftMax -= 2*blockSize
                tList1.append( [leftMax,leftMax+blockSize] )
                i1 += 1
            else:
                break
        i2 = 0
        while True:
            if rightMax in posList:
                rightMax += blockSize
                tList2[i2][1] = rightMax
            elif (rightMax+blockSize) in posList:
                rightMax += 2*blockSize
                tList2.append( [rightMax-blockSize,rightMax] )
                i2 += 1
            else:
                break
        tList = tList1+tList2
        self.scopeList = []
        for item in tList:
            if item not in self.scopeList:
                self.scopeList.append(item)
        #另一种去除重复元素的方法是：先转换为集合set（），再转换回列表list（set（））。但由于列表元素（每个item都是list）是不可哈希的，因此不能转换为集合，这里不适合此方法。
        self.scope = (leftMax, rightMax)
        # initialize the sprite
        self.imgLeftList = [ pygame.image.load("image/stg5/wolf0.png").convert_alpha(), pygame.image.load("image/stg5/wolf1.png").convert_alpha(), \
            pygame.image.load("image/stg5/wolf2.png").convert_alpha(), pygame.image.load("image/stg5/wolf3.png").convert_alpha(), \
            pygame.image.load("image/stg5/wolf4.png").convert_alpha(), pygame.image.load("image/stg5/wolf5.png").convert_alpha() ]
        self.imgRightList = [ pygame.transform.flip(self.imgLeftList[0], True, False), pygame.transform.flip(self.imgLeftList[1], True, False), \
            pygame.transform.flip(self.imgLeftList[2], True, False), pygame.transform.flip(self.imgLeftList[3], True, False), \
            pygame.transform.flip(self.imgLeftList[4], True, False), pygame.transform.flip(self.imgLeftList[5], True, False) ]

        self.imgIndx = 0
        self.attIndx = 0
        self.image = self.imgLeftList[0]
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.left = wall.rect.left+wall.rect.width//2-self.rect.width//2
        self.rect.bottom = wall.rect.top
        self.damage = 8.5
        self.coolDown = 0
        self.snd = pygame.mixer.Sound("audio/wolf.wav")
        self.alterSpeed( choice( [-2, 0, 2] ) )
        self.status = "wandering"          # wandering表示闲逛的状态，alarming表示发现英雄的状态
        self.tgt = None                    # 指示要攻击的英雄

    # 这个move()函数是供外界调动的接口，这里仅起根据传入的英雄参数判断状态的作用。判断完成后，修改自身的状态，然后执行相应的函数。
    def move(self, delay, sprites):
        for hero in sprites:
            # 如果有英雄在同一层，则将速度改为朝英雄方向。(这里的两套体系，英雄的层数为偶数，而怪物用的层数都是奇数)
            if (hero.onlayer-1)==self.onlayer and ( self.scope[0]<=getPos(hero,1,0.5)[0] ) and ( getPos(hero,0,0.5)[0]<=self.scope[1] ):
                self.status = "alarming"
                self.tgt = hero
                break      # ***这里碰到第一个英雄符合条件就退出了。因此，如果两个英雄同时在一层中，P1总是会被针对，而P2永远不会被选中为目标。问题留着以后修正。
            else:
                self.status = "wandering"
        if self.status == "wandering":
            self.wander( delay )
        elif self.status == "alarming":
            self.attack( sprites )
        self.checkImg(delay)
        self.checkHitBack()

    def checkImg(self, delay):
        trPos = [ self.rect.left + self.rect.width//2, self.rect.bottom ]
        # renew the image of the wolf
        if self.speed and not (delay % 5 ):
            self.imgIndx = (self.imgIndx+1) % len(self.imgLeftList)
            self.image = self.imgLeftList[self.imgIndx] if ( self.speed<0 ) else self.imgRightList[self.imgIndx]
        elif self.speed == 0:
            self.imgIndx = 0
            self.image = self.imgLeftList[self.imgIndx]# if ( random()<0.5 ) else self.imgRightList[self.imgIndx]
        notIn = 0
        for scope in self.scopeList:
            if (getPos(self,0.3,1)[0] >= scope[0]) and (getPos(self,0.7,1)[0] <= scope[1]):
                self.jumping = False
                break
            else:
                notIn += 1
        if notIn >= len(self.scopeList):        # 本狼不在任何一个合理的scope内，因此判定是在空中
            self.jumping = True
            self.imgIndx = 3
            self.image = self.imgLeftList[self.imgIndx] if ( self.speed<0 ) else self.imgRightList[self.imgIndx]
        self.rect = self.image.get_rect()
        self.rect.left = trPos[0]-self.rect.width//2
        self.rect.bottom = trPos[1]

    def wander(self, delay):
        if (self.speed):                        # speed!=0，在运动。
            if not self.jumping:
                self.rect.left += self.speed
            else:
                self.rect.left += self.speed*1.5
            if (getPos(self, 0.7, 1)[0] >= self.scope[1] and self.speed > 0) or (getPos(self, 0.3, 1)[0] <= self.scope[0] and self.speed < 0):
                self.alterSpeed(-self.speed)
            if not self.jumping and not delay % 20 and random()<0.08:
                self.alterSpeed(0)
        elif not delay % 20 and random()<0.08:  # 否则，在休息。此时若随机数满足条件，进入奔跑状态
            self.alterSpeed( choice( [2,-2] ) )
    
    def attack(self, sprites):
        if getPos( self.tgt, 1, 0 )[0]<getPos( self, 0, 0 )[0]:
            self.alterSpeed(-2)
        elif getPos( self.tgt, 0, 0 )[0]>getPos( self, 1, 0 )[0]:
            self.alterSpeed(2)
        if not self.jumping:
            self.rect.left += self.speed * 1.5
        else:
            self.rect.left += self.speed * 2
        if ( self.coolDown==0 ):
            for each in sprites:
                if pygame.sprite.collide_mask(self, each):
                    self.snd.play(0)           # 撞到英雄，咆哮
                    self.coolDown = 48
        else:
            self.coolDown -= 1
            if ( self.coolDown == 42 ):
                cldList( self, sprites )

    def level(self, dist):
        self.rect.left += dist
        self.scope = (self.scope[0]+dist, self.scope[1]+dist)
        for scp in self.scopeList:
            scp[0] += dist
            scp[1] += dist

# -----------------------------
class IceTroll(Monster):

    def __init__(self, wallGroup, blockSize, onlayer):
        # calculate its position
        Monster.__init__(self, "iceTroll", (255,0,0,240), 38, 0, 2, onlayer, 3, 2)
        self.wallList = []       # 存储本行的所有砖块; # 每次初始化一个新实例时，清空此类的wallList（否则会在上一个实例的基础上再加！）
        posList = []             # 辅助列表，用于暂时存储本行砖块的位置（左边线）
        for aWall in wallGroup:  # 由于spriteGroup不好进行索引/随机选择操作，因此将其中的sprite逐个存入列表中存储
            self.wallList.append(aWall)
            posList.append(aWall.rect.left)
        wall = choice(self.wallList)
        leftMax = wall.rect.left
        rightMax = wall.rect.right # note：此处砖块的右坐标即下一砖块的左坐标
        while True:
            if leftMax in posList:
                leftMax -= blockSize
            else:
                leftMax += blockSize  # 将多减的加回来
                break
        while True:
            if rightMax in posList:
                rightMax += blockSize
            else:
                break
        self.scope = (leftMax, rightMax)
        # initialize the sprite
        self.imgLeftList = [ pygame.image.load("image/stg5/iceTroll0.png").convert_alpha(), pygame.image.load("image/stg5/iceTroll1.png").convert_alpha(), \
            pygame.image.load("image/stg5/iceTroll2.png").convert_alpha(), pygame.image.load("image/stg5/iceTroll1.png").convert_alpha(), \
            pygame.image.load("image/stg5/iceTroll0.png").convert_alpha(), pygame.image.load("image/stg5/iceTroll3.png").convert_alpha(), \
            pygame.image.load("image/stg5/iceTroll4.png").convert_alpha(), pygame.image.load("image/stg5/iceTroll3.png").convert_alpha() ]
        self.imgRightList = [ pygame.transform.flip(self.imgLeftList[0], True, False), pygame.transform.flip(self.imgLeftList[1], True, False), \
            pygame.transform.flip(self.imgLeftList[2], True, False), pygame.transform.flip(self.imgLeftList[3], True, False), \
            pygame.transform.flip(self.imgLeftList[4], True, False), pygame.transform.flip(self.imgLeftList[5], True, False), \
            pygame.transform.flip(self.imgLeftList[6], True, False), pygame.transform.flip(self.imgLeftList[7], True, False) ]

        self.attLeft = pygame.image.load("image/stg5/iceTrollAtt.png").convert_alpha()
        self.attRight = pygame.transform.flip(self.attLeft, True, False)
        self.alarmLeft = pygame.image.load("image/stg5/alarmLeft.png").convert_alpha()
        self.alarmRight = pygame.transform.flip(self.alarmLeft, True, False)

        self.imgIndx = 0
        self.attIndx = 0
        self.image = self.imgLeftList[0]
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.left = wall.rect.left
        self.rect.bottom = wall.rect.top
        self.coolDown = 0
        if self.rect.left > leftMax:
            self.alterSpeed(-1)          
        elif self.rect.right < rightMax:
            self.alterSpeed(1)
        else:
            self.alterSpeed(0)
        
        self.snd = pygame.mixer.Sound("audio/iceTroll.wav")
        self.airCnt = 0           # indicate if I'm spitting!

    def move(self, delay, sprites, spatters):
        self.checkHitBack()
        if (self.airCnt==0):
            if self.speed:
                if not (delay % 2):
                    self.rect.left += self.speed
                    if (self.rect.right >= self.scope[1] and self.speed > 0) or (self.rect.left <= self.scope[0] and self.speed < 0):
                        self.alterSpeed(-self.speed)
                if not (delay % 10):
                    self.image = self.imgLeftList[self.imgIndx] if self.speed < 0 else self.imgRightList[self.imgIndx]
                    self.mask = pygame.mask.from_surface(self.image)   # 更新rect，使得与hero重合的判断更加精确
                    self.imgIndx = (self.imgIndx+1) % len(self.imgLeftList)
            else:
                if not (delay % 10):
                    self.image = self.imgLeftList[0]
            if random()<0.02 :           # 开喷
                self.airCnt = 72
                self.snd.play(0)
        elif (self.airCnt > 0):
            self.airCnt -= 1
            if self.airCnt > 54:
                self.image = self.alarmLeft if (self.speed<=0) else self.alarmRight
            else:
                self.image = self.attLeft if (self.speed<=0) else self.attRight
                for i in range(0, 3, 1): # 每次刷新均吐出3个气团
                    if self.speed <= 0:
                        spd = [ choice([-3, -2, -1]), choice([-3, -2, -1, 0, 1, 2, 3]) ]
                        startX = 0.32
                    elif self.speed > 0:
                        spd = [ choice([1, 2, 3]), choice([-3, -2, -1, 0, 1, 2, 3]) ]
                        startX = 0.68
                    atom = AirAtom( getPos(self, startX, 0.32), spd, sprites )
                    spatters.add( atom )

    def level(self, dist):
        self.rect.left += dist
        self.scope = (self.scope[0]+dist, self.scope[1]+dist)

class AirAtom(pygame.sprite.Sprite):

    def __init__(self, pos, spd, sprites): # 参数color:推荐带上透明度RGBA；参数speed:为一个二元组
        pygame.sprite.Sprite.__init__(self)
        self.r = choice( [1, 3, 5] )
        self.color = choice( [(120,120,160,255),(200,200,240,255),(160,160,200,255)] )
        self.initPos = [ randint(pos[0]-1, pos[0]+1), randint(pos[1]-1, pos[1]+1) ]
        self.pos = self.initPos
        self.speed = spd
        if self.speed[0]>0:
            self.push = 3
        else:
            self.push = -3
        self.cnt = choice( [32, 40, 48] )
        self.tgts = sprites
    
    def move(self):
        if self.cnt > 0:
            self.pos[0] += self.speed[0]
            self.pos[1] += self.speed[1]
            self.cnt -= 1
            if random()<0.5:
                self.speed[1] = - self.speed[1]
        else:
            self.kill()
            del self
            return True
        for hero in self.tgts:
            if hero.rect.left < self.pos[0] < hero.rect.right and hero.rect.top < self.pos[1] < hero.rect.bottom:
                hero.hitted( 0.01, self.push )
                hero.freeze(1)        # 速度-1

# -----------------------------------
class FrostTitan(Monster):

    def __init__(self, x, y, onlayer):
        # initialize the sprite
        Monster.__init__(self, "FrostTitan", (255, 0, 0, 240), 200, 1, 8, onlayer, 40, 20)
        # ----- body part (the core of the FrostTitan) ------
        self.bodyLeft = pygame.image.load("image/stg5/FrostTitan.png").convert_alpha()
        self.bodyRight = pygame.transform.flip(self.bodyLeft, True, False)
        self.imgIndx = 0
        self.image = self.bodyLeft
        self.mask = pygame.mask.from_surface(self.image)
        self.status = "await"
        # calculate its position
        self.rect = self.image.get_rect()
        self.rect.left = x
        self.rect.top = y
        self.alterSpeed(-2)
        # ------------- arm part --------------
        self.headLeft = [ pygame.image.load("image/stg1/DragonHead0.png").convert_alpha(), pygame.image.load("image/stg1/DragonHead1.png").convert_alpha(), 
            pygame.image.load("image/stg1/DragonHead2.png").convert_alpha() ]
        self.headRight = [ pygame.transform.flip(self.headLeft[0], True, False), pygame.transform.flip(self.headLeft[1], True, False), 
            pygame.transform.flip(self.headLeft[2], True, False) ]
        self.headR = { "left":[ (0,0.6), (0,0.61), (0,0.62) ], "right":[ (1,0.6), (1,0.61), (1,0.62) ] }    # 分别为左和右时的位置信息
        self.head = Ajunction( self.headLeft[2], getPos(self, self.headR[self.direction][0][0], self.headR[self.direction][0][1]) )
        self.headIndx = 0

        self.activated = False

    def move(self, delay, sprites, canvas, bg_size): # 当前此函数只考虑在屏幕右侧进出，不考虑左侧。
        if delay%2:
            if self.status=="await":
                # 倘若尚未就为，则继续移动。
                if self.rect.left >= bg_size[0]-120:
                    self.rect.left += self.speed
                # 就位
                else:
                    if random() <= 0.1:    # 离开视野，暂时休息
                        self.status = "hide"
                        self.alterSpeed(2)
                #do sth when await
                #满足条件 status="hammering"
                #满足条件 status="blizard"
            elif self.status=="hide":
                # 倘若身体尚在屏幕范围内，继续向屏幕外移动
                if self.rect.left<=bg_size[0]:
                    self.rect.left += self.speed
                # 就位
                else:
                    if random() <= 0.4:   # 休息一段时间后进入屏幕
                        self.status = "await"
                        self.alterSpeed(-2)
            elif self.status=="hammering":
                pass
                # do sth when hammering
                # 满足条件 status="await"
            elif self.status=="blizzard":
                pass
                # do sth when blizzard
                # 满足条件 status=="await"

# ==========================================================================
# --------------------------------- stage6 ---------------------------------
# ==========================================================================
class Dwarf(Monster):

    def __init__(self, wallGroup, blockSize, onlayer):
        # calculate its position
        Monster.__init__(self, "dwarf", (255,0,0,240), 28, 5, 1, onlayer, 2, 1)
        self.wallList = []       # 存储本行的所有砖块; # 每次初始化一个新实例时，清空此类的wallList（否则会在上一个实例的基础上再加！）
        posList = []             # 辅助列表，用于暂时存储本行砖块的位置（左边线）
        for aWall in wallGroup:  # 由于spriteGroup不好进行索引/随机选择操作，因此将其中的sprite逐个存入列表中存储
            self.wallList.append(aWall)
            posList.append(aWall.rect.left)
        wall = choice(self.wallList)
        leftMax = wall.rect.left
        rightMax = wall.rect.right # note：此处砖块的右坐标即下一砖块的左坐标
        while True:
            if leftMax in posList:
                leftMax -= blockSize
            else:
                leftMax += blockSize  # 将多减的加回来
                break
        while True:
            if rightMax in posList:
                rightMax += blockSize
            else:
                break
        self.scope = (leftMax, rightMax)
        # initialize the sprite
        self.imgLeftList = [ pygame.image.load("image/stg6/dwarf0.png").convert_alpha(), pygame.image.load("image/stg6/dwarf1.png").convert_alpha(), \
            pygame.image.load("image/stg6/dwarf2.png").convert_alpha(), pygame.image.load("image/stg6/dwarf1.png").convert_alpha() ]
        self.imgRightList = [ pygame.transform.flip(self.imgLeftList[0], True, False), pygame.transform.flip(self.imgLeftList[1], True, False), \
            pygame.transform.flip(self.imgLeftList[2], True, False), pygame.transform.flip(self.imgLeftList[3], True, False) ]

        self.imgIndx = 0
        self.attIndx = 0
        self.image = self.imgLeftList[0]
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.left = wall.rect.left+wall.rect.width//2-self.rect.width//2
        self.rect.bottom = wall.rect.top
        self.damage = 4.5
        self.coolDown = 0
        self.snd = pygame.mixer.Sound("audio/wolf.wav")
        self.alterSpeed( choice( [-1, 0, 1] ) )
        self.status = "wandering"          # wandering表示闲逛的状态，alarming表示发现英雄的状态
        self.tgt = None                    # 指示要攻击的英雄

    # 这个move()函数是供外界调动的接口，这里仅起根据传入的英雄参数判断状态的作用。判断完成后，修改自身的状态，然后执行相应的函数。
    def move(self, delay, sprites):
        for hero in sprites:
            # 如果有英雄在同一层，则将速度改为朝英雄方向。(这里的两套体系，英雄的层数为偶数，而怪物用的层数都是奇数)
            if (hero.onlayer-1)==self.onlayer and ( self.scope[0]<=getPos(hero,1,0.5)[0] ) and ( getPos(hero,0,0.5)[0]<=self.scope[1] ):
                self.status = "alarming"
                self.tgt = hero
                break     # ***这里碰到第一个英雄符合条件就退出了。因此，如果两个英雄同时在一层中，P1总是会被针对，而P2永远不会被选中为目标。问题留着以后修正。
            else:
                self.status = "wandering"
        if self.status == "wandering":
            self.wander( delay )
        elif self.status == "alarming":
            self.speed = 1 if getPos( self.tgt, 0.5, 0.5 )[0]>getPos( self, 0.5, 0.5 )[0] else -1
            self.attack( sprites )
        self.checkImg(delay)
        self.checkHitBack()

    def checkImg(self, delay):
        trPos = [ self.rect.left + self.rect.width//2, self.rect.bottom ]
        # renew the image
        if self.speed and not (delay % 8 ):
            self.imgIndx = (self.imgIndx+1) % len(self.imgLeftList)
            self.image = self.imgLeftList[self.imgIndx] if ( self.speed<0 ) else self.imgRightList[self.imgIndx]
        elif self.speed == 0:
            self.imgIndx = 0
            self.image = self.imgLeftList[self.imgIndx]# if ( random()<0.5 ) else self.imgRightList[self.imgIndx]
        self.rect = self.image.get_rect()
        self.rect.left = trPos[0]-self.rect.width//2
        self.rect.bottom = trPos[1]

    def wander(self, delay):
        if (self.speed):                        # speed!=0，在运动。
            self.rect.left += self.speed
            if (getPos(self, 0.7, 1)[0] >= self.scope[1] and self.speed > 0) or (getPos(self, 0.3, 1)[0] <= self.scope[0] and self.speed < 0):
                self.alterSpeed( -self.speed )
            if not delay % 20 and random()<0.08:
                self.alterSpeed(0)
        elif not delay % 20 and random()<0.08:  # 否则，在休息。此时若随机数满足条件，进入奔跑状态
            self.alterSpeed( choice( [1,-1] ) )
    
    def attack(self, sprites):
        self.rect.left += self.speed * 2
        if ( self.coolDown<=0 ):
            for each in sprites:
                if pygame.sprite.collide_mask(self, each):
                    self.snd.play(0)    # 撞到英雄，咆哮
                    self.coolDown = 48
        else:
            self.coolDown -= 1
            if ( self.coolDown == 38 ):
                cldList( self, sprites )

    def level(self, dist):
        self.rect.left += dist
        self.scope = (self.scope[0]+dist, self.scope[1]+dist)

# ------------------------------------
class Gunner(Monster):

    def __init__(self, wallGroup, blockSize, onlayer, boundaries):
        # calculate its position
        Monster.__init__(self, "gunner", (20,20,20,240), 50, 0, 2, onlayer, 4, 3)
        self.wallList = []       # 存储本行的所有砖块; # 每次初始化一个新实例时，清空此类的wallList（否则会在上一个实例的基础上再加！）
        posList = []             # 辅助列表，用于暂时存储本行砖块的位置（左边线）
        for aWall in wallGroup:  # 由于spriteGroup不好进行索引/随机选择操作，因此将其中的sprite逐个存入列表中存储
            self.wallList.append(aWall)
            posList.append(aWall.rect.left)
        wall = choice(self.wallList)
        leftMax = wall.rect.left
        rightMax = wall.rect.right # note：此处砖块的右坐标即下一砖块的左坐标
        while True:
            if leftMax in posList:
                leftMax -= blockSize
            else:
                leftMax += blockSize  # 将多减的加回来
                break
        while True:
            if rightMax in posList:
                rightMax += blockSize
            else:
                break
        self.scope = (leftMax, rightMax)
        self.boundaries = boundaries
        # initialize the sprite
        self.imgLeftList = [ pygame.image.load("image/stg6/gunner0.png").convert_alpha(), pygame.image.load("image/stg6/gunner1.png").convert_alpha() ]
        self.imgRightList = [ pygame.transform.flip(self.imgLeftList[0], True, False), pygame.transform.flip(self.imgLeftList[1], True, False) ]
        self.fireLeft = pygame.image.load("image/stg6/gunnerFire.png").convert_alpha()
        self.fireRight = pygame.transform.flip(self.fireLeft, True, False)
        self.imgIndx = 0
        self.attIndx = 0
        self.image = self.imgLeftList[0]
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.left = wall.rect.left+wall.rect.width//2-self.rect.width//2
        self.rect.bottom = wall.rect.top

        self.eyePos = getPos(self, 0.5, 0.2)
        self.bulletList = pygame.sprite.Group()
        self.coolDown = 0
        self.snd = pygame.mixer.Sound("audio/wolf.wav")
        self.alterSpeed( choice( [-1, 0, 1] ) )
        self.status = "wandering"          # wandering表示闲逛的状态，alarming表示发现英雄的状态
        # 生成一个自管理的透明画布
        self.canvas, self.canvasRect = createCanvas( (800, 620), (0,0,0) )
        self.fireSnd = pygame.mixer.Sound("audio/gunner.wav")

    # 这个move()函数是供外界调动的接口，这里仅起根据传入的英雄参数判断状态的作用。判断完成后，修改自身的状态，然后执行相应的函数。
    def move(self, delay, sprites):
        # fill the canvas with black (transparent): clear former lines
        self.canvas.fill((0,0,0))
        # move if it's alive!
        if self.health>0:
            for hero in sprites:
                # 如果有英雄在同一层，则将速度改为朝英雄方向。(这里的两套体系，英雄的层数为偶数，而怪物用的层数都是奇数)
                if ( (hero.onlayer-1)==self.onlayer and ( ( self.direction=="left" and getPos(self,0.5,0.5)[0]>getPos(hero,0.5,0.5)[0] ) or ( self.direction=="right" and getPos(self,0.5,0.5)[0]<getPos(hero,0.5,0.5)[0] ) ) ) or self.coolDown>0:
                    self.status = "alarming"
                    break     # ***这里碰到第一个英雄符合条件就退出了。因此，如果两个英雄同时在一层中，P1总是会被针对，而P2永远不会被选中为目标。问题留着以后修正。
                else:
                    self.status = "wandering"
            if self.status == "wandering":
                self.patrol( delay )
            elif self.status == "alarming" or self.coolDown>0:
                self.speed = 0
                self.fire( sprites )
            # renew the image of the gunner; if its speed = 0, do not change image
            trPos = [ self.rect.left + self.rect.width//2, self.rect.bottom ]
            self.image = self.imgLeftList[self.imgIndx] if ( self.direction=="left" ) else self.imgRightList[self.imgIndx]
            if self.speed and not (delay % 5 ):
                self.imgIndx = (self.imgIndx+1) % len(self.imgLeftList)
            elif 86>=self.coolDown>=83 or 81>=self.coolDown>=78 or 76>=self.coolDown>=73:
                    self.image = self.fireLeft if ( self.direction=="left" ) else self.fireRight
            self.rect = self.image.get_rect()
            self.rect.left = trPos[0]-self.rect.width//2
            self.rect.bottom = trPos[1]
            self.eyePos = getPos(self, 0.5, 0.2)
            # inspecting line
            if self.direction=="right":
                pygame.draw.line( self.canvas, (255,0,0), self.eyePos, (self.boundaries[1],self.eyePos[1]), 1)
            else:
                pygame.draw.line( self.canvas, (255,0,0), self.eyePos, (self.boundaries[0],self.eyePos[1]), 1)
        # If it's dead, stop moving and check whether it still has bullets flying.
        elif len(self.bulletList)<=0:
            self.erase()
            return False
        # bullet moving (no matter the gunner is alive or dead, as long as it has created flying bullets)
        for each in self.bulletList:
            each.move()
            pygame.draw.circle(self.canvas, each.color[0], each.pos, each.r)
            #pygame.draw.circle(self.canvas, each.color[1], each.pos, each.r//2)

    def patrol(self, delay):
        if (self.speed):                        # speed!=0，在运动。
            self.rect.left += self.speed
            if (getPos(self, 0.7, 1)[0] >= self.scope[1] and self.speed > 0) or (getPos(self, 0.3, 1)[0] <= self.scope[0] and self.speed < 0):
                self.speed = - self.speed
                self.direction = "right" if self.direction=="left" else "left"
            if not delay % 20 and random()<0.08:
                self.speed = 0
        elif not delay % 20 and random()<0.08:  # 否则，在休息。此时若随机数满足条件，进入奔跑状态
            self.speed = choice( [1,-1] )
            self.direction = "right" if self.speed>0 else "left"
    
    def fire(self, sprites):
        if ( self.coolDown==0 ):
            self.coolDown = 90
            self.fireSnd.play(0)
        if self.coolDown==85 or self.coolDown==80 or self.coolDown==75:
            bullet = GunBullet(getPos(self, 0, 0.4), -5, sprites, self.boundaries) if self.direction=="left" else GunBullet(getPos(self, 1, 0.4), 5, sprites, self.boundaries)
            self.bulletList.add(bullet)
        self.coolDown -= 1
    
    def lift(self, dist):
        self.rect.bottom += dist
        for each in self.bulletList:
            each.pos[1] += dist
    
    def level(self, dist):
        self.rect.left += dist
        self.scope = (self.scope[0]+dist, self.scope[1]+dist)
        self.boundaries = (self.boundaries[0]+dist, self.boundaries[1]+dist)
        for each in self.bulletList:
            each.pos[0] += dist

    def hitted(self, damage, pushed):
        if pushed>0:   # 向右击退
            self.hitBack = max( pushed-self.weight, 0 )
        elif pushed<0: # 向左击退
            self.hitBack = min( pushed+self.weight, 0 )
        self.health -= damage
        if self.health <= 0:                # dead
            self.health = 0
            return True

class GunBullet(pygame.sprite.Sprite): 

    def __init__(self, pos, spd, sprites, boundaries): # 参数color:推荐带上透明度RGBA；参数speed:为一个二元组
        pygame.sprite.Sprite.__init__(self)
        self.r = 3
        self.color = [ (20,20,0,255), (1,1,1,255) ]
        self.pos = pos
        self.speed = spd
        if spd > 0:
            self.push = 5
        else:
            self.push = -5
        self.tgts = sprites
        self.boundaries = boundaries
    
    def move(self):
        self.pos[0] += self.speed
        if self.pos[0]<=self.boundaries[0] or self.pos[0]>=self.boundaries[1]:  # 撞墙
            self.kill()
            del self
            return
        for hero in self.tgts:
            if hero.rect.left < self.pos[0] < hero.rect.right and hero.rect.top < self.pos[1] < hero.rect.bottom:
                hero.hitted( 3, self.push )
                self.kill()
                del self
                return

# ------------------------------------
class WarMachine(Monster):

    arm = None        # 是一个单独的sprite
    packet = None

    def __init__(self, groupList, onlayer, boundaries):
        # initialize the sprite
        Monster.__init__(self, "WarMachine", (10, 30, 10, 240), 200, 6, 4, onlayer, 40, 20)
        self.onlayer = int(onlayer)
        self.boundaries = boundaries
        self.initLayer(groupList)
        # ----- body part (the core of the WarMachine) ------
        self.bodyLeftList = [ pygame.image.load("image/stg6/WarMachine0.png").convert_alpha(), pygame.image.load("image/stg6/WarMachine1.png").convert_alpha() ]
        self.bodyRightList = [ pygame.transform.flip(self.bodyLeftList[0], True, False), pygame.transform.flip(self.bodyLeftList[1], True, False) ]
        self.imgIndx = 0
        self.image = self.bodyLeftList[0]
        self.mask = pygame.mask.from_surface(self.image)
        # calculate its position
        self.rect = self.image.get_rect()
        self.rect.left = self.initPos[0]-self.rect.width//2  # 位于砖块居中
        self.rect.bottom = self.initPos[1]
        self.coolDown = 0           
        self.alterSpeed( choice( [-1, 1] ) )
        # ------------- arm part --------------
        self.armLeft = [ pygame.image.load("image/stg6/arm.png").convert_alpha(), pygame.image.load("image/stg6/armFire.png").convert_alpha() ]
        self.armRight = [ pygame.transform.flip(self.armLeft[0], True, False), pygame.transform.flip(self.armLeft[1], True, False) ]
        self.armR = { "left":[ (0.5,0.4), (0.5,0.4) ], "right":[ (0.5,0.4), (0.5,0.4) ] }     # 分别为左和右时的位置信息
        self.arm = Ajunction( self.armLeft[0], getPos(self, self.armR[self.direction][0][0], self.armR[self.direction][0][1]) )
        self.armIndx = 0
        # ------------- packet part ----------------
        self.pktLeft = [ pygame.image.load("image/stg6/packet.png").convert_alpha(), pygame.image.load("image/stg6/packetBroken.png").convert_alpha() ]
        self.pktRight = [ pygame.transform.flip(self.pktLeft[0], True, False), pygame.transform.flip(self.pktLeft[1], True, False) ]
        self.pktR = { "left":[ (0.75,0.42), (0.75,0.42) ], "right":[ (0.25,0.42), (0.25,0.42) ] }
        self.packet = Ajunction( self.pktLeft[0], getPos(self, self.pktR[self.direction][0][0], self.pktR[self.direction][0][1]) )
        self.pktIndx = 0
        # ----------- other attributes -------------------------
        self.cnt = 0         # count for the loop of shift position
        self.coolDown = 0    # count for attack coolDown
        self.fireSnd = pygame.mixer.Sound("audio/MachineGrenade.wav")
        self.moanSnd = pygame.mixer.Sound("audio/MachineCollapse.wav")
        self.sparkySnd = pygame.mixer.Sound("audio/sparky.wav")
        self.fireList = pygame.sprite.Group()
        self.jetting = False
        self.jetImg = [ pygame.image.load("image/stg6/jet0.png").convert_alpha(), pygame.image.load("image/stg6/jet1.png").convert_alpha() ]
        self.jetIndx = 0
        # 生成一个自管理的透明画布
        self.canvas, self.canvasRect = createCanvas( (800, 620), (0,0,0) )
        self.sparkyCnt = 0
        self.chargeList = []   # 用于存放电磁炮蓄力充能时的充能粒子信息
        self.activated = False

    def move(self, delay, sprites, canvas, groupList):
        self.checkHitBack()
        # change layer
        if not (delay%20) and self.sparkyCnt==0 and random()<0.04:
            self.jetting = True
            # 处理层数。他需要在合理的范围内，因此先找出最大的层数
            klist = []
            for key in groupList:
                klist.append(int(key))
            if self.onlayer <=-1:               # 如果在最底下一层
                self.onlayer += 2
            elif self.onlayer >= max(klist)-2:  # 如果在最高层
                self.onlayer -= 2
            else:                               # 处于中间，随机选择一个新的层数
                self.onlayer = choice( [self.onlayer-2, self.onlayer+2] )
            self.initLayer(groupList)           # 计算其在新一行的水平scope
        # 某科学的电磁炮，发射！
        if not (delay%20) and self.sparkyCnt==0 and random()<0.08:
            self.chargeList = []
            self.armIndx = 1    # 开炮手势
            self.sparkyCnt = 60
        
        if not ( delay % 2 ):
            #优先处理 jetting $$$$$$$
            if self.jetting:
                self.rect.bottom += ( (self.initPos[1]-getPos(self, 0.5, 1)[1]) // 10 )
                self.rect.left += ( (self.initPos[0]-getPos(self, 0.5, 1)[0]) // 10 )
                #以竖直方向为标准，若已抵达(等于或略高于)目标行，则将jetting标记为False
                if 0<= (self.initPos[1]-self.rect.bottom) < 10:
                    self.rect.bottom = self.initPos[1]
                    self.jetting = False
                self.jetIndx = (self.jetIndx+1) % len(self.jetImg)  # 更新喷火的图片
            # 然后处理 激光炮！！ $$$$$$$
            if self.sparkyCnt>0:
                self.canvas.fill((0,0,0))
                self.sparkyCnt -= 1
                if self.direction=="left":
                    muzzle = getPos(self.arm, 0, 0.85)
                    limitX = self.boundaries[0]
                elif self.direction=="right":
                    muzzle = getPos(self.arm, 1, 0.85)
                    limitX = self.boundaries[1]
                if self.sparkyCnt >= 20:  # 蓄力充能阶段
                    if self.sparkyCnt == 20:
                        self.sparkySnd.play(0)
                    if random()<0.4:      # 某概率添加新粒子
                        r = choice( [2,3,4] )
                        XRange = list(range(muzzle[0]-50,muzzle[0]-30)) + list(range(muzzle[0]+30,muzzle[0]+50))
                        YRange = list(range(muzzle[1]-50,muzzle[1]-30)) + list(range(muzzle[1]+30,muzzle[1]+50))
                        pos = [ choice( XRange ), choice( YRange ) ]
                        color = choice( [(240,240,255),(170,170,255),(100,100,255)] )
                        self.chargeList.append( (r, pos, color) )
                    for each in self.chargeList:  # 绘制并移动粒子
                        pygame.draw.circle( self.canvas, each[2], each[1], each[0] )  # 充能粒子
                        each[1][0] += (muzzle[0]-each[1][0]) // 8
                        each[1][1] += (muzzle[1]-each[1][1]) // 8
                    pygame.draw.circle( self.canvas, (100,100,255), muzzle, (60-self.sparkyCnt)//2 ) #聚能中心
                else:
                    pygame.draw.line( self.canvas, (100,100,255), muzzle, (limitX,muzzle[1]), 10)     # 开炮！！
                    canvas.addSpatters( 4, [2,3,4], [6,8,10], choice( [(240,240,255),(170,170,255),(100,100,255)] ), (limitX,muzzle[1]) )
                    for each in sprites:
                        if ( ( getPos(each,0.5,0.5)[0]>getPos(self.arm, 0.5, 1)[0] and self.direction=="right" ) or ( getPos(each,0.5,0.5)[0]<getPos(self.arm, 0.5, 1)[0] and self.direction=="left" ) ) and each.rect.top <= getPos(self.arm, 0.5, 1)[1] <= each.rect.bottom: # 被激光击中！！！
                            each.hitted( 1, self.push )
            # 只有不在jet 且没有发射激光 的时候才可以做自由水平移动 $$$$$$$
            if not self.jetting and self.sparkyCnt==0:
                self.armIndx = 0  # 重置手势
                self.rect.left += self.speed
                if (self.rect.right >= self.scope[1] and self.speed > 0) or (self.rect.left <= self.scope[0] and self.speed < 0):
                    self.alterSpeed(-self.speed)
                if not delay%6:
                    self.imgIndx = (self.imgIndx+1) % len(self.bodyLeftList) #自由移动，主体图像变动
            # 更新各组件的图像
            if self.direction == "left":
                self.image = self.bodyLeftList[self.imgIndx]
                self.mask = pygame.mask.from_surface(self.image)
                self.packet.updateImg( self.pktLeft[self.pktIndx] )
                self.arm.updateImg( self.armLeft[self.armIndx] )
            elif self.direction == "right":
                self.image = self.bodyRightList[self.imgIndx]
                self.mask = pygame.mask.from_surface(self.image)
                self.packet.updateImg( self.pktRight[self.pktIndx] )
                self.arm.updateImg( self.armRight[self.armIndx] )
        # 不管是什么时候，都应该及时更新ajunction的位置（还会有英雄击退）
        self.packet.updatePos( getPos(self, self.pktR[self.direction][self.pktIndx][0], self.pktR[self.direction][self.pktIndx][1]) )
        self.arm.updatePos( getPos(self, self.armR[self.direction][self.armIndx][0], self.armR[self.direction][self.armIndx][1]) )
        # check coolDown and fire the packet 背部榴弹的喷射
        if self.coolDown == 0:
            self.coolDown = 150
        elif (self.coolDown > 0):
            self.coolDown -= 1
            if self.coolDown==140 or self.coolDown==130 or self.coolDown==120 or self.coolDown==110:
                if random()<0.5:
                    self.fireSnd.play(0)
                fire = Fire( getPos(self.packet,0.5,0), self.onlayer, randint(-3,3), randint(-6,-4))
                self.fireList.add(fire)
                return fire

    # 此函数用于确定新一行中的位置及scope
    def initLayer(self, groupList):
        self.wallList = []          # 存储本行的所有砖块; # 每次初始化一个新实例时，清空此类的wallList（否则会在上一个实例的基础上再加！）
        posList = []                # 辅助列表，用于暂时存储本行砖块的位置（左边线）
        for aWall in groupList[str(self.onlayer)]:  # 由于spriteGroup不好进行索引/随机选择操作，因此将其中的sprite逐个存入列表中存储
            self.wallList.append(aWall)
            posList.append(aWall.rect.left)
        wall = choice(self.wallList)
        self.initPos = getPos(wall, 0.5, 0)   # 新点，居中
        leftMax = wall.rect.left
        rightMax = wall.rect.right  # note：此处砖块的右坐标即下一砖块的左坐标
        while True:
            if (leftMax in posList) or (leftMax-wall.rect.width in posList): # warmachine比较宽，可以占两格行进
                leftMax -= wall.rect.width
            else:
                leftMax += wall.rect.width  # 将多减的加回来
                break
        while True:
            if (rightMax in posList) or (rightMax+wall.rect.width in posList):
                rightMax += wall.rect.width
            else:
                break
        leftMax = self.boundaries[0] if (leftMax-wall.rect.width<self.boundaries[0]) else leftMax-wall.rect.width
        rightMax = self.boundaries[1] if (rightMax+wall.rect.width>self.boundaries[1]) else rightMax+wall.rect.width
        self.scope = (leftMax, rightMax)

    def lift(self, dist):
        self.rect.bottom += dist
        self.initPos[1] += dist
    
    def level(self, dist):
        self.rect.left += dist
        self.scope = (self.scope[0]+dist, self.scope[1]+dist)
        self.boundaries = (self.boundaries[0]+dist, self.boundaries[1]+dist)

    # 鉴于本对象的构造非常复杂，因此提供一个专门的绘制接口
    # 给此函数传递一个surface参数，即可在该surface上绘制（blit）完整的本对象
    def paint(self, screen):
        if self.jetting:
            jetRect = self.jetImg[self.jetIndx].get_rect()
            jetRect.left, jetRect.top = getPos(self, 0.2, 1)
            screen.blit( self.jetImg[self.jetIndx], jetRect )
            jetRect.left, jetRect.top = getPos(self, 0.8, 1)
            screen.blit( self.jetImg[self.jetIndx], jetRect )
        screen.blit( self.image, self.rect )
        screen.blit( self.packet.image, self.packet.rect )
        screen.blit( self.arm.image, self.arm.rect )
        if self.sparkyCnt>0:
            screen.blit( self.canvas, self.canvasRect )
        #for each in self.fireList:
        #    screen.blit( each.image, each.rect )
    
    def erase(self):
        self.moanSnd.play(0)
        self.packet.kill()
        del self.packet
        self.arm.kill()
        del self.arm
        self.kill()
        del self
        return True   # dead

# ==========================================================================
# --------------------------------- stage7 ---------------------------------
# ==========================================================================
class Guard(Monster):

    def __init__(self, wallGroup, blockSize, onlayer):
        # calculate its position
        Monster.__init__(self, "guard", (255,0,0,240), 28, 6, 1, onlayer, 3, 2)
        self.wallList = []            # 存储本行的所有砖块; # 每次初始化一个新实例时，清空此类的wallList（否则会在上一个实例的基础上再加！）
        posList = []                  # 辅助列表，用于暂时存储本行砖块的位置（左边线）
        for aWall in wallGroup:       # 由于spriteGroup不好进行索引/随机选择操作，因此将其中的sprite逐个存入列表中存储
            self.wallList.append(aWall)
            posList.append(aWall.rect.left)
        wall = choice(self.wallList)
        leftMax = wall.rect.left
        rightMax = wall.rect.right    # note：此处砖块的右坐标即下一砖块的左坐标
        while True:
            if leftMax in posList:
                leftMax -= blockSize
            else:
                leftMax += blockSize  # 将多减的加回来
                break
        while True:
            if rightMax in posList:
                rightMax += blockSize
            else:
                break
        self.scope = (leftMax, rightMax)
        # initialize the sprite
        self.imgList = createImgList( [ pygame.image.load("image/stg7/guard0.png").convert_alpha(), pygame.image.load("image/stg7/guard1.png").convert_alpha(), 
            pygame.image.load("image/stg7/guard2.png").convert_alpha(), pygame.image.load("image/stg7/guard3.png").convert_alpha() ] )
        self.attList = createImgList( [ pygame.image.load("image/stg7/att0.png").convert_alpha(), pygame.image.load("image/stg7/att1.png").convert_alpha(), 
            pygame.image.load("image/stg7/att0.png").convert_alpha() ] )

        self.imgIndx = 0
        self.image = self.imgList["left"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.left = wall.rect.left+wall.rect.width//2-self.rect.width//2
        self.rect.bottom = wall.rect.top
        self.damage = 6.5
        self.coolDown = 0
        self.snd = pygame.mixer.Sound("audio/guardAtt.wav")
        self.speed = choice( [-1, 0, 1] )  # 0表示原地不动，负数表示向左移动，正数表示向右移动
        if self.speed == 1:
            self.direction = "right"
        self.status = "wandering"          # wandering表示闲逛的状态，alarming表示发现英雄的状态
        self.tgt = None                    # 指示要攻击的英雄
        # Define shield.
        self.shieldR = { "left":(0.2,0.62), "right":(0.8,0.62) }
        self.shieldImg = createImgList( [pygame.image.load("image/stg7/shield.png").convert_alpha()] )
        self.shield = Ajunction( self.shieldImg["left"], getPos(self, self.shieldR["left"][0], self.shieldR["left"][1]) )
        # Define spear.
        self.spearR = { "left":(0.15,0.6), "right":(0.85,0.6) }
        self.spearAttR = { "left":(0.08,0.65), "right":(0.92,0.65) }
        self.spearImg = createImgList( [pygame.image.load("image/stg7/spear.png").convert_alpha()] )
        self.spearAttImg = createImgList( [pygame.image.load("image/stg7/spearAtt.png").convert_alpha()] )
        self.spear = Ajunction( self.spearImg["left"], getPos(self, self.spearR["left"][0], self.spearR["left"][1]) )

    # 这个move()函数是供外界调动的接口，这里仅起根据传入的英雄参数判断状态的作用。判断完成后，修改自身的状态，然后执行相应的函数。
    def move(self, delay, sprites):
        for hero in sprites:
            # 如果有英雄在同一层，则将速度改为朝英雄方向。(这里的两套体系，英雄的层数为偶数，而怪物用的层数都是奇数)
            if ( (hero.onlayer-1)==self.onlayer and ( self.scope[0]<=getPos(hero,1,0.5)[0] ) and ( getPos(hero,0,0.5)[0]<=self.scope[1] ) ) or self.coolDown>0:
                self.status = "alarming"
                self.tgt = hero
                break     # ***这里碰到第一个英雄符合条件就退出了。因此，如果两个英雄同时在一层中，P1总是会被针对，而P2永远不会被选中为目标。问题留着以后修正。
            else:
                self.status = "wandering"
        if self.status == "wandering":
            self.wander( delay )
        elif self.status == "alarming":
            self.attack( sprites )
        self.checkImg(delay)

    def checkImg(self, delay):
        trPos = [ self.rect.left + self.rect.width//2, self.rect.bottom ]
        # renew the image of the guard
        if self.coolDown==0:
            if self.speed and not (delay % 10 ):
                self.imgIndx = (self.imgIndx+1) % len(self.imgList)
            elif self.speed == 0:
                self.imgIndx = 0
            self.image = self.imgList[self.direction][self.imgIndx]
            self.spear.updateImg( self.spearImg[self.direction] )
            self.spear.updatePos( getPos(self, self.spearR[self.direction][0], self.spearR[self.direction][1]) )
        else:
            self.image = self.attList[self.direction][self.coolDown // 13]
            self.spear.updateImg( self.spearAttImg[self.direction] )
            self.spear.updatePos( getPos(self, self.spearAttR[self.direction][0], self.spearAttR[self.direction][1]) )
        self.rect = self.image.get_rect()
        self.rect.left = trPos[0]-self.rect.width//2
        self.rect.bottom = trPos[1]
        # adjust shield and spear
        self.shield.updateImg( self.shieldImg[self.direction] )
        self.shield.updatePos( getPos(self, self.shieldR[self.direction][0], self.shieldR[self.direction][1]) )

    def wander(self, delay):
        if (self.speed):                          # speed!=0，在运动。
            self.rect.left += self.speed
            if (getPos(self, 0.7, 1)[0] >= self.scope[1] and self.speed > 0) or (getPos(self, 0.3, 1)[0] <= self.scope[0] and self.speed < 0):
                self.speed = - self.speed
                self.direction = "left" if self.direction=="right" else "right"
            if not delay % 20 and random()<0.08:  # 随机进入休息状态。
                self.speed = 0
                self.direction = "left" if random()<0.5 else "right"
        elif not delay % 20 and random()<0.08:    # 否则，在休息。此时若随机数满足条件，进入巡逻状态
            self.speed = choice( [1,-1] )
            self.direction = "left" if self.speed == -1 else "right"
    
    def attack(self, sprites):
        if not self.coolDown:
            if getPos( self.tgt, 0.5, 0.5 )[0]>getPos( self, 0.5, 0.5 )[0]:
                self.speed = 1
                self.direction = "right"
            else:
                self.speed = -1
                self.direction = "left"
        self.rect.left += self.speed * 2
        if self.coolDown==0:
            for each in sprites:
                if abs(getPos(self, 0.5, 0.5)[0]-getPos(each, 0.5, 0.5)[0])<40:
                    self.snd.play(0)    # 攻击英雄，咆哮
                    self.speed = 0
                    self.coolDown = 38
        else:
            self.coolDown -= 1
            if self.coolDown == 20:
                for each in sprites:
                    if pygame.sprite.collide_mask(self.spear, each):
                        cldList( self, sprites )
    
    def paint(self, screen):
        screen.blit( self.spear.image, self.spear.rect )
        screen.blit( self.image, self.rect )
        screen.blit( self.shield.image, self.shield.rect )
    
    def level(self, dist):
        self.rect.left += dist
        self.scope = (self.scope[0]+dist, self.scope[1]+dist)
        self.boundaries = (self.boundaries[0]+dist, self.boundaries[1]+dist)
    
    def hitted(self, damage, pushed):
        if pushed>0:   # 向右击退
            self.hitBack = max( pushed-self.weight, 0 )
        elif pushed<0: # 向左击退
            self.hitBack = min( pushed+self.weight, 0 )
        
        self.bldColor = (255,0,0,240)
        if ( pushed<0 and self.direction=="right" ) or ( pushed>0 and self.direction=="left"):
            self.bldColor = (200,200,200,240)
            return False
        
        self.health -= damage
        if self.health <= 0:       # dead
            self.health = 0
            self.erase()
            return True