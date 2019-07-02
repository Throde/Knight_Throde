# map generator and controller
import sys
import traceback
import math

import pygame
from pygame.locals import *
from random import *

'''----------------------------------- MAP GENERATORS -------------------------------'''
# ================================================================================
# ================================ 冒险模式 map ===================================
# ================================================================================
class AdventureTower():
    # some properties of the MapManager
    oriPos = (0,0)    # parameters about the screen (px)
    blockSize = 0      # parameters about the block size (px)  EVEN NUMBER RECOMMENDED !
    diameter = 0       # total width of the tower (number)   MUST BE OVER 7 !
    layer = 0          # total layers of the current stage (number), should be an even number
    stg = 1
    area = 0           # default: 0
    boundaries = ()
    
    specialOn = True   # the tag that indicate if we generate special wall in the map
    groupList = {}     # dictionary restoring wallsprite by classified groups {"layer": Group, "layer": Group, ...}，其中-1表示边砖，-3表示装饰物
    heightList = {}    # dictionary for the y pixel of each line. 注意，这里存储的是每一行的底部，如‘-1’值为basewall的底端，即720.
    elemList = None

    doubleP = 0        # possibility that one chest contains 2 stuffs
    chestList = None
    porter = None
    monsters = None
    goalieList = None  # a group to indicate all goalies in this area.

    # Constructor of MapManager
    # Area: 0,1,2. 0~initial area; 1~middle area;2~top area.
    def __init__(self, oriPos, block_size, diameter, layer, stg, area, specialOn, doubleP):
        if (diameter < 7):
            return False
        self.oriPos = oriPos
        self.blockSize = block_size
        self.diameter = diameter
        self.layer = layer
        leftBound = self.oriPos[0] + self.blockSize
        rightBound = self.oriPos[0] + (self.diameter-1)*self.blockSize
        self.boundaries = (leftBound, rightBound)
        
        self.groupList = {}
        self.groupList["-1"] = pygame.sprite.Group()  # prepare to include the side walls of left & right side
        self.groupList["0"] = pygame.sprite.Group()   # prepare to include lineDecors
        self.heightList = {}
        
        self.stg = stg
        self.area = area
        self.specialOn = specialOn
        self.elemList = pygame.sprite.Group()

        self.chestList = pygame.sprite.Group()
        self.doubleP = doubleP
        self.monsters = pygame.sprite.Group()
        self.goalieList = pygame.sprite.Group()

    # 生成随机地图的函数
    def generateMap(self):
        # 从地下2层（y=-2）开始，创建各层的砖块
        # note that: y 像素设定为每个wall的 bottom 像素值
        y = -2
        pixlY = self.oriPos[1]+self.blockSize
        while ( y <= self.layer+3 ):          # 包括-2、-1层和layer+3层(roof层)
            self.heightList[str(y)] = pixlY   # 将新一行的位置信息写入HeightList中
            x = 0                             # 每次开始新一行的循环时，都将x置为第 0 格
            pixlX = self.oriPos[0]
            # 首先在groupList中为本行初始化一个group。如果该行是奇数行（1，3，5...）或最顶层（最顶层为layer+2，是偶数）则添加随机数量的wall
            if ( y%2 == 1 ) or ( y == self.layer+2 ):
                if y>0:  # -1行不能新建一行
                    self.groupList[ str(y) ] = pygame.sprite.Group() # note that 该 group 的 key 以 y 命名
                rowWallList = self.wallClassifier( y )
            # 行级循环：
            while x < self.diameter:
                # 判断：若是塔的两侧,或是随机指定的墙块
                # 若为边砖：加入砖 group "-1" 中
                if ( (x==0) or (x == self.diameter-1) ):
                    # 如果不为最低10层、不为最高的几层，则有0.65的概率会有边砖。
                    if y<=10 or y>=self.layer-1 or random()<0.65:
                        brick = SideWall( pixlX, pixlY-self.blockSize, self.stg, (x,y) )
                        self.groupList["-1"].add(brick)
                # roof层，铺满base砖。
                elif (y == self.layer+3):
                    brick = Wall( pixlX, pixlY-self.blockSize, "baseWall", self.stg, (x,y) )
                    self.groupList[ str(y) ].add(brick)
                # 否则，则为行砖：加入当前行的 group 中
                elif (y%2 == 1):
                    if x in rowWallList:
                        if ( y > 0 and y < self.layer):
                            # 处理行内砖块
                            if self.specialOn and y<(self.layer-1) and random()<=0.12:
                                brick = SpecialWall( pixlX, pixlY-self.blockSize, self.stg, (x,y) )
                                if brick.elem:
                                    self.elemList.add(brick.elem)
                            else:
                                brick = Wall(pixlX, pixlY-self.blockSize, "lineWall", self.stg, (x,y))
                                if random() < 0.16:
                                    decor = Decoration( (pixlX+self.blockSize//2-6, pixlX+self.blockSize//2+6), pixlY-self.blockSize, "lineDecor", self.stg, (x,y), ("A","B"), 0 )
                                    self.groupList["0"].add(decor)
                                if self.stg==3:      # 避免了公主与chest重合，且避免第三关中的补给品出现在掉落砖块上
                                    self.addChest( pixlX, pixlY, (x,y), 0.18 )
                            if not self.stg==3:
                                self.addChest( pixlX, pixlY, (x,y), 0.15 )
                        elif (y <= 0): # 最底层的砖特殊
                            brick = Wall(pixlX, pixlY-self.blockSize, "baseWall", self.stg, (x,y))
                        self.groupList[ str(y) ].add(brick)
                    # 以下是x不在rowWallList当中的情况。第二关中要铺设webWall：
                    elif self.stg==2 and self.area>=2 and y>=10:
                        web = WebWall( pixlX, pixlY-self.blockSize, self.stg, (x,y) )
                        self.elemList.add(web)
                x = x + 1
                pixlX = pixlX + self.blockSize
            y = y + 1
            pixlY = pixlY - self.blockSize
        # 整个area完成之后，给进出口处增加接口。不同区域的接口要求不同。
        if self.area==0:
            for sideWall in self.groupList["-1"]:
                self.addInterface( sideWall, 0, "left", True, "notice" )
                self.addInterface( sideWall, self.layer, "right", False, "door" )
        elif self.area==1:
            for sideWall in self.groupList["-1"]:
                self.addInterface( sideWall, 0, "left", False, "notice" )
                self.addInterface( sideWall, self.layer, "right", False, "door" )
        elif self.area==2:
            for sideWall in self.groupList["-1"]:
                self.addInterface( sideWall, 0, "left", False, "notice" )    #左侧，连接上一区域
                self.addInterface( sideWall, 0, "right", True, "hostage" )   #右侧，营救对象所在
                self.addInterface( sideWall, self.layer, "right", True, "exit" )
        # 接口完成后，返回本area的极左位置值。（包括伸出的平台接口计算在内）
        return ( self.oriPos[0]+(self.diameter+2)*self.blockSize, self.oriPos[1]-self.blockSize*self.layer )

    def addChest(self, pixlX, pixlY, coord, rate):
        if random() <= rate:
            contains = 1
            if random() < self.doubleP:
                contains = 2
            supply = Chest( pixlX+self.blockSize//2, pixlY-self.blockSize, supClassify( self.stg ), coord, (960, 720), contains )
            self.chestList.add(supply)

    # 以下是两个创造塔楼间接口的函数。
    # Close参数为布尔值，指明该接口是否封闭。layer采用的是英雄的一套层数体系（偶数体系）。
    def addInterface(self, sideWall, layer, direction, close, porterCate):
        if direction=="left":
            x = 0  # 格
            ctr = sideWall.rect.left
            x1 = sideWall.rect.left-self.blockSize  # 像素坐标
            x2 = sideWall.rect.left-2*self.blockSize
        elif direction=="right":
            x = self.diameter-1
            ctr = sideWall.rect.right
            x1 = sideWall.rect.right
            x2 = sideWall.rect.right+self.blockSize
        # 首先，若是close，则将两块sideWall向外平移两格；若不close，则直接清除。
        if ( sideWall.coord[1]==layer or sideWall.coord[1]==layer+1 ) and (sideWall.coord[0]==x):
            if close:
                dist = x2-sideWall.rect.left
                sideWall.level( dist )
                sideWall.coord = ( sideWall.coord[0]+round(dist/self.blockSize), sideWall.coord[1] )
            else:
                sideWall.erase()
        # 然后进行扩展搭建。
        elif ( sideWall.coord[1]==layer-1 or sideWall.coord[1]==layer+2) and (sideWall.coord[0]==x):
            # 上下层必须盖两个
            brick = Wall( x1, sideWall.rect.top, "sideWall", self.stg, (sideWall.coord[0]+1,sideWall.coord[1]) )
            self.groupList["-1"].add(brick)
            if close:
                brick = Wall( x2, sideWall.rect.top, "sideWall", self.stg, (sideWall.coord[0]+1,sideWall.coord[1]) )
                self.groupList["-1"].add(brick)
            # 在接口处建立需要的物品（关卡门或其他东西）🚪
            if sideWall.coord[1]==layer-1:
                if porterCate=="door" or porterCate=="exit":
                    self.porter = Porter( ctr, sideWall.rect.top, porterCate, self.stg, (sideWall.coord[0]+1,self.layer) )
                    self.chestList.add(self.porter)
                elif porterCate=="notice" or porterCate=="hostage":
                    port = Porter( ctr, sideWall.rect.top, porterCate, self.stg, (sideWall.coord[0]+1,self.layer) )
                    self.chestList.add(port)  # 当前当作装饰

    # assistant method: y should be an odd number
    def wallClassifier(self, y):
        rowWallList = []
        if ( y >= 0 ) and ( y <= self.layer ):
            wallNum = randint( 3, self.diameter-4 ) # 一行中至少要留两个缺口，至少有3格砖块
            i = 0
            while i < wallNum:
                m = choice(range(1, self.diameter-1))
                if m not in rowWallList:                   # 如果随机数与以前的不重复，则可取，并且i++，否则什么都不执行，继续循环
                    rowWallList.append(m)
                    i = i + 1
            if (y==self.layer-1) and (self.diameter-2 not in rowWallList):
                rowWallList.append(self.diameter-2)
        # 处理layer+1（即roof-1）层：这层要空出来，所以不铺砖
        elif ( y==self.layer+1 ):
            pass
        # 处理-1层或塔顶层(layer+2)：全部铺满砖
        else:
            for num in range(1, self.diameter-1):
                rowWallList.append(num)
        return rowWallList

    # ----- search the wall's rect.top according to the given line number ----
    def getTop(self, layer):
        if str(layer) in self.heightList:
            return self.heightList[str(layer)]-self.blockSize
        else:
            return False

    def lift(self, dist):
        for h in self.heightList:
            self.heightList[h] = self.heightList[h] + dist

    def level(self, dist):
        self.boundaries = ( self.boundaries[0]+dist, self.boundaries[1]+dist )

# ================================================================================
# ================================ 休闲模式 map ===================================
# ================================================================================
class EndlessTower():

    # some properties of the MapManager
    bg_size = (0,0)    # parameters about the screen (px)
    blockSize = 0      # parameters about the block size (px)  EVEN NUMBER RECOMMENDED !
    diameter = 0       # total width of the tower (number)   MUST BE OVER 7 !       
    stg = 1
    iniLayer = 60      # layers of the initial stage (number), should be an even number
    addLayer = 10
    curLayer = 0
    boundaries = ()

    groupList = {}     # dictionary restoring wallsprite by classified groups {"layer": Group, "layer": Group, ...}
    heightList = {}
    elemList = None
    chestList = None
    monsters = None
    
    # ====================================================================
    # Constructor of MapManager ------------------------------------------
    def __init__(self, bg_size, block_size, diameter, stg):
        # initialize the properties of the object
        if (diameter < 7):
            return False
        self.bg_size = bg_size
        self.blockSize = block_size
        self.diameter = diameter
        leftBound = (self.bg_size[0] - self.diameter * self.blockSize) // 2 + self.blockSize
        rightBound = (self.bg_size[0] + self.diameter * self.blockSize) // 2 - self.blockSize
        self.boundaries = (leftBound, rightBound)

        self.groupList = {}
        self.groupList["-1"] = pygame.sprite.Group() # include the side walls of left & right side
        self.groupList["0"] = pygame.sprite.Group()  # prepare to include lineDecors
        self.elemList = pygame.sprite.Group()        # store all elements of special bricks
        self.chestList = pygame.sprite.Group()
        self.heightList = {}
        self.stg = stg

        self.monsters = pygame.sprite.Group()

    # =====================================================================
    # construct the initial 60 layers -------------------------------------
    def generateIni(self, screen):
        y = -1            # 从地下一层（y=-1）开始，创建各层的砖块
        pixlY = self.bg_size[1]          # y 像素设定为每个wall的 bottom 像素值
        while ( y <= self.iniLayer ):    # 包括-1层至initLayer(60)层
            self.heightList[str(y)] = pixlY   # 将新一行的位置信息写入HeightList中
            x = 0         # 每次开始新一行的循环时，都将x置为第 0 格
            pixlX = (self.bg_size[0] - self.diameter * self.blockSize) // 2
            # 如果该行是奇数行（1，3，5...）则添加随机数量的wall
            if ( y % 2 == 1 ):
                self.groupList[ str(y) ] = pygame.sprite.Group() # 该 group 的 key 以 y 命名
                rowWallList = self.wallClassifier( y )
            # 行级循环：
            while x < self.diameter:
                # 若为边砖，则加入砖 group "-1" 中
                if (x==0) or (x == self.diameter-1):
                    brick = SideWall( pixlX, pixlY-self.blockSize, self.stg, (x,y) )
                    self.groupList["-1"].add(brick)
                # 否则为行内砖，加入当前行的 group 中
                elif (y%2 == 1) and (x in rowWallList):
                    if ( y > 0 and y < self.iniLayer):
                        # 处理砖块
                        if random()<=0.12:
                            brick = SpecialWall( pixlX, pixlY-self.blockSize, self.stg, (x,y) )
                            if brick.elem:
                                self.elemList.add(brick.elem)
                        else:
                            brick = Wall(pixlX, pixlY-self.blockSize, "lineWall", self.stg, (x,y))
                            if random() < 0.16:
                                decor = Decoration( (pixlX+self.blockSize//2-6, pixlX+self.blockSize//2+6), pixlY-self.blockSize, "lineDecor", self.stg, (x,y), ("A","B"), 0 )
                                self.groupList["0"].add(decor)
                            if self.stg==3:          # 避免了第三关中的补给品出现在掉落砖块上
                                self.addChest( pixlX, pixlY, (x,y), 0.18 )
                        # 处理砖块上的物品（如宝箱）
                        if not self.stg==3:
                            self.addChest( pixlX, pixlY, (x,y), 0.15 )
                    else:
                        brick = Wall(pixlX, pixlY-self.blockSize, "baseWall", self.stg, (x,y)) # 最地下一层的砖特殊，加入到-1层当中
                    self.groupList[ str(y) ].add(brick)
                x = x + 1
                pixlX = pixlX + self.blockSize
            y = y + 1
            pixlY = pixlY - self.blockSize
        self.curLayer = self.iniLayer

    # 生成更多
    def addMore(self):
        y = self.curLayer + 1            # 从第y=当前最高+1行开始，增加数层的砖块
        pixlY = self.getTop(self.curLayer)  # 从sideWall中找出纵坐标等于当前层数的砖，确定增加的起始位置
        while ( y <= self.curLayer+20 ): # 循环20次
            self.heightList[str(y)] = pixlY
            x = 0
            pixlX = (self.bg_size[0] - self.diameter * self.blockSize) // 2
            if ( y % 2 == 1 ):           # 如果该行是奇数行（1，3，5...）则添加随机数量的wall
                self.groupList[ str(y) ] = pygame.sprite.Group()
                rowWallList = self.wallClassifier( y )
            while x < self.diameter:     # 行级循环：
                if (x==0) or (x == self.diameter-1):   # 若为边砖，则加入砖 group "-1" 中
                    if random()<0.65:
                        brick = SideWall( pixlX, pixlY-self.blockSize, self.stg, (x,y) )
                        self.groupList["-1"].add(brick)
                elif (y%2 == 1) and (x in rowWallList):# 否则为行内砖，加入当前行的 group 中
                    # 处理砖块 (这里操作的砖块必须是iniLayer以上的，故不可能为0)
                    if random()<=0.12:
                        brick = SpecialWall( pixlX, pixlY-self.blockSize, self.stg, (x,y) )
                        if brick.elem:
                            self.elemList.add(brick.elem)
                    else:
                        brick = Wall(pixlX, pixlY-self.blockSize, "lineWall", self.stg, (x,y))
                        if random() < 0.16:
                            decor = Decoration( (pixlX+self.blockSize//2-6, pixlX+self.blockSize//2+6), pixlY-self.blockSize, "lineDecor", self.stg, (x,y), ("A","B"), 0)
                            self.groupList["0"].add(decor)
                        if self.stg==3:          # 避免了第三关中的补给品出现在掉落砖块上
                            self.addChest( pixlX, pixlY, (x,y), 0.18 )
                    # 处理砖块上的物品（如宝箱）
                    if not self.stg==3:
                        self.addChest( pixlX, pixlY, (x,y), 0.15 )
                    self.groupList[ str(y) ].add(brick)
                x = x + 1
                pixlX = pixlX + self.blockSize
            y = y + 1
            pixlY = pixlY - self.blockSize
        self.curLayer += 20           # 处理完毕后当前的塔层数+10
        # 增加10层后，删除最下方的10层砖块，以保证运动的只有60块砖
        # （注意，这里不删除groupList中的字典项，因此低层的会变成空项，依然可以被索引到）
        for line in self.groupList:
            for wall in self.groupList[line]:    # 删除处理所有过低的 Wall
                if wall.coord[1] <= self.curLayer-60:
                    wall.erase()
        for chest in self.chestList:
            if chest.coord[1] <= self.curLayer-60:
                chest.erase()
        for elem in self.elemList:
            if elem.coord[1] <= self.curLayer-60:
                elem.erase()
        # 由于字典在迭代过程中长度不能变化，因此使用一个辅助的列表来存储所有需要删掉的key。
        aidList = []
        for height in self.heightList:
            if int(height)<=self.curLayer-60:
                aidList.append(height)
        for height in aidList:
            self.heightList.pop(height)

    def addChest(self, pixlX, pixlY, coord, rate):
        if random() <= rate:
            contains = 1
            if random() < 0.2:
                contains = 2
            supply = Chest( pixlX+self.blockSize//2, pixlY-self.blockSize, supClassify( self.stg ), coord, self.bg_size, contains )
            self.chestList.add(supply)

    # assistant method: y should be an odd number
    def wallClassifier(self, y):
        rowWallList = []
        if ( y >= 0 ):
            wallNum = randint( 3, self.diameter-4 ) # 一行中至少要留两个缺口，至少有3格砖块
            i = 0
            while i < wallNum:
                m = choice(range(1, self.diameter-1))
                if m not in rowWallList:                   # 如果随机数与以前的不重复，则可取，并且i++，否则什么都不执行，继续循环
                    rowWallList.append(m)
                    i = i + 1
        else:         # -1层全部铺满砖
            for num in range(1, self.diameter-1):
                rowWallList.append(num)
        return rowWallList
    
    # ----- search the wall according to the given line number ----
    def getTop(self, layer):
        if str(layer) in self.heightList:
            return self.heightList[str(layer)]-self.blockSize
        else:
            return False

# ================================================================================
# ================================= 练习场 map ===================================
# ================================================================================
class PracticeTower():
    # some properties of the MapManager
    bg_size = (0,0)     # parameters about the screen (px)
    blockSize = 0      # parameters about the block size (px)  EVEN NUMBER RECOMMENDED !
    diameter = 14      # total width of the tower (number, including sideWalls)   MUST BE OVER 7 !
    layer = 6          # total layers of the current stage (number), should be an even number
    boundaries = ()
    
    house = None
    stg = 0
    groupList = {}     # dictionary restoring wallsprite by classified groups {"layer": Group, "layer": Group, ...}，其中-1表示边砖，-3表示装饰物
    heightList = {}    # dictionary for the y pixel of each line. 注意，这里存储的是每一行的底部，如‘-1’值为basewall的底端，即720.
    elemList = None
    monsters = None

    # Constructor of MapManager.
    # 本model和另外两个模式的map相比较为固定且特殊，故不需外界model传入位置、宽高信息，均由本manager自行掌握。
    def __init__(self, bg_size, block_size):
        self.bg_size = bg_size
        self.blockSize = block_size
        leftBound = (self.bg_size[0] - (self.diameter-2)*self.blockSize) // 2  # 剪掉了sidewall。故boundaries是岛内的区域。
        rightBound = (self.bg_size[0] + (self.diameter-2)*self.blockSize) // 2
        self.boundaries = (leftBound, rightBound)
        self.house = None
        
        self.groupList = {}
        self.groupList["-1"] = pygame.sprite.Group()  # prepare to include the side walls of left & right side
        self.groupList["0"] = pygame.sprite.Group()   # prepare to include lineDecors
        self.heightList = {}
        self.elemList = pygame.sprite.Group()
        self.monsters = pygame.sprite.Group()

    # 生成随机地图的函数
    def generateMap(self):
        # 从地下一层（y=-1）开始，创建各层的砖块
        # note that: y 像素设定为每个wall的 bottom 像素值
        y = -1
        pixlY = self.bg_size[1]+self.blockSize//3         # 略微下沉一些。
        while ( y <= self.layer+3 ):          # 包括-1层和layer+3层(roof层)
            self.heightList[str(y)] = pixlY   # 将新一行的位置信息写入HeightList中
            x = 0                             # 每次开始新一行的循环时，都将x置为第 0 格。
            pixlX = self.boundaries[0]-self.blockSize     # boundaries中没有纳入边砖的范围，故这里重新算上。
            # 首先在groupList中为本行初始化一个group。如果该行是奇数行（1，3，5...）或最顶层（最顶层为layer+2，是偶数）则添加随机数量的wall
            if ( y%2 == 1 ) or ( y == self.layer+2 ):
                self.groupList[ str(y) ] = pygame.sprite.Group() # note that 该 group 的 key 以 y 命名
                rowWallList = self.wallClassifier( y )
            # 行级循环：
            while x < self.diameter:
                # 判断：若是塔的两侧，仅在第0、1、2层设置sideWall，且根据不同层数设置不同样式的边砖。
                if ( (x==0) or (x == self.diameter-1) ):
                    if y<2:
                        brick = Wall(pixlX, pixlY-self.blockSize, "sideWall"+str(y+1), self.stg, (x,y))
                        brick.category = "sideWall"
                        self.groupList[ "-1" ].add(brick)
                        if x==0:
                            brick.image = pygame.transform.flip(brick.image, True, False)
                # 否则，则为行砖：加入当前行的 group 中
                elif y%2 and y<self.layer:
                    # 处理行内砖块
                    if rowWallList[x] == "lineWall" or rowWallList[x] == "baseWall":
                        brick = Wall(pixlX, pixlY-self.blockSize, rowWallList[x], self.stg, (x,y))
                        self.groupList[ str(y) ].add(brick)
                        if (y==3 and 3<=x<=5):
                            # 添加房子
                            if x==4:
                                self.house = Porter( brick.rect.left+self.blockSize//2, brick.rect.top, "house", self.stg, brick.coord )
                        else:
                            if random() < 0.8:
                                decor = Decoration( (pixlX+self.blockSize//2, pixlX+self.blockSize//2), pixlY-self.blockSize, "lineDecor", self.stg, (x,y), ("A","B","C"), 10 )
                                self.groupList["0"].add(decor)
                    elif rowWallList[x] == "specialWall":
                        brick = SpecialWall( pixlX, pixlY-self.blockSize, self.stg, (x,y) )
                        self.groupList[ str(y) ].add(brick)
                        if brick.elem:
                            self.elemList.add(brick.elem)
                x = x + 1
                pixlX = pixlX + self.blockSize
            y = y + 1
            pixlY = pixlY - self.blockSize

    # assistant method: y should be an odd number
    def wallClassifier(self, y):  # y: -1, 1, 3, 5
        if not y%2:
            return
        rowWallDic = {}
        i = 1
        while i < self.diameter-1:
            rowWallDic[i] = None
            i += 1
        # For the basic layer, tile all.
        if y==-1:
            for key in rowWallDic:
                rowWallDic[key] = "baseWall"
        # 第二层随机tile. 全为specialWall.
        elif y==1:
            i = 0
            while i < 6:    # Max is 8/14.
                wall = randint( 3, self.diameter-4 )# 左右要空出2 tile。
                if rowWallDic[wall]==None:          # 如果该位置为vaccant，则可取，并且i++；否则什么都不执行，继续循环。
                    rowWallDic[wall] = "specialWall"
                    i = i + 1
        # Third Layer 左侧 build house，所以固定3 tile.
        elif y==3:
            rowWallDic[3] = "lineWall"
            rowWallDic[4] = "lineWall"
            rowWallDic[5] = "lineWall"
            i = 0
            while i < 3:    # Maxis 3/14.
                wall = randint( 6, self.diameter-4 )
                if rowWallDic[wall]==None:
                    rowWallDic[wall] = "lineWall"
                    i = i + 1
        # Forth Layer 左侧给 house 让位，空出3格
        elif y==5:
            rowWallDic[3] = "lineWall"
            rowWallDic[4] = "lineWall"
            rowWallDic[5] = "lineWall"
            i = 0
            while i < 3:
                wall = randint( 6, self.diameter-4 )
                if rowWallDic[wall]==None:
                    rowWallDic[wall] = "lineWall"
                    i = i + 1
            rowWallDic[3] = None
            rowWallDic[4] = None
            rowWallDic[5] = None
        return rowWallDic

    # ----- search the wall's rect.top according to the given line number ----
    def getTop(self, layer):
        if str(layer) in self.heightList:
            return self.heightList[str(layer)]-self.blockSize
        else:
            return False

    def lift(self, dist):
        for h in self.heightList:
            self.heightList[h] = self.heightList[h] + dist

    def level(self, dist):
        self.boundaries = ( self.boundaries[0]+dist, self.boundaries[1]+dist )

# ================================================================================
# ============================ accessaries of the map ============================
# ================================================================================
class Wall(pygame.sprite.Sprite):

    def __init__(self, x, y, cate, stg, coord):
        pygame.sprite.Sprite.__init__(self)
        src = "image/stg"+ str(stg) + "/" + cate + ".png"
        self.image = pygame.image.load(src).convert_alpha()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.left = x
        self.rect.top = y
        self.coord = coord
        self.category = cate
    
    def paint(self, surface):
        surface.blit(self.image, self.rect)

    def erase(self):
        self.kill()
        del self
    
    def lift(self, dist):
        self.rect.bottom += dist

    def level(self, dist):
        self.rect.left += dist
# -----------------------------------------------------------
class SpecialWall(Wall):
    def __init__(self, x, y, stg, coord):
        Wall.__init__(self, x, y, "specialWall", stg, coord)
        self.elem = None
        # 这里的special Elements的坐标都是其所在的wall的坐标
        if stg == 1:
            self.elem = BlockFire(x+self.rect.width//2, y, coord)
        elif stg == 2:
            self.elem = BlockStone(x+self.rect.width//2, y, coord)
        elif stg == 3:
            self.clpCnt = 0  # 等待英雄的踩踏中
        elif stg == 4:
            self.elem = BlockOoze(x+self.rect.width//2, y+4, coord)
        elif stg == 5:
            pass
        elif stg == 6:
            self.elem = Fan(x+self.rect.width//2, y+self.rect.width, coord)
        elif stg == 7:
            self.elem = Stabber(x+self.rect.width//2, y, coord)
        elif stg == 0:
            self.elem = Crop(x+self.rect.width//2, y, coord)

    def collapse(self):
        if self.clpCnt > 0:
            self.rect.bottom += self.clpCnt
            if self.clpCnt <= 8:
                self.clpCnt += 1

# -----------------------------------------------------------
class WebWall(Wall):
    def __init__(self, x, y, stg, coord):
        Wall.__init__(self, x, y, "webWall", stg, coord)
        self.oriImage = self.image
        self.imgBroken = pygame.image.load("image/stg2/webWallBroken.png").convert_alpha()
        self.imgPulled = pygame.image.load("image/stg2/webPulled.png").convert_alpha()
        self.valid = True
        self.ctr = [self.rect.left+self.rect.width//2, self.rect.top+self.rect.height//3]  # 黏贴点
        self.bldColor = (255,255,255,255)
        self.onlayer = coord[1]
        self.exp = 0
    
    # 对于英雄来说，被击穿后本web依然会挂在hero的trapper变量上。但仅仅trap效果生效，而没有了重力的限制，因此英雄会下落，造成一种释放开的错觉。
    def stick(self, sprites):
        if not self.valid:  # 已被打破，则失效
            return False
        for hero in sprites:
            if pygame.sprite.collide_mask(self, hero):
                self.image = self.imgPulled
                hero.trapper = self
                if hero.gravity>1:
                    hero.gravity -= 2
                return True
        self.image = self.oriImage
    
    def hitted(self, damage, pushed):
        self.valid = False
        self.image = self.imgBroken

    def lift(self, dist):
        self.rect.bottom += dist
        self.ctr[1]

    def level(self, dist):
        self.rect.left += dist
        self.ctr[0] += dist

# -----------------------------------------------------------
class SideWall(Wall):

    def __init__(self, x, y, stg, coord):
        Wall.__init__(self, x, y, "sideWall", stg, coord)
        self.decor = None
        # 墙壁的装饰：
        if random() < 0.16:
            self.decor = Decoration( (x+14,x+58), y+62, "sideDecor", stg, (x,y), None, 0 )

    def paint(self, surface):
        surface.blit(self.image, self.rect)
        if self.decor:
            self.decor.alter()
            surface.blit(self.decor.image, self.decor.rect)

    def erase(self):
        if self.decor:
            self.decor.erase()
        self.kill()
        del self
    
    def lift(self, dist):
        self.rect.bottom += dist
        if self.decor:
            self.decor.lift(dist)

    def level(self, dist):
        self.rect.left += dist
        if self.decor:
            self.decor.level(dist)

# -----------------------------------
class BlockFire(pygame.sprite.Sprite):
    def __init__(self, x, y, coord):
        pygame.sprite.Sprite.__init__(self)
        self.imgList = [ pygame.image.load("image/stg1/blockFire0.png").convert_alpha(), pygame.image.load("image/stg1/blockFire1.png").convert_alpha(), pygame.image.load("image/stg1/blockFire2.png").convert_alpha(), pygame.image.load("image/stg1/blockFire1.png").convert_alpha() ]
        self.image = self.imgList[0]
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.left = x-self.rect.width//2
        self.rect.bottom = y
        self.imgIndx = 0
        self.coord = coord
        self.category = "blockFire"
        self.damage = 0.4
    
    def burn(self, delay, sprites, canvas):
        if not (delay%2):
            smokePos = ( self.rect.left+self.rect.width//2, self.rect.bottom-10 )
            canvas.addSmoke( 1, (2, 4, 6), 4, [0,-1], (2,2,2,200), smokePos, 24 )
            for hero in sprites:
                # 只有hero在这一层时才进行hero的重合check，否则无权进行伤害。
                if hero.onlayer==self.coord[1]+1 and pygame.sprite.collide_mask(self, hero):
                    hero.hitted(self.damage, 0)
        if not (delay % 6):
            self.imgIndx = (self.imgIndx+1) % len(self.imgList)
            lft = self.rect.left
            btm = self.rect.bottom
            self.image = self.imgList[self.imgIndx]
            self.rect = self.image.get_rect()
            self.rect.left = lft
            self.rect.bottom = btm

    def erase(self):
        self.kill()
        del self

    def lift(self, dist):
        self.rect.bottom += dist

    def level(self, dist):
        self.rect.left += dist

# -----------------------------------------
class BlockStone(pygame.sprite.Sprite):
    def __init__(self, x, y, coord):
        pygame.sprite.Sprite.__init__(self)
        self.imgList = [ pygame.image.load("image/stg2/blockStone0.png").convert_alpha(), pygame.image.load("image/stg2/blockStone1.png").convert_alpha(), pygame.image.load("image/stg2/blockStone2.png").convert_alpha() ]
        self.image = self.imgList[0]
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.left = x-self.rect.width//2
        self.rect.bottom = y
        self.coord = coord
        self.onlayer = coord[1]+1
        self.category = "blockStone"
        self.bldColor = (180,180,180,240)
        self.health = 80
        self.exp = 0
    
    def hitted(self, damage, pushed):
        self.health -= damage
        if self.health < 0:
            self.erase()
            return
        elif self.health < 24:
            self.image = self.imgList[2]
        elif self.health < 60:
            self.image = self.imgList[1]

    def erase(self):
        self.kill()
        del self
    
    def lift(self, dist):
        self.rect.bottom += dist

    def level(self, dist):
        self.rect.left += dist

# ---------------------------------------
class BlockOoze(pygame.sprite.Sprite):
    def __init__(self, x, y, coord):
        pygame.sprite.Sprite.__init__(self)
        self.imgList = [ pygame.image.load("image/stg4/blockOoze0.png").convert_alpha(), pygame.image.load("image/stg4/blockOoze1.png").convert_alpha(), pygame.image.load("image/stg4/blockOoze2.png").convert_alpha(), pygame.image.load("image/stg4/blockOoze3.png").convert_alpha() ]
        self.image = self.imgList[0]
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.left = x-self.rect.width//2
        self.rect.bottom = y
        self.coord = coord
        self.category = "blockOoze"
        self.imgIndx = 0

    def bubble(self, delay, sprites):
        for hero in sprites:
            # 只有hero在这一层且处于此砖上方才进行hero的重合check，否则无权对hero的stuck进行决定。
            if hero.onlayer==self.coord[1]+1 and pygame.sprite.collide_mask(self, hero):
                hero.trapper = self
        if not (delay % 12):
            lft = self.rect.left
            btm = self.rect.bottom
            self.imgIndx = (self.imgIndx + 1) % len(self.imgList)
            self.image = self.imgList[self.imgIndx]
            self.rect = self.image.get_rect()
            self.rect.left = lft
            self.rect.bottom = btm

    def erase(self):
        self.kill()
        del self
    
    def lift(self, dist):
        self.rect.bottom += dist

    def level(self, dist):
        self.rect.left += dist
        
# --------------------------------------
class Fan(pygame.sprite.Sprite):
    def __init__(self, x, y, coord):
        pygame.sprite.Sprite.__init__(self)
        self.imgList = [ pygame.image.load("image/stg6/fan0.png").convert_alpha(), pygame.image.load("image/stg6/fan1.png").convert_alpha(), pygame.image.load("image/stg6/fan2.png").convert_alpha() ]
        self.image = self.imgList[0]
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.left = x-self.rect.width//2
        self.rect.top = y-self.rect.height//2
        self.center = [x,y]
        self.coord = coord
        self.category = "fan"
        self.imgIndx = 0

    def whirl(self, delay, sprites):
        if not delay%2:
            for hero in sprites:
                if pygame.sprite.collide_mask(self, hero):
                    if hero.rect.left+hero.rect.width//2 > self.center[0]:
                        hero.hitted(1, 2)
                    else:
                        hero.hitted(1, -2)
        if not (delay % 3):
            self.imgIndx = (self.imgIndx + 1) % len(self.imgList)
            self.image = self.imgList[self.imgIndx]
            self.rect = self.image.get_rect()
            self.rect.left = self.center[0]-self.rect.width//2
            self.rect.top = self.center[1]-self.rect.height//2

    def erase(self):
        self.kill()
        del self
    
    def lift(self, dist):
        self.rect.bottom += dist
        self.center[1] += dist
    
    def level(self, dist):
        self.rect.left += dist
        self.center[0] += dist

# --------------------------------------
class Stabber(pygame.sprite.Sprite):
    def __init__(self, x, y, coord):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("image/stg7/stabber.png").convert_alpha()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.left = x-self.rect.width//2
        self.rect.top = y
        self.coord = coord
        self.category = "stabber"
        self.cnt = 0

    def stab(self, delay, sprites):
        self.cnt = (self.cnt+1) % 180
        if self.cnt >= 100:          # 若cnt<100，表示藏在砖内的状态。cnt>=110时，真正活动、对英雄造成伤害。
            if not delay%2:
            # 只有hero在这一层时才进行hero的重合check，否则无权进行伤害。
                for hero in sprites:
                    if hero.onlayer==self.coord[1]+1 and pygame.sprite.collide_mask(self, hero):
                        hero.hitted(0.5, 0)
            elif self.cnt < 118:     # 向上突刺，100~118，18个cnt
                self.rect.top -= 2
            elif self.cnt < 162:     # 停留
                pass
            else:                    # 向下收回，162~180，18个cnt
                self.rect.top += 2

    def erase(self):
        self.kill()
        del self
    
    def lift(self, dist):
        self.rect.bottom += dist
    
    def level(self, dist):
        self.rect.left += dist

# --------------------------------------
class Crop(pygame.sprite.Sprite):
    def __init__(self, x, y, coord):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("image/stg0/crop.png").convert_alpha()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.left = x-self.rect.width//2
        self.rect.bottom = y
        self.coord = coord
        self.category = "crop"

    def move(self):
        pass

    def erase(self):
        self.kill()
        del self
    
    def lift(self, dist):
        self.rect.bottom += dist
    
    def level(self, dist):
        self.rect.left += dist
# ========================================================================
# ========================================================================
class Chest(pygame.sprite.Sprite):

    # constructor: note that y here should be the bottom point of the supply
    def __init__(self, x, y, cate, coord, bg_size, contains):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("image/chest.png").convert_alpha()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.left = x - self.rect.width//2
        self.rect.bottom = y
        self.category = cate
        self.coord = coord    # 这里的coord是该chest所在的brick的坐标
        self.contains = int(contains)

        self.tgtPos = [0,0]   # 箱内物品打开后飞向的目的地，在open时会确定。
        self.bg_size = bg_size
        self.opened = False
        self.reached = False
        self.getItemSnd = pygame.mixer.Sound("audio/getItem.wav")

    def open(self, hero):
        if self.opened:    # 打开后仍保持此类在hero的checkList中，只是opened标记为True时，此函数不会执行
            return False
        if not hero.onlayer==self.coord[1]+1: # 如果hero和chest不在同一行，不允许打开。
            return False
        self.getItemSnd.play(0)
        self.opened = True
        hero.eventList.append(self)
        trPos = [ self.rect.left + self.rect.width//2, self.rect.bottom ]  # 为保证图片位置正确，临时存储之前的位置信息
        self.image = pygame.image.load("image/chestOpen.png").convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.left = trPos[0]-self.rect.width//2
        self.rect.bottom = trPos[1]
        # 修改相应的hero属性数量，同时设定substance的目的坐标，确定substance的图片
        if self.category == "supAmmo":
            hero.arrow += self.contains
            self.tgtPos = [ hero.propPos["ammo"][0]+self.bg_size[0]//2, hero.propPos["ammo"][1]+self.bg_size[1]//2 ]
            self.substance = hero.ammoImg
        else:
            hero.bag[ self.category ] += 1
            self.tgtPos = [ hero.propPos["bag"][0]+self.bg_size[0]//2, hero.propPos["bag"][1]+self.bg_size[1]//2 ]
            self.substance = pygame.image.load("image/"+self.category+".png").convert_alpha()
        # deal inside substance imgs (其只是一张img，不是sprite个体)
        self.subsRect = self.substance.get_rect()
        self.subsRect.left = self.rect.left - self.subsRect.width//2
        self.subsRect.bottom = self.rect.bottom
        return True

    def subsMove(self):
        if not self.opened or self.reached:
            return False
        spdX = ( self.subsRect.left - self.tgtPos[0] ) // 20
        self.subsRect.left -= spdX
        spdY = ( self.subsRect.bottom - self.tgtPos[1] ) // 20
        self.subsRect.bottom -= spdY
        if spdX == 0 or spdY == 0:
            self.reached = True

    def erase(self):
        self.kill()
        del self
    
    def lift(self, dist):
        self.rect.bottom += dist

    def level(self, dist):
        self.rect.left += dist

    def paint(self, surface):
        surface.blit(self.image, self.rect)

# ------ 帮助以一定概率区分 chest 内 supply 类型的函数 -------
def supClassify(stg):
    number = random()
    if stg==3:
        if number < 0.74:
            return "supAmmo"  # 0.74
        elif number < 0.84:
            return "fruit"    # 0.1
        elif number < 0.92:
            return "torch"    # 0.08
        else:
            return "medicine" # 0.08
    else:
        if number < 0.88:
            return "supAmmo"
        else:
            return "fruit"

# ========================================================================
# ========================================================================
class Decoration(pygame.sprite.Sprite):

    imgList = []
    freq = 5   # 图片切换频率，默认为5此刷新切换一次。

    # constructor: If you want a door or hostage, x should be an integer; If you want decorations, x should be a pair of integers (tuple).
    # cate could be either "lineDecor" or "sideDecor"; options should be like ("A", "B", "C"...)
    def __init__(self, x, y, cate, stg, coord, options, freq):
        pygame.sprite.Sprite.__init__(self)
        self.category = cate
        self.t = 0
        if freq==0:
            self.freq = 5  # 0表示使用默认的5
        else:
            self.freq = freq
        if cate == "lineDecor":
            if stg==4:
                x = [x[0]+6, x[1]-6]
            # 有多种装饰可供选择。尾号为A或B……从options参数中选择一个。
            tail = choice( options )
            self.imgList = [ pygame.image.load("image/stg"+str(stg)+"/"+cate+tail+"0.png").convert_alpha(), pygame.image.load("image/stg"+str(stg)+"/"+cate+tail+"1.png").convert_alpha(), \
                pygame.image.load("image/stg"+str(stg)+"/"+cate+tail+"2.png").convert_alpha(), pygame.image.load("image/stg"+str(stg)+"/"+cate+tail+"1.png").convert_alpha() ]
        elif cate == "sideDecor":
            if stg==4:
                x = [x[0]-14+36, x[1]-58+36]
            self.imgList = [ pygame.image.load("image/stg"+str(stg)+"/"+cate+"0.png").convert_alpha(), pygame.image.load("image/stg"+str(stg)+"/"+cate+"1.png").convert_alpha(), \
                pygame.image.load("image/stg"+str(stg)+"/"+cate+"2.png").convert_alpha(), pygame.image.load("image/stg"+str(stg)+"/"+cate+"1.png").convert_alpha() ]
        # 有一半的可能性会方向相反
        if random()>=0.5:
            self.imgList = [ pygame.transform.flip(self.imgList[0], True, False), pygame.transform.flip(self.imgList[1], True, False),
                pygame.transform.flip(self.imgList[2], True, False), pygame.transform.flip(self.imgList[3], True, False) ]
            x = x[1]
        else:
            x = x[0]
        self.image = self.imgList[0]
        self.indx = 0
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.left = x - self.rect.width//2
        self.rect.top = y - self.rect.height
        self.coord = coord

    def alter(self):
        self.t = (self.t + 1) % self.freq
        if not self.t:
            tx = self.rect.left
            ty = self.rect.bottom
            self.indx = ( self.indx+1 ) % len(self.imgList)
            self.image = self.imgList[self.indx]
            self.rect = self.image.get_rect()
            self.rect.left = tx
            self.rect.bottom = ty

    def erase(self):
        self.kill()
        del self

    def lift(self, dist):
        self.rect.bottom += dist

    def level(self, dist):
        self.rect.left += dist

# ========================================================================
# ========================================================================
class Porter(pygame.sprite.Sprite):

    imgList = []

    # constructor: If you want a door or hostage, x should be an integer; If you want decorations, x should be a pair of integers (tuple).
    def __init__(self, x, y, cate, stg, coord):
        pygame.sprite.Sprite.__init__(self)
        self.category = cate
        self.unlockList = []
        self.t = 0
        if cate == "door" or cate=="exit":
            self.locked = True
            self.imgList = [ pygame.image.load("image/stg"+str(stg)+"/"+cate+"Locked0.png").convert_alpha(), pygame.image.load("image/stg"+str(stg)+"/"+cate+"Locked1.png").convert_alpha() ]
            self.unlockList = [ pygame.image.load("image/stg"+str(stg)+"/"+cate+"0.png").convert_alpha(), pygame.image.load("image/stg"+str(stg)+"/"+cate+"1.png").convert_alpha() ]
        elif cate == "hostage":
            self.locked = True
            self.imgList = [ pygame.image.load("image/stg"+str(stg)+"/hostage0.png").convert_alpha(), pygame.image.load("image/stg"+str(stg)+"/hostage1.png").convert_alpha() ]
        elif cate == "notice":       # cate == "" or cate == "house"
            self.imgList = [ pygame.image.load("image/notice.png").convert_alpha() ]
        elif cate == "house":
            self.bgImg = pygame.image.load("image/stg0/houseBG.png").convert_alpha()
            self.bgRect = self.bgImg.get_rect()
            self.bgRect.left = x - self.bgRect.width//2
            self.bgRect.top = y - self.bgRect.height
            self.imgList = [ pygame.image.load("image/stg0/house.png").convert_alpha() ]
        self.lumi = 0
        self.image = self.imgList[0]
        self.indx = 0
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.left = x - self.rect.width//2
        self.rect.top = y - self.rect.height
        self.coord = coord
        self.msgList = []
    
    def paint(self, surface, canvas, font, lgg):
        self.t = (self.t + 1) % 5
        if not self.t:
            tx = self.rect.left
            ty = self.rect.bottom
            self.indx = ( self.indx+1 ) % len(self.imgList)
            self.image = self.imgList[self.indx]
            self.rect = self.image.get_rect()
            self.rect.left = tx
            self.rect.bottom = ty
        if self.category == "house":
            if not self.t:
                smokePos = ( round(self.bgRect.left+self.bgRect.width*0.72), round(self.bgRect.top+self.bgRect.height*0.05) )
                canvas.addSmoke( 1, (4, 6, 8), 1, [0,-1], (10,10,10,120), smokePos, 4 )
            surface.blit(self.bgImg, self.bgRect)
        surface.blit(self.image, self.rect)
        # 显示消息
        for msg in self.msgList:
            txt = font[lgg].render( msg[lgg], True, (255,255,255) )
            rect = txt.get_rect()
            rect.left = self.rect.left+self.rect.width//2-rect.width//2
            rect.bottom = self.rect.bottom - 90
            bg = pygame.Surface( (rect.width, rect.height) ).convert_alpha()
            bgRect = bg.get_rect()
            bgRect.left = rect.left
            bgRect.top = rect.top
            bg.fill( (0,0,0,180) )
            surface.blit( bg, bgRect )
            surface.blit( txt, rect )
            self.msgList.remove(msg)
    
    def unlock(self):
        if self.locked:
            self.locked = False
            if self.category == "door" or self.category == "exit":
                self.imgList = self.unlockList

    def erase(self):
        self.kill()
        del self

    def conversation(self):
        if self.category=="hostage":
            self.msgList.append( ("Press Whip Key to take me.","按近战攻击键将我加入队伍。") )
        elif self.category=="exit":
            self.msgList.append( ("Bring hostage here to escape.","将人质引导至这里逃离塔楼。") )
        elif self.category=="notice":
            self.msgList.append( ("Press Enter to for Pause.","按回车键可暂停游戏。") )
        elif self.category=="door":
            self.msgList.append( ("Eliminate all Area Keepers first.","需要消灭所有当前区域的守卫者。") )

    def lift(self, dist):
        self.rect.bottom += dist
        if self.category=="house":
            self.bgRect.bottom += dist

    def level(self, dist):
        self.rect.left += dist
        if self.category=="house":
            self.bgRect.left += dist

'''-------------------------------------------- MAP ORNAMENTS -------------------------------------------'''

# ===================================================================================
# =========================== 自然现象装饰（雨、雪、雾） ==============================
# ===================================================================================
class Nature():

    drops = []     # 储存运动的单个对象（雨、雪、雾团等）
    wind = 0       # 风向（速）
    width = 0      # 窗口的宽高
    height = 0
    canvas = None  # 实际绘制对象的透明画布

    def __init__(self, bg_size, stg, num, wind):
        self.drops = []
        self.width = bg_size[0]
        self.height = bg_size[1]
        self.wind = wind

        self.canvas = pygame.Surface(bg_size).convert_alpha()
        self.canvas.set_colorkey( (0,0,0) )  # set black as transparent color, generally make the canvas transparent
        self.rect = self.canvas.get_rect()
        self.rect.left = 0
        self.rect.top = 0
        if stg==1:
            self.ashFloat( num, (250,200,0,200) )
            self.dropType = "ash"
        elif stg==2:
            self.snowDrop( num, (20,20,20,210), [16, 20, 24] )
            self.dropType = "snow"
        elif stg==3:
            self.ashFloat( num, (10,0,20,160) )
            self.dropType = "ash"
        elif stg==4 or stg==7:
            self.rainDrop( num )
            self.dropType = "rain"
        elif stg==5:
            self.snowDrop( num, (255, 255, 255, 160), [4, 5, 6, 7] )
            self.dropType = "snow"
        elif stg==6:
            self.clusterPos = [0,self.height//2]   # 对于第6关，有一个特别的聚集点，作为每次刷新时的初始点（初始值：左侧中间）
            self.count = 80            # 计时器，每隔一段时间（倒计时变0）重置一次火花
            self.sparks( num )
            self.dropType = "spark"
        elif stg==0:
            self.ashFloat( num, (180,250,200,200) )
            self.dropType = "ash"

    def rainDrop(self, num):
        for i in range(0, num, 1):
            thickness = choice( [1, 2] )
            length = choice( [20, 30, 40] )
            startPos = [ randint( 0, self.width ), randint(-self.height, 0) ]
            speed = choice( [30, 36, 42] )
            drop = Rain( thickness, length, startPos, speed )
            self.drops.append( drop )

    def snowDrop(self, num, color, spdList):
        for i in range(0, num, 1):
            radius = choice( [3, 6, 9] )
            startPos = [ randint( 0, self.width ), randint(-self.height, 0) ]
            speed = choice( spdList )
            drop = Snow( radius, startPos, speed, color )
            self.drops.append( drop )

    def ashFloat(self, num, color):
        for i in range(0, num, 1):
            radius = choice( [2, 4, 6] )
            drop = Ash( radius, color )
            drop.reset(self.width, self.height)
            self.drops.append( drop )

    def sparks(self, num):
        for i in range(0, num, 1):
            radius = choice( [2, 4, 5] )
            drop = Spark( radius, (255,220,0,210), self.clusterPos)
            self.drops.append( drop )

    # 供外部调用的更新drops对象的接口
    def update(self, screen):
        self.canvas.fill( (0,0,0,0) )        # 填充透明的黑色（覆盖上一次的绘画记录）
        if self.dropType == "spark":
            self.count -= 1
            for each in self.drops:
                each.move(self.width, self.height, self.clusterPos, self.count)
                pygame.draw.circle(self.canvas, each.color, each.pos, each.r)
            if self.count <= 0:
                newFrom = randint( 0, 2 )# 随机选择一条出现的边，0表示从左，1表示从右
                if newFrom == 0:
                    self.clusterPos = [ 0, randint(20,self.height-100) ]
                elif newFrom == 1:
                    self.clusterPos = [ self.width, randint(20,self.height-100) ]
                self.count = 60          # 倒计时重置为60
        else:
            for each in self.drops:
                each.move( self.width, self.height, self.wind )
                if self.dropType == "rain":
                    pygame.draw.line(self.canvas, (255,255,255,160), each.head, each.tail, each.thickness)  # 抗锯齿的单个线段
                elif self.dropType == "snow":
                    pygame.draw.circle(self.canvas, each.color, each.pos, each.r)
                    if random()<0.001:
                        self.wind = -self.wind
                elif self.dropType == "ash":
                    pygame.draw.circle(self.canvas, each.color, each.pos, each.r)
        screen.blit( self.canvas, self.rect )

# --------------------------------------------------------------
# --------------------------------------------------------------
class Rain(pygame.sprite.Sprite):
    def __init__(self, thickness, length, startPos, speed):  # 参数：雨线的粗细；雨线的长度；雨滴的起始位置
        pygame.sprite.Sprite.__init__(self)
        self.thickness = thickness
        self.length = length
        self.speed = speed
        self.head = startPos

    def move(self, width, height, wind):
        if self.head[1] < height:  # 尚在屏幕内，继续下落
            self.head[1] += self.speed
            self.head[0] += wind
        else:
            self.head[1] = 0       # 触底则重置到顶端
            self.head[0] = randint( 0, width )
        self.tail = [self.head[0]-wind, self.head[1]-self.length] # 尾部减掉了风速，以保持雨丝倾斜

# --------------------------------------------------------------
# --------------------------------------------------------------
class Snow(pygame.sprite.Sprite):
    def __init__(self, radius, startPos, speed, color):  # 参数：雪花的半径；雪花的起始位置
        pygame.sprite.Sprite.__init__(self)
        self.r = radius
        self.speed = speed
        self.pos = startPos
        self.color = color

    def move(self, width, height, wind):
        if (self.pos[1] < height) and (0 < self.pos[0] < width):  # 尚在屏幕内，继续下落
            self.pos[1] += self.speed
            self.pos[0] += wind
        else:
            self.pos[1] = 0       # 出界则重置到顶端
            self.pos[0] = randint( 0, width )

# --------------------------------------------------------------
# --------------------------------------------------------------
class Ash(pygame.sprite.Sprite):
    def __init__(self, radius, color):  # 参数color:推荐带上透明度RGBA；参数speed:为一个二元组
        pygame.sprite.Sprite.__init__(self)
        self.r = radius
        self.speed = [ 0, 0 ]
        self.pos = [ 0, 0 ]
        self.color = color
    
    def move(self, width, height, wind):
        if (-10 < self.pos[0] < width+10) and (-10 < self.pos[1] < height+10):  # 尚在屏幕内，继续滚动
            self.pos[0] += self.speed[0]
            self.pos[1] += self.speed[1]
        else:
            self.reset(width, height)
    
    def reset(self, width, height):  # 初始化本ash的所有状态
        # 随机选择一条出现的边：
        newFrom = randint( 0, 3 )        # 0表示从上，1表示从左，2表示从下，3表示从右
        if newFrom == 0:
            self.pos[0] = randint( 0, width )
            self.pos[1] = randint( -10, 0 )
            self.speed = [ randint(-2,2), randint(1,2) ]
        elif newFrom == 1:
            self.pos[0] = randint( -10, 0 )
            self.pos[1] = randint( 0, height )
            self.speed = [ randint(1,2), randint(-2,2) ]
        elif newFrom == 2:
            self.pos[0] = randint( 0, width )
            self.pos[1] = randint( height, height+10 )
            self.speed = [ randint(-2,2), randint(-2,-1) ]
        elif newFrom == 3:
            self.pos[0] = randint( width, width+10 )
            self.pos[1] = randint( 0, height )
            self.speed = [ randint(-2,-1), randint(-2,2) ]
            
# ----------------------------------------------------------
# ----------------------------------------------------------
class Spark(pygame.sprite.Sprite):
    def __init__(self, radius, color, startPos): # 参数color:推荐带上透明度RGBA；参数speed:为一个二元组
        pygame.sprite.Sprite.__init__(self)
        self.r = radius
        self.color = color
        self.reset(1, startPos)                  # 因为初始是从屏幕左侧，所以无需给width，这里直接给1
    
    def move(self, width, height, newPos, cnt):
        if cnt > 0:
            self.pos[0] += self.speed[0]
            self.pos[1] += self.speed[1]
            if self.speed[1]<24:
                self.speed[1] += 1               # 竖直速度增加，以实现下落效果
        elif cnt<=0:
            self.reset(width, newPos)
    
    def reset(self, width, newPos):              # 初始化本spark的所有状态
        self.pos = [ newPos[0], randint(newPos[1]-2, newPos[1]+2) ]
        if newPos[0] <= 0:
            self.speed = [ choice([2, 3, 4, 5, 6]), choice( range(-8,4,1) ) ]
        elif newPos[0] >= width:
            self.speed = [ choice([-2, -3, -4, -5, -6]), choice( range(-8,4,1) ) ]

# ======================================================================
# ============================ 溅射效果反馈 =============================
# ======================================================================
class SpurtCanvas():

    spatters = None  # 储存运动的单个血滴，或冲击波边界圆
    canvas = None    # 实际绘制对象的透明画布
    rect = None

    def __init__(self, bg_size):
        self.spatters = pygame.sprite.Group()
        self.canvas = pygame.Surface(bg_size).convert_alpha()
        self.canvas.set_colorkey( (0,0,0) )     # set black as transparent color, generally make the canvas transparent
        self.rect = self.canvas.get_rect()
        self.rect.left = 0
        self.rect.top = 0
    
    # Document: This method provide a encapsuled way to represent a spattering effect from a center point to all directions.
    def addSpatters(self, num, rList, cList, rgba, pos):
        for i in range(0, num, 1):
            radius = choice( rList )
            cnt = choice( cList ) #[10, 12, 14] )
            randPos = [ randint(pos[0]-1, pos[0]+1), randint(pos[1]-1, pos[1]+1) ]
            speed = [ choice([-3, -2, -1, 1, 2, 3]), choice([-3, -2, -1, 1, 2, 3]) ]
            spatter = Spatter( radius, rgba, randPos, cnt, speed )
            self.spatters.add( spatter )

    def addSmoke(self, num, rList, fade, speed, rgba, pos, xRange):
        for i in range(0, num, 1):
            radius = choice( rList )
            randPos = [ randint(pos[0]-xRange, pos[0]+xRange), randint(pos[1]-2, pos[1]+2) ]
            smoke = Smoke( radius, rgba, randPos, speed, fade )
            self.spatters.add( smoke )
    
    def addWaves(self, pos, color, initR, capR, increm):
        wave = Wave( pos, color, initR, capR, increm )
        self.spatters.add( wave )
    
    def addTrails(self, rList, cList, rgba, pos ):
        radius = choice( rList )
        cnt = choice( cList )
        spatter = Spatter( radius, rgba, pos, cnt, [0,0] )
        self.spatters.add( spatter )
    
    def addSouls(self, num, rList, cList, rgba, pos, tgt):
        for i in range(0, num, 1):
            radius = choice( rList )
            cnt = choice( cList )
            randPos = [ randint(pos[0]-1, pos[0]+1), randint(pos[1]-1, pos[1]+1) ]
            speed = [ choice([-3, -2, -1, 1, 2, 3]), choice([-3, -2, -1, 1, 2, 3]) ]
            soul = Soul( radius, rgba, randPos, cnt, speed, tgt )
            self.spatters.add( soul )

    def update(self, screen):
        self.canvas.fill( (0,0,0,0) )           # 填充透明的黑色（覆盖上一次的绘画记录）
        for each in self.spatters:
            each.move()
            pygame.draw.circle(self.canvas, each.color, each.pos, each.r)
        screen.blit( self.canvas, self.rect )

# ----------------------------------------------------------
# ----------------------------------------------------------
class Spatter(pygame.sprite.Sprite):
    def __init__(self, radius, color, pos, cnt, speed): # 参数color:推荐带上透明度RGBA；参数speed:为一个二元组
        pygame.sprite.Sprite.__init__(self)
        self.r = radius
        self.color = color
        self.pos = pos
        self.speed = speed
        self.cnt = cnt
    
    def move(self):
        # 若还有cnt，则进行移动，且减cnt。
        if self.cnt > 0:
            self.pos[0] += self.speed[0]
            self.pos[1] += self.speed[1]
            self.cnt -= 1
        # 否则，该质点应该消散。半径减1.
        elif self.r > 0:
            self.r -= 1
        # 最后，当半径也减至0，将该点删除。
        else:
            self.kill()
            del self
            return True

# ----------------------------------------------------------
# Smoke class will fade in alpha, and expand in size.
class Smoke(pygame.sprite.Sprite):
    def __init__(self, radius, color, pos, speed, fade): # 参数color:推荐带上透明度RGBA；参数speed:为一个二元组
        pygame.sprite.Sprite.__init__(self)
        self.r = radius
        self.color = color
        self.pos = pos
        self.speed = speed
        self.fade = fade
    
    def move(self):
        # 若颜色消失，则删除
        if self.color[3]<=0:
            self.kill()
            del self
            return True
        # 否则，质点移动且颜色淡化
        elif self.color[3]>0:
            self.color = (self.color[0], self.color[1], self.color[2], self.color[3]-self.fade)
            self.pos[0] += self.speed[0]
            self.pos[1] += self.speed[1]

# ----------------------------------------------------------
class Wave(pygame.sprite.Sprite):
    def __init__(self, pos, color, initR, capR, increm):
        pygame.sprite.Sprite.__init__(self)
        self.pos = pos
        self.color = color
        self.r = initR
        self.capR = capR
        self.increm = increm
    
    def move(self):
        if self.r < self.capR:
            self.r += self.increm
        else:
            self.kill()
            del self
            return True

# ---------------------------------------------------------  
class Soul(pygame.sprite.Sprite):
    def __init__(self, radius, color, pos, cnt, speed, tgt): # 参数color:推荐带上透明度RGBA；参数speed:为一个二元组
        pygame.sprite.Sprite.__init__(self)
        self.r = radius
        self.color = color
        self.pos = pos
        self.speed = speed
        self.cnt = cnt
        self.tgt = tgt
    
    def move(self):
        self.pos[0] += self.speed[0]
        self.pos[1] += self.speed[1]
        # 若还有cnt，则进行散开移动，且减cnt。
        if self.cnt > 0:
            self.cnt -= 1
        # 否则，该质点进入第二状态，追随self.tgt。
        else:
            self.speed[0] = (self.tgt.rect.left+self.tgt.rect.width//2 - self.pos[0])//10
            self.speed[1] = (self.tgt.rect.top+self.tgt.rect.height//2 - self.pos[1])//10
            # 最后，当和tgt重合，将该点删除。
            if self.tgt.rect.left<self.pos[0]<self.tgt.rect.right and self.tgt.rect.top<self.pos[1]<self.tgt.rect.bottom:
                self.tgt.eventList.append("exp")
                self.tgt.expSnd.play(0)
                self.tgt.expInc += 1
                self.kill()
                del self
                return True
# ======================================================================
# ============================ 屏幕画面布置 =============================
# ======================================================================
class HaloCanvas():

    canvas = None
    canvasRect = None

    def __init__(self, bg_size):

        self.canvas = pygame.Surface(bg_size).convert_alpha()
        self.canvas.set_colorkey( (0,0,0) )     # set black as transparent color, generally make the canvas transparent
        self.rect = self.canvas.get_rect()
        self.rect.left = 0
        self.rect.top = 0
        self.ctr = bg_size[0]//2, bg_size[1]//2
        self.diagonal = math.ceil( math.sqrt(bg_size[0]**2+bg_size[1]**2) )
        # For the sake of game's running effect, 3 at most are allowed to be added in one period.
        # The first one "monsHalo" is special, and will be treated in a different way.
        self.halos = { "monsHalo":None, "hitHalo":None, "frzHalo":None }
    
    # Document: This method provide a encapsuled way to represent a halo effect around the edge of the screen.
    # radRat should be a List that contains 4 numbers (pixls), indicating 4 different layers of halos.
    # fadeSpd can be either positive or negative, indicating how should overall alpha value of the halo changes.
    def addHalo(self, haloType, radList, rgba, fadeSpd):
        if haloType in self.halos:  # Check to ensure type is in self.halos.
            self.halos[haloType] = [radList, rgba, fadeSpd]

    def update(self, delay, screen):
        self.canvas.fill((0,0,0, 0))
        for each in self.halos:
            if not self.halos[each]:
                continue
            pygame.draw.circle( self.canvas, (self.halos[each][1]), self.ctr, self.diagonal, 0 )
            pygame.draw.circle( self.canvas, (self.halos[each][1][0], self.halos[each][1][1], self.halos[each][1][2], self.halos[each][1][3]*0.75), self.ctr, self.halos[each][0][3], 0 )
            pygame.draw.circle( self.canvas, (self.halos[each][1][0], self.halos[each][1][1], self.halos[each][1][2], self.halos[each][1][3]*0.5), self.ctr, self.halos[each][0][2], 0 )
            pygame.draw.circle( self.canvas, (self.halos[each][1][0], self.halos[each][1][1], self.halos[each][1][2], self.halos[each][1][3]*0.25), self.ctr, self.halos[each][0][1], 0 )
            pygame.draw.circle( self.canvas, (0, 0, 0, 0), self.ctr, self.halos[each][0][0], 0 )
            # 营造视野圆圈摇曳效果
            if delay % 2:
                self.halos[each][0][0] -= 10
            else:
                self.halos[each][0][0] += 10
            # 变化透明度
            if 0 <= self.halos[each][1][3]+self.halos[each][2] <= 255:
                self.halos[each][1] = ( self.halos[each][1][0], self.halos[each][1][1], self.halos[each][1][2], self.halos[each][1][3]+self.halos[each][2] )
            else:
                if self.halos[each][2]>0:               # 如果是增加透明度的过程，在最深阶段不应立即删除，要有一个反向淡化的过程。
                    self.halos[each][2] = -self.halos[each][2]
                else:
                    self.halos[each] = None
        screen.blit( self.canvas, self.rect )