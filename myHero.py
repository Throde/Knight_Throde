# hero module
import pygame
import math
from random import *

import enemy
import mapManager

# =========================================
class Hero(pygame.sprite.Sprite):

    # some properties of hero
    name = "knight"
    heroNo = 0
    gender = "Male"
    health = 100
    full = 100
    arrow = 12
    fruit = 1
    armor = 1         # 范围0~1
    dmgReduction = 1  # 调节游戏难度所引起的受伤减少，为百分比。1表示原伤害。

    speed = 3         # 英雄用于计算的移动速度（可因某些因素而减慢）
    shootNum = 1      # 用于指示每次射击射出的投掷物数量（某些英雄可能不同，默认为1）
    power = 20
    imgIndx = 0
    status = "left"
    propPos = {}     # 本英雄相关属性值在屏幕上的坐标对字典，依次为slot, ammo, bag, health
    itemDic = { "supAmmo":("arrow","箭矢"), "fruit":("fruit","水果"), "medicine":("medicine","药剂"), "torch":("torch","火把"), "exp":("Exp","经验") }
    score = 0
    expInc = 0

    k1 = 0           # 一阶跳的标志
    k2 = 0           # 二阶跳的标志
    kNum = 13        # 单阶段跳跃的计算总次数（从离地到抵达最高点的次数，单向上升过程）
    jmpCap = 0       # 单次跳跃的上升距离，将在初始化时计算得出
    aground = True   # indicate whether hero is on the ground
    gravity = 1
    shootCnt = 0     # 射击时更换图片过程的计数
    whipCnt = 0      # 砍杀过程的倒计时
    hitBack = 0      # 受伤击退效果，受伤时将此值设置为击退像素（仅在水平方向上）

    wpPos = [0,0,0]  # weapon相对于hero的位置比例：pos[0]表示x坐标比例，pos[1]表示y坐标比例，pos[2]表示层级，0表示weapon在self下层，1表示weapon在self上层。
    hitFeedIndx = 0
    arrowList = []
    category = "hero"
    checkList = None   # spriteGroup that stores wall or supply sprites used for checking collide
    preyList = []      # A list to store info of the killed or damaged enemy by this hero. Can be added by checkImg() or hero's bullet. Can be taken by the model loop. 
    eventList = []     # A list to store events info such as getItem.

    affected = -1      # 可取3个值：-1表示健康；0表示正在感染（感染效果）；1表示已感染
    freezeCnt = 0      # 当前被冰冻减速的倒计时
    torchCnt = 0       # 当前火炬明亮能力的倒计时
    trapper = None     # 指向当前导致英雄减速、无法跳跃状态的对象，将引用挂在这里
    shootSnd = None
    jmpSnd = None
    imgSwt = 8         # 行走时图片的切换频率。对于大部分英雄为8，某些英雄可能需要更快切换
    underWater = False

    bldColor = (255,10,10,210)
    exp = 0
    jpCnt = 0
    image = None
    rect = None
    mask = None
    onlayer = 0        # indicate which layer hero is. only can be even number
    maxLayer = 0       # indicate the score

    # Storage Information: 以下是hero的库信息部分，保存易被修改的hero的原始信息。
    # 这部分在__init__时设置完成后，不允许再被修改。当需要恢复被改变的属性时，可以从这里读取恢复。
    oriSpd = 3           # 指示hero正常的移动速度
    oriImgLeftList = []  # hero的行走图片列表
    oriImgRightList = []
    oriImgJumpLeft = None
    oriImgJumpRight = None
    oriImgHittedLeft = None
    oriImgHittedRight = None
    oriWeaponR = {}
    oriWpJumpLeft = None
    oriWpJumpRight = None

    # constructor of hero
    def __init__(self, pos, blockSize, VHero, propPos, dmgReduction):
        pygame.sprite.Sprite.__init__(self)
        if VHero.no == 0:
            self.name = "knight"
            self.push = 7
            self.weight = 2
            self.speed = 3
            self.itemDic["supAmmo"] = ("arrow","箭矢")
            # 一个尝试：只保留left方向下的位置数据，根据hero的状态进行区分。right方向下，保持第二项不变，第一项用1去减即可。第三项只可取0或1。
            self.oriWeaponR = {"normal":(0.1,0.9,0), "whip":[ (0.01,0.56,0), (-0.04,0.56,0), (-0.04,0.72,0), (0.1,0.88,1) ], "jump":(0.1,0.6,0), "hide":(0.52,0.72,0)}
            self.specLeft = pygame.image.load("image/knight/defend.png")
            self.specRight = pygame.transform.flip(self.specLeft, True, False)
            self.defending = False
            self.imgSwt = 8
            self.gender = "Male"
        elif VHero.no == 1:
            self.name = "princess"
            self.push = 6
            self.weight = 1
            self.speed = 3
            self.itemDic["supAmmo"] = ("bullet","炮弹")
            self.oriWeaponR = { "normal":(0.5,0.5,0), "whip":[ (0.3,0.76,1), (0.2,0.77,1), (0.1,0.77,1), (0.3,0.77,0) ], "jump":(0.5,0.5,0), "hide":(0.5,0.5,0)}
            self.imgSwt = 8
            self.gender = "Female"
        elif VHero.no == 2:
            self.name = "prince"
            self.push = 8
            self.weight = 3
            self.speed = 3
            self.itemDic["supAmmo"] = ("javelin","掷枪")
            self.oriWeaponR = {"normal":(0.56,0.76,1), "whip":[ (0.42,0.76,1), (0.34,0.72,1), (0.24,0.7,1), (0.16,0.68,1) ], "jump":(0.66,0.44,1), "hide":(0.56,0.76,1)}
            self.imgSwt = 8
            self.gender = "Male"
        elif VHero.no == 3:
            self.name = "wizard"
            self.push = 6
            self.weight = 2
            self.speed = 3
            self.itemDic["supAmmo"] = ("fire element","火元素")
            self.oriWeaponR = {"normal":(0.09,0.64,0), "whip":[ (0.52,0.7,1), (0.52,0.7,1), (0.5,0.76,1), (0.4,0.77,0) ], "jump":(0.09,0.64,0), "hide":(0.1,0.64,0)}
            self.imgSwt = 6
            self.gender = "Male"
        elif VHero.no == 4:
            self.name = "huntress"
            self.push = 6
            self.weight = 1
            self.speed = 3
            self.itemDic["supAmmo"] = ("dart","飞镖")
            self.oriWeaponR = {"normal":(0.3,0.7,0), "whip":[ (-0.1,0.78,1), (-0.4,0.72,1), (-0.2,0.66,0), (0,0.6,0) ], "jump":(0.3,0.5,0), "hide":(0.3,0.7,0)}
            self.imgSwt = 6
            self.gender = "Female"
        elif VHero.no == 5:
            self.name = "priest"
            self.push = 6
            self.weight = 1
            self.speed = 3
            self.itemDic["supAmmo"] = ("jade","玉石")
            self.oriWeaponR = {"normal":(0.3,0.71,0), "whip":[ (0.2,0.7,0), (0.18,0.68,0), (0.18,0.64,0), (0.2,0.61,0) ], "jump":(0.12,0.68,0), "hide":(0.2,0.68,0)}
            self.imgSwt = 8
            self.gender = "Female"
        elif VHero.no == 6:
            self.name = "king"
            self.push = 8
            self.weight = 2
            self.speed = 3
            self.itemDic["supAmmo"] = ("shots","散弹")
            self.oriWeaponR = {"normal":(0.05,0.75,0), "whip":[ (0.64,0.7,1), (0.46,0.78,1), (0.04,0.78,0), (0.16,0.52,0) ], "jump":(0,0.68,0), "hide":(0.95,0.75,0)}
            self.imgSwt = 8
            self.shootNum = 5
            self.gender = "Male"

        self.health = VHero.hp
        self.power = VHero.pw
        self.rDamage = VHero.dmg
        self.full = self.health
        self.oriSpd = self.speed
        self.heroNo = VHero.no
        self.lvl = VHero.lvl
        
        # About the bag: -------------------------------------------
        self.bag = { "fruit":2, "torch":0, "medicine":0 }  #store all items in the form of dictionary. It doesnot support index, so a buffer is needed.
        self.slot = pygame.image.load("image/slot.png").convert_alpha()
        self.bagImgList = { "fruit":pygame.image.load("image/fruit.png").convert_alpha(), "torch":pygame.image.load("image/torch.png").convert_alpha(), "medicine":pygame.image.load("image/medicine.png").convert_alpha() }
        self.bagBuf = []         #a list serving as a buffer for hero.bag, dynamically renew itself each fresh, only store items that are more than one.
        for item in self.bag:    #Initialize the buffer with only "fruit".
            if self.bag[item]>0:
                self.bagBuf.append( item )
        self.bagPt = 0           # A pointer that indicates the current item in the bag buffer.
        
        self.expInc = 0
        
        self.arrow = 12
        self.armor = 0
        self.jpCnt = 0
        self.dmgReduction = 1
        self.ammoImg = pygame.image.load("image/"+self.name+"/supAmmo.png")
        self.lumi = 0     # 在迷雾中将会起作用，lumi值越大，明亮范围越大
        self.hitBack = 0
        self.haloCanvas = None
        self.propPos = propPos
        self.dmgReduction = dmgReduction
        self.checkList = pygame.sprite.Group()
        self.preyList = []
        self.eventList = []
        self.weaponR = self.oriWeaponR

        # 初始化hero的图片库
        self.oriImgLeftList = [ pygame.image.load("image/"+self.name+"/heroLeft0.png").convert_alpha(), pygame.image.load("image/"+self.name+"/heroLeft1.png").convert_alpha(), \
            pygame.image.load("image/"+self.name+"/heroLeft2.png").convert_alpha(), pygame.image.load("image/"+self.name+"/heroLeft3.png").convert_alpha() ]
        self.oriImgRightList = [ pygame.transform.flip(self.oriImgLeftList[0], True, False), pygame.transform.flip(self.oriImgLeftList[1], True, False), 
            pygame.transform.flip(self.oriImgLeftList[2], True, False), pygame.transform.flip(self.oriImgLeftList[3], True, False) ]
        self.oriImgJumpLeft = pygame.image.load("image/"+self.name+"/jumpLeft.png").convert_alpha()
        self.oriImgJumpRight = pygame.transform.flip(self.oriImgJumpLeft, True, False)
        self.oriImgHittedLeft = pygame.image.load("image/"+self.name+"/hittedLeft.png").convert_alpha()
        self.oriImgHittedRight = pygame.transform.flip(self.oriImgHittedLeft, True, False)
        self.oriWpJumpLeft = pygame.image.load("image/"+self.name+"/wpJump.png").convert_alpha()
        self.oriWpJumpRight = pygame.transform.flip(self.oriWpJumpLeft, True, False)
        
        # 正式全面初始化hero的图片
        self.imgLeftList = self.oriImgLeftList
        self.imgRightList = self.oriImgRightList
        self.weaponLeft = pygame.image.load("image/"+self.name+"/weapon.png").convert_alpha()
        self.weaponRight = pygame.transform.flip(self.weaponLeft, True, False)

        self.shootLeftList = [ pygame.image.load("image/"+self.name+"/shootLeft0.png").convert_alpha(), 
            pygame.image.load("image/"+self.name+"/shootLeft1.png").convert_alpha(), pygame.image.load("image/"+self.name+"/shootLeft2.png").convert_alpha() ]
        self.shootRightList = [ pygame.transform.flip(self.shootLeftList[0], True, False), 
            pygame.transform.flip(self.shootLeftList[1], True, False), pygame.transform.flip(self.shootLeftList[2], True, False) ]
        self.wpHideLeft = pygame.image.load("image/"+self.name+"/wpHide.png").convert_alpha()
        self.wpHideRight = pygame.transform.flip(self.wpHideLeft, True, False)
        
        self.whipLeftList = [ pygame.image.load("image/"+self.name+"/whipLeft0.png").convert_alpha(), pygame.image.load("image/"+self.name+"/whipLeft1.png").convert_alpha(), 
            pygame.image.load("image/"+self.name+"/whipLeft2.png").convert_alpha(), pygame.image.load("image/"+self.name+"/whipLeft3.png").convert_alpha() ]
        self.whipRightList = [ pygame.transform.flip(self.whipLeftList[0], True, False), pygame.transform.flip(self.whipLeftList[1], True, False), 
            pygame.transform.flip(self.whipLeftList[2], True, False), pygame.transform.flip(self.whipLeftList[3], True, False) ]
        self.wpAttLeft = [ pygame.image.load("image/"+self.name+"/wpAtt0.png").convert_alpha(), pygame.image.load("image/"+self.name+"/wpAtt1.png").convert_alpha(), 
            pygame.image.load("image/"+self.name+"/wpAtt2.png").convert_alpha(), pygame.image.load("image/"+self.name+"/wpAtt3.png").convert_alpha() ]
        self.wpAttRight = [ pygame.transform.flip(self.wpAttLeft[0], True, False), pygame.transform.flip(self.wpAttLeft[1], True, False), 
            pygame.transform.flip(self.wpAttLeft[2], True, False), pygame.transform.flip(self.wpAttLeft[3], True, False) ]
        self.affWhipLeft = pygame.image.load("image/"+self.name+"/affAtt.png").convert_alpha()
        self.affWhipRight = pygame.transform.flip(self.affWhipLeft, True, False)

        self.imgJumpLeft = self.oriImgJumpLeft
        self.imgJumpRight = self.oriImgJumpRight
        self.wpJumpLeft = self.oriWpJumpLeft
        self.wpJumpRight = self.oriWpJumpRight

        self.imgHittedLeft = self.oriImgHittedLeft
        self.imgHittedRight = self.oriImgHittedRight
        self.affLeftList = [pygame.image.load("image/"+self.name+"/affLeft0.png").convert_alpha(), pygame.image.load("image/"+self.name+"/affLeft1.png").convert_alpha()]
        self.affRightList = [pygame.transform.flip(self.affLeftList[0], True, False), pygame.transform.flip(self.affLeftList[1], True, False)]

        # initialize the position of hero ------------------------------
        self.image = self.imgLeftList[0]
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.left = pos[0]-self.rect.width//2
        self.rect.bottom = pos[1]
        # Initialize the melee weapon of the hero ----------------------
        self.weapon = enemy.Ajunction( self.weaponLeft, enemy.getPos(self, self.weaponR["normal"][0], self.weaponR["normal"][1]) )
        self.wpPos = [ self.weaponR["normal"][0], self.weaponR["normal"][1], self.weaponR["normal"][2] ]   # 初始化为normal
        # Jump dust imgs -----------------------------------------------
        self.dustList = [pygame.image.load("image/stg2/alarm10.png").convert_alpha(), pygame.image.load("image/stg2/alarm9.png").convert_alpha(), \
            pygame.image.load("image/stg2/alarm8.png").convert_alpha(), pygame.image.load("image/stg2/alarm7.png").convert_alpha(), \
            pygame.image.load("image/stg2/alarm6.png").convert_alpha(), pygame.image.load("image/stg2/alarm5.png").convert_alpha(), \
            pygame.image.load("image/stg2/alarm4.png").convert_alpha(), pygame.image.load("image/stg2/alarm3.png").convert_alpha(), \
            pygame.image.load("image/stg2/alarm2.png").convert_alpha(), pygame.image.load("image/stg2/alarm1.png").convert_alpha(), \
            pygame.image.load("image/stg2/alarm0.png").convert_alpha()]

        self.brand = pygame.image.load("image/"+self.name+"/brand.png").convert_alpha()
        self.jmpPos = [0,0]
        self.jmpInfo = ()
        self.jmpCap = (1+self.kNum) * self.kNum //2

        self.jmpSnd = pygame.mixer.Sound("audio/"+self.name+"/jump.wav")
        self.oriJmpSnd = self.jmpSnd
        self.whipSnd = pygame.mixer.Sound("audio/"+self.name+"/whip.wav")
        self.oriWhipSnd = self.whipSnd
        self.shootSnd = pygame.mixer.Sound("audio/"+self.name+"/shoot.wav")
        self.fruitSnd = pygame.mixer.Sound("audio/eatFruit.wav")
        # affection related
        self.affSnd = pygame.mixer.Sound("audio/affect"+self.gender+".wav")
        self.affJmp = pygame.mixer.Sound("audio/affJump"+self.gender+".wav")
        self.expSnd = pygame.mixer.Sound("audio/exp.wav")
        self.vomiSnd = pygame.mixer.Sound("audio/vomiSplash.wav")
        self.vomiList = pygame.sprite.Group()
        #self.shootVoice = [ pygame.mixer.Sound("audio/"+self.name+"/shootVoiceE.wav"), pygame.mixer.Sound("audio/"+self.name+"/shootVoiceC.wav") ]

    # define the moving methods of hero
    def jump(self, keyLine):
        # 一段跳
        if ( self.k2==0 ):
            if (self.k1==1):   # 一段跳刚开始时，获取起跳时的位置
                if random()<0.33: 
                    self.jmpSnd.play(0)
                self.jpCnt = 12
                self.jmpPos[0] = self.rect.left + self.rect.width//2
                self.jmpPos[1] = self.rect.bottom
            self.rect.bottom -= (self.kNum-self.k1)
            self.k1 = self.k1 + 1
            if self.k1 > self.kNum:
                self.k1 = 0
        # 二段跳
        else:
            self.rect.bottom -= (self.kNum-self.k2)
            self.k2 = self.k2 + 1
            if self.k2 > self.kNum:
                self.k2 = 0
        while ( getCld(self, self.checkList, ["sideWall","blockStone"]) ):  # 如果和参数中的物体重合，则回退1高度
            self.rect.bottom += 1        # 循环+1，直到不再和任何物体重合为止，跳出循环
            self.k1 = 0
            self.k2 = 0
        if ( self.rect.bottom <= keyLine ):
            self.shiftLayer(2, None)
            if self.onlayer > self.maxLayer:
                self.maxLayer += 2
                self.score += 1
        self.aground = False

    def moveX(self, delay, to):
        if not (delay % self.imgSwt ):
            self.imgIndx = (self.imgIndx+1) % len(self.imgLeftList)
        if to=="left":
            self.status = "left"
            self.rect.left -= self.speed
        elif to=="right":
            self.status = "right"
            self.rect.left += self.speed
        for each in self.checkList:
            if ( pygame.sprite.collide_mask(self, each) ):
                if each.category == "sideWall" or each.category == "blockStone":
                    # 尝试身高坐标-5，再看是否还会碰撞。5以内的高度都可以自动踩上去
                    self.rect.top -= 5
                    if getCld(self, self.checkList, ["sideWall","blockStone"]):
                        self.rect.top += 5
                        self.rect.left = self.rect.left+self.speed if ( to=="left" ) else self.rect.left-self.speed
                elif each.category == "door" and each.locked:
                    each.conversation()
                    self.rect.left = self.rect.left+self.speed if ( to=="left" ) else self.rect.left-self.speed
                elif each.category == "supAmmo" or each.category == "fruit" or each.category == "torch" or each.category == "medicine":
                    each.open(self)

    def fall(self, keyLine, newLine, stg, heightList):
        self.rect.bottom += self.gravity  # 尝试将自身纵坐标减去重力值
        clders = pygame.sprite.spritecollide(self, self.checkList, False, pygame.sprite.collide_mask) # 获得所有碰撞了的物体对象
        for item in clders:               # 针对每一个碰撞了的item执行相应的响应动作
            if item.category == "supAmmo" or item.category == "fruit" or item.category == "torch" or item.category == "medicine":
                item.open(self)
            elif item.category == "specialWall":
                if stg == 3:
                    item.clpCnt += 1
                elif stg == 5:
                    self.moveX(0, self.status)
            elif item.category == "hostage" or item.category=="exit" or item.category=="notice":
                item.conversation()
        while ( getCld(self, self.checkList, ["lineWall","baseWall","specialWall","sideWall","blockStone","column","house"]) ):  # 如果和参数中的物体重合，则回退1高度
            self.rect.bottom -= 1    # 循环-1，直到不再和任何物体重合为止，跳出循环
            self.aground = True      # 这两个值反复设置没有关系，只要循环结束后保证两个值分别为true和1即可
            self.gravity = 0
        if (self.gravity <= 6):      # 下落幅度最大为7px
            self.gravity += 1
        if ( self.rect.top >= keyLine ):
            self.shiftLayer(-2, heightList)
        self.renewCheckList(newLine) # 每次都更新self.checkList（跳跃函数中不必更新，只有这里需要更新）
    
    def shiftLayer(self, to, heightList):
        if to<0:
            # 下跳则检查：在最底层不能下跳；# 若英雄高度超过所在行的高度-跳跃距离的一半，则不能下跳。
            if (self.onlayer<=0) or ( self.rect.bottom < heightList[str(self.onlayer)]-self.jmpCap//2 ):
                return
        self.onlayer += to

    def whip(self):
        if self.affected>0 and (self.whipCnt == 0):
            self.whipSnd.play(0)
            self.vomiSnd.play(0)
            self.whipCnt = 40
            return
        if (self.shootCnt == 0) and (self.whipCnt == 0):   # Couldn't whip too fast! Hero must not be whiping or shooting.
            self.whipSnd.play(0)
            self.whipCnt = 20

    def shoot(self, allElements, delay):
        if (self.arrow > 0) and (self.whipCnt == 0):  # couldn't shoot too fast! Hero mustn't be whiping.
            self.shootSnd.play()
            #if random() <= 0.3:
            #    self.shootVoice[1].play(0)
            self.shootCnt = 18
            i = 1
            while i<=self.shootNum:
                arrow = Ammo( self, i )
                self.arrowList.append(arrow)
                allElements.add(arrow)
                i += 1
            self.arrow -= 1

    '''def special(self):
        if self.name == "knight":
            if not self.defending:
                self.defending = True
                self.image = self.specLeft if self.status == "left" else self.specRight
                self.armor = 0.4
            elif self.defending:
                self.image = self.imgLeftList[0] if self.status == "left" else self.imgRightList[0]
                self.defending = False
        elif self.name == "princess":
            pass
        elif self.name == "prince":
            pass'''

    def hitted(self, damage, pushed):
        self.health -= damage * self.dmgReduction
        if (self.health < 0):
            self.health = 0
            return True
        self.hitFeedIndx = 6
        if pushed>0:    # 向右击退
            self.hitBack = max( pushed-self.weight, 0 )
        elif pushed<0:  # 向左击退
            self.hitBack = min( pushed+self.weight, 0 )
        # 若本对象是玩家操控的英雄而非AI，则对整个频幕进行渲染反馈。
        if self.category == "hero":
            self.haloCanvas.addHalo( "hitHalo", [380,420,460,500], (255,0,0,120), -6 )
        # 以下是硬直效果，取消所有的英雄砍杀、射箭、二段跳行为
        self.whipCnt = self.shootCnt = self.k2 = 0

    # 以下是hitted函数的重载，适用于血掉落后自动回满（永远不会死亡）的需求。
    def hittedRevival(self, damage, pushed):
        self.health -= damage * self.dmgReduction
        if (self.health < 0):
            self.health = self.full
        self.hitFeedIndx = 6
        if pushed>0:    # 向右击退
            self.hitBack = max( pushed-self.weight, 0 )
        elif pushed<0:  # 向左击退
            self.hitBack = min( pushed+self.weight, 0 )
        if self.category == "hero":
            self.haloCanvas.addHalo( "hitHalo", [380,420,460,500], (255,0,0,120), -6 )
        # 以下是硬直效果，取消所有的英雄砍杀、射箭、二段跳行为
        self.whipCnt = self.shootCnt = self.k2 = 0
    
    # ==这个函数是每次刷新都会调用的，因此不止起到检查图片的作用，还可以检查hero的状态，如计数器。
    def checkImg(self, delay, spurtCanvas, monsters):
        if self.jpCnt > 0:   # 画起跳的灰尘
            self.jpCnt -= 1
            self.dustRect = self.dustList[ self.jpCnt-1 ].get_rect()
            self.dustRect.left = self.jmpPos[0] - self.dustRect.width // 2
            self.dustRect.bottom = self.jmpPos[1]
            self.jmpInfo = ( self.dustList[ self.jpCnt-1 ], self.dustRect )
        else:
            self.jmpInfo = ()
        # Check when hero is shooting an arrow.
        if ( self.shootCnt > 0 ):
            if not ( self.shootCnt % 6 ):
                indx = len(self.shootLeftList) - self.shootCnt//6  # 指示图片序号的临时变量。工作原理：Cnt=18的时候，imgIndx应该为0；同理，Cnt=12,imgIndx=1；Cnt=6，indx=3。
                if self.status == "left":
                    rht = self.rect.right
                    btm = self.rect.bottom
                    self.image = self.shootLeftList[indx]
                    self.rect = self.image.get_rect()              # 获取新的图片的rect
                    self.rect.right = rht
                    self.rect.bottom = btm
                    self.weapon.updateImg( self.wpHideLeft )       # weapon的图片序号和wIndx图片序号保持同步
                    self.wpPos[0] = self.weaponR["hide"][0]
                elif self.status == "right":
                    lft = self.rect.left
                    btm = self.rect.bottom
                    self.image = self.shootRightList[indx]
                    self.rect = self.image.get_rect()
                    self.rect.left = lft
                    self.rect.bottom = btm
                    self.weapon.updateImg( self.wpHideRight )
                    self.wpPos[0] = 1 - self.weaponR["hide"][0]
                self.wpPos[1] = self.weaponR["hide"][1]
                self.wpPos[2] = self.weaponR["hide"][2]
            self.shootCnt -= 1
        # Check when hero is whiping his weapon.
        elif ( self.whipCnt > 0 ) and self.affected<0:
            if not ( self.whipCnt % 5 ):     # Cnt每次等于5的倍数的时候就更换一次图片
                indx = len(self.whipLeftList) - self.whipCnt//5   # 指示图片序号的临时变量。工作原理：Cnt=20的时候，imgIndx应该为0；同理，Cnt=15,imgIndx=1...Cnt=5，indx=3。
                if self.status == "left":
                    rht = self.rect.right
                    btm = self.rect.bottom
                    self.image = self.whipLeftList[indx]
                    self.rect = self.image.get_rect()              # 获取新的图片的rect
                    self.rect.right = rht
                    self.rect.bottom = btm
                    self.weapon.updateImg( self.wpAttLeft[indx] )  # weapon的图片序号和wIndx图片序号保持同步
                    self.wpPos[0] = self.weaponR["whip"][indx][0]
                elif self.status == "right":
                    lft = self.rect.left
                    btm = self.rect.bottom
                    self.image = self.whipRightList[indx]
                    self.rect = self.image.get_rect()
                    self.rect.left = lft
                    self.rect.bottom = btm
                    self.weapon.updateImg( self.wpAttRight[indx] )
                    self.wpPos[0] = 1 - self.weaponR["whip"][indx][0]
                self.wpPos[1] = self.weaponR["whip"][indx][1]
                self.wpPos[2] = self.weaponR["whip"][indx][2]
                # whenever change the img, deal damage. (2 times in all)
                if self.whipCnt==15 or self.whipCnt==10:
                    for each in monsters:
                        if pygame.sprite.collide_mask(self.weapon, each):
                            realPush = self.push if self.status=="right" else -self.push
                            dead = each.hitted( self.power, realPush )
                            if dead:
                                self.score += each.score
                                deadInfo = each.category
                            else:
                                deadInfo = False
                            # 以下封装需要传递给主函数进行击中反馈的信息：
                            # 确定击中点的坐标pos
                            pos = [ 0, self.rect.top+self.rect.height//2 ]
                            if self.status == "left":
                                pos[0]=self.rect.left
                            elif self.status == "right":
                                pos[0]=self.rect.right
                            bldNum = 8
                            self.preyList.append( (self.status, pos, each.bldColor, bldNum, deadInfo, each.exp) )
            self.whipCnt -= 1
        # Check when hero is jumping in the air. Note that the statement "elif" makes that hero's image will be whiping when he whip even in the air.
        elif not self.aground:
            if self.status == "left":
                self.image = self.imgJumpLeft
                self.weapon.updateImg( self.wpJumpLeft )
                self.wpPos[0] = self.weaponR["jump"][0]
            elif self.status == "right":
                self.image = self.imgJumpRight
                self.weapon.updateImg( self.wpJumpRight )
                self.wpPos[0] = 1 - self.weaponR["jump"][0]
            self.wpPos[1] = self.weaponR["jump"][1]
            self.wpPos[2] = self.weaponR["jump"][2]
        # Check when hero is suffering damage.
        elif self.hitFeedIndx > 0:
            self.image = self.imgHittedRight if (self.status == "right") else self.imgHittedLeft
            self.hitFeedIndx -= 1
        # If hero is not shooting, not whiping, not jumping and not hurting, he should only be in normal status.
        else:
            if self.status == "left":
                self.image = self.imgLeftList[self.imgIndx]
                self.weapon.updateImg( self.weaponLeft )
                self.wpPos[0] = self.weaponR["normal"][0]
            elif self.status == "right":
                self.image = self.imgRightList[self.imgIndx]
                self.weapon.updateImg( self.weaponRight )
                self.wpPos[0] = 1 - self.weaponR["normal"][0]
            self.wpPos[1] = self.weaponR["normal"][1]
            self.wpPos[2] = self.weaponR["normal"][2]
        # Always renew the position of the weapon.
        self.weapon.updatePos( enemy.getPos(self, self.wpPos[0], self.wpPos[1]) )
        # Refresh hero.bag's buffer, delete 0 items and add new items.
        for item in self.bagBuf:
            if self.bag[item] == 0 and not item=="fruit":    # 如果有一项数值变为0，则从缓冲区删除（fruit除外）
                self.bagBuf.remove(item)
                self.bagPt -= 1
        for item in self.bag:
            if self.bag[item] > 0 and item not in self.bagBuf: # 如果有新的项，则添加到缓冲区
                self.bagBuf.append( item )
        # deal freezeCnt
        if self.freezeCnt > 0:
            self.freezeCnt -= 1
        else:
            self.speed = self.oriSpd   # 解冻
        # deal stuck if there is a trapper in effect.
        if self.trapper:
            if not pygame.sprite.collide_mask(self, self.trapper):
                self.trapper = None
            else:
                self.speed = self.oriSpd-2
        self.underWater = False
        # deal torchCnt and renew torch (if there is one).
        if self.torchCnt > 0:
            self.torchCnt -= 1         # 当火炬烧尽（torchCnt减为0，lumi也会自动减为0）
            self.lumi = self.torchCnt
            if self.lumi > 50:
                self.lumi = 50
            if not (delay%3):
                self.torchIndx = (self.torchIndx+1) % len(self.torchLeft)
                if self.status=="left":
                    self.torch.updateImg( self.torchLeft[self.torchIndx] )
                elif self.status=="right":
                    self.torch.updateImg( self.torchRight[self.torchIndx] )
            xR = self.torchR[self.torchIndx][0] if self.status=="left" else 1 - self.torchR[self.torchIndx][0]
            yR = self.torchR[self.torchIndx][1]
            self.torch.updatePos( enemy.getPos(self, xR, yR) )
        # 处理击退位移，如果值不为0的话。
        if abs(self.hitBack)>0:
            if self.hitBack>6:
                realBack = 6
            elif self.hitBack<-6:
                realBack = -6
            else:
                realBack = self.hitBack
            self.rect.left += realBack
            spurtCanvas.addSpatters( 1, [2, 3, 4], [8, 9, 10], (240,10,10,240), enemy.getPos(self,0.5,0.5) )
            for each in self.checkList:
                if ( pygame.sprite.collide_mask(self, each) ):
                    if each.category == "sideWall" or each.category == "blockStone" or (each.category == "door" and each.locked):
                        # 尝试身高坐标-6，再看是否还会碰撞。6以内的高度都可以自动踩上去
                        self.rect.top -= 6
                        if getCld(self, self.checkList, ["sideWall","blockStone"]):
                            self.rect.top += 6
                            self.rect.left -= realBack
                    elif each.category == "supAmmo" or each.category == "fruit" or each.category == "torch" or each.category == "medicine":
                        each.open(self)
            if self.hitBack>0:
                self.hitBack -= 1
            else:
                self.hitBack += 1
        # deal affection
        if self.affected == 0:
            self.affected = 1
            spurtCanvas.addSpatters( 12, [3, 4, 5], [10, 11, 12], (10,10,10,240), enemy.getPos(self, 0.5, 0.5) )
        elif self.affected>0:
            if self.whipCnt > 0:
                self.whipCnt -= 1
                if self.status == "left":
                    rht = self.rect.right
                    btm = self.rect.bottom
                    self.image = self.affWhipLeft
                    self.rect = self.image.get_rect()       # 获取新的图片的rect
                    self.rect.right = rht
                    self.rect.bottom = btm
                elif self.status == "right":
                    lft = self.rect.left
                    btm = self.rect.bottom
                    self.image = self.affWhipRight
                    self.rect = self.image.get_rect()
                    self.rect.left = lft
                    self.rect.bottom = btm
                # 每次刷新均吐出1个vomi
                spdX = 7-self.whipCnt//8
                if self.status == "left":
                    spd = [ -spdX, 0 ]
                    startX = 0
                elif self.status == "right":
                    spd = [ spdX, 0 ]
                    startX = 1
                vomi = Vomitus( enemy.getPos(self, startX, 0.35), spd, monsters, spurtCanvas )
                self.vomiList.add(vomi)
    
    def useItem(self, spurtCanvas):
        if self.bagBuf[self.bagPt] == "fruit":
            if ( self.bag["fruit"]>0 ) and self.affected<0:   # fruit 有可能为0，因此需要检查；感染时不能回血
                self.fruitSnd.play(0)
                self.bag["fruit"] -= 1
                self.health += 10
                if (self.health > self.full):
                    self.health = self.full
                spurtCanvas.addSpatters( 12, [3, 4, 5], [10, 12, 14], (100,255,100,240), enemy.getPos(self, 0.5, 0.5) )
        elif self.bagBuf[self.bagPt] == "medicine":
            if self.affected > 0:         # 不需检查是否有，只需检查是否感染
                self.fruitSnd.play(0)
                self.bag["medicine"] -= 1
                spurtCanvas.addSpatters( 12, [3, 4, 5], [10, 12, 14], (100,100,255,240), enemy.getPos(self, 0.5, 0.5) )
                # 恢复图片和相关属性值
                self.affected = -1
                self.imgLeftList = self.oriImgLeftList
                self.imgRightList = self.oriImgRightList
                self.imgJumpLeft = self.oriImgJumpLeft
                self.imgJumpRight = self.oriImgJumpRight
                self.wpJumpLeft = self.oriWpJumpLeft
                self.wpJumpRight = self.oriWpJumpRight
                self.imgHittedLeft = self.oriImgHittedLeft
                self.imgHittedRight = self.oriImgHittedRight
                self.imgIndx = 0
                self.weaponR = self.oriWeaponR
                self.jmpSnd = self.oriJmpSnd
                self.whipSnd = self.oriWhipSnd
        elif self.bagBuf[self.bagPt] == "torch":
            if self.affected < 0 and self.torchCnt <= 50:
                self.bag["torch"] -= 1
                self.torchCnt = 1800
                # Create the torch and attach to the hero.
                self.torchLeft = [ pygame.image.load("image/torchOn0.png").convert_alpha(), pygame.image.load("image/torchOn1.png").convert_alpha(), pygame.image.load("image/torchOn2.png").convert_alpha() ]
                self.torchRight = [ pygame.transform.flip(self.torchLeft[0], True, False), pygame.transform.flip(self.torchLeft[1], True, False), pygame.transform.flip(self.torchLeft[2], True, False) ]
                self.torchR = [ (0.6,0.64), (0.6,0.64), (0.6,0.64) ]    # 只保留左向时的位置信息
                self.torch = enemy.Ajunction( self.torchLeft[2], enemy.getPos(self, self.torchR[0][0], self.torchR[0][1]) )
                self.torchIndx = 0

    def renewCheckList(self, new):  # 动态调节checkList内的检测砖块，以减轻负担
        for each in self.checkList:
            if each.category == "lineWall" or each.category == "specialWall" or each.category == "column" or each.category == "house" or each.category == "roofWall":
                self.checkList.remove(each)
        for each in new:
            self.checkList.add(each)
    
    def freeze(self, decre):
        #if duration > self.freezeCnt:
        #    self.freezeCnt = duration
        self.freezeCnt = 120
        if self.speed == self.oriSpd:
            self.speed = self.oriSpd - decre
        self.haloCanvas.addHalo( "frzHalo", [380,420,460,500], (60,60,250,160), -1 )
        
    def affect(self):
        self.affSnd.play(0)
        self.affected = 0     # 置为0，以指示受到感染的瞬间
        self.torchCnt = 0     # 如果感染时有火炬，则将之熄灭
        self.imgLeftList = self.affLeftList
        self.imgRightList = self.affRightList
        self.weaponR["normal"] = self.weaponR["hide"]
        self.imgIndx = 0
        self.imgJumpLeft = self.affLeftList[0]
        self.imgJumpRight = self.affRightList[0]
        self.wpJumpLeft = self.wpHideLeft
        self.wpJumpRight = self.wpHideRight
        self.weaponR["jump"] = self.weaponR["hide"]
        self.imgHittedLeft = self.affLeftList[1]
        self.imgHittedRight = self.affRightList[1]
        # sound
        self.jmpSnd = self.affJmp
        self.whipSnd = self.affSnd
    
    def paint(self, screen):
        #按层级顺序画weapon和self
        if self.wpPos[2]==0:
            screen.blit( self.weapon.image, self.weapon.rect )
            screen.blit( self.image, self.rect )
        elif self.wpPos[2]==1:
            screen.blit( self.image, self.rect )
            screen.blit( self.weapon.image, self.weapon.rect )
        # 画火炬
        if self.torchCnt > 0:
            screen.blit( self.torch.image, self.torch.rect )
        if self.affected>0:
            for vomi in self.vomiList:
                vomi.move( self.rect.bottom )
                pygame.draw.circle(screen, vomi.color, vomi.pos, vomi.r)
    
    def lift(self, dist):
        self.rect.bottom += dist
        self.jmpPos[1] += dist
        for vomi in self.vomiList:
            vomi.pos[1] += dist
    
    def level(self, dist):
        self.rect.left += dist
        self.jmpPos[0] += dist
        for vomi in self.vomiList:
            vomi.pos[0] += dist

# -----------------------------------------------Assistant function for hero.fall
def getCld(core, group, cateList):
    spriteList = []
    cldList = pygame.sprite.spritecollide(core, group, False, pygame.sprite.collide_mask)
    for item in cldList:
        if item.category in cateList:
            spriteList.append(item)
    return spriteList

# ===================================================
class Vomitus(pygame.sprite.Sprite):

    def __init__(self, pos, spd, sprites, canvas): # 参数color:推荐带上透明度RGBA；参数speed:为一个二元组
        pygame.sprite.Sprite.__init__(self)
        self.r = choice( [3, 4, 5] )
        self.color = choice( [(80,80,120,255),(100,100,140,255)] )
        self.initPos = [ randint(pos[0]-2, pos[0]+2), randint(pos[1]-2, pos[1]+2) ]
        self.pos = self.initPos
        self.speed = spd
        self.cnt = 0
        self.tgts = sprites
        self.canvas = canvas
        self.hit = False
    
    def move(self, btLine):
        if self.pos[1]<btLine:
            self.cnt += 1
            if not self.cnt%2:
                if not self.hit:
                    for mons in self.tgts:
                        if mons.rect.left < self.pos[0] < mons.rect.right and mons.rect.top < self.pos[1] < mons.rect.bottom:
                            mons.hitted( 0.4, 0 )
                            if self.speed[0]>0:
                                mons.hitBack = 1
                            else:
                                mons.hitBack = -1
                            self.canvas.addSpatters(2, (1,2), (3,4), self.color, self.pos)
                            self.hit = True
                self.pos[0] += self.speed[0]
                self.pos[1] += self.speed[1]
                #self.canvas.addTrails( [2,3], [8, 9, 10], self.color, self.pos )
                if self.speed[1]<6 and not self.cnt%4:
                    self.speed[1] += 1
        else:
            self.canvas.addSpatters(2, (1,2), (3,4), self.color, self.pos)
            self.kill()
            del self
            return

# hero's ammo class ===============================================================
# Ammo类：各种英雄弹药的基本原型
class Ammo(pygame.sprite.Sprite):
    # Constructor
    # 参数hero为发射者的对象引用。
    def __init__(self, hero, i):
        pygame.sprite.Sprite.__init__(self)
        self.direct = hero.status
        self.hitSnd = pygame.mixer.Sound("audio/"+hero.name+"/hit.wav")
        self.checkList = pygame.sprite.Group()
        for each in hero.checkList:
            if each.category == "sideWall" or each.category == "lineWall":
                self.checkList.add(each)
        
        if hero.name == "knight":
            self.category = "bullet"  # bullet是最原始的子弹模型，函数简单、经典，没有花里胡哨的能力和效果
            self.push = 6
            self.speed = [8,0]
            bldNum = 6
        elif hero.name == "princess":
            self.category = "bullet"
            self.push = 7
            self.speed = [8,0]
            bldNum = 8
        elif hero.name == "prince":
            self.category = "bulletPlus"
            self.push = 5
            self.speed = [6,0]    # speed[1] can be interpreted as gravity.
            bldNum = 4
            self.move = javelinMove
            self.rotated = 0
        elif hero.name == "wizard":
            self.category = "bulletPlus"
            self.push = 5
            self.speed = [6,0]
            bldNum = 6
            self.imgList = [ pygame.image.load("image/"+hero.name+"/arrow_" + self.direct + "0.png").convert_alpha(), pygame.image.load("image/"+hero.name+"/arrow_" + self.direct + "1.png").convert_alpha() ]
            self.imgIndx = 0
            self.doom = -1
            self.move = wizFireMove
        elif hero.name == "huntress":
            self.category = "bulletPlus"
            self.push = 4
            self.speed = [7,0]
            bldNum = 2
            self.imgList = [ pygame.image.load("image/"+hero.name+"/arrow_" + self.direct + "0.png").convert_alpha(), pygame.image.load("image/"+hero.name+"/arrow_" + self.direct + "1.png").convert_alpha() ]
            self.imgIndx = 0
            self.attCnt = 0
            self.move = dartMove
        elif hero.name == "priest":
            self.category = "bulletPlus"
            self.push = 5
            self.speed = [5,0]
            bldNum = 5
            self.lastTgt = None
            self.newTgt = None
            self.move = lightMove
        elif hero.name == "king":
            self.category = "bullet"
            self.push = 4
            if i == 1:
                self.speed = [6,2]
            elif i==2:
                self.speed = [7,1]
            elif i==3:
                self.speed = [8,0]
            elif i==4:
                self.speed = [7,-1]
            elif i==5:
                self.speed = [6,-2]
            bldNum = 4

        if self.direct=="left":
            self.speed[0] = -self.speed[0]
        self.damage = hero.rDamage
        self.bldNum = bldNum
        self.owner = hero

        src = "image/"+hero.name+"/arrow_" + self.direct + ".png"
        self.image = pygame.image.load(src).convert_alpha() if not (hero.name=="wizard" or hero.name=="huntress") else self.imgList[0]
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        # initialize the position of the center of the screen
        self.rect.left = hero.rect.left
        self.rect.top = hero.rect.top+42

    def move(self, monsters, canvas, bg_size):
        self.rect.left += self.speed[0]
        self.rect.top += self.speed[1]
        if pygame.sprite.spritecollide(self, self.checkList, False, pygame.sprite.collide_mask) or self.rect.left>bg_size[0] or self.rect.right<0: # 撞上墙壁或砖块
            canvas.addSpatters(4, [1,2,3], [3,4,5], [20,20,20,240], enemy.getPos(self, 0.5, 0.5))
            self.erase()
            return False
        hitInfo = self.hitMonster(monsters)
        if hitInfo:
            self.erase()
            return hitInfo
    
    def hitMonster(self, monsters):
        for each in monsters:
            if pygame.sprite.collide_mask(self, each):
                self.hitSnd.play()
                # 对命中的怪物进行受伤操作，返回其是否死亡的真值：
                realPush = self.push if self.direct=="right" else -self.push
                dead = each.hitted(self.damage, realPush)
                if dead:
                    self.owner.score += each.score
                    deadInfo = each.category
                else:
                    deadInfo = False
                # 以下封装需要传递给主函数进行击中反馈的信息：
                # 确定击中点的坐标pos
                pos = [ 0, self.rect.top+self.rect.height//2 ]
                if self.direct == "left":
                    pos[0]=self.rect.left
                elif self.direct == "right":
                    pos[0]=self.rect.right
                self.owner.preyList.append( (self.direct, pos, each.bldColor, self.bldNum, deadInfo, each.exp) )
                return True

    def erase(self):
        self.kill()
        self.owner.arrowList.remove(self)
        del self
        return

    def lift(self, dist):
        self.rect.bottom += dist
    
    def level(self, dist):
        self.rect.left += dist

# varieties of function move() --------------------------------------------------------------
def javelinMove(self, delay, monsters, canvas, bg_size):
    self.rect.left += self.speed[0]
    self.rect.top += self.speed[1]
    if not ( delay % 3 ):         # 3的倍数才掉落
        # 旋转
        if self.rotated < 90:
            if self.speed[0]<0:
                rotate(self, 5)
            elif self.speed[0]>0:
                rotate(self, -5)
            self.mask = pygame.mask.from_surface(self.image)
            self.rotated += 5
        # 移动
        if self.speed[1] <= 8:
            self.speed[1] += 1    # 竖直速度增加
        elif self.speed[0]>0:
            self.speed[0] -= 1
    # 撞上墙壁或砖块，或者掉落出界 
    if pygame.sprite.spritecollide(self, self.checkList, False, pygame.sprite.collide_mask) or self.rect.top>=bg_size[1]:
        canvas.addSpatters(4, [1,2,3], [3,4,5], [180,180,180,240], enemy.getPos(self, 0.5, 0.5))
        self.erase()
        return False
    hitInfo = self.hitMonster(monsters)
    if hitInfo:
        self.erase()
        return hitInfo

# -----------------------------------------------------------------
def wizFireMove(self, delay, monsters, canvas, bg_size):
    self.rect.left += self.speed[0]
    self.rect.top += self.speed[1]
    canvas.addTrails( [1,2,3], [4, 5, 6], (250,160,120,240), enemy.getPos(self, choice([0.4,0.5,0.6]), choice([0.4,0.5,0.6])) )
    # 飞行状态下不产生伤害。
    if self.doom<0:
        # 如果撞上墙壁/砖块或monster，则爆炸。
        if pygame.sprite.spritecollide(self, self.checkList, False, pygame.sprite.collide_mask) or pygame.sprite.spritecollide(self, monsters, False, pygame.sprite.collide_mask):
            self.hitSnd.play(0)
            self.imgIndx = -1
            self.imgList = [ pygame.image.load("image/wizard/explo0.png").convert_alpha(), pygame.image.load("image/wizard/explo1.png").convert_alpha(),
                pygame.image.load("image/wizard/explo2.png").convert_alpha(), pygame.image.load("image/wizard/explo3.png").convert_alpha() ]
            self.doom = 0
            self.speed[0] = self.speed[0]//5
            return
        elif self.rect.left>bg_size[0] or self.rect.right<0:
            self.erase()
            return False
        if not delay%6:
            self.imgIndx = (self.imgIndx+1) % len(self.imgList)
            self.image = self.imgList[self.imgIndx]
    # 爆炸状态。在第一张爆炸图片时就计算伤害。
    else:
        if self.doom==1:
            self.mask = pygame.mask.from_surface(self.image)
            dmgMons = pygame.sprite.spritecollide(self, monsters, False, pygame.sprite.collide_mask)
            for each in dmgMons:    # 对命中的怪物进行受伤操作，返回其是否死亡的真值：
                realPush = self.push if self.direct=="right" else -self.push
                dead = each.hitted(self.damage, realPush)
                if dead:
                    self.owner.score += each.score
                    deadInfo = each.category
                else:
                    deadInfo = False
                pos = [ 0, self.rect.top+self.rect.height//2 ]
                if self.direct == "left":
                    pos[0]=self.rect.left
                elif self.direct == "right":
                    pos[0]=self.rect.right
                self.owner.preyList.append( (self.direct, pos, each.bldColor, self.bldNum, deadInfo, each.exp) )
        elif self.doom>=24:
            self.erase()
            return
        if not self.doom%6:
            if self.doom == 0:
                formerPos = [self.rect.left, self.rect.top+self.rect.height//2] if self.direct=="left" else [self.rect.right, self.rect.top+self.rect.height//2]
            else:
                formerPos = [self.rect.right-self.rect.width//2, self.rect.top+self.rect.height//2]
            self.imgIndx = (self.imgIndx+1) % len(self.imgList)
            self.image = self.imgList[self.imgIndx]
            self.rect = self.image.get_rect()
            self.rect.left = formerPos[0]-self.rect.width//2
            self.rect.top = formerPos[1]-self.rect.height//2
        self.doom += 1

# --------------------------------------------------------------
def dartMove(self, delay, monsters, canvas, bg_size):
    self.rect.left += self.speed[0]
    self.rect.top += self.speed[1]
    if not delay%5:
        self.imgIndx = (self.imgIndx+1) % len(self.imgList)
        self.image = self.imgList[self.imgIndx]
    if pygame.sprite.spritecollide(self, self.checkList, False, pygame.sprite.collide_mask) or self.rect.left>bg_size[0] or self.rect.right<0: # 撞上墙壁或砖块
        canvas.addSpatters(4, [1,2,3], [3,4,5], [20,20,20,240], enemy.getPos(self, 0.5, 0.5))
        self.erase()
        return False
    self.attCnt += 1
    if (self.attCnt % 4 == 0):      # 将伤害频率降低至1/4
        hitInfo = self.hitMonster(monsters)
        if hitInfo:
            return hitInfo

# --------------------------------------------------------------
def lightMove(self, delay, monsters, canvas, bg_size):
    # move the object, and generate a wake to its tail.
    self.rect.left += self.speed[0]
    self.rect.top += self.speed[1]
    canvas.addTrails( [1,2,3], [6, 7, 8], (255,192,203,240), enemy.getPos(self, choice([0.4,0.5,0.6]), choice([0.4,0.5,0.6])) )
    # No matter what phase it is, when hit wall, stop it.
    if pygame.sprite.spritecollide(self, self.checkList, False, pygame.sprite.collide_mask): # 撞上墙壁或砖块
        self.hitSnd.play(0)
        self.erase()
        # draw hit effect.
        canvas.addWaves( enemy.getPos(self, 0.5, 0.5), (255,192,203,240), 20, 40, 1 )
        canvas.addWaves( enemy.getPos(self, 0.5, 0.5), (0,0,0,0), 0, 40, 2 )
        return False
    elif self.rect.left>bg_size[0] or self.rect.right<0:
        self.erase()
        return False
    # Deal damage and continue the light when it hit monsters.
    for each in monsters:
        if pygame.sprite.collide_mask(self, each):
            if each == self.lastTgt:
                continue
            self.hitSnd.play(0)
            # 对命中的怪物进行受伤操作，返回其是否死亡的真值：
            realPush = self.push if self.direct=="right" else -self.push
            dead = each.hitted(self.damage, realPush)
            if dead:
                self.owner.score += each.score
                deadInfo = each.category
            else:
                self.lastTgt = each
                deadInfo = False
            pos = [ 0, self.rect.top+self.rect.height//2 ]
            if self.direct == "left":
                pos[0]=self.rect.left
            elif self.direct == "right":
                pos[0]=self.rect.right
            self.owner.preyList.append( (self.direct, pos, each.bldColor, self.bldNum, deadInfo, each.exp) )
            # draw hit effect.
            canvas.addWaves( enemy.getPos(self, 0.5, 0.5), (255,192,203,240), 20, 40, 1 )
            canvas.addWaves( enemy.getPos(self, 0.5, 0.5), (0,0,0,0), 0, 40, 2 )
            self.damage -= 4  # 击中后，伤害减少4点
            if self.damage>0:
                self.newTgt = None
                # find new tgt.
                for innerEach in monsters:
                    if not innerEach==self.lastTgt and innerEach.rect.bottom>0 and innerEach.rect.top<960:
                        dist = math.pow( enemy.getPos(innerEach,0.5,0.5)[0]-enemy.getPos(self,0.5,0.5)[0], 2 ) + math.pow( enemy.getPos(innerEach,0.5,0.5)[1]-enemy.getPos(self,0.5,0.5)[1], 2 )
                        if dist <= (180*180):
                            self.newTgt = innerEach
                            self.speed[0] = ( enemy.getPos(innerEach,0.5,0.5)[0] - enemy.getPos( self, 0.5, 0.5 )[0] )//10
                            self.speed[1] = ( enemy.getPos(innerEach,0.5,0.5)[1] - enemy.getPos( self, 0.5, 0.5 )[1] )//10
                            break
                # 遍历执行到这里说明没有符合距离要求的对象，故执行删除
                if not self.newTgt:
                    self.erase()
            else:
                self.erase()
            return True

# ==============辅助函数============
# ------------------------------
def rot_center(image, angle):
    """rotate an image while keeping its center and size"""
    orig_rect = image.get_rect()
    rot_image = pygame.transform.rotate(image, angle)
    rot_rect = orig_rect.copy()
    rot_rect.center = rot_image.get_rect().center
    rot_image = rot_image.subsurface(rot_rect).copy()
    return rot_image
# -------------
def rotate(sprite, degree):
    sprite.image = pygame.transform.rotate(sprite.image, degree)
    lft = sprite.rect.left
    top = sprite.rect.top
    sprite.rect = sprite.image.get_rect()
    sprite.rect.left = lft
    sprite.rect.top = top

# =========================================================
# ----- 脚本英雄。冒险模式下的人质跟班、训练营的训英雄练师 ----
# =========================================================
class Follower(Hero):

    master = None
    secFlag = False
    category = "follower"

    def __init__(self, bg_size, blockSize, heroNo, master, pos):
        Hero.__init__(self, bg_size, blockSize, heroNo, {}, master.dmgReduction)
        self.master = master
        self.secFlag = False
        self.rect.left = pos[0]
        self.rect.bottom = pos[1]
        self.onlayer = master.onlayer

    def decideAction(self, delay, heightList, monsters, exit):
        # 判断是否抵达最终出口。
        if exit.category=="exit" and not exit.locked and pygame.sprite.collide_mask(self, exit):
            return True
        # 判断是否需要二段跳。
        if ( self.secFlag ) and ( self.k1==self.kNum) and self.k2==0:
            self.secFlag = False
            self.k2 = 1
        # 判断是否要砍怪
        for each in monsters:
            if pygame.sprite.collide_mask(self, each):
                self.whip()
        # 如果在master之上，则下跳一层。
        if self.onlayer>self.master.onlayer:
            if not delay%80:
                self.shiftLayer(-2, heightList)
        else:
            # 否则若处于同一层或在master之下，则跳跃，并将二段跳的标志设为true。
            if self.onlayer<self.master.onlayer:
                if not self.trapper and self.aground and ( self.k1 == 0 ):
                    self.secFlag = True
                    self.k1 = 1
            if self.rect.left>=self.master.rect.right-10:
                self.moveX(delay, "left")
            elif self.rect.right<=self.master.rect.left+10:
                self.moveX(delay, "right")
        return False

    def freeze(self, decre):
        #if duration > self.freezeCnt:
        #    self.freezeCnt = duration
        self.freezeCnt = 120
        if self.speed == self.oriSpd:
            self.speed = self.oriSpd - decre

# ========================================
class Trainer(Hero):

    rival = None
    secFlag = False
    halt = False     # The flag that decides trainer's status of charging or waiting.
    category = "trainer"

    def __init__(self, bg_size, blockSize, heroNo, rival, pos):
        Hero.__init__(self, bg_size, blockSize, heroNo, {}, rival.dmgReduction)
        self.rival = rival
        self.secFlag = False
        self.rect.left = pos[0]
        self.rect.bottom = pos[1]
        self.onlayer = 4
        self.free = False

    def decideAction(self, delay, heightList, allElements):
        # 判断是否需要二段跳。
        if ( self.secFlag ) and ( self.k1==self.kNum) and self.k2==0:
            self.secFlag = False
            self.k2 = 1
        # 判断是否要水平移动。
        if not delay%10 and random()<0.1:
            self.free = not self.free
        if self.free:
            if self.rect.left>=self.rival.rect.right-12:
                self.moveX(delay, "left")
            elif self.rect.right<=self.rival.rect.left+12:
                self.moveX(delay, "right")
            # 如果在master之上，则下跳一层。
            if self.onlayer>self.rival.onlayer:
                if not delay%60:
                    self.shiftLayer(-2, heightList)
            # 否则若处于master之下，则跳跃，并将二段跳的标志设为true。
            elif self.onlayer<self.rival.onlayer:
                if not self.trapper and self.aground and ( self.k1 == 0 ):
                    self.secFlag = True
                    self.k1 = 1
        # 判断是否要whip.
        if pygame.sprite.collide_mask(self, self.rival):
            self.whip()
        # 判断是否要shoot:在shoot的攻击范围内且距离足够远。
        rvPos = enemy.getPos(self.rival, 0.5, 0.5)
        if not delay%60 and ( self.rect.bottom > rvPos[1] > self.rect.top ):
            if ( rvPos[0] > self.rect.right ) and ( rvPos[0]-self.rect.right > 36 ):
                self.moveX(self.imgSwt, "right")
            elif ( rvPos[0] < self.rect.left ) and ( rvPos[0]-self.rect.left < -36 ):
                self.moveX(self.imgSwt, "left")
            else:
                return
            self.shoot(allElements, delay)
            self.arrow = 12

    def freeze(self, decre):
        self.freezeCnt = 120
        if self.speed == self.oriSpd:
            self.speed = self.oriSpd - decre
