import sys
import math
from random import *

import pygame
from pygame.locals import *

import enemy
import mapManager
import myHero
import plotManager

"""有3个透明画布（surface）在所有元素之上，一是用于画自然元素（如雪，雨）；第二个是画全屏效果的；第三个是用于画击中时的血的溅射效果"""

# =============================================================================================================
# -------------------------------------------------------------------------------------------------------------
# ------------------------------------ stage running class ----------------------------------------------------
# -------------------------------------------------------------------------------------------------------------
# =============================================================================================================
class AdventureModel():
    
    allElements = None    # a big Group for all sprites in this stage
    bg_size = ()          # 屏幕的宽高（二元组）
    towerD = 10           # 单人模式为10（默认），双人模式为11
    towerH = 160
    blockSize = 72
    ctrY = -130           # 右上角控件的水平偏移位置（像素）
    language = 0          # 初始默认为英文，可在构造函数中设定
    fntSet = []
    remindedArea = []
    win = False           # 标记最终结果

    stg = 1
    curArea = 0
    scrnSpd = 4           # 屏幕上下移动的速度，单位像素
    delay = 120           # 延时变量，用于在不影响游戏正常运行的情况下给图片切换增加延迟
    msgList = []          # 用于存储消息的列表（列表包含列表）：[ [heroName, incident, cntDown (,sticker)], ... ]
    subsList = []         # The buffer containing those newly opened chests' substances.
    vibration = 0         # Cnt to indicate the vibration of the screen.
    # 双人模式下的特殊变量
    frontier = 0          # 两者中的较高像素值
    frnLayer = 0          # 两者中的较高层数

    heroes = []           # 保存hero对象的引用；可能为1个或2个
    tomb = []
    tower = None
    screen = None         # 保存屏幕对象的引用
    clock = None
    towerBG = None        # 当前关卡的背景jpg
    towerBGRect = None
    nature = None         # 自然元素的画布
    spurtCanvas = None    # 击中反馈溅血的画布（比你想象中的更万能！不只是能画血噢😄嘻嘻）
    haloCanvas = None     # boss出现时的全屏阴影画布
    plotManager = None    # 管理剧情信息

    msgStick = {}
    hostage = None
    natON = True          # 自然装饰效果是否开启
    music = None          # bgm （Sound对象）
    controller = []       # 右上角控件
    controllerOn = []
    paused = True
    musicOn = True
    setBG = False
    gameOn = True         # 游戏循环标志，默认为True，玩家点击退出或游戏结束时变为False

    # 本model构造函数说明：
    # heroInfoList 是一个列表，列表的每一项是一个hero的信息，每一项信息包括heroNo和该英雄的keyDic。即形如：[ (heroNo1, keyDic1), (heroNo2, keyDic2) ]。可为1-2个。
    def __init__(self, stg, areas, heroList, bg_size, screen, language, fntSet, musicObj, diffi, natON, monsDic, VHostage):
        
        self.allElements = pygame.sprite.Group()
        self.stg = stg
        self.screen = screen
        self.bg_size = bg_size
        self.language = language
        self.fntSet = fntSet
        self.natON = natON
        self.monsAcc = monsDic    # 当前关卡的所有怪物名及其VMons对象组成的字典
        # 右上角的控件图片 及其他控制器
        self.controller = [pygame.image.load("image/quit.png").convert_alpha(), 
            pygame.image.load("image/BGMusic.png").convert_alpha(), pygame.image.load("image/mute.png").convert_alpha()]
        self.controllerOn = [pygame.image.load("image/quitOn.png").convert_alpha(), 
            pygame.image.load("image/BGMusicOn.png").convert_alpha(), pygame.image.load("image/muteOn.png").convert_alpha()]
        self.aimImg = pygame.image.load("image/aim.png").convert_alpha()
        self.clock = pygame.time.Clock()
        self.music = musicObj
        self.msgStick = { "msg":pygame.image.load("image/tip.png").convert_alpha(), 
            "dlg":pygame.image.load("image/stg"+str(self.stg)+"/preFig.png").convert_alpha() }
        # Initialize game canvas.
        self.gameOn = True
        self.paused = True
        self.setBG = False
        self.nature = None
        if self.natON:
            if self.stg == 1:
                self.nature = mapManager.Nature(self.bg_size, self.stg, 8, 1)
            elif self.stg == 2:
                self.nature = mapManager.Nature(self.bg_size, self.stg, 1, 0)
            elif self.stg == 3:
                self.nature = mapManager.Nature(self.bg_size, self.stg, 8, 1)
            elif self.stg == 4 or self.stg == 7:
                self.nature = mapManager.Nature(self.bg_size, self.stg, 18, 0)
            elif self.stg == 5:
                self.nature = mapManager.Nature(self.bg_size, self.stg, 10, -1)
            elif self.stg == 6:
                self.nature = mapManager.Nature(self.bg_size, self.stg, 8, 1)
        self.spurtCanvas = mapManager.SpurtCanvas( self.bg_size )
        self.haloCanvas = mapManager.HaloCanvas( self.bg_size )
        # Select and overlap the moveMons() method.
        if self.stg == 1:
            self.moveMons = moveMonsStg1
        elif self.stg == 2:
            self.moveMons = moveMonsStg2
        elif self.stg == 3:
            self.moveMons = moveMonsStg3
        elif self.stg == 4:
            self.moveMons = moveMonsStg4
        elif self.stg == 5:
            self.moveMons = moveMonsStg5
        elif self.stg == 6:
            self.moveMons = moveMonsStg6
        elif self.stg == 7:
            self.moveMons = moveMonsStg7
        # Plot Manager & Effect Manager.
        self.plotManager = plotManager.Dialogue( stg )
        self.effecter = plotManager.Controller(bg_size)

        self.remindedArea = [0]    # 存储已加载过关卡对话的区域。
        for msg in self.plotManager.getPre(self.curArea):
            self.msgList.append( [ "message", msg, 150, self.msgStick["dlg"] ] )
        # tower背景图片 及其移动速度
        self.towerBG = pygame.image.load( "image/stg"+ str(self.stg) +"/towerBG.jpg" ).convert()
        self.towerBGRect = self.towerBG.get_rect()
        self.towerBGRect.left = (self.bg_size[0]-self.towerBGRect.width) // 2
        self.towerBGRect.top = (self.bg_size[1]-self.towerBGRect.height) // 2
        if diffi == 0:
            dmgReduction = 0.6  # 伤害减轻
            enemy.Monster.healthBonus = 0.8
            doubleP = 0.4       # 宝箱爆率翻倍的概率
            self.towerH = 40    # 每区域层数
        elif diffi == 1:
            dmgReduction = 1
            enemy.Monster.healthBonus = 1
            doubleP = 0.2
            self.towerH = 60
        elif diffi == 2:
            dmgReduction = 1.2
            enemy.Monster.healthBonus = 1.5
            doubleP = 0
            self.towerH = 80
        # create the map (note: for good influency of the screen, please no more than 240 layers) --------------- 🏯
        if len(heroList)>1:
            self.towerD = 11
        oriPos = ( (self.bg_size[0] - self.towerD*self.blockSize) // 2, self.bg_size[1]-self.blockSize )
        if self.stg==1 or self.stg==6:
            specialOn = (False, True, True)
        else:
            specialOn = (True, True, True)
        # Build 3 areas and link them as one big tower.
        tower0 = mapManager.AdventureTower(oriPos, self.blockSize, self.towerD, self.towerH, self.stg, 0, specialOn[0], doubleP)
        oriPos = tower0.generateMap()
        tower1 = mapManager.AdventureTower(oriPos, self.blockSize, self.towerD, self.towerH, self.stg, 1, specialOn[1], doubleP)
        oriPos = tower1.generateMap()
        tower2 = mapManager.AdventureTower(oriPos, self.blockSize, self.towerD, self.towerH, self.stg, 2, specialOn[2], doubleP)
        tower2.generateMap()
        self.areaList = [tower0, tower1, tower2]
        self.curArea = 0
        self.tower = self.areaList[self.curArea]
        self.hostage = None
        # create the hero -----------------🐷
        self.tomb = []
        self.heroes = []
        for each in heroList:      # 根据传入的VHero参数信息生成hero
            if each[2] == "p1":
                propPos = { "slot":(-300,290), "ammo":(-335,268), "bag":(-230,268), "health":(115,660) }
                initPos = (tower0.boundaries[0]-self.blockSize-10, bg_size[1]-2*self.blockSize)
            elif each[2] == "p2":
                propPos = { "slot":(180,290), "ammo":(145,268), "bag":(250,268), "health":(595,660) }
                initPos = (tower0.boundaries[0]-self.blockSize+10, bg_size[1]-2*self.blockSize)
            hero = myHero.Hero(initPos, self.blockSize, each[0], propPos, dmgReduction )
            hero.keyDic = each[1]
            hero.haloCanvas = self.haloCanvas  # 受伤反馈画布
            self.heroes.append(hero)
            self.allElements.add(hero)
        # Initialize towers and heroes.
        for tower in self.areaList:
            # add elems of each area to the allElements and hero's checkList.
            for key in tower.groupList:
                for brick in tower.groupList[key]:
                    self.allElements.add( brick )    # 加入walls
                    if brick.category == "sideWall" or (brick.category == "baseWall" and brick.coord[1]==0):
                        for hero in self.heroes:
                            hero.checkList.add( brick )
            for sup in tower.chestList:
                if sup.category == "hostage":        # 选出hostage挂在self.hostage上，并设置其VHero所需的信息。
                    self.hostage = sup
                    self.hostage.hp = VHostage.hp
                    self.hostage.pw = VHostage.pw
                    self.hostage.dmg = VHostage.dmg
                    self.hostage.no = VHostage.no
                    self.hostage.lvl = VHostage.lvl
                self.allElements.add(sup)            # 加入supply
                for hero in self.heroes:
                    hero.checkList.add(sup)
            for elem in tower.elemList:
                self.allElements.add(elem)
                for hero in self.heroes:
                    hero.checkList.add(elem)
            # create natural impediments and monsters for each area.
            if (self.stg==1):
                if tower.area == 0:
                    makeMons( 0, tower.layer, 0.7, 1, tower )
                elif tower.area == 1:
                    makeMons( 0, tower.layer, 0.65, 1, tower )
                    makeMons( 2, tower.layer, 0.45, 2, tower )
                elif tower.area == 2:
                    makeMons( 0, tower.layer, 0.55, 1, tower )
                    makeMons( 2, tower.layer, 0.4, 2, tower )
                    makeMons( 20, 22, 1, 3, tower )    # boss必须出现，所以概率给1；层数给指定的层数21(20~22之间)
                    for i in range(2):
                        f = enemy.InfernoFire(self.bg_size)
                        self.allElements.add(f)
            elif (self.stg==2):
                if tower.area == 0:
                    makeMons( 0, tower.layer, 0.6, 1, tower )
                else:
                    makeMons( 0, tower.layer, 0.6, 1, tower )
                    makeMons( 2, tower.layer, 0.4, 2, tower )
                    if tower.area == 2:
                        makeMons( 20, 22, 1, 3, tower )
            elif (self.stg==3):
                if tower.area == 0:
                    makeMons( 2, tower.layer, 0.8, 3, tower )
                    makeMons( 2, tower.layer, 0.6, 2, tower )
                elif tower.area >= 1:
                    makeMons( 0, tower.layer, 0.6, 1, tower )
                    makeMons( 2, tower.layer, 0.5, 2, tower )
                    makeMons( 2, tower.layer, 0.6, 3, tower )
                    if tower.area == 2:
                        makeMons( 20, 22, 1, 4, tower )
            elif (self.stg==4):
                if tower.area == 0:
                    makeMons( 0, tower.layer, 0.65, 1, tower )
                    makeMons( 2, tower.layer, 0.55, 2, tower )
                    #makeMons( 4, 6, 1, 4, tower )
                if tower.area >= 1:
                    makeMons( 0, tower.layer, 0.6, 1, tower )
                    makeMons( 2, tower.layer, 0.45, 2, tower )
                    makeMons( 4, tower.layer, 0.5, 3, tower )
            elif (self.stg==5):
                makeMons( 0, tower.layer, 0.7, 1, tower )
                makeMons( 2, tower.layer, 0.6, 2, tower )
                #makeMons( 6, 8, 1, 3, tower )
            elif (self.stg==6):
                makeMons( 0, tower.layer, 0.7, 1, tower )
                makeMons( 2, tower.layer, 0.7, 2, tower )
                if tower.area == 2:
                    makeMons( 20, 22, 1, 3, tower )
            elif (self.stg==7):
                makeMons( 0, tower.layer, 0.7, 1, tower )
            # 随机指定任意个区域封锁者
            i = 0
            for minion in tower.monsters:
                i += 1
                self.allElements.add(minion)
                if random()<0.1 or ( i==len(tower.monsters) and len(tower.goalieList)==0 ):
                    tower.goalieList.add( minion )

    def go(self, themeColor, horns, heroBook, stgManager, diffi):
        
        self.music.play(-1)
        self.screen.fill( (0, 0, 0) )
        self.screen.blit( self.towerBG, self.towerBGRect )
        if self.stg==2:
            c = enemy.Column(self.bg_size, self.tower.groupList)
            self.allElements.add(c)
        elif self.stg==3:
            mist = enemy.Mist(self.bg_size)
        elif self.stg==4:
            ooze = enemy.Ooze(self.bg_size, self.blockSize, self.fntSet[0][1]) # 中文
        elif self.stg==5:
            blizzard = enemy.blizzardGenerator(self.bg_size)
        for item in self.allElements:
            self.screen.blit( item.image, item.rect )
        while self.gameOn:
            if not self.paused: # 若未 pause.
                # respond to the player's ongoing keydown event.
                # get the list including the boolean status of all keys:
                key_pressed = pygame.key.get_pressed()
                for hero in self.heroes:
                    if hero.category == "follower":
                        continue
                    if key_pressed[ hero.keyDic["leftKey"] ]:
                        hero.moveX( self.delay, "left" )
                    elif key_pressed[ hero.keyDic["rightKey"] ]:
                        hero.moveX( self.delay, "right" )
                self.frontier = self.bg_size[1]
                self.frnLayer = 0
                for hero in self.heroes:
                    self.frontier = min(self.frontier, hero.rect.bottom)
                    self.frnLayer = max(self.frnLayer, hero.onlayer)
                
                # move all if the screen need to be adjusted.
                gap = ( self.bg_size[0] - (self.tower.boundaries[0]+self.tower.boundaries[1]) ) //2
                if gap:
                    lvl = min(gap, 10) if gap>0 else max(gap, -10)
                    for tower in self.areaList:
                        tower.level( lvl )
                    for elem in self.allElements:
                        elem.level( lvl )
                if ( self.tower.getTop(self.frnLayer) < self.bg_size[1]*0.42 ):
                    for elem in self.allElements:
                        elem.lift(self.scrnSpd)
                    for tower in self.areaList:
                        tower.lift(self.scrnSpd)
                    if self.stg==4:
                        ooze.lift(self.scrnSpd)
                elif ( self.tower.getTop(self.frnLayer)+self.blockSize > self.bg_size[1]*0.7 ) and ( self.tower.getTop(-1)+2*self.blockSize>=self.bg_size[1] ) :
                    for elem in self.allElements:
                        elem.lift(-self.scrnSpd)
                    for tower in self.areaList:
                        tower.lift(-self.scrnSpd)
                    if self.stg==4:
                        ooze.lift(-self.scrnSpd)
                
                # check hero's jump and fall:
                for hero in self.heroes:
                    # 若处于跳跃状态，则执行跳跃函数
                    if hero.k1 > 0:
                        hero.jump( self.tower.getTop(hero.onlayer+1) )
                    # 否则，执行掉落函数
                    else:
                        fallChecks = self.tower.groupList[str(hero.onlayer-1)]
                        if self.stg==2 and hero.rect.bottom <= (c.rect.top+2):   # 英雄的位置比石柱高时，在调用hero.fall进行掉落检查时加入石柱，调用完成后会自动清除
                            hero.checkList.add( c )
                        hero.fall(self.tower.getTop(hero.onlayer-1), fallChecks, self.stg, self.tower.heightList)
                
                # repaint all elements
                self.screen.blit( self.towerBG, self.towerBGRect )
                for item in self.allElements:
                    self.moveMons( self, item, self.heroes )       # 分关卡处理所有的敌人（自然阻碍和怪兽）。由于是覆盖的函数，需要给self参数。
                    if item.category=="sideWall" or item.category=="lineWall" or item.category=="baseWall" or item.category=="specialWall" or \
                        item.category == "supAmmo" or item.category == "fruit" or item.category == "torch" or item.category == "medicine":
                        item.paint(self.screen)
                    elif item.category == "lineDecor":
                        item.alter()
                        self.screen.blit(item.image, item.rect)
                    elif item.category == "hostage" or item.category == "door" or item.category == "notice" or item.category == "exit":
                        item.paint(self.screen, self.spurtCanvas, self.fntSet[0], self.language)
                    # 处理投掷物：投掷物的move函数将返回三种情况：1.返回False，表示未命中；2.返回包含两个元素的元组，含义分别为投掷物的方向“right”或“left”，以及投掷物击中的坐标（x，y）；
                    # 3.返回包含三个元素的元组，第三个元组为标志命中目标是否死亡。
                    elif item.category=="bullet" or item.category=="bulletPlus":
                        arrCheck = self.tower.monsters
                        if self.stg==2:        # 第二关加上障碍物大石头、蛛网
                            for elem in self.tower.elemList:
                                #if elem.category=="webWall" and not elem.valid:
                                #    continue
                                arrCheck.add(elem)
                        if item.category=="bullet":
                            item.move(arrCheck, self.spurtCanvas, self.bg_size)
                        else:
                            item.move(item, self.delay, arrCheck, self.spurtCanvas, self.bg_size) # 这里还要传入投掷物本身
                        self.screen.blit(item.image, item.rect)
                    elif item.category == "follower":
                        win = item.decideAction(self.delay, self.tower.heightList, self.tower.monsters, self.tower.porter)
                        if win:
                            self.music.stop()
                            self.gameOn = False
                            self.win = True
                            #return [True, self.heroes+self.tomb]         # win: return True and exp
                        drawHealth( self.screen, item.rect.left+item.rect.width//2, item.rect.top-8, 0, 8, item.health, item.full, 1 )
                        item.paint(self.screen)
                
                for hero in self.heroes:
                    # decide the image of Hero
                    hero.checkImg( self.delay, self.spurtCanvas, self.tower.monsters )
                    hero.paint( self.screen )
                    if len(hero.jmpInfo)>0:        # 绘画跳跃烟尘效果
                        self.screen.blit( hero.jmpInfo[0], hero.jmpInfo[1] )
                    # 从hero的preyList信息列表中取击中信息。
                    for hitInfo in hero.preyList:
                        self.spurtCanvas.addSpatters( hitInfo[3], [2, 3, 4], [10, 11, 12], hitInfo[2], hitInfo[1] )
                        if hitInfo[4] and (hitInfo[4] in self.monsAcc):   # 击中的目标死亡
                            self.spurtCanvas.addSouls( hitInfo[5], [5, 6], [15, 18, 20], (210,210,255,250), hitInfo[1], hero )
                            if self.monsAcc[ hitInfo[4] ].collec():       # 尝试搜集该怪物。若已收集，则返回False；否则收集成功，返回True。
                                self.msgList.append( ["message", ("New monster collected to Collection!","新的怪物已收集至图鉴！"), 150, self.msgStick["msg"] ] )
                    hero.preyList = []  # 每次刷新读取所有信息后，将list重置为空表
                    # 从hero的eventList事件列表中取事件信息，并将these newly opened chests加入self.subsList中。
                    for item in hero.eventList:
                        if item=="exp":
                            self.msgList.append( [hero, item, 60] )
                        else:
                            self.msgList.append( [hero, item, 60] )
                            self.subsList.append(item)
                    hero.eventList = []

                # 第三关增加游戏难度 ---
                if ( self.stg==3 ):
                    sprites = [self.tower.porter]
                    for hero in self.heroes:
                        sprites.append(hero)
                    mist.renew( self.delay, sprites )
                    self.screen.blit( mist.canvas, mist.canvasRect )
                    if self.curArea >= 1:
                        mist.pervade = True
                    if not ( self.delay % 60 ):   # 每隔一段时间在屏幕范围内生成一波骷髅兵
                        for line in range( self.frnLayer-3, self.frnLayer+3, 2 ):  # 起点，终点，跨度，变hero的偶数为groupList的奇数（hero.onlayer +- 4 - 1）
                            if ( 0 < line < self.towerH-1 ) and len(self.tower.monsters) < 120 and ( random() < 0.1 ):
                                skeleton = enemy.Skeleton(self.tower.groupList[str(line)], self.blockSize, line)
                                self.tower.monsters.add(skeleton)
                                self.allElements.add(skeleton)
                elif (self.stg==4):
                    sprites = []
                    for hero in self.heroes:
                        sprites.append(hero)
                    for each in self.tower.monsters:
                        sprites.append(each)
                    ooze.rise( self.delay, self.screen, sprites, self.spurtCanvas )
                    if ( self.frnLayer>=30 ) and ( ooze.speed<=self.curArea+2 ):      # 每个area的速度上限，如area0上限为2，area1上限为3.
                        ooze.speed += 1
                        self.msgList.append( [ "message", ("The Ooze speeds up rising!","泥沼上涨速度加快！"), 150, self.msgStick["msg"] ] )
                elif (self.stg==5):
                    blizzard.storm(self.heroes, self.nature.wind, self.spurtCanvas)
                
                if self.vibration > 0:
                    if (self.vibration % 2 == 0):
                        for elem in self.allElements:
                            elem.lift(4)
                            elem.level(4)
                    elif (self.vibration % 2 == 1):
                        for elem in self.allElements:
                            elem.lift(-4)
                            elem.level(-4)
                    self.vibration -= 1

                # 绘制三层画布
                if self.spurtCanvas:
                    self.spurtCanvas.update(self.screen)
                if self.haloCanvas:
                    self.haloCanvas.update( self.delay, self.screen )
                if self.nature:
                    self.nature.update(self.screen)
                # 目标怪物
                if self.delay <= 120:
                    for each in self.tower.goalieList:
                        self.addSymm( self.aimImg, enemy.getPos(each,0.5,0.5)[0]-480, enemy.getPos(each,0.5,0.5)[1]-360)
                # 在迷雾/画布之后再画获得的补给品，否则会被迷雾/画布盖掉
                for item in self.subsList:
                    if not item.reached:
                        item.subsMove()
                        self.screen.blit(item.substance, item.subsRect)
                    else:
                        self.subsList.remove(item)

                # draw hero status info
                for hero in self.heroes:
                    if hero.category == "follower":
                        continue
                    self.addSymm( hero.slot, hero.propPos["slot"][0], hero.propPos["slot"][1] )
                    self.addSymm( hero.brand, hero.propPos["slot"][0]-110, hero.propPos["slot"][1] )
                    self.addTXT( ("Level "+str(hero.lvl), "等级"+str(hero.lvl)), 0, (255,255,255), hero.propPos["slot"][0]-100, hero.propPos["slot"][1]+24 )
                    self.addSymm( hero.ammoImg, hero.propPos["ammo"][0], hero.propPos["ammo"][1] )
                    self.addTXT( (str(hero.arrow), str(hero.arrow)), 1, (255,255,255), hero.propPos["ammo"][0]+36, hero.propPos["ammo"][1] )
                    # 画背包物品
                    if len(self.effecter.SSList)==0:
                        if len(hero.bagBuf)>1:
                            nxtItem = hero.bagBuf[(hero.bagPt + 1) % len(hero.bagBuf)]
                            nxtRect = hero.bagImgList[nxtItem].get_rect()
                            nxtImg = pygame.transform.smoothscale(hero.bagImgList[nxtItem], ( int(nxtRect.width*0.7), int(nxtRect.height*0.7) ) )
                            nxtRect = self.addSymm( nxtImg, hero.propPos["bag"][0]-20, hero.propPos["bag"][1]+10 )
                        item = hero.bagBuf[hero.bagPt]
                        bagRect = self.addSymm( hero.bagImgList[item], hero.propPos["bag"][0], hero.propPos["bag"][1] )
                        self.addTXT( (str(hero.bag[item]),str(hero.bag[item])), 1, (255,255,255), hero.propPos["bag"][0]+36, hero.propPos["bag"][1] )
                    drawHealth( self.screen, hero.propPos["health"][0], hero.propPos["health"][1], 20, 18, hero.health, hero.full, 2 )
                
                pos = pygame.mouse.get_pos()
                bannerTuple = self.renderBanner(pos)
                self.showMsg(bannerTuple[2])   # 将第3个section（rect）传递给showMsg函数。
                menu = bannerTuple[3]

                # check big events.
                # 因为有的怪物（如戈仑石人）存在死亡延迟，故在杀死怪物的瞬间判断会不准确。故放在外面一直侦听。
                if self.tower.area<=2 and len(self.tower.goalieList)==0 and self.tower.porter.locked: #（限于前三个区域）
                    self.tower.porter.unlock()
                    self.msgList.append( [ "message", ("The Area is unblocked!","区域封锁已解除！"), 150, self.msgStick["msg"] ] )
                for hero in self.heroes:
                    if ( hero.rect.top >= self.bg_size[1] ):
                        hero.hitted(2, 0)
                    if ( hero.health <= 0 ):
                        self.heroes.remove(hero)
                        self.tomb.append(hero)
                        # 有一名英雄死亡，检查其死亡后heroes列表中的英雄情况。
                        if hero.category=="follower":  # 失败情况1：要营救的对象死亡
                            self.music.stop()
                            self.gameOn = False
                            self.win = False
                            return [False, self.heroes+self.tomb]
                        else:
                            if self.hostage:               # 失败情况2：当营救对象未加入时，所有玩家死亡
                                if (len(self.heroes)<=0):  # 死亡的不是营救对象，但所有玩家死亡
                                    self.music.stop()
                                    self.gameOn = False
                                    self.win = False
                                    #return [False, self.heroes+self.tomb]         # died: return False
                            else:
                                if (len(self.heroes)<=1):  # 失败情况3：营救对象在队列中，除ta以外的所有玩家死亡
                                    self.music.stop()
                                    self.gameOn = False
                                    self.win = False
                                    #return [False, self.heroes+self.tomb]       # died: return False
                    # 进入下一tower。
                    if hero.category == "follower":
                        continue
                    if hero.onlayer>=self.tower.layer and enemy.getPos(hero, 0.5, 0.5)[0]>self.tower.boundaries[1]+2*self.blockSize:
                        self.curArea += 1
                        self.tower = self.areaList[self.curArea]
                        hero.onlayer = 0
                        # 若进入的是新区域，则将区域对话加入消息列表。
                        if self.curArea not in self.remindedArea:
                            self.remindedArea.append(self.curArea)
                            for msg in self.plotManager.getPre(self.curArea):
                                self.msgList.append( [ "message", msg, 150, self.msgStick["dlg"] ] )
                    # 返回上一tower。
                    elif hero.onlayer<=0 and enemy.getPos(hero, 0.5, 0.5)[0]<self.tower.boundaries[0]-2*self.blockSize:
                        self.curArea -= 1
                        self.tower = self.areaList[self.curArea]
                        hero.onlayer = self.tower.layer
                
            else:                
                # 透明灰色打底
                if not self.setBG:
                    self.setBG = True
                    drawRect( 0, 0, self.bg_size[0], self.bg_size[1], (0,0,0,180), self.screen )
                    tip = choice( self.plotManager.tips )
                # 加Board to represent some tips.
                self.addSymm( pygame.image.load("image/cardBoard.png"), 0, 0 )
                self.addSymm( pygame.image.load("image/Enter.png").convert_alpha(), 0, -60 )
                self.addTXT( ["continue/pause","继续/暂停"], 0, (20,20,20), 0, -30)
                # tip area. 
                drawRect( self.bg_size[0]//2-240, self.bg_size[1]//2+20, 480, 100, (210,180,120,120), self.screen )
                topAlign = 50
                for line in tip:
                    self.addTXT( line, 0, (0,0,0), 0, topAlign )
                    topAlign += 20
                
                # handle controllers images and click events -----------------------------------
                home = self.addSymm( self.controller[0], -260, self.ctrY)
                BGMusic = self.addSymm( self.controller[1], -200, self.ctrY) if self.musicOn else self.addSymm( self.controller[2], -200, self.ctrY)
                pos = pygame.mouse.get_pos()
                if ( home.left < pos[0] < home.right ) and ( home.top < pos[1] < home.bottom ):  # 退出（放弃）当前关卡
                    home = self.addSymm( self.controllerOn[0], -260, self.ctrY)
                    self.addTXT( ("quit","放弃"), 0, (60,60,60), -260, self.ctrY+40 )
                elif ( BGMusic.left < pos[0] < BGMusic.right ) and (BGMusic.top < pos[1] < BGMusic.bottom ):
                    if self.musicOn:
                        BGMusic = self.addSymm( self.controllerOn[1], -200, self.ctrY)
                        self.addTXT( ("music off","关闭音乐"), 0, (60,60,60), -200, self.ctrY+40 )
                    else:
                        BGMusic = self.addSymm( self.controllerOn[2], -200, self.ctrY)
                        self.addTXT( ("music on","开启音乐"), 0, (60,60,60), -200, self.ctrY+40 )
                    
            # 一次性的鼠标点击或按键事件
            for event in pygame.event.get():
                if ( event.type == QUIT ):
                    pygame.quit()
                    sys.exit()
                elif ( event.type == KEYDOWN ):
                    if not self.paused:
                        for hero in self.heroes:
                            if hero.category == "follower":
                                continue
                            if ( event.key == hero.keyDic["wrestleKey"] ):    # 挥刀
                                if (hero.onlayer == 0) and self.hostage and ( pygame.sprite.collide_mask(hero, self.hostage) ):
                                    # 将hostage变为一个hero并加入heroes队列。
                                    pos = (self.hostage.rect.left, self.hostage.rect.bottom)
                                    follower = myHero.Follower(self.bg_size, self.blockSize, self.hostage, hero, pos)
                                    for tower in self.areaList:
                                        for brick in tower.groupList["-1"]:
                                            follower.checkList.add( brick )
                                        for elem in tower.elemList:
                                            follower.checkList.add(elem)
                                    self.heroes.append(follower)
                                    self.allElements.add(follower)
                                    # 已经被带起，将原来的hostage删除。
                                    self.hostage.kill()
                                    self.hostage = None
                                else:
                                    hero.whip()
                            elif ( event.key == hero.keyDic["jumpKey"] ):   # 跳跃
                                if ( hero.k1 > 0 ) and ( hero.k2 == 0 ):
                                    hero.k2 = 1
                                if not hero.trapper and hero.aground and ( hero.k1 == 0 ):
                                    hero.k1 = 1
                            elif ( event.key == hero.keyDic["shootKey"] ) and hero.affected<0:    # 射箭
                                hero.shoot( self.allElements, self.delay )
                            elif ( event.key == hero.keyDic["itemKey"] ):    # 使用背包物品
                                hero.useItem( self.spurtCanvas )
                            elif ( event.key == hero.keyDic["downKey"] ):    # 下跳
                                hero.shiftLayer(-2, self.tower.heightList)
                            elif ( event.key == hero.keyDic["bagKey"] ) and len(self.effecter.SSList)==0 and len(hero.bagBuf)>1:     # 切换背包物品
                                self.effecter.addSmoothSwitch(hero.bagImgList[item], bagRect, 0.7, -20, -10, 10)
                                self.effecter.addSmoothSwitch(nxtImg, nxtRect, 1.4, 20, -10, 10)
                                hero.bagPt = (hero.bagPt + 1) % len(hero.bagBuf)
                            # elif ( event.key == pygame.K_u ):              # 特殊技能
                            #     self.hero.special()
                    if ( event.key == pygame.K_RETURN ):          # 暂停/解除暂停
                        self.paused = not self.paused
                        self.setBG = False # 用以指示可以铺一层透明背景
                elif event.type == pygame.MOUSEBUTTONUP:          # 鼠标事件
                    if self.paused:
                        if ( home.left < pos[0] < home.right ) and ( home.top < pos[1] < home.bottom ):  # 退出（放弃）当前关卡
                            self.music.stop()
                            self.gameOn = False
                            self.win = False
                            #return [False, self.heroes+self.tomb]
                        elif ( BGMusic.left < pos[0] < BGMusic.right ) and (BGMusic.top < pos[1] < BGMusic.bottom ):
                            if self.musicOn:
                                self.music.stop()
                                self.musicOn = False
                            else:
                                self.music.play(-1)
                                self.musicOn = True
                    else:
                        if ( menu.left < pos[0] < menu.right ) and ( menu.top < pos[1] < menu.bottom ):
                            self.paused = not self.paused

            pygame.display.flip()   # from buffer area load the pic to the screen
            self.delay -= 1
            if not self.delay:
                self.delay = 240
            self.clock.tick(60)
        
        # ===================================================================
        # Game Loop 结束，渲染 Stage Over 界面。
        drawRect( 0, 0, self.bg_size[0], self.bg_size[1], themeColor, self.screen )
        # 播放音效。
        if self.win:
            horns[0].play(0)
            self.addTXT( ("Successful Rescue!","营救成功！"), 3, (255,255,255), 0, -120)
            if self.stg<len(heroBook.accList) and not heroBook.accList[self.stg]:
                heroBook.accList[self.stg] = True    # 当前关卡通过，下一关的英雄角色解锁 ✔herobook
                heroBook.heroList[self.stg].acc = True
                hName = heroBook.heroList[self.stg].name
                self.addTXT( ("New hero "+hName[0]+" is now accessible.","新英雄 "+hName[1]+" 已解锁。"), 1, (255,255,255), 0, -120)
            # 修改关卡通过信息
            line = plotManager.readFile( "r", 1, None )
            info = stgManager.renewRec( line, self.stg-1, diffi, 0 )
            plotManager.readFile( "w", 1, info)
        else:
            horns[1].play(0)
            self.addTXT( ("Mission Failed.","营救失败。"), 3, (255,255,255), 0, -120)
        # 不论胜负与否，都显示参与本关的英雄的经验值信息，并计算经验值获得。
        y1 = 20
        for hero in (self.heroes + self.tomb):
            if not hero.category=="follower":
                heroBook.heroList[int(hero.heroNo)].increaseExp(hero.expInc)

                vHero = heroBook.heroList[hero.heroNo]  # 从heroBook的列表中取VHero类型
                # brand of the hero.
                brd = self.addSymm(hero.brand, -120, y1)
                # level.
                bar = heroBook.drawExp( self.screen, brd.right+6, brd.bottom-26, int(vHero.exp), int(vHero.nxtLvl), 2 )
                expTXT = ( "Level"+str(vHero.lvl)+" (EXP+"+str(hero.expInc)+")","等级"+str(vHero.lvl)+"（经验+"+str(hero.expInc)+"）" )
                self.addTXT( expTXT, 1, (240,230,230), bar.left+bar.width//2-self.bg_size[0]//2, (bar.top-40)-self.bg_size[1]//2 )
                y1 += 90

        while True:
            # two Basic Buttons.
            restart = drawRect( self.bg_size[0]//2-220, 560, 200, 60, themeColor, self.screen )
            retreat = drawRect( self.bg_size[0]//2+20, 560, 200, 60, themeColor,self.screen )

            pos = pygame.mouse.get_pos()
            if ( restart.left < pos[0] < restart.right ) and ( restart.top < pos[1] < restart.bottom ):
                drawRect( restart.left+5, restart.top+5, restart.width-10, restart.height-10, (210,210,210,60), self.screen )
                if pygame.mouse.get_pressed()[0]:
                    horns[2].play(0)
                    return True  # 返回True，则main中的循环继续。
            elif ( retreat.left < pos[0] < retreat.right ) and ( retreat.top < pos[1] < retreat.bottom ):
                drawRect( retreat.left+5, retreat.top+5, retreat.width-10, retreat.height-10, (210,210,210,60), self.screen )
                if pygame.mouse.get_pressed()[0]:
                    horns[2].play(0)
                    return False # 返回False，则结束main中的循环。
            
            self.addTXT( ("Retry","重试"), 2, (255,255,255), -120, 230)
            self.addTXT( ("Home","主菜单"), 2, (255,255,255), 120, 230)
            for event in pygame.event.get():  # 必不可少的部分，否则事件响应会崩溃
                if ( event.type == QUIT ):
                    pygame.quit()
                    sys.exit()
                
            pygame.display.flip()   # from buffer area load the pic to the screen
            self.clock.tick(60)

    # ---- clear all elements in the model ----
    def clearAll(self):
        for each in self.allElements:
            each.kill()
            del each
        for tower in self.areaList:
            del tower

    # ---- show feedback of hero motion ----
    def showMsg(self, msgSect):
        vaccant = True
        for msg in self.msgList:
            if msg[2] == 0: # 倒计时减为0时从列表删除
                self.msgList.remove(msg)
                continue
            # 判断消息的类型。首先检查第一个信息是否为“message”，是则要在banner的消息框中显示。
            if msg[0]=="message":
                if vaccant:
                    ctr = (msgSect.left+msgSect.width//2-self.bg_size[0]//2, msgSect.top+msgSect.height//2-self.bg_size[1]//2 )
                    self.addSymm( msg[3], msgSect.left+30-self.bg_size[0]//2, ctr[1] )  # 消息栏左侧显示消息图标。
                    self.addTXT( msg[1], 1, (255,255,255), ctr[0], ctr[1])
                    msg[2] -= 1
                    vaccant = False
            #若不是message字段，则表示是宝箱获得补给物品：
            else:
                if msg[1]=="exp":
                    txt = ( msg[0].itemDic[msg[1]][0]+ "+1", msg[0].itemDic[msg[1]][1]+ "+1" )
                else:
                    txt = ( msg[0].itemDic[msg[1].category][0]+ "+" + str(msg[1].contains), msg[0].itemDic[msg[1].category][1]+ "+" + str(msg[1].contains) )
                ctr = ( msg[0].rect.left+msg[0].rect.width//2-self.bg_size[0]//2, msg[0].rect.top-self.bg_size[1]//2-(60-msg[2]) )
                self.addTXT( txt, 0, (255,255,255), ctr[0], ctr[1])
                msg[2] -= 1      # 消息显示倒计时-1
    
    # --- paint upper banner (contains 4 sections) ---
    def renderBanner(self, pos):
        # paint 4 background sections and get their rect.
        sect1 = drawRect(20, 10, 60, 40, (0,0,0,120), self.screen)    # Goalie Information.
        sect2 = drawRect(100, 10, 80, 40, (0,0,0,120), self.screen)   # Area Number.
        sect3 = drawRect(200, 10, 660, 40, (0,0,0,120), self.screen)  # Message Bar.
        sect4 = drawRect(880, 10, 60, 40, (0,0,0,120), self.screen)   # Menu Option.
        # give banner info.
        ctr = (sect1.left+sect1.width//2-self.bg_size[0]//2, sect1.top+sect1.height//2-self.bg_size[1]//2)  # 更改为中心坐标系统的中心点参数
        self.addSymm( pygame.image.load("image/goalie.png").convert_alpha(), ctr[0], ctr[1] )
        self.addTXT( ( str(len(self.tower.goalieList)), str(len(self.tower.goalieList)) ), 1, (255,255,255), ctr[0], ctr[1])

        ctr = (sect2.left+sect2.width//2-self.bg_size[0]//2, sect2.top+sect2.height//2-self.bg_size[1]//2)
        self.addTXT( ("Area%d" % (self.curArea+1), "区域%d" % (self.curArea+1)), 1, (255,255,255), ctr[0], ctr[1] )

        ctr = (sect4.left+sect4.width//2-self.bg_size[0]//2, sect4.top+sect4.height//2-self.bg_size[1]//2)
        menu = self.addSymm( pygame.image.load("image/menu.png").convert_alpha(), ctr[0], ctr[1] )
        if ( menu.left < pos[0] < menu.right ) and ( menu.top < pos[1] < menu.bottom ):  # 
            menu = self.addSymm( pygame.image.load("image/menuOn.png").convert_alpha(), ctr[0], ctr[1] )
            self.addTXT( ("menu","菜单"), 0, (255,255,255), ctr[0], ctr[1] )
        
        return (sect1, sect2, sect3, sect4)

    # ========================================================================
    # ================= Game Loop 结束后的Stage总结界面 =======================
    #def renderConclusion(self, heroBook):
    #    pass

    # ========================================================================
    # ================= 用于检测item为敌人的情况下，并移动该敌人 ================
    # 将这一部分从go()分离出来的目的是不让主函数显得过于庞大，单独成为一个辅助函数有助于之后的维护和修改
    # ========================================================================
    def moveMons(self, item, heroes):
        # This function should be overlapped in the initial constrction according to the stage.
        pass

    # ===========================================
    # Surface对象； x，y为正负（偏离屏幕中心点）像素值，确定了图像的中点坐标
    def addSymm(self, surface, x, y):
        rect = surface.get_rect()
        rect.left = (self.bg_size[0] - rect.width) // 2 + x
        rect.top = (self.bg_size[1] - rect.height) // 2 + y
        self.screen.blit( surface, rect )
        return rect   # 返回图片的位置信息以供更多操作

    # ===========================================
    # x,y为正负（偏离屏幕中心点）像素值，y则确定了文字行矩形的中点坐标（居中对齐）。
    # 这样改动是为了和addSymm()函数保持一个相对统一的系统。
    def addTXT(self, txtList, fntSize, color, x, y):
        txt = self.fntSet[fntSize][self.language].render( txtList[self.language], True, color )
        rect = txt.get_rect()
        rect.left = (self.bg_size[0] - rect.width) //2 + x
        rect.top = (self.bg_size[1] - rect.height) //2 + y
        self.screen.blit( txt, rect )
        return rect

# =============================================================================================================
# -------------------------------------------------------------------------------------------------------------
# ------------------------------------ stage running class ----------------------------------------------------
# -------------------------------------------------------------------------------------------------------------
# =============================================================================================================
class EndlessModel():
    
    allElements = None    # a big Group for all sprites in this stage
    bg_size = ()          # 屏幕的宽高（二元组）
    towerD = 10
    blockSize = 72
    ctrY = -130           # 右上角控件的水平偏移位置（像素）
    language = 0          # 初始默认为英文，可在构造函数中设定
    fntSet = []

    stg = 1
    scrnSpd = 4           # 屏幕上下移动的速度，单位像素
    delay = 120           # 延时变量，用于在不影响游戏正常运行的情况下给图片切换增加延迟
    msgList = []          # 用于存储消息的列表（列表包含列表）：[[incident, cntDown]]
    subsList = []
    vibration = 0         # 用于震动全屏的参数
    keyDic = []
    monsters = None

    hero = None
    tower = None
    screen = None         # 保存屏幕对象的引用
    clock = None
    towerBG = None        # 当前关卡的背景jpg
    towerBGRect = None
    nature = None
    plotManager = None
    haloCanvas = None     # boss出现时的全屏阴影画布

    msgStick = None
    music = None          # bgm （Sound对象）
    controller = []       # 右上角控件
    controllerOn = []
    paused = True
    musicOn = True
    setBG = False
    gameOn = True         # model循环标志，默认为True，player点击退出或gameover时变为False
    monsBroc = [ (),      # mons生成手册：记录每个stg有哪些mons，比例分别为多少.当前是stg0，不记录任何东西。
        ( (1,0.8), (2,0.6) ),           # stg1
        ( (1,0.75), (2,0.55) ),
        ( (1,0.9), (2,0.7), (3,0.7) ),
        ( (1,0.8), (2,0.6), (3,0.5) ),  # stg4
        ( (1,0.85), (2,0.75) ),
        ( (1,0.85), (2,0.85) ),
        ( (1,0.7), (1, 0.4) ) ]

    def __init__(self, stg, keyDic, bg_size, screen, language, fntSet, musicObj, natON, VHero):
        
        self.allElements = pygame.sprite.Group()
        self.stg = stg
        self.screen = screen
        self.bg_size = bg_size
        self.language = language
        self.keyDic = keyDic
        self.fntSet = fntSet
        self.plotManager = plotManager.Dialogue(self.stg)
        self.msgStick = pygame.image.load("image/tip.png").convert_alpha()
        self.nature = None
        if natON:
            if self.stg == 1:
                self.nature = mapManager.Nature(self.bg_size, self.stg, 8, 1)
            elif self.stg == 2:
                self.nature = mapManager.Nature(self.bg_size, self.stg, 1, 0)
            elif self.stg == 3:
                self.nature = mapManager.Nature(self.bg_size, self.stg, 8, 1)
            elif self.stg == 4 or self.stg == 7:
                self.nature = mapManager.Nature(self.bg_size, self.stg, 18, 0)
            elif self.stg == 5:
                self.nature = mapManager.Nature(self.bg_size, self.stg, 10, -1)
            elif self.stg == 6:
                self.nature = mapManager.Nature(self.bg_size, self.stg, 8, 1)
        self.spurtCanvas = mapManager.SpurtCanvas( self.bg_size)
        self.haloCanvas = mapManager.HaloCanvas( self.bg_size)
        self.effecter = plotManager.Controller( bg_size )
        # create the hero
        propPos = { "slot":(-300,290), "ammo":(-335,268), "bag":(-230,268), "health":(115,660) }
        initPos = (self.bg_size[0]//2, self.bg_size[1]-self.blockSize)
        self.hero = myHero.Hero(initPos, self.blockSize, VHero, propPos, 1)
        self.allElements.add(self.hero)
        self.hero.haloCanvas = self.haloCanvas
        # Select and overlap the moveMons() method.
        if self.stg == 1:
            self.moveMons = moveMonsStg1
        elif self.stg == 2:
            self.moveMons = moveMonsStg2
        elif self.stg == 3:
            self.moveMons = moveMonsStg3
        elif self.stg == 4:
            self.moveMons = moveMonsStg4
        elif self.stg == 5:
            self.moveMons = moveMonsStg5
        elif self.stg == 6:
            self.moveMons = moveMonsStg6
        elif self.stg == 7:
            self.moveMons = moveMonsStg7
        enemy.Monster.healthBonus = 1
        # create the map (note: for good influency of the screen, please no more than 240 layers)
        self.tower = mapManager.EndlessTower(bg_size, self.blockSize, self.towerD, stg)
        self.tower.generateIni(self.screen)
        for key in self.tower.groupList:
            for brick in self.tower.groupList[key]:
                self.allElements.add( brick )    # 加入walls
                if brick.category == "sideWall" or brick.category == "baseWall":
                    self.hero.checkList.add( brick )
        for sup in self.tower.chestList:
            self.allElements.add(sup)            # 加入supply
            self.hero.checkList.add(sup)
        for elem in self.tower.elemList:
            self.allElements.add(elem)
            self.hero.checkList.add(elem)
        # tower背景图片
        self.towerBG = pygame.image.load( "image/stg"+ str(stg) +"/towerBG.jpg" ).convert()
        self.towerBGRect = self.towerBG.get_rect()
        self.towerBGRect.left = (self.bg_size[0]-self.towerBGRect.width) // 2
        self.towerBGRect.top = (self.bg_size[1]-self.towerBGRect.height) // 2
        # 右上角的控件图片
        self.controller = [pygame.image.load("image/quit.png").convert_alpha(), pygame.image.load("image/BGMusic.png").convert_alpha(), pygame.image.load("image/mute.png").convert_alpha()]
        self.controllerOn = [pygame.image.load("image/quitOn.png").convert_alpha(), pygame.image.load("image/BGMusicOn.png").convert_alpha(), pygame.image.load("image/muteOn.png").convert_alpha(),]
        self.clock = pygame.time.Clock()
        self.music = musicObj

    def go(self, themeColor, horns, stgManager):
        self.music.play(-1)
        # create natural impediments and monsters
        if (self.stg==1):
            infernoFires = pygame.sprite.Group()
            for i in range(2):
                f = enemy.InfernoFire(self.bg_size)
                infernoFires.add(f)
                self.allElements.add(f)
            makeMons( 0, self.tower.curLayer, 0.65, 1, self.tower )
            makeMons( 60, self.tower.curLayer, 0.45, 2, self.tower )
        elif (self.stg==2):
            c = enemy.Column(self.bg_size, self.tower.groupList)
            self.allElements.add(c)
            makeMons( 0, self.tower.curLayer, 0.6, 1, self.tower )
            makeMons( 60, self.tower.curLayer, 0.4, 2, self.tower )
        elif (self.stg==3):
            mist = enemy.Mist(self.bg_size)
            makeMons( 0, self.tower.curLayer, 0.8, 1, self.tower )
            makeMons( 10, self.tower.curLayer, 0.6, 2, self.tower )
        elif (self.stg==4):
            ooze = enemy.Ooze(self.bg_size, self.blockSize//2, self.fntSet[0][1]) # 中文
            #self.allElements.add(ooze)
            makeMons( 0, self.tower.curLayer, 0.65, 1, self.tower )
            makeMons( 2, self.tower.curLayer, 0.55, 2, self.tower )
        elif (self.stg==5):
            blizzard = enemy.blizzardGenerator(self.bg_size)
            makeMons( 0, self.tower.curLayer, 0.7, 1, self.tower )
            makeMons( 12, self.tower.curLayer, 0.6, 2, self.tower )
        elif (self.stg==6):
            makeMons( 0, self.tower.curLayer, 0.7, 1, self.tower )
            makeMons( 2, self.tower.curLayer, 0.7, 2, self.tower )
        elif (self.stg==7):
            makeMons( 0, self.tower.curLayer, 0.7, 1, self.tower )
        for minion in self.tower.monsters:
            self.allElements.add(minion)
        self.screen.fill( (0, 0, 0) )
        self.screen.blit( self.towerBG, self.towerBGRect )
        for item in self.allElements:
            self.screen.blit( item.image, item.rect )

        while self.gameOn:

            if not self.paused: # 若未暂停
                # respond to the player's ongoing keydown event
                # get the list including the boolean status of all keys:
                key_pressed = pygame.key.get_pressed()
                if key_pressed[ self.keyDic["leftKey"] ]:
                    self.hero.moveX( self.delay, "left" )
                elif key_pressed[ self.keyDic["rightKey"] ]:
                    self.hero.moveX( self.delay, "right" )

                # move all if the screen need to be adjusted
                if ( self.tower.getTop(self.hero.onlayer) < self.bg_size[1]*0.45 ):
                    for elem in self.allElements:
                        elem.lift(self.scrnSpd)
                    for each in self.tower.heightList:
                        self.tower.heightList[each] += self.scrnSpd
                    if self.stg==4:
                        ooze.lift(self.scrnSpd)
                    
                # check if it's needed to add More Layers
                if ( self.hero.onlayer >= (self.tower.curLayer-10) ):
                    self.tower.addMore()
                    # 添加至allElements
                    for key in self.tower.groupList:
                        for brick in self.tower.groupList[key]:
                            if not brick in self.allElements:
                                self.allElements.add( brick )
                                if brick.category == "sideWall" or brick.category == "baseWall":
                                    self.hero.checkList.add( brick )
                    for sup in self.tower.chestList:
                        if not sup in self.allElements:
                            self.allElements.add(sup)
                            self.hero.checkList.add(sup)
                    for elem in self.tower.elemList:
                        if not elem in self.allElements:
                            self.allElements.add(elem)
                            self.hero.checkList.add(elem)
                    # 增加新层的怪物
                    for each in self.monsBroc[self.stg]:
                        makeMons( self.tower.curLayer-10, self.tower.curLayer, each[1], each[0], self.tower )
                    for mons in self.tower.monsters:
                        if mons not in self.allElements:
                            self.allElements.add(mons)
                    # 删除低层的怪物(这里不好严格用layer来操作，因为飞行的monster没有特定的onlayer。因此用屏幕的高度为判断范围，超出两倍则判定删除)
                    for mons in self.tower.monsters:
                        if mons.rect.top >= 2*self.bg_size[1]:
                            mons.erase()
                
                # check jump and fall:
                if self.hero.k1 > 0:
                    self.hero.jump( self.tower.getTop( self.hero.onlayer+1 ) )
                else:
                    fallChecks = self.tower.groupList[str(self.hero.onlayer-1)]
                    if self.stg==2 and self.hero.rect.bottom < (c.rect.top+2):
                        self.hero.checkList.add( c )
                    self.hero.fall(self.tower.getTop(self.hero.onlayer-1), fallChecks, self.stg, self.tower.heightList)

                # repaint all elements
                self.screen.blit( self.towerBG, self.towerBGRect )
                for item in self.allElements:
                    self.moveMons( self, item, [self.hero] )
                    if item.category == "sideWall" or item.category == "lineWall" or item.category == "baseWall" or item.category == "specialWall" or \
                        item.category == "supAmmo" or item.category == "fruit" or item.category == "torch" or item.category == "medicine":
                        item.paint(self.screen)
                    elif item.category == "lineDecor":
                        item.alter()
                        self.screen.blit(item.image, item.rect)
                    elif item.category=="bullet" or item.category=="bulletPlus":
                        arrCheck = self.tower.monsters
                        if self.stg==2:
                            for elem in self.tower.elemList:
                                arrCheck.add(elem)
                        if item.category == "bullet":
                            item.move(arrCheck, self.spurtCanvas, self.bg_size)
                        else:
                            item.move(item, self.delay, arrCheck, self.spurtCanvas, self.bg_size) # 这里还要传入投掷物本身
                        self.screen.blit(item.image, item.rect)

                # decide the image of Hero
                self.hero.checkImg( self.delay, self.spurtCanvas, self.tower.monsters )
                self.hero.paint( self.screen )
                if len(self.hero.jmpInfo)>0:       # 绘画跳跃烟尘效果
                    self.screen.blit( self.hero.jmpInfo[0], self.hero.jmpInfo[1] )
                # Fetch hitInfo from hero's preyList.
                for hitInfo in self.hero.preyList:
                    self.spurtCanvas.addSpatters(hitInfo[3], [2, 3, 4], [10, 11, 12], hitInfo[2], hitInfo[1])
                self.hero.preyList = []
                # 从hero的eventList事件列表中取事件信息。
                for item in self.hero.eventList:
                    self.msgList.append( [item, 60] )
                    self.subsList.append(item)
                self.hero.eventList = [] 
                
                # 分关卡增加游戏难度 ---
                if ( self.stg==1 ):
                    if ( self.hero.onlayer >= 40 and len(infernoFires) < 3 ) or ( self.hero.onlayer >= 80 and len(infernoFires) < 4 ) or ( self.hero.onlayer >= 120 and len(infernoFires) < 5 ):
                        f = enemy.InfernoFire( self.bg_size )
                        infernoFires.add(f)
                        self.allElements.add(f)
                elif ( self.stg==3 ):
                    mist.renew( self.delay, [self.hero] )
                    self.screen.blit( mist.canvas, mist.canvasRect )
                    if (self.hero.onlayer >= 20):
                        mist.pervade = True
                    if not ( self.delay % 60 ):  # 每隔一段时间在屏幕范围内生成一波骷髅兵
                        #self.msgList.append( [("Skeletons popping out!","骷髅兵正在活动！"), 150] )
                        for line in range( self.hero.onlayer-3, self.hero.onlayer+3, 2 ): # 起点，终点，跨度，变hero的偶数为groupList的奇数（hero.onlayer +- 4 - 1）
                            if ( line > 0 ) and len(self.tower.monsters) < 120 and ( random() < 0.1 ):
                                skeleton = enemy.Skeleton(self.tower.groupList[str(line)], self.blockSize, line)
                                self.tower.monsters.add(skeleton)
                                self.allElements.add(skeleton)
                elif ( self.stg==4 ):
                    sprites = [self.hero]
                    for each in self.tower.monsters:
                        sprites.append(each)
                    ooze.rise( self.delay, self.screen, sprites, self.spurtCanvas )
                    if ( self.hero.maxLayer>=10 and ooze.speed<=1 ) or ( self.hero.maxLayer>=60 and ooze.speed<=2 ) or ( self.hero.maxLayer>=150 and ooze.speed<=3 ) or ( self.hero.maxLayer>=240 and ooze.speed<=4 ):
                        ooze.speed += 1
                        self.msgList.append( [("The Ooze speeds up rising!","泥沼上涨速度加快！"), 150] )
                elif ( self.stg==5 ):
                    blizzard.storm([self.hero], self.nature.wind, self.spurtCanvas)
                
                if self.vibration > 0:
                    if (self.vibration % 2 == 0):
                        for elem in self.allElements:
                            elem.lift(4)
                            elem.level(4)
                    elif (self.vibration % 2 == 1):
                        for elem in self.allElements:
                            elem.lift(-4)
                            elem.level(-4)
                    self.vibration -= 1

                # 绘制两层画布
                if self.haloCanvas:
                    self.haloCanvas.update( self.delay, self.screen )
                if self.spurtCanvas and not self.paused:
                    self.spurtCanvas.update(self.screen)
                if self.nature and not self.paused:
                    self.nature.update(self.screen)
                 # 在迷雾之后再画一遍，否则会被迷雾盖掉
                for item in self.subsList:
                    if not item.reached:
                        item.subsMove()
                        self.screen.blit(item.substance, item.subsRect)
                    else:
                        self.subsList.remove(item)
                
                # draw hero status info
                self.addSymm( self.hero.slot, self.hero.propPos["slot"][0], self.hero.propPos["slot"][1] )
                self.addSymm( self.hero.brand, self.hero.propPos["slot"][0]-110, self.hero.propPos["slot"][1] )
                self.addTXT( ("Level "+str(self.hero.lvl), "等级"+str(self.hero.lvl)), 0, (255,255,255), self.hero.propPos["slot"][0]-100, self.hero.propPos["slot"][1]+24 )
                self.addSymm( self.hero.ammoImg, self.hero.propPos["ammo"][0], self.hero.propPos["ammo"][1] )
                self.addTXT( (str(self.hero.arrow), str(self.hero.arrow)), 1, (255,255,255), self.hero.propPos["ammo"][0]+36, self.hero.propPos["ammo"][1] )
                # 画 bag item.
                if len(self.effecter.SSList)==0:
                    if len(self.hero.bagBuf)>1:
                        nxtItem = self.hero.bagBuf[(self.hero.bagPt + 1) % len(self.hero.bagBuf)]
                        nxtRect = self.hero.bagImgList[nxtItem].get_rect()
                        nxtImg = pygame.transform.smoothscale(self.hero.bagImgList[nxtItem], ( int(nxtRect.width*0.7), int(nxtRect.height*0.7) ) )
                        nxtRect = self.addSymm( nxtImg, self.hero.propPos["bag"][0]-20, self.hero.propPos["bag"][1]+10 )
                    item = self.hero.bagBuf[self.hero.bagPt]
                    bagRect = self.addSymm( self.hero.bagImgList[item], self.hero.propPos["bag"][0], self.hero.propPos["bag"][1] )
                    self.addTXT( (str(self.hero.bag[item]),str(self.hero.bag[item])), 1, (255,255,255), self.hero.propPos["bag"][0]+36, self.hero.propPos["bag"][1] )
                self.effecter.doSwitch(self.screen)
                drawHealth( self.screen, self.hero.propPos["health"][0], self.hero.propPos["health"][1], 20, 18, self.hero.health, self.hero.full, 2 )

                pos = pygame.mouse.get_pos()
                bannerList = self.renderBanner(pos)
                self.showMsg( bannerList[1] )
                menu = bannerList[2]

                # check collide.
                if ( self.hero.rect.top >= self.bg_size[1] ):
                    self.hero.hitted(2, 0)
                if ( self.hero.health <= 0 ):
                    self.music.stop()
                    self.gameOn = False

            else:   # 暂停状态
                # 透明灰色打底
                if not self.setBG:
                    self.setBG = True
                    drawRect( 0, 0, self.bg_size[0], self.bg_size[1], (0,0,0,180), self.screen )
                    tip = choice( self.plotManager.tips )
                # 加Board to represent some tips.
                self.addSymm( pygame.image.load("image/cardBoard.png"), 0, 0 )
                self.addSymm( pygame.image.load("image/Enter.png").convert_alpha(), 0, -60 )
                self.addTXT( ["continue/pause","继续/暂停"], 0, (20,20,20), 0, -30)
                # tip area. 
                drawRect( self.bg_size[0]//2-240, self.bg_size[1]//2+20, 480, 100, (210,180,120,120), self.screen )
                topAlign = 50
                for line in tip:
                    self.addTXT( line, 0, (0,0,0), 0, topAlign )
                    topAlign += 20
                
                # handle controllers images and click events -----------------------------------
                home = self.addSymm( self.controller[0], -260, self.ctrY)
                BGMusic = self.addSymm( self.controller[1], -200, self.ctrY) if self.musicOn else self.addSymm( self.controller[2], -200, self.ctrY)
                pos = pygame.mouse.get_pos()
                if ( home.left < pos[0] < home.right ) and ( home.top < pos[1] < home.bottom ):  # 退出（放弃）当前关卡
                    home = self.addSymm( self.controllerOn[0], -260, self.ctrY)
                    self.addTXT( ("quit","放弃"), 0, (60,60,60), -260, self.ctrY+40 )

                elif ( BGMusic.left < pos[0] < BGMusic.right ) and (BGMusic.top < pos[1] < BGMusic.bottom ):
                    if self.musicOn:
                        BGMusic = self.addSymm( self.controllerOn[1], -200, self.ctrY)
                        self.addTXT( ("music off","关闭音乐"), 0, (60,60,60), -200, self.ctrY+40 )
                    else:
                        BGMusic = self.addSymm( self.controllerOn[2], -200, self.ctrY)
                        self.addTXT( ("music on","开启音乐"), 0, (60,60,60), -200, self.ctrY+40 )

            # 一次性的鼠标点击或按键事件
            for event in pygame.event.get():
                if ( event.type == QUIT ):
                    pygame.quit()
                    sys.exit()
                elif ( event.type == KEYDOWN ):
                    if not self.paused:
                        if ( event.key == self.keyDic["wrestleKey"] ):   #挥刀
                            self.hero.whip()
                        elif ( event.key == self.keyDic["jumpKey"] ):    #跳跃
                            if ( self.hero.k1 > 0 ) and ( self.hero.k2 == 0 ):
                                self.hero.k2 = 1
                            if not self.hero.trapper and (self.hero.aground) and ( self.hero.k1 == 0 ):
                                self.hero.k1 = 1
                        elif ( event.key == self.keyDic["shootKey"] ) and self.hero.affected<0:    #射箭
                            self.hero.shoot( self.allElements, self.delay )
                        elif ( event.key == self.keyDic["itemKey"] ):    #使用背包物品
                            self.hero.useItem( self.spurtCanvas )
                        elif ( event.key == self.keyDic["downKey"] ):    #下跳
                            self.hero.shiftLayer(-2, self.tower.heightList)
                        elif ( event.key == self.keyDic["bagKey"] )and len(self.effecter.SSList)==0 and len(self.hero.bagBuf)>1:     # 切换背包物品
                            self.effecter.addSmoothSwitch(self.hero.bagImgList[item], bagRect, 0.7, -20, -10, 10)
                            self.effecter.addSmoothSwitch(nxtImg, nxtRect, 1.4, 20, -10, 10)
                            self.hero.bagPt = (self.hero.bagPt + 1) % len(self.hero.bagBuf)
                    #    elif ( event.key == pygame.K_u ):               #特殊技能
                    #        self.hero.special()
                    if ( event.key == pygame.K_RETURN ):            # 暂停/解除暂停
                        self.paused = not self.paused
                        self.setBG = False # 用以指示可以铺一层透明背景
                elif event.type == pygame.MOUSEBUTTONUP:            # 鼠标事件
                    if self.paused:
                        if ( home.left < pos[0] < home.right ) and ( home.top < pos[1] < home.bottom ):  # 退出（放弃）当前stg.
                            self.music.stop()
                            self.gameOn = False
                        elif ( BGMusic.left < pos[0] < BGMusic.right ) and (BGMusic.top < pos[1] < BGMusic.bottom ):
                            if self.musicOn:
                                self.music.stop()
                                self.musicOn = False
                            else:
                                self.music.play(-1)
                                self.musicOn = True
                    else:
                        if ( menu.left < pos[0] < menu.right ) and ( menu.top < pos[1] < menu.bottom ):
                            self.paused = not self.paused
            
            pygame.display.flip()   # from buffer area load the pic to the screen
            self.delay -= 1
            if not self.delay:
                self.delay = 240
            self.clock.tick(60)
        
        # ===================================================================
        # Game Loop 结束，渲染 Stage Over 界面。
        drawRect( 0, 0, self.bg_size[0], self.bg_size[1], themeColor, self.screen )
        if ( self.hero.score > stgManager.high[self.stg-1] ):
            horns[0].play(0)
            self.addTXT( ("New highest!","新的最高纪录！"), 3, (255,255,255), 0, -240)
            line = plotManager.readFile( "r", 1, None )
            info = stgManager.renewRec( line, self.stg-1, self.hero.score, 1 )
            plotManager.readFile( "w", 1, info)
        self.addTXT( ("Previous best: %d" % stgManager.high[self.stg-1],"历史最佳：%d" % stgManager.high[self.stg-1]), 1, (255,255,255), 0, -120)
        self.addTXT( ("Your score: %d" % self.hero.score,"本次得分：%d" % self.hero.score), 3, (255,255,255), 0, -160)

        while True:
            # two Basic Buttons.
            restart = drawRect( self.bg_size[0]//2-220, 560, 200, 60, themeColor, self.screen )
            retreat = drawRect( self.bg_size[0]//2+20, 560, 200, 60, themeColor, self.screen )

            pos = pygame.mouse.get_pos()
            if ( restart.left < pos[0] < restart.right ) and ( restart.top < pos[1] < restart.bottom ):
                drawRect( restart.left+5, restart.top+5, restart.width-10, restart.height-10, (210,210,210,60), self.screen )
                if pygame.mouse.get_pressed()[0]:
                    horns[2].play(0)
                    return True
            elif ( retreat.left < pos[0] < retreat.right ) and ( retreat.top < pos[1] < retreat.bottom ):
                drawRect( retreat.left+5, retreat.top+5, retreat.width-10, retreat.height-10, (210,210,210,60), self.screen )
                if pygame.mouse.get_pressed()[0]:
                    horns[2].play(0)
                    return False
            
            self.addTXT( ("Retry","重试"), 2, (255,255,255), -120, 230)
            self.addTXT( ("Home","主菜单"), 2, (255,255,255), 120, 230)
            for event in pygame.event.get():  # 必不可少的部分，否则事件响应会崩溃
                if ( event.type == QUIT ):
                    pygame.quit()
                    sys.exit()
                
            pygame.display.flip()   # from buffer area load the pic to the screen
            self.clock.tick(60)

    # ---- clear all elements in the current stg ---
    def clearAll(self):
        for each in self.allElements:
            each.kill()
            del each
        self.hero.checkList.empty()

    # ---- show feedback of hero motion ----
    def showMsg(self, msgSect):
        vaccant = True
        for msg in self.msgList:
            if msg[1] == 0: # 倒计时减为0时从列表删除
                self.msgList.remove(msg)
                continue
            # 判断消息的类型。首先检查第一个信息是否为“message”，是则要在banner的消息框中显示。
            if type(msg[0]).__name__=="tuple":
                if vaccant:
                    ctr = (msgSect.left+msgSect.width//2-self.bg_size[0]//2, msgSect.top+msgSect.height//2-self.bg_size[1]//2 )
                    self.addSymm( self.msgStick, msgSect.left+30-self.bg_size[0]//2, ctr[1] )  # 消息栏左侧显示消息图标。
                    self.addTXT( msg[0], 1, (255,255,255), ctr[0], ctr[1] )
                    vaccant = False
                    msg[1] -= 1
            # 若不是message字段，则表示是宝箱获得补给物品：
            else:
                txt = ( self.hero.itemDic[msg[0].category][0]+ "+" + str(msg[0].contains), self.hero.itemDic[msg[0].category][1]+ "+" + str(msg[0].contains) )
                ctr = ( self.hero.rect.left+self.hero.rect.width//2-self.bg_size[0]//2, self.hero.rect.top-self.bg_size[1]//2-(60-msg[1]) )
                self.addTXT( txt, 0, (255,255,255), ctr[0], ctr[1] )
                msg[1] -= 1      # 消息显示倒计时-1

    # --- paint upper banner (contains 3 sections) ---
    def renderBanner(self, pos):
        # paint 4 background sections and get their rect.
        sect1 = drawRect(20, 10, 180, 40, (0,0,0,120), self.screen)   # Score Information.
        sect2 = drawRect(220, 10, 640, 40, (0,0,0,120), self.screen)  # Message Bar.
        sect3 = drawRect(880, 10, 60, 40, (0,0,0,120), self.screen)   # Menu Option.
        # give banner info.
        ctr = (sect1.left+sect1.width//2-self.bg_size[0]//2, sect1.top+sect1.height//2-self.bg_size[1]//2)  # 更改为中心坐标系统的中心点参数
        self.addTXT(("Your score: %d" % self.hero.score,"你的得分：%d" % self.hero.score), 1, (255,255,255), ctr[0], ctr[1])

        ctr = (sect3.left+sect3.width//2-self.bg_size[0]//2, sect3.top+sect3.height//2-self.bg_size[1]//2)
        menu = self.addSymm( pygame.image.load("image/menu.png").convert_alpha(), ctr[0], ctr[1] )
        if ( menu.left < pos[0] < menu.right ) and ( menu.top < pos[1] < menu.bottom ):
            menu = self.addSymm( pygame.image.load("image/menuOn.png").convert_alpha(), ctr[0], ctr[1] )
            self.addTXT( ("menu","菜单"), 0, (255,255,255), ctr[0], ctr[1] )
        
        return (sect1, sect2, sect3)
        
    # ==========================================================
    def moveMons(self, item, heroes):
        pass
        
    # ================================================================================
    # Surface对象； x，y为正负（偏离中心点）像素值
    def addSymm(self, surface, x, y):
        rect = surface.get_rect()
        rect.left = (self.bg_size[0] - rect.width) // 2 + x
        rect.top = (self.bg_size[1] - rect.height) // 2 + y
        self.screen.blit( surface, rect )
        return rect   # 返回图片的位置信息以供更多操作

    # ==========================================
    # x,y为正负（偏离屏幕中心点）像素值，确定了文字行的左上角坐标。这样改动是为了和addSymm()函数保持一个相对统一的系统。
    def addTXT(self, txtList, fntSize, color, x, y):
        txt = self.fntSet[fntSize][self.language].render( txtList[self.language], True, color )
        rect = txt.get_rect()
        rect.left = (self.bg_size[0] - rect.width) //2 + x
        rect.top = (self.bg_size[1] - rect.height) //2 + y
        self.screen.blit( txt, rect )
        return rect

# -----------------------------------------------------------------------------------------
# ------------------------------- 分关卡的敌人移动函数群 ------------------------------------
# -----------------------------------------------------------------------------------------
# 需要额外传入heroes参数是因为要可在两个model内均可用，但两个函数的hero引用方式不同。
def moveMonsStg1(self, item, heroes):
    if item.category == "infernoFire":
        item.move( self.delay, heroes, self.spurtCanvas )
        self.screen.blit(item.image, item.rect)
    elif item.category == "fire":
        item.move(self.delay, self.tower.groupList["-1"], self.tower.groupList[str(item.onlayer)], self.tower.getTop(item.onlayer)+self.blockSize, heroes, self.spurtCanvas, self.bg_size ) 
        self.screen.blit(item.image, item.rect)
    elif item.category == "RedDragon":
        if item.activated:
            if not self.haloCanvas.halos["monsHalo"]:
                self.haloCanvas.addHalo( "monsHalo", [430,460,490,520], (1,1,1,0), 2 )
            fdbc = item.move( heroes, self.spurtCanvas )
            if fdbc == "vib" and self.vibration==0:
                self.vibration = 6
            item.paint( self.screen )
            drawHealth( self.screen, item.rect.left+item.rect.width//2, item.rect.top-8, 0, 8, item.health, item.full, 1 )
        elif ( item.rect.bottom >= 0 ) and ( item.rect.top <= self.bg_size[1] ):
            item.activated = True
    elif ( item.rect.bottom >= 0 ) and ( item.rect.top <= self.bg_size[1] ):  # moves only if the gozilla appears in the screen
        if item.category == "gozilla" or item.category=="megaGozilla":
            item.move(self.delay, heroes)
            drawHealth( self.screen, item.rect.left+item.rect.width//2, item.rect.top-8, 0, 8, item.health, item.full, 1 )
            self.screen.blit(item.image, item.rect)
        elif item.category == "dragon":
            fire = item.move(self.delay)
            drawHealth( self.screen, item.rect.left+item.rect.width//2, item.rect.top-8, 0, 8, item.health, item.full, 1 )
            if fire:
                self.allElements.add(fire)
            self.screen.blit(item.image, item.rect)
        elif item.category == "blockFire":
            item.burn(self.delay, heroes, self.spurtCanvas)
            self.screen.blit(item.image, item.rect)

def moveMonsStg2(self,item, heroes):
    if item.category == "column":
        frnLayer = 0
        for hero in heroes:
            frnLayer = max(frnLayer, hero.onlayer)
        fdbc = item.move( heroes, frnLayer, self.tower.groupList )
        self.screen.blit(item.image, item.rect)
        if fdbc == "vib" and self.vibration==0:
            self.vibration = 6
        elif fdbc == "alarm":
            self.screen.blit(item.canvas, item.canvasRect)
        elif fdbc:
            self.screen.blit( fdbc[0], fdbc[1] )
    elif item.category == "stone":
        item.move(self.delay, self.tower.groupList["-1"], self.tower.groupList[str(item.onlayer)], self.tower.getTop(item.onlayer)+self.tower.blockSize, heroes, self.spurtCanvas)
        self.screen.blit(item.image, item.rect)
    elif ( item.rect.bottom >= 0 ) and ( item.rect.top <= self.bg_size[1] ):
        if item.category == "golem":
            more = item.move( self.delay, heroes )
            if more:
                for each in more:
                    self.tower.monsters.add( each )
                    self.allElements.add( each )
                    #self.tower.layerMons[str(each.onlayer)] += 1
            if not item.doom:
                drawHealth( self.screen, item.rect.left+item.rect.width//2, item.rect.top-8, 0, 8, item.health, item.full, 1 )
            elif item in self.tower.monsters:
                self.tower.monsters.remove(item)
            self.screen.blit(item.image, item.rect)
        elif item.category == "bowler":
            item.move(self.delay, heroes)
            drawHealth( self.screen, item.rect.left+item.rect.width//2, item.rect.top-8, 0, 8, item.health, item.full, 1 )
            stone = item.throw(self.delay)
            if stone:
                self.allElements.add(stone)
            self.screen.blit(item.image, item.rect) # blit item
        elif item.category == "blockStone":
            self.screen.blit(item.image, item.rect)
        elif item.category == "webWall":
            item.stick(heroes)
            item.paint(self.screen)
        elif item.category == "GiantSpider":
            self.haloCanvas.pervade = True
            item.move( self.delay, heroes, self.spurtCanvas )
            item.paint( self.screen )
            drawHealth( self.screen, item.rect.left+item.rect.width//2, item.rect.top-8, 0, 8, item.health, item.full, 1 )

def moveMonsStg3(self, item, heroes):
    if item.category == "Vampire":
        if item.activated:
            if not self.haloCanvas.halos["monsHalo"]:
                self.haloCanvas.addHalo( "monsHalo", [430,460,490,520], (1,1,1,0), 2 )
            minions = item.move( self.delay, heroes, self.tower.groupList )
            if minions:      # create more minions.
                for each in minions:
                    if each[0] == "skeleton":
                        mini = enemy.Skeleton(self.tower.groupList[str(item.onlayer)], self.tower.blockSize, item.onlayer)
                        mini.birth[0] = each[1][0]
                    elif each[0] == "bat":
                        mini = enemy.Bat(self.tower.groupList[str(item.onlayer+2)], item.onlayer+2)
                        mini.tgt = choice(mini.wallList)
                        mini.rect.left, mini.rect.bottom = each[1]
                    self.spurtCanvas.addSpatters( 5, [3, 4], [9, 10, 11], (80,10,80,255), each[1] )
                    self.tower.monsters.add( mini )
                    self.allElements.add( mini )
                    #self.tower.layerMons[str(mini.onlayer)] += 1
            item.paint( self.screen, self.spurtCanvas )
            drawHealth( self.screen, item.rect.left+item.rect.width//2, item.rect.top-10, 0, 8, item.health, item.full, 1 )
        elif ( item.rect.bottom >= 0 ) and ( item.rect.top <= self.bg_size[1] ):
            item.activated = True
    elif ( item.rect.bottom >= 0 ) and ( item.rect.top <= self.bg_size[1] ):
        if item.category == "skeleton":
            if not item.popping:
                item.fall( self.tower.getTop(item.onlayer), self.tower.groupList )
                drawHealth( self.screen, item.rect.left+item.rect.width//2, item.rect.top-8, 0, 8, item.health, item.full, 1 )
            item.move( self.delay, heroes )
            self.screen.blit(item.image, item.rect)
        elif item.category == "dead":
            drawHealth( self.screen, item.rect.left+item.rect.width//2, item.rect.top-8, 0, 8, item.health, item.full, 1 )
            item.move( self.delay, heroes, self.spurtCanvas )
            item.fall( self.tower.getTop(item.onlayer), self.tower.groupList )
            item.paint(self.screen)
        elif item.category == "bat":
            item.move( self.delay, heroes )
            self.screen.blit(item.image, item.rect)
            drawHealth( self.screen, item.rect.left+item.rect.width//2, item.rect.top-12, 0, 8, item.health, item.full, 1 )
        elif item.category == "specialWall":
            item.collapse()

def moveMonsStg4(self, item, heroes):
    if ( item.rect.bottom >= 0 ) and ( item.rect.top <= self.bg_size[1] ):
        if item.category == "worm":
            keyLine = self.tower.getTop(item.onlayer)
            item.move( self.delay, self.tower.groupList[str(item.onlayer)], keyLine, self.tower.groupList["-1"], heroes )
            drawHealth( self.screen, item.rect.left+item.rect.width//2, item.rect.top-8, 0, 8, item.health, item.full, 1 )
            self.screen.blit(item.image, item.rect)
        elif item.category == "nest":
            more = item.move( self.delay, self.allElements, self.tower.monsters )
            if more:
                for each in more:
                    self.tower.monsters.add( each )
                    self.allElements.add( each )
                    #self.tower.layerMons[str(each.onlayer)] += 1
            else:
                drawHealth( self.screen, item.rect.left+item.rect.width//2, item.rect.top-8, 0, 8, item.health, item.full, 1 )
            self.screen.blit(item.image, item.rect)
        elif item.category == "fly":
            item.move(self.delay, heroes)
            drawHealth( self.screen, item.rect.left+item.rect.width//2, item.rect.top-8, 0, 8, item.health, item.full, 1 )
            self.screen.blit(item.image, item.rect)
        elif item.category == "blockOoze":
            item.bubble( self.delay, heroes )
            self.screen.blit(item.image, item.rect)
        elif item.category == "slime":
            new = item.move(self.delay, heroes)
            drawHealth( self.screen, item.rect.left+item.rect.width//2, item.rect.top-8, 0, 8, item.health, item.full, 1 )
            self.screen.blit(item.image, item.rect)
            if new:
                self.tower.monsters.add(new)
                self.allElements.add(new)
                #self.tower.layerMons[str(new.onlayer)] += 1
        elif item.category == "Python":
            item.move( self.delay )
            item.paint( self.screen )
            drawHealth( self.screen, item.rect.left+item.rect.width//2, item.rect.top-8, 0, 8, item.health, item.full, 1 )

def moveMonsStg5(self, item, heroes):
    if item.category == "FrostTitan":
        if item.activated:
            if not self.haloCanvas.halos["monsHalo"]:
                self.haloCanvas.addHalo( "monsHalo", [430,460,490,520], (1,1,1,0), 2 )
            item.move( self.delay, heroes, self.spurtCanvas, self.bg_size )
            item.paint( self.screen )
            drawHealth( self.screen, item.rect.left+item.rect.width//2, item.rect.top-8, 0, 8, item.health, item.full, 1 )
        elif ( item.rect.bottom >= 0 ) and ( item.rect.top <= self.bg_size[1] ):
            item.activated = True
    elif ( item.rect.bottom >= 0 ) and ( item.rect.top <= self.bg_size[1] ):  # moves only if the gozilla appears in the screen
        if item.category == "wolf":
            item.move(self.delay, heroes)
            drawHealth( self.screen, item.rect.left+item.rect.width//2, item.rect.top-8, 0, 8, item.health, item.full, 1 )
            self.screen.blit(item.image, item.rect)
            #self.addTXT( (str(item.jumping),str(item.jumping)), 0, (255,0,0), item.rect.left-self.bg_size[0]//2, item.rect.top-self.bg_size[1]//2 )
        elif item.category == "iceTroll":
            drawHealth( self.screen, item.rect.left+item.rect.width//2, item.rect.top-8, 0, 8, item.health, item.full, 1 )
            item.move( self.delay, heroes, self.spurtCanvas.spatters )
            self.screen.blit(item.image, item.rect)

def moveMonsStg6(self, item, heroes):
    if item.category == "fire":
        item.move(self.delay, self.tower.groupList["-1"], self.tower.groupList[str(item.onlayer)], self.tower.getTop(item.onlayer)+self.tower.blockSize, heroes, self.spurtCanvas, self.bg_size ) 
        self.screen.blit(item.image, item.rect)
    elif item.category == "WarMachine":
        if item.activated:
            if not self.haloCanvas.halos["monsHalo"]:
                self.haloCanvas.addHalo( "monsHalo", [430,460,490,520], (1,1,1,0), 2 )
            fire = item.move( self.delay, heroes, self.spurtCanvas, self.tower.groupList )
            item.paint( self.screen )
            drawHealth( self.screen, item.rect.left+item.rect.width//2, item.rect.top-8, 0, 8, item.health, item.full, 1 )
            if fire:
                self.allElements.add(fire)
        elif ( item.rect.bottom >= 0 ) and ( item.rect.top <= self.bg_size[1] ):
            item.activated = True
    elif ( item.rect.bottom >= 0 ) and ( item.rect.top <= self.bg_size[1] ):  # moves only if the gozilla appears in the screen
        if item.category == "dwarf":
            item.move(self.delay, heroes)
            drawHealth( self.screen, item.rect.left+item.rect.width//2, item.rect.top-8, 0, 8, item.health, item.full, 1 )
            self.screen.blit(item.image, item.rect)
        elif item.category == "gunner":
            item.move(self.delay, heroes)
            self.screen.blit(item.canvas, item.canvasRect)
            if item.health>0:
                drawHealth( self.screen, item.rect.left+item.rect.width//2, item.rect.top-8, 0, 8, item.health, item.full, 1 )
                self.screen.blit(item.image, item.rect)
            elif item in self.tower.monsters:
                self.tower.monsters.remove(item)
        elif item.category == "fan":
            item.whirl(self.delay, heroes)
            self.screen.blit(item.image, item.rect)

def moveMonsStg7(self, item, heroes):
    if item.category == "stabber":
        item.stab(self.delay, heroes ) 
        self.screen.blit(item.image, item.rect)
    elif item.category == "guard":
        item.move(self.delay, heroes)
        drawHealth( self.screen, item.rect.left+item.rect.width//2, item.rect.top-8, 0, 8, item.health, item.full, 1 )
        item.paint( self.screen )

# ------------------------------------------------------------------------------------------
# document of the method: -- return a list with all monsters it has made (will fill the Grouplist given)
# About the parameters:
# btmLayer is the layer that only above which would the minions may appear;
# topLayer is the layer by which the minions would stop appearring;
# randRate (0-1) is the possibility that each layer may have a monster;
# mType(number1,2) is object type, indicate what kind of monster you want to make;
# tower is the mapManager Object Reference that will provide many useful variables for the process; it contains a SpriteGroup-type container that
# you wish to fill up with created minions.
def makeMons(btmLayer, topLayer, randRate, mType, tower):
    for group in tower.groupList:         # deal every odd row; group is the key (a number str of layer)
        if ( btmLayer < int(group) < topLayer ) and ( len(tower.groupList[group])>0 ) and  ( random() <= randRate ):
            if ( tower.stg==1 ):
                if mType == 1:
                    minion = enemy.Gozilla(tower.groupList[group], tower.blockSize, group)
                elif mType == 2:
                    minion = enemy.Dragon(tower.groupList[group], group, tower.boundaries)
                elif mType == 3:    # boss - Red Dragon
                    x = tower.oriPos[0] + tower.diameter*tower.blockSize
                    y = tower.getTop(int(group))+tower.blockSize
                    minion = enemy.RedDragon(x, y, group)    
            elif ( tower.stg==2 ):
                if mType == 1:
                    minion = enemy.Golem(tower.groupList[group], tower.blockSize, group)
                elif mType == 2:
                    minion = enemy.Bowler(tower.groupList[group], group)
                elif mType == 3:
                    minion = enemy.GiantSpider(tower.groupList[group], tower.blockSize, group, tower.boundaries)
                    tower.monsters.add(minion)
                    break
            elif ( tower.stg==3 ):
                if mType == 1:
                    minion = enemy.Skeleton(tower.groupList[group], tower.blockSize, group)
                elif mType == 2:
                    minion = enemy.Dead(tower.groupList[group], tower.blockSize, group)
                elif mType == 3:
                    minion = enemy.Bat(tower.groupList[group], group)
                elif mType == 4:    # boss - Vampire
                    minion = enemy.Vampire(tower.groupList, group, tower.boundaries)
                    tower.monsters.add(minion)
                    break
            elif ( tower.stg==4 ):
                if mType == 1:
                    minion = enemy.Slime(tower.groupList[group], tower.blockSize, group)
                elif mType == 2:
                    minion = enemy.Nest(tower.groupList[group], group)
                elif mType == 3:
                    XRange = (tower.boundaries[0], tower.boundaries[1])
                    y = tower.getTop(int(group))+tower.blockSize
                    minion = enemy.Fly( XRange, y, group )
                elif mType == 4:
                    minion = enemy.Python( group, tower.getTop(int(group)), tower.boundaries, tower.blockSize )
            elif ( tower.stg==5 ):
                if mType == 1:
                    minion = enemy.Wolf(tower.groupList[group], tower.blockSize, group)
                elif mType == 2:
                    minion = enemy.IceTroll(tower.groupList[group], tower.blockSize, group)
                elif mType == 3:
                    x = tower.boundaries[1] + 2*tower.blockSize
                    y = tower.getTop(int(group))+tower.blockSize
                    minion = enemy.FrostTitan(x, y, group)
            elif ( tower.stg==6 ):
                if mType == 1:
                    minion = enemy.Dwarf(tower.groupList[group], tower.blockSize, group)
                elif mType == 2:
                    minion = enemy.Gunner(tower.groupList[group], tower.blockSize, group, tower.boundaries)
                elif mType == 3:  # boss - War Machine
                    minion = enemy.WarMachine(tower.groupList, group, tower.boundaries)
                    tower.monsters.add(minion)
                    break
            elif ( tower.stg==7 ):
                if mType == 1:
                    minion = enemy.Guard(tower.groupList[group], tower.blockSize, group)
            tower.monsters.add(minion)
            #tower.layerMons[group] += 1

# ------------------------------------------------------------------------------------------
# drawHealth函数文档：Receive 7 essential parameters:
# 'surface' can be screen or surface, used to draw the health bar.
# 'x' and 'y' stand for the position of health bar, representing different meanings according to whether 'w' is zero or non-zero.
# 'w' and 'h' decide the size of the bar; (they should be over 4, and w is recommended to be times of 10)
# 'w' 的值若为0，表示使用默认的血格长度设定（blockLen=10），血条长度与血量成正比。此时的参数x应为对象的中线长度。若为非零数字，表示调用者希望自定义血条的长度（blockLen=w），此时直接从x开始画血条。
# 'health' is current amount of health; full is the max of item's health.
# 'gap' is the width of white frame into the bar.
def drawHealth(surface, x, y, w, h, health, full, gap):
    if health < 0:
        health = 0
    if health/full >= 0.3:
        color = (0, 240, 0)
        shadeColor = (0, 160, 0)   # 血块下方的条形阴影的颜色
    elif health/full >= 0.2:       # 血量少于20%则显示为红色
        color = (200, 200, 0)
        shadeColor = (120, 120, 0)
    else:
        color = (255, 0, 0)
        shadeColor = (180, 0, 0)  
    blockVol = 10        # 每个方格满时表示10滴血
    if w == 0:
        blockLen = 10    # 每个方格长度至多为10像素
        length = full + ( math.ceil( full/blockVol )-1)*gap +gap*2       # 血条总长度（第二个数是格子中间间隔的数量）
        x = x-length//2
    else:
        blockLen = w     # 自定义格子的长度
        length = full*blockLen//blockVol + ( math.ceil( full/blockVol )-1)*gap +gap*2       # 血条总长度（第二个数是格子中间间隔的数量）
    # 画外边框（白色底框）
    outRect = pygame.Rect( x, y, length, h )
    pygame.draw.rect( surface, (255,255,255), outRect )

    # 画内部血格
    offset = 0           # 用于计算每个方格的偏移值
    while (health >= blockVol):
        block = pygame.Rect( x+gap+offset, y+gap, blockLen, h-gap*2 )
        pygame.draw.rect( surface, color, block )
        shadow = pygame.Rect( x+gap+offset, block.bottom-gap, blockLen, gap )
        pygame.draw.rect( surface, shadeColor, shadow )
        health -= blockVol
        offset += (blockLen+gap)
    if (health > 0):     # 当所有满格都画完之后，画剩余的一格
        block = pygame.Rect( x+gap+offset, y+gap, health, h-gap*2 )
        pygame.draw.rect( surface, color, block )
        shadow = pygame.Rect( x+gap+offset, block.bottom-gap, health, gap )
        pygame.draw.rect( surface, shadeColor, shadow )

# ===========================================
# -----------常用的画方格surface函数：---------
def drawRect(x, y, width, height, rgba, screen):
    surf = pygame.Surface( (width, height) ).convert_alpha()
    rect = surf.get_rect()
    rect.left = x
    rect.top = y
    surf.fill( rgba )
    screen.blit( surf, rect )
    return rect
    
# =============================================================================================================
# -------------------------------------------------------------------------------------------------------------
# ------------------------------------ stage running class ----------------------------------------------------
# -------------------------------------------------------------------------------------------------------------
# =============================================================================================================
class PracticeModel():
    
    allElements = None    # a big Group for all sprites in this stage
    bg_size = ()          # 屏幕的宽高（二元组）
    towerH = 160
    blockSize = 72
    language = 0          # 初始默认为英文，可在构造函数中设定
    fntSet = []

    stg = 0
    scrnSpd = 4           # 屏幕上下移动的速度，单位像素
    delay = 120           # 延时变量，用于在不影响游戏正常运行的情况下给图片切换增加延迟
    msgList = []          # 用于存储消息的列表（列表包含列表）：[[heroName, incident, cntDown]]
    vibration = 0         # Cnt to indicate the vibration of the screen.
    # 双人模式下的特殊变量
    frontier = 0          # 两者中的较高像素值
    frnLayer = 0          # 两者中的较高层数

    hero = None           # 保存hero对象的引用
    tower = None
    screen = None         # 保存屏幕对象的引用
    clock = None
    towerBG = None        # 当前关卡的背景jpg
    towerBGRect = None
    nature = None         # 自然元素的画布
    spurtCanvas = None    # 击中反馈溅血的画布（比你想象中的更万能！不只是能画血噢😄嘻嘻）
    haloCanvas = None     # boss出现时的全屏阴影画布
    plotManager = None    # 管理剧情信息

    trainer = None        # 英雄训练师
    natON = True          # 自然装饰效果是否开启
    music = None          # bgm （Sound对象）
    controller = []       # 右上角控件
    controllerOn = []
    paused = True
    musicOn = True
    setBG = False
    gameOn = True         # 游戏循环标志，默认为True，玩家点击退出时变为False

    # 本model构造函数说明：
    # heroInfo 是一个hero的信息，包括heroNo和该英雄的keyDic。即形如：(VHero, keyDic1)。
    def __init__(self, heroInfo, trainerInfo, bg_size, screen, language, fntSet, musicObj, natON):
        
        self.allElements = pygame.sprite.Group()
        self.stg = 0
        self.screen = screen
        self.bg_size = bg_size
        self.language = language
        self.fntSet = fntSet
        self.natON = natON
        # 右上角的控件图片 及其他控制器
        self.controller = [pygame.image.load("image/quit.png").convert_alpha(), pygame.image.load("image/tips.png").convert_alpha(), 
            pygame.image.load("image/BGMusic.png").convert_alpha(), pygame.image.load("image/mute.png").convert_alpha()]
        self.controllerOn = [pygame.image.load("image/quitOn.png").convert_alpha(), pygame.image.load("image/tipsOn.png").convert_alpha(), 
            pygame.image.load("image/BGMusicOn.png").convert_alpha(), pygame.image.load("image/muteOn.png").convert_alpha()]
        self.aimImg = pygame.image.load("image/aim.png").convert_alpha()
        self.clock = pygame.time.Clock()
        self.music = musicObj
        # Initialize game canvas.
        self.gameOn = True
        self.paused = True
        self.setBG = False
        self.nature = None
        if self.natON:     # 自然效果可以是0（绿色流萤），4（雨），5（雪）中的随机一种。
            self.nature = mapManager.Nature(self.bg_size, choice([0,4,5]), 8, 1)
        self.spurtCanvas = mapManager.SpurtCanvas( self.bg_size )
        self.haloCanvas = mapManager.HaloCanvas( self.bg_size )
        # create the hero
        initPos = ( bg_size[0]//2, bg_size[1]-self.blockSize )
        self.hero = myHero.Hero(initPos, self.blockSize, heroInfo[0], {}, 1 )   # 英雄槽为空字典；伤害减轻为正常（为1）
        self.hero.keyDic = heroInfo[1]
        self.hero.haloCanvas = self.haloCanvas  # 受伤反馈画布
        self.hero.hitted = self.hero.hittedRevival
        self.allElements.add(self.hero)
        # 剧情管理员
        self.plotManager = plotManager.Dialogue(0)
        # tower背景图片 及其移动速度
        self.towerBG = pygame.image.load( "image/stg"+ str(self.stg) +"/towerBG.jpg" ).convert()
        self.towerBGRect = self.towerBG.get_rect()
        self.towerBGRect.left = (self.bg_size[0]-self.towerBGRect.width) // 2
        self.towerBGRect.top = (self.bg_size[1]-self.towerBGRect.height) // 2
        # create the map
        self.tower = mapManager.PracticeTower(self.bg_size, self.blockSize)
        self.tower.generateMap()
        self.pool = enemy.Pool(self.bg_size, self.blockSize*2)

        # 训练师。
        pos = (self.tower.house.rect.left, self.tower.house.rect.bottom)
        self.trainer = myHero.Trainer(self.bg_size, self.blockSize, trainerInfo[0], self.hero, pos)
        self.trainer.hitted = self.trainer.hittedRevival
        # self.allElements.add(self.trainer)
        # add elems of each area to the allElements and hero's checkList.
        for key in self.tower.groupList:
            for brick in self.tower.groupList[key]:
                self.allElements.add( brick )    # 加入walls
                if key=="-1":
                    self.hero.checkList.add( brick )
                    self.trainer.checkList.add( brick )
        for elem in self.tower.elemList:
            self.allElements.add(elem)
            self.hero.checkList.add(elem)
            self.trainer.checkList.add( elem )
        self.allElements.add(self.tower.house)
        # create natural impediments and monsters for each area.
        for group in self.tower.groupList:         # deal every odd row; group is the key (a number str of layer)
            if int(group)>0 and ( len(self.tower.groupList[group])>0 ) and  ( random() <= 0.9 ):
                minion = enemy.Strawman(self.tower.groupList[group], self.tower.blockSize, group)
                self.tower.monsters.add(minion)
                self.allElements.add(minion)

    def go(self):
        self.music.play(-1)
        self.screen.fill( (0, 0, 0) )
        self.screen.blit( self.towerBG, self.towerBGRect )
        for item in self.allElements:
            self.screen.blit( item.image, item.rect )
        while self.gameOn:
            if not self.paused: # 若未暂停
                # respond to the player's ongoing keydown event
                # get the list including the boolean status of all keys:
                key_pressed = pygame.key.get_pressed()
                if key_pressed[ self.hero.keyDic["leftKey"] ]:
                    self.hero.moveX( self.delay, "left" )
                elif key_pressed[ self.hero.keyDic["rightKey"] ]:
                    self.hero.moveX( self.delay, "right" )
                self.frontier = min(self.bg_size[1], self.hero.rect.bottom)
                self.frnLayer = max(0, self.hero.onlayer)
                
                # move all if the screen need to be adjusted.
                gap = ( self.bg_size[0] - (self.tower.boundaries[0]+self.tower.boundaries[1]) ) //2
                if gap:
                    lvl = min(gap, 10) if gap>0 else max(gap, -10)
                    self.tower.level( lvl )
                    for elem in self.allElements:
                        elem.level( lvl )
                
                # check hero's jump and fall:
                # 若处于跳跃状态，则执行跳跃函数
                if self.hero.k1 > 0:
                    self.hero.jump( self.tower.getTop(self.hero.onlayer+1) )
                # 否则，执行掉落函数
                else:
                    fallChecks = self.tower.groupList[str(self.hero.onlayer-1)]
                    if self.hero.rect.bottom <= self.tower.house.rect.top+2:
                        self.hero.checkList.add( self.tower.house )
                    self.hero.fall(self.tower.getTop(self.hero.onlayer-1), fallChecks, self.stg, self.tower.heightList)
                
                # 每隔一段时间在屏幕范围内生成一波strawMan，上限为4.
                if not ( self.delay % 60 ) and len(self.tower.monsters)<=3 and random() <= 0.3:
                    line = choice( ["1","3","5"] )
                    minion = enemy.Strawman(self.tower.groupList[line], self.blockSize, line)
                    self.tower.monsters.add(minion)
                    self.allElements.add(minion)
                
                # repaint all elements
                self.screen.blit( self.towerBG, self.towerBGRect )
                for item in self.allElements:
                    self.moveMons( item, [self.hero] )       # 分关卡处理所有的敌人（自然阻碍和怪兽）。由于是覆盖的函数，需要给self参数。
                    if item.category=="lineWall" or item.category=="baseWall" or item.category=="sideWall" or item.category=="specialWall":
                        item.paint(self.screen)
                    elif item.category == "lineDecor":
                        item.alter()
                        self.screen.blit(item.image, item.rect)
                    elif item.category=="house":
                        item.paint(self.screen, self.spurtCanvas, self.fntSet[0], self.language )
                    # 处理投掷物：投掷物的move函数将返回三种情况：1.返回False，表示未命中；2.返回包含两个元素的元组，含义分别为投掷物的方向“right”或“left”，以及投掷物击中的坐标（x，y）；
                    # 3.返回包含三个元素的元组，第三个元组为标志命中目标是否死亡。
                    elif item.category=="bullet" or item.category=="bulletPlus":
                        if item.owner.category=="hero":
                            tgts = self.tower.monsters
                            if self.trainer not in tgts:
                                tgts.add(self.trainer)
                        else:
                            tgts = [self.hero]     # 是trainer发出的弹药，目标是玩家。
                        if item.category=="bullet":
                            item.move(tgts, self.spurtCanvas, self.bg_size)
                        else:
                            item.move(item, self.delay, tgts, self.spurtCanvas, self.bg_size) # 这里还要传入投掷物本身
                        self.screen.blit(item.image, item.rect)
                
                # 操作训练师。
                if self.trainer:
                    # check trainer's jump and fall:
                    # 若处于跳跃状态，则执行跳跃函数
                    if self.trainer.k1 > 0:
                        self.trainer.jump( self.tower.getTop(self.trainer.onlayer+1) )
                    # 否则，执行掉落函数
                    else:
                        fallChecks = self.tower.groupList[str(self.trainer.onlayer-1)]
                        if self.trainer.rect.bottom <= self.tower.house.rect.top+2:
                            self.trainer.checkList.add( self.tower.house )
                        self.trainer.fall(self.tower.getTop(self.trainer.onlayer-1), fallChecks, self.stg, self.tower.heightList)
                    self.trainer.decideAction(self.delay, self.tower.heightList, self.allElements)
                    self.trainer.checkImg( self.delay, self.spurtCanvas, [self.hero] )
                    self.trainer.paint(self.screen)
                    drawHealth( self.screen, self.trainer.rect.left+self.trainer.rect.width//2, self.trainer.rect.top-8, 0, 8, self.trainer.health, self.trainer.full, 1 )

                if self.delay <= 120:
                    for each in self.tower.monsters:
                        self.addSymm( self.aimImg, enemy.getPos(each,0.5,0.5)[0]-480, enemy.getPos(each,0.5,0.5)[1]-360)

                # decide the image of Hero
                self.hero.checkImg( self.delay, self.spurtCanvas, self.tower.monsters )
                self.hero.paint( self.screen )
                drawHealth( self.screen, self.hero.rect.left+self.hero.rect.width//2, self.hero.rect.top-8, 0, 8, self.hero.health, self.hero.full, 1 )
                if len(self.hero.jmpInfo)>0:        # 绘画跳跃烟尘效果
                    self.screen.blit( self.hero.jmpInfo[0], self.hero.jmpInfo[1] )
                # 从hero的preyList信息列表中取击中信息。
                for hitInfo in self.hero.preyList:
                    self.spurtCanvas.addSpatters( hitInfo[3], [2, 3, 4], [10, 11, 12], hitInfo[2], hitInfo[1])
                self.hero.preyList = []    # 每次刷新读取所有信息后，将list重置为空表
                self.hero.eventList = []   # 没有宝箱事件，也没有其他触发事件，故置为空以防溢出

                if self.vibration > 0:
                    if (self.vibration % 2 == 0):
                        for elem in self.allElements:
                            elem.lift(4)
                            elem.level(4)
                    elif (self.vibration % 2 == 1):
                        for elem in self.allElements:
                            elem.lift(-4)
                            elem.level(-4)
                    self.vibration -= 1

                # Pool & 绘制三层画布
                sprites = [self.hero, self.trainer]
                #for each in self.tower.monsters:
                #    sprites.append(each)
                self.pool.flow( self.delay, self.screen, sprites, self.spurtCanvas )
                self.screen.blit( self.pool.canvas, self.pool.canvasRect )
                if self.spurtCanvas:
                    self.spurtCanvas.update(self.screen)
                if self.haloCanvas:
                    self.haloCanvas.update( self.delay, self.screen )
                if self.nature:
                    self.nature.update(self.screen)

                pos = pygame.mouse.get_pos()
                bannerList = self.renderBanner(pos)
                back = bannerList[0]
                tips = bannerList[3]
                BGMusic = bannerList[4]
                # check big events.
                heroC = enemy.getPos(self.hero, 0.5, 0.5)[0]
                if heroC<0 or heroC>self.bg_size[0]:
                    self.music.stop()
                    self.clearAll()
                    self.gameOn = False
                    return [False]

            else:
                # 透明灰色打底
                if not self.setBG:
                    self.setBG = True
                    drawRect( 0, 0, self.bg_size[0], self.bg_size[1], (0,0,0,180), self.screen )
                    tip = choice( self.plotManager.tips )
                # 加Board to represent some tips.
                self.addSymm( pygame.image.load("image/cardBoard.png"), 0, 0 )
                self.addSymm( pygame.image.load("image/Enter.png").convert_alpha(), 0, -60 )
                self.addTXT( ["continue/pause","继续/暂停"], 0, (20,20,20), 0, -30)
                # tip area. 
                drawRect( self.bg_size[0]//2-240, self.bg_size[1]//2+20, 480, 100, (210,180,120,120), self.screen )
                topAlign = 50
                for line in tip:
                    self.addTXT( line, 0, (0,0,0), 0, topAlign )
                    topAlign += 20
                    
            # 一次性的鼠标点击或按键事件
            for event in pygame.event.get():
                if ( event.type == QUIT ):
                    pygame.quit()
                    sys.exit()
                elif ( event.type == KEYDOWN ):
                    if not self.paused:
                            if ( event.key == self.hero.keyDic["wrestleKey"] ):   # 挥刀
                                self.hero.whip()
                            elif ( event.key == self.hero.keyDic["jumpKey"] ):    # 跳跃
                                if ( self.hero.k1 > 0 ) and ( self.hero.k2 == 0 ):
                                    self.hero.k2 = 1
                                if not self.hero.trapper and self.hero.aground and ( self.hero.k1 == 0 ):
                                    self.hero.k1 = 1
                            elif ( event.key == self.hero.keyDic["shootKey"] ) and self.hero.affected<0:    # 射箭
                                self.hero.shoot( self.allElements, self.delay )
                                self.hero.arrow = 12
                            elif ( event.key == self.hero.keyDic["itemKey"] ):    # 使用背包物品
                                self.hero.useItem( self.spurtCanvas )
                            elif ( event.key == self.hero.keyDic["downKey"] ):    # 下跳
                                self.hero.shiftLayer(-2, self.tower.heightList)
                            elif ( event.key == self.hero.keyDic["bagKey"] ):     # 切换背包物品
                                self.hero.bagPt = (self.hero.bagPt + 1) % len(self.hero.bagBuf)
                            # elif ( event.key == pygame.K_u ):              # 特殊技能
                            #     self.hero.special()
                    if ( event.key == pygame.K_RETURN ):          # 暂停/解除暂停
                        self.paused = not self.paused
                        self.setBG = False # 用以指示可以铺一层透明背景
                elif event.type == pygame.MOUSEBUTTONUP:          # 鼠标事件
                    if not self.paused:
                        if ( back.left < pos[0] < back.right ) and ( back.top < pos[1] < back.bottom ):  # 退出（放弃）当前关卡
                            self.music.stop()
                            self.clearAll()
                            self.gameOn = False
                            return [False]
                        elif ( tips.left < pos[0] < tips.right ) and (tips.top < pos[1] < tips.bottom ):
                            self.paused = not self.paused
                        elif ( BGMusic.left < pos[0] < BGMusic.right ) and (BGMusic.top < pos[1] < BGMusic.bottom ):
                            if self.musicOn:
                                self.music.stop()
                                self.musicOn = False
                            else:
                                self.music.play(-1)
                                self.musicOn = True
            pygame.display.flip()   # from buffer area load the pic to the screen

            self.delay -= 1
            if not self.delay:
                self.delay = 240
            self.clock.tick(60)

    # ---- clear all elements in the current area ----
    def clearAll(self):
        for each in self.allElements:
            each.kill()
            del each
    
    # ========================================================================
    # ================= 用于检测item为敌人的情况下，并移动该敌人 ================
    # 将这一部分从go()分离出来的目的是不让主函数显得过于庞大，单独成为一个辅助函数有助于之后的维护和修改
    # ========================================================================
    def moveMons(self, item, heroes):
        if ( item.rect.bottom >= 0 ) and ( item.rect.top <= self.bg_size[1] ):  # moves only if the gozilla appears in the screen
            if item.category == "strawman":
                item.move(self.delay, heroes)
                drawHealth( self.screen, item.rect.left+item.rect.width//2, item.rect.top-8, 0, 8, item.health, item.full, 1 )
                self.screen.blit(item.image, item.rect)
            elif item.category == "crop":
                item.move()
                self.screen.blit(item.image, item.rect)

    # --- paint upper banner (contains 3 sections) ---
    def renderBanner(self, pos):
        # paint 4 background sections and get their rect.
        sect1 = drawRect(20, 10, 60, 40, (0,0,0,120), self.screen)    # Back Option.
        sect2 = drawRect(100, 10, 120, 40, (0,0,0,120), self.screen)  # Practice Model.
        sect3 = drawRect(240, 10, 540, 40, (0,0,0,120), self.screen)  # Msg Option.
        sect4 = drawRect(800, 10, 60, 40, (0,0,0,120), self.screen)   # Tip Option.
        sect5 = drawRect(880, 10, 60, 40, (0,0,0,120), self.screen)   # Music Option.
        # give banner info.
        ctr = (sect1.left+sect1.width//2-self.bg_size[0]//2, sect1.top+sect1.height//2-self.bg_size[1]//2)  # 更改为中心坐标系统的中心点参数
        back = self.addSymm( pygame.image.load("image/back.png").convert_alpha(), ctr[0], ctr[1] )   # 返回箭头
        if ( back.left < pos[0] < back.right ) and ( back.top < pos[1] < back.bottom ):  # 退出（放弃）当前关卡
            back = self.addSymm( pygame.image.load("image/backOn.png").convert_alpha(), ctr[0], ctr[1] )
            self.addTXT( ("quit","放弃"), 0, (255,255,255), ctr[0], ctr[1] )

        ctr = (sect2.left+sect2.width//2-self.bg_size[0]//2, sect2.top+sect2.height//2-self.bg_size[1]//2)
        self.addTXT( ("Practice", "训练场"), 1, (255,255,255), ctr[0], ctr[1] )

        ctr = (sect4.left+sect4.width//2-self.bg_size[0]//2, sect4.top+sect4.height//2-self.bg_size[1]//2)
        tips = self.addSymm( self.controller[1], ctr[0], ctr[1] )
        if ( tips.left < pos[0] < tips.right ) and (tips.top < pos[1] < tips.bottom ):
            tips = self.addSymm( self.controllerOn[1], ctr[0], ctr[1])
            self.addTXT( ("tips","帮助"), 0, (255,255,255), ctr[0], ctr[1] )

        ctr = (sect5.left+sect5.width//2-self.bg_size[0]//2, sect5.top+sect5.height//2-self.bg_size[1]//2)
        BGMusic = self.addSymm( self.controller[2], ctr[0], ctr[1] ) if self.musicOn else self.addSymm( self.controller[3], ctr[0], ctr[1] )
        if ( BGMusic.left < pos[0] < BGMusic.right ) and (BGMusic.top < pos[1] < BGMusic.bottom ):
            if self.musicOn:
                BGMusic = self.addSymm( self.controllerOn[2], ctr[0], ctr[1] )
                self.addTXT( ("music off","关闭音乐"), 0, (255,255,255), ctr[0], ctr[1] )
            else:
                BGMusic = self.addSymm( self.controllerOn[3], ctr[0], ctr[1] )
                self.addTXT( ("music on","开启音乐"), 0, (255,255,255), ctr[0], ctr[1] )

        return (sect1, sect2, sect3, sect4, sect5)
                
    # ===========================================
    # Surface对象； x，y为正负（偏离屏幕中心点）像素值，确定了图像的中点坐标
    def addSymm(self, surface, x, y):
        rect = surface.get_rect()
        rect.left = (self.bg_size[0] - rect.width) // 2 + x
        rect.top = (self.bg_size[1] - rect.height) // 2 + y
        self.screen.blit( surface, rect )
        return rect   # 返回图片的位置信息以供更多操作

    # ===========================================
    # x,y为正负（偏离屏幕中心点）像素值，确定了文字行的左上角坐标。这样改动是为了和addSymm()函数保持一个相对统一的系统。
    def addTXT(self, txtList, fntSize, color, x, y):
        txt = self.fntSet[fntSize][self.language].render( txtList[self.language], True, color )
        rect = txt.get_rect()
        rect.left = (self.bg_size[0] - rect.width) //2 + x
        rect.top = (self.bg_size[1] - rect.height) //2 + y
        self.screen.blit( txt, rect )
        return rect
