# main.py
import sys
import traceback
from random import *

import pygame
from pygame.locals import *

import model
import mapManager
import plotManager

# ======================================================
# Note:
# All sprites in this game would at least have the following properties:
# image, rect, mask, category
# category indicates the name or class of the sprite
# ======================================================
# SOME BIG SPRITE GROUPS：
# allElements: [walls, supplies, impediments, monsters, hero, arrows]
# heroCheck: [sideWall, lineWall, impediment, supply, monster]
# arrowCheck: [sideWall, monsters]
# ======================================================
# record format:
# 0,000; 0,000; 0,000 (stg completed,best score;)
# 0;0;0;0; (monster accessibility)
# 105; 75 (key value)
# 106; 76 (key value)
# 1; 1; 100; 1; 1; 2 (settings: language, difficulty, volume, natOrnam, heroNo1&2)
# ======================================================
# the following variables are global variables, which could be used in any place in main.py

pygame.init()
bg_size = width, height = 960, 720
screen = pygame.display.set_mode( (bg_size) )#, FULLSCREEN|HWSURFACE )
pygame.display.set_caption("Knight Throde 6.8")

# ============================================================================================
# ============================================================================================
# ============================================================================================
def main():

    # language and font set ------------------------------------------
    global language   # 若不声明全局变量，则会报错，错误类型 Unbound local error: local variable xxx used before refered
    language = int( readFile( "r", 6, None)[0] )  # 初始默认为英语(0)，可切换为汉语(1)
    fntSet = [ ( pygame.font.Font("font/ebangkok.ttf", 16), pygame.font.Font("font/hanSerif.otf", 16) ), \
        ( pygame.font.Font("font/ebangkok.ttf", 24), pygame.font.Font("font/hanSerif.otf", 24) ), \
        ( pygame.font.Font("font/ebangkok.ttf", 36), pygame.font.Font("font/hanSerif.otf", 36) ), \
        ( pygame.font.Font("font/ebangkok.ttf", 48), pygame.font.Font("font/hanSerif.otf", 48) ) ]
    # difficulty: 0-easy; 1-normal; 2-hard
    diffi = int( readFile( "r", 6, None)[1] )     # 初始默认为1（普通）
    # volume: originally 100 
    vol = int( readFile( "r", 6, None)[2] )       # 初始默认为满：100
    # nature effect of game process: true or false
    natON = int( readFile( "r", 6, None)[3] )     # 初始默认为开启

    # gameModel: Single Adventure or Biplayer Adventure
    gameMod = 0                                   # 初始默认为0：冒险模式
    P2in = False                                  # 初始默认为单人，即P2不参战
    controller = plotManager.Controller( bg_size )
    #addTXT( ("Loading...","载入资源中……"), fntSet[2], (255,255,255), 0, 0.45 )
    phrSet = {"prior":("prior", "上一个"), "next":("next", "下一个"), "start":("start", "开始"), "select":("select","选为出战"), \
            "Collection":("Collection","图鉴"), "Heroes":("Heroes","英雄书"), "Settings":("Settings","设置")}
    # 下方说明
    instruction = {"A":pygame.image.load("image/A.png").convert_alpha(), "D":pygame.image.load("image/D.png").convert_alpha(), "Enter":pygame.image.load("image/Enter.png").convert_alpha(), \
        "S":pygame.image.load("image/S.png").convert_alpha(), "W":pygame.image.load("image/W.png").convert_alpha(), "Down":pygame.image.load("image/Down.png").convert_alpha(), \
        "Up":pygame.image.load("image/Up.png").convert_alpha(), "Prior":pygame.image.load("image/Prior.png").convert_alpha(), "Next":pygame.image.load("image/Next.png").convert_alpha(), \
        "click0":pygame.image.load("image/click0.png").convert_alpha(), "click1":pygame.image.load("image/click1.png"), "roller":pygame.image.load("image/rollMouse.png"), \
        "leftOpt":pygame.image.load("image/leftOpt.png"), "rightOpt":pygame.image.load("image/rightOpt.png")}
    # 返回按钮 & 界面选项等控件。
    backImg = [pygame.image.load("image/back.png").convert_alpha(), pygame.image.load("image/backOn.png").convert_alpha()]
    option = ( pygame.image.load("image/option.png").convert_alpha(), pygame.image.load("image/optionOn.png").convert_alpha() )
    menus = ( pygame.image.load("image/menu1.png").convert_alpha(), pygame.image.load("image/menu2.png").convert_alpha(), 
        pygame.image.load("image/menu3.png").convert_alpha(), pygame.image.load("image/menu4.png").convert_alpha() )
    ######## 一个管理宏观关卡信息的大类
    stgManager = plotManager.StgManager( readFile("r",1,None) )
    # ===============================================================
    # ==================== 英雄书和图鉴管理大类 =======================
    ########
    heroBook = plotManager.HeroBook(bg_size)
    collection = plotManager.Collection(bg_size, stgManager.nameList)
    
    # music and sound -----------------------------------------------
    musicList = [ pygame.mixer.Sound("audio/story.wav"), pygame.mixer.Sound("audio/stg1BG.wav") , pygame.mixer.Sound("audio/stg2BG.wav"), 
        pygame.mixer.Sound("audio/stg3BG.wav"), pygame.mixer.Sound("audio/stg4BG.wav"), pygame.mixer.Sound("audio/stg5BG.wav"), 
        pygame.mixer.Sound("audio/stg6BG.wav"), pygame.mixer.Sound("audio/stg7BG.wav") ]
    soundList = [ pygame.mixer.Sound("audio/victoryHorn.wav"), pygame.mixer.Sound("audio/gameOver.wav"), pygame.mixer.Sound("audio/click1.wav"), pygame.mixer.Sound("audio/switch.wav") ]
    # adjust the volume
    for snd in musicList:
        snd.set_volume(vol/100)
    for snd in soundList:
        snd.set_volume(vol/100)
    # ===============================================================
    # key dictionary(字典value为按键在pygame中的标识码)
    kd1 = list( map(lambda x:int(x), readFile( "r", 3, None )) )
    keyDic1 = dict( leftKey=kd1[0], rightKey=kd1[1], downKey=kd1[2], wrestleKey=kd1[3], jumpKey=kd1[4], shootKey=kd1[5], itemKey=kd1[6], bagKey=kd1[7] )  # 97;100;115;106;107;108;105;119
    kd2 = list( map(lambda x:int(x), readFile( "r", 4, None)) )
    keyDic2 = dict( leftKey=kd2[0], rightKey=kd2[1], downKey=kd2[2], wrestleKey=kd2[3], jumpKey=kd2[4], shootKey=kd2[5], itemKey=kd2[6], bagKey=kd2[7] ) # 276;275;274;260;261;262;264;273
    ##########
    setManager = plotManager.Settings(keyDic1, keyDic2)

    clock = pygame.time.Clock()
    curStg = 1            # 关卡标记，初始为1
    choosable = True
    page = "index"  # 可取5个值：index, stgChoosing, collection, heroBook, settings
    running = True
    fileChck = 1          # 1表示需要检查文件，0表示不需要

    backPos = (-420, -300) # 返回按钮的中心位置
    instrucY = (330, 0.94) # 依次为说明图案的img纵偏移（相对于中线）；说明文字的txt纵坐标（相对于整个屏幕的百分比）
    edge = 8
    nature = None          # 关卡的特殊自然装饰（雨雪等）
    spurtCanvas = mapManager.SpurtCanvas(bg_size)

    while running:
        # deal fundamental canvas (main canvas): -----
        # --------------------------------------------
        screen.blit( collection.paperList[collection.activePaper], collection.paperRect[collection.activePaper] )
        # ==================================================
        # =================== 选关界面 ======================
        if ( page == "index" ):
            menuY = (-254, -190, -126, -62)  # 左侧按钮的Y位置
            menuX = -450           # X位置
            modY = (110, 174, 238)
            modX = -392
            if not pygame.mixer.get_busy():
                musicList[0].play(-1)  # 播放bgm
            # deal title canvas: ------------------------
            drawRect( 0, 0, bg_size[0], 60, stgManager.themeColor[0] )
            drawRect( 0, bg_size[1]-60, bg_size[0], 60, stgManager.themeColor[0] )
            # 左侧选项菜单img
            menu1 = addSymm( option[0], menuX-30, menuY[0] )
            menu2 = addSymm( option[0], menuX-30, menuY[1] )
            menu3 = addSymm( option[0], menuX-30, menuY[2] )
            menu4 = addSymm( option[0], menuX-30, menuY[3] )
            # 游戏模式选项
            advt = addSymm( option[0], modX, modY[0] )
            casl = addSymm( option[0], modX, modY[1] )
            qit = addSymm( option[0], modX, modY[2] )
            # 大标题
            if language == 0:
                addSymm( pygame.image.load("image/titleE_bot.png"), -2, -272 )
                addSymm( pygame.image.load("image/titleE.png"), -0, -270 )
            elif language == 1:
                addSymm( pygame.image.load("image/titleC_bot.png"), -2, -272 )
                addSymm( pygame.image.load("image/titleC.png"), -0, -270 )
            
            # handle the mouse click events ( active when not prepared )
            pos = pygame.mouse.get_pos()
            if ( advt.left < pos[0] < advt.right ) and ( advt.top < pos[1] < advt.bottom ):
                advt = addSymm( option[1], modX, modY[0] )
                addTXT( ("Explore various towers and rescue those trapped heroes!","探索不同的地图，营救困在其中的英雄！"), fntSet[0], (255,255,255), 0, 0.93 )
            elif ( casl.left < pos[0] < casl.right ) and ( casl.top < pos[1] < casl.bottom ):
                casl = addSymm( option[1], modX, modY[1] )
                addTXT( ("Try endless tower and find out how high you can reach!","尝试无穷高的高塔，挑战你的极限高度！"), fntSet[0], (255,255,255), 0, 0.93 )
            elif ( qit.left < pos[0] < qit.right ) and ( qit.top < pos[1] < qit.bottom ):
                qit = addSymm( option[1], modX, modY[2] )
                addTXT( ("Save and quit the game.","保存并退出游戏。"), fntSet[0], (255,255,255), 0, 0.93 )
            
            elif ( menu1.left < pos[0] < menu1.right ) and ( menu1.top < pos[1] < menu1.bottom ):
                menu1 = addSymm( option[1], menuX+55, menuY[0] )
                addTXT( phrSet["Collection"], fntSet[1], (1,1,1), menuX+70, 0.12 )
                addTXT( ("Check the monsters you have met.","查看你所收集的所有怪物信息。"), fntSet[0], (255,255,255), 0, 0.93 )
            elif ( menu2.left < pos[0] < menu2.right ) and ( menu2.top < pos[1] < menu2.bottom ):
                menu2 = addSymm( option[1], menuX+55, menuY[1] )
                addTXT( phrSet["Heroes"], fntSet[1], (1,1,1), menuX+70, 0.21 )
                addTXT( ("Check or change the hero embatled.","查看英雄信息或更换出战英雄。"), fntSet[0], (255,255,255), 0, 0.93 )
            elif ( menu3.left < pos[0] < menu3.right ) and ( menu3.top < pos[1] < menu3.bottom ):
                menu3 = addSymm( option[1], menuX+55, menuY[2] )
                addTXT( phrSet["Settings"], fntSet[1], (1,1,1), menuX+70, 0.3 )
                addTXT( ("Set player's key and other system settings.","设置玩家键位和其他游戏设定。"), fntSet[0], (255,255,255), 0, 0.93 )
            elif ( menu4.left < pos[0] < menu4.right ) and ( menu4.top < pos[1] < menu4.bottom ):
                menu4 = addSymm( option[1], menuX+55, menuY[3] )
                addTXT( ("Practice","练习场"), fntSet[1], (1,1,1), menuX+70, 0.39 )
                addTXT( ("Practice your skill in the peaceful farmyard.","在宁静的田园里练习你的作战技巧。"), fntSet[0], (255,255,255), 0, 0.93 )

            addSymm( menus[0], menuX, menuY[0] )
            addSymm( menus[1], menuX, menuY[1] )
            addSymm( menus[2], menuX, menuY[2] )
            addSymm( menus[3], menuX, menuY[3] )
            controller.shadowTXT( ("Adventure","冒险模式")[language], fntSet[1][language], (0,0,0), (250,250,250), -400, 110, screen )
            controller.shadowTXT( ("Casual","休闲模式")[language], fntSet[1][language], (0,0,0), (250,250,250), -400, 172, screen )
            controller.shadowTXT( ("Quit","退出游戏")[language], fntSet[1][language], (0,0,0), (250,250,250), -400, 234, screen )
            
            # handle the key events
            for event in pygame.event.get():  # 必不可少的部分，否则事件响应会崩溃
                if ( event.type == QUIT ):
                    pygame.quit()
                    sys.exit()
                elif ( event.type == KEYDOWN ):
                    pass
                elif ( event.type == pygame.MOUSEBUTTONUP ): 
                    soundList[2].play(0)
                    if ( advt.left < pos[0] < advt.right ) and ( advt.top < pos[1] < advt.bottom ):
                        gameMod = 0
                        page = "stgChoosing"
                    elif ( casl.left < pos[0] < casl.right ) and ( casl.top < pos[1] < casl.bottom ):
                        gameMod = 1
                        page = "stgChoosing"
                    elif ( qit.left < pos[0] < qit.right ) and ( qit.top < pos[1] < qit.bottom ):
                        pygame.quit()
                        sys.exit()
                    elif ( menu1.left < pos[0] < menu1.right ) and ( menu1.top < pos[1] < menu1.bottom ):
                        page = "collection"
                    elif ( menu2.left < pos[0] < menu2.right ) and ( menu2.top < pos[1] < menu2.bottom ):
                        page = "heroBook"
                    elif ( menu3.left < pos[0] < menu3.right ) and ( menu3.top < pos[1] < menu3.bottom ):
                        page = "settings"
                    elif ( menu4.left < pos[0] < menu4.right ) and ( menu4.top < pos[1] < menu4.bottom ):
                        musicList[0].stop()
                        mod = model.PracticeModel( (heroBook.heroList[heroBook.curHero[0]],keyDic1,"p1"), (heroBook.heroList[heroBook.curHero[1]],keyDic2,"p2"), bg_size, screen, language, fntSet, musicList[curStg], natON ) # Note: accList会在model中直接被操作。
                        mod.go()
                    break
        # ==================================================
        # =================== 选关界面 ======================
        elif ( page == "stgChoosing" ):
            # 检查上一关是否通关，据此设定本关的choosable
            if (fileChck==1):    
                fileChck = 0
                line = readFile("r", 1, None)
                if (curStg == 1) or ( int(line[curStg-2].split(",")[0])>=0 ):  # 若stg=1，第一个符合则直接判定成功，否则才会继续检查第二个条件。
                    choosable = True
                else:
                    choosable = False
            # deal the transparent canvas when choosing stg:
            #drawRect( 0, 0, bg_size[0], bg_size[1], stgManager.themeColor[curStg] )
            drawRect( 0, 60, bg_size[0]//2, bg_size[1]-120, stgManager.themeColor[curStg] )
            addSymm( stgManager.compass, stgManager.curPos[0], stgManager.curPos[1] )
            stgManager.moveCompass(curStg-1)
            drawRect( 0, 0, bg_size[0], 60, stgManager.themeColor[0] )
            drawRect( 0, bg_size[1]-60, bg_size[0], 60, stgManager.themeColor[0] )
            drawRect( 480, 60, bg_size[0]//2, bg_size[1]-120, stgManager.themeColor[curStg] )
            
            if len(spurtCanvas.spatters)<=0:
                spurtCanvas.addWaves( (240,360), (250,250,250,250), 20, 40, 1 )
                spurtCanvas.addWaves( (240,360), (0,0,0,0), 0, 40, 2 )
            
            back = addSymm( backImg[0], backPos[0], backPos[1] )   # 返回箭头

            mid = 190
            # add Ribbon 1
            addSymm( pygame.image.load("image/option.png"), mid+190, -142 )
            pos = pygame.mouse.get_pos()
            if ( back.left < pos[0] < back.right ) and ( back.top < pos[1] < back.bottom ):
                back = addSymm( backImg[1], backPos[0], backPos[1] )
                if pygame.mouse.get_pressed()[0]:
                    soundList[2].play(0)
                    page = "index"
            P1P2 = None
            difRect = None
            if gameMod == 0:
                # add ribbon 2
                P1P2 = addSymm( pygame.image.load("image/option.png"), mid+190, -75 )
                if ( P1P2.left < pos[0] < P1P2.right ) and ( P1P2.top < pos[1] < P1P2.bottom ):
                    P1P2 = addSymm( pygame.image.load("image/optionOn.png"), mid+190, -75 )
                # add ribbon 3
                difRect = addSymm( pygame.image.load("image/option.png"), mid+190, -8 )
                if ( difRect.left < pos[0] < difRect.right ) and ( difRect.top < pos[1] < difRect.bottom ):
                    difRect = addSymm( pygame.image.load("image/optionOn.png"), mid+190, -8 )
                # draw stars.
                if choosable:
                    i = 0
                    while i<3:
                        if i <= stgManager.star[curStg-1]:
                            addSymm( pygame.image.load("image/star.png"), -240+(i-1)*45, -60 )
                        else:
                            addSymm( pygame.image.load("image/voidStar.png"), -240+(i-1)*45, -60 )
                        i += 1
                addTXT( ("Adventure","冒险模式"), fntSet[1], (255,255,255), 0, 0.03 )
            elif gameMod == 1:
                addTXT( ("Casual","休闲模式"), fntSet[1], (255,255,255), 0, 0.03 )
            
            # 关卡封面及前后缩略图
            if len(controller.SSList)==0:
                if not (curStg == 1):
                    leftC = addSymm( stgManager.coverAbb[curStg-2], mid-130, 100 )
                if not ( curStg == len(stgManager.nameList) ):
                    rightC = addSymm( stgManager.coverAbb[curStg], mid+130, 100 )
                coverRect = addSymm( stgManager.coverList[curStg-1], mid, 0 )
                pygame.draw.rect( screen, stgManager.themeColor[curStg], coverRect, edge )
                pygame.draw.rect( screen, (255,255,255), coverRect, edge//4 )
                #if edge<20:   # 边框的波动效果
                #    edge += 1
                #elif edge == 20:
                #    edge = 1
            # 关卡可选，则给出关卡名；否则加上灰色幕布和锁🔒
            if choosable:         
                addTXT( stgManager.nameList[curStg-1], fntSet[3], (255,255,255), mid, 0.74 )
            else:
                drawRect( coverRect.left, coverRect.top, coverRect.width, coverRect.height, stgManager.themeColor[0] )
                addSymm( stgManager.lock, mid, 0 )
                addTXT( ("Complete stage "+str(curStg-1)+" to unlock","完成第"+str(curStg-1)+"关以解锁本关"), fntSet[1], (255,255,255), mid, 0.76 ) # 关卡名处用这句提示代替
            # 关卡序号
            addTXT( ("STAGE "+str(curStg),"关卡"+str(curStg)), fntSet[1], (255,255,255), mid+190, 0.28 )
            if gameMod == 0:
                # 玩家数量设置标签
                if P2in:
                    addSymm( heroBook.heroList[heroBook.curHero[1]].brand, mid+215, -75 )
                    addTXT( ("P2","P2"), fntSet[0], (255,255,255), mid+215, 0.38 )
                    addSymm( heroBook.heroList[heroBook.curHero[0]].brand, mid+165, -75 )
                    addTXT( ("P1","P1"), fntSet[0], (255,255,255), mid+165, 0.38 )
                else:
                    addSymm( heroBook.heroList[heroBook.curHero[0]].brand, mid+190, -75 )
                    addTXT( ("P1","P1"), fntSet[1], (255,255,255), mid+190, 0.38 )
                # 难度设置标签
                if diffi == 0:
                    addTXT( ("Easy","简单"), fntSet[1], (255,255,255), mid+190, 0.46 )
                elif diffi == 1:
                    addTXT( ("Normal","标准"), fntSet[1], (255,128,128), mid+190, 0.46 )
                elif diffi == 2:
                    addTXT( ("Hard","困难"), fntSet[1], (255,0,0), mid+190, 0.46 )
                    addSymm( pygame.image.load("image/upfix.png"), mid, -209 )          # poster upfix
            elif gameMod == 1:
                if choosable:
                    addTXT( ("Highest Record: %d" %stgManager.high[curStg-1],"历史最高：%d"%stgManager.high[curStg-1]), fntSet[0], (255,255,255), mid+190, 0.2 )
            # 下方指示说明
            addSymm( instruction["A"], 100, instrucY[0] )
            addSymm( instruction["Prior"], 144, instrucY[0] )
            addTXT( phrSet["prior"], fntSet[0], (210,210,200), 192, instrucY[1])
            addSymm( instruction["D"], 240, instrucY[0] )
            addSymm( instruction["Next"], 284, instrucY[0] )
            addTXT( phrSet["next"], fntSet[0], (210,210,200), 332, instrucY[1])
            addSymm( instruction["Enter"], 378, instrucY[0] )
            addTXT( phrSet["start"], fntSet[0], (210,210,200), 425, instrucY[1])
            if choosable:
                addTXT( stgManager.infoList[curStg][0], fntSet[0],(255,255,255), -210, 0.925 )
                addTXT( stgManager.infoList[curStg][1], fntSet[0],(255,255,255), -210, 0.955 )
            else:
                addTXT( stgManager.infoList[0][0], fntSet[0],(255,255,255), -210, 0.925 )
                addTXT( stgManager.infoList[0][1], fntSet[0],(255,255,255), -210, 0.955 )
            # natural decoration:
            controller.doSwitch(screen)
            spurtCanvas.update(screen)
            # handle the key events
            for event in pygame.event.get():  # 必不可少的部分，否则事件响应会崩溃
                if ( event.type == QUIT ):
                    pygame.quit()
                    sys.exit()
                elif ( event.type == KEYDOWN ):
                    fileChck = 1
                    if ( ( event.key == pygame.K_a ) or ( event.key == pygame.K_LEFT ) ) and len(controller.SSList)==0:  # prior
                        soundList[3].play(0)
                        if not (curStg == 1):
                            controller.addSmoothSwitch(stgManager.coverList[curStg-1], coverRect, 0.4, 120, 90, 10)  # 向右退位
                            controller.addSmoothSwitch(stgManager.coverAbb[curStg-2], leftC, 2.8, 120, -90, 10)   # 左侧上位
                            curStg -= 1
                            nature = None
                    if ( ( event.key == pygame.K_d ) or ( event.key == pygame.K_RIGHT ) ) and len(controller.SSList)==0:  # next
                        soundList[3].play(0)
                        if not ( curStg == len(stgManager.nameList) ):
                            controller.addSmoothSwitch(stgManager.coverList[curStg-1], coverRect, 0.4, -120, 90, 10)  # 向左退位
                            controller.addSmoothSwitch(stgManager.coverAbb[curStg], rightC, 2.8, -120, -90, 10)   # 右侧上位
                            curStg += 1
                            nature = None
                    if ( event.key == pygame.K_RETURN ):
                        soundList[3].play(0)
                        if choosable:
                            if curStg>6:
                                controller.msgList.append( ["comingSoon", 40] )
                                break
                            musicList[0].stop()
                            going = True
                            if gameMod == 0:
                                if heroBook.heroList[heroBook.curHero[0]].no==curStg:
                                    controller.msgList.append( ["banHero", 40] )
                                    break
                                while going:
                                    if not P2in:
                                        mod = model.AdventureModel( curStg, 3, [ (heroBook.heroList[heroBook.curHero[0]],keyDic1,"p1") ], bg_size, screen, language, fntSet, musicList[curStg], diffi, natON, collection.monsList[curStg], heroBook.heroList[curStg] ) # Note: accList会在model中直接被操作。
                                    elif P2in:
                                        mod = model.AdventureModel( curStg, 3, [ (heroBook.heroList[heroBook.curHero[0]],keyDic1,"p1"), (heroBook.heroList[heroBook.curHero[1]],keyDic2,"p2") ], bg_size, screen, language, fntSet, musicList[curStg], diffi, natON, collection.monsList[curStg], heroBook.heroList[curStg] )
                                    # 返回的going：True表示winning，False表示failing. (由go()函数最后的conclusion界面确定。)
                                    going = mod.go( stgManager.themeColor[curStg], soundList, heroBook, stgManager, diffi )
                                    mod.clearAll()
                            elif gameMod == 1:
                                while going:
                                    mod = model.EndlessModel( curStg, keyDic1, bg_size, screen, language, fntSet, musicList[curStg], natON, heroBook.heroList[heroBook.curHero[0]] )
                                    going = mod.go( stgManager.themeColor[curStg], soundList, stgManager )
                                    mod.clearAll()
                        else:
                            controller.msgList.append( ["falseStg", 40] )
                elif event.type == pygame.MOUSEBUTTONUP: 
                    if P1P2 and ( P1P2.left < pos[0] < P1P2.right ) and ( P1P2.top < pos[1] < P1P2.bottom ):
                        soundList[2].play(0)
                        if heroBook.accList[1]==True:
                            P2in = not P2in
                        else:
                            controller.msgList.append( ["false2P", 40] )
                    elif difRect and ( difRect.left < pos[0] < difRect.right ) and ( difRect.top < pos[1] < difRect.bottom ):
                        soundList[2].play(0)
                        #if ( event.key == pygame.K_a ) or ( event.key == pygame.K_LEFT ):
                        #    diffi = (diffi-1) % 3
                        #elif ( event.key == pygame.K_d ) or ( event.key == pygame.K_RIGHT ):
                        diffi = (diffi+1) % 3
                        # 修改文件
                        m = readFile( "r", 6, None )
                        m[1] = str(diffi)
                        readFile( "w", 6, ";".join(m) )
        # ==============================================
        # ================= 图鉴收藏 ====================
        elif ( page == "collection" ):
            drawRect( 0, 0, bg_size[0], bg_size[1], stgManager.themeColor[0] )
            back = addSymm( backImg[0], backPos[0], backPos[1] )
            # Print titles.
            titleList = []
            i = 0
            left = -200 * len(collection.subject)//2  # 每个title200px宽。left是第一个标题的左侧。
            for title in collection.subject:
                if title == collection.curSub:
                    titleList.append( drawRect( bg_size[0]//2+left+i*200, 50, 200, 70, (20,20,20,160) ) )
                else:
                    titleList.append( drawRect( bg_size[0]//2+left+i*200, 50, 200, 70, (0,0,0,0) ) )
                addTXT( collection.subject[title], fntSet[2], (255,255,255), left+i*200+100, 0.08 )
                i += 1
            
            # 鼠标点击事件
            pos = pygame.mouse.get_pos()
            if ( back.left < pos[0] < back.right ) and ( back.top < pos[1] < back.bottom ):
                back = addSymm( backImg[1], backPos[0], backPos[1] )
                if pygame.mouse.get_pressed()[0]:
                    soundList[2].play(0)
                    collection.display = None
                    page = "index"

            # check all cards whether chosed ---------------------------
            # 怪物图鉴。
            if collection.curSub == 0:
                innerQuit = collection.renderWindow( pos, fntSet[0], language )
                collection.addRoller()
                screen.blit(collection.window, collection.WDRect)
                
                addTXT( ("Values presented are under the Normal Difficulty.","显示的属性值均为“标准”难度下的数值。"), fntSet[0],(255,255,255), -210, 0.925 )
                addTXT( ("Easy: 80% HP & 60% PW; Hard: 150% HP & 120% PW.","简单：80%生命、60%伤害；困难：150%生命、120%伤害。"), fntSet[0],(255,255,255), -210, 0.955 )
                addSymm( instruction["click0"], 98, instrucY[0] )
                addTXT( ("check","查看"), fntSet[0], (255,255,255), 150, instrucY[1])
            # 墙纸收藏。
            elif collection.curSub == 1:
                collection.renderGallery( pos, fntSet[0], language )
                collection.addRoller()
                screen.blit(collection.window, collection.WDRect)

                addTXT( ("More wallpapers coming soon.","更多壁纸将在后续更新中逐步发放。"), fntSet[0],(255,255,255), -210, 0.925 )
                addSymm( instruction["click0"], 98, instrucY[0] )
                addTXT( ("set active","设为使用"), fntSet[0], (255,255,255), 150, instrucY[1])
            
            # 下方指示说明。
            addSymm( instruction["roller"], 208, instrucY[0] )
            addSymm( instruction["W"], 252, instrucY[0] )
            addSymm( instruction["S"], 296, instrucY[0] )
            addSymm( instruction["Up"], 340, instrucY[0] )
            addSymm( instruction["Down"], 384, instrucY[0] )
            addTXT( ("roll","滚动"), fntSet[0], (210,210,200), 430, instrucY[1])
            
            # KeyBoard Event - Rolling Roller by Pressing KeyBoard.
            key_pressed = pygame.key.get_pressed()
            if ( key_pressed[pygame.K_s] or key_pressed[pygame.K_DOWN] ) and collection.rollerY[collection.curSub] < collection.rollerRange[1]:
                collection.roll(1, -1)
            elif ( key_pressed[pygame.K_w] or key_pressed[pygame.K_UP] ) and collection.rollerY[collection.curSub] > collection.rollerRange[0]:
                collection.roll(-1, 1)
            # handle the key events
            for event in pygame.event.get():    # 必不可少的部分，否则事件响应会崩溃。
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                elif ( event.type == KEYDOWN ):
                    pass
                elif event.type == pygame.MOUSEBUTTONDOWN:  # 鼠标滚轮滚动事件。
                    if (event.button == 4) and collection.rollerY[collection.curSub] > collection.rollerRange[0]:    # page-down
                        collection.roll(-1, 1)
                    elif (event.button == 5) and collection.rollerY[collection.curSub] < collection.rollerRange[1]:  # page-up
                        collection.roll(1, -1)
                elif event.type == pygame.MOUSEBUTTONUP:    # 鼠标单击事件。
                    #print(event.button)
                    if (event.button == 1):
                        # check title.
                        for title in titleList:
                            if ( title.left < pos[0] < title.right ) and ( title.top < pos[1] < title.bottom ):
                                soundList[2].play(0)
                                collection.curSub = titleList.index(title)
                        # Check monster cards.
                        if collection.curSub == 0:
                            if not collection.display:
                                for i in (1,2,3,4,5,6,7):    # 逐关地print。
                                    for each in collection.monsList[i]:  # 处理每一关中地所有VMons
                                        c = collection.monsList[i][each].rect
                                        if ( c.left+40 < pos[0] < c.right+40 ) and ( c.top+120 < pos[1] < c.bottom+120 ):
                                            if collection.monsList[i][each].acc:
                                                collection.display = collection.monsList[i][each]
                                            else:
                                                controller.msgList.append( ["notFound", 40] )
                                            break
                            # 展示monster's detial的情况下，innerQuit有值，表示此事件发生时mouse is hanging over the innerquit button.
                            elif innerQuit:
                                collection.display = None
                        elif collection.curSub == 1:
                            for j in (0, 1, 2, 3):
                                for i in (0, 1, 2):
                                    if i+j*3<=5:
                                        p = collection.paperAbbRect[i+j*3]
                                        if ( p.left+40 < pos[0] < p.right+40 ) and ( p.top+120 < pos[1] < p.bottom+120 ):
                                            collection.activePaper = i+j*3
                                            # 修改文件
                                            m = readFile( "r", 6, None )
                                            m[4] = str(i+j*3)
                                            readFile( "w", 6, ";".join(m) )
                                            break
        # ==============================================
        # ================= 英雄图鉴 ====================
        elif ( page == "heroBook" ):
            drawRect( 0, 0, bg_size[0], bg_size[1], stgManager.themeColor[0] ) # BG Pure.
            addSymm( heroBook.book[0], 0, 0 )                                  # BG Book.
            drawRect( 0, 0, bg_size[0], 60, stgManager.themeColor[0] )         # Upper banner.
            drawRect( 0, bg_size[1]-60, bg_size[0], 60, stgManager.themeColor[0] )               # Lower Banner.

            # ------- Draw content. ---------
            bkx = 180
            drawRect(500, 350, 320, 210, (210,180,120,150))                    # description frame.

            pos = pygame.mouse.get_pos()
            if heroBook.accList[heroBook.pointer]:
                addTXT( heroBook.heroList[heroBook.pointer].name, fntSet[2], (0,0,0), -bkx, 0.1)  # Name.
                addSymm( heroBook.heroList[heroBook.pointer].image, -180, -20 )                   # Image.
                # Attributes.
                attrPair = heroBook.printAttri( screen, fntSet[1], fntSet[0], language, pos )
                if attrPair[1]:
                    addTXT( ("Allocate one SP to strengthen it by clicking the bar.","点击该属性，消耗一个技能点以强化。"), fntSet[0],(255,255,255), -210, 0.925 )
                    addTXT( ("Each time the hero levels up you gain a Skill Point for him.","每当该英雄升级时，其都将获得一个技能点。"), fntSet[0],(255,255,255), -210, 0.955 )
                # Description.
                rateY = 0.5
                for statement in heroBook.heroList[heroBook.pointer].desc:
                    addTXT( statement, fntSet[1], (0,0,0), bkx, rateY)
                    rateY += 0.05
                # Script.
                addTXT( heroBook.heroList[heroBook.pointer].script, fntSet[0], (80,80,80), bkx, 0.8)
            else:
                addSymm( heroBook.notFound, -180, -20 )
                # Unlock condition.
                addTXT( heroBook.heroList[heroBook.pointer].note, fntSet[0], (0,0,0), bkx, 0.8)
            
            # check whether the current hero is chosen
            if heroBook.pointer == heroBook.curHero[heroBook.playerNo]:
                addSymm( pygame.image.load("image/selected.png"), -300, 200 )
                addTXT( ("Selected","已选中"), fntSet[1], (255,255,255), -300, 0.81 )
            # Check if there should be turn-page animation effect.
            pgInfo = heroBook.turnAnimation()
            if pgInfo:
                addSymm( pgInfo[0], pgInfo[1], pgInfo[2] )

            # Upper Back Option & Lower Instruction.
            back = addSymm( backImg[0], backPos[0], backPos[1] )
            addSymm( instruction["A"], 100, instrucY[0] )
            addSymm( instruction["Prior"], 144, instrucY[0] )
            addTXT( phrSet["prior"], fntSet[0], (255,255,255), 192, instrucY[1])
            addSymm( instruction["D"], 240, instrucY[0] )
            addSymm( instruction["Next"], 284, instrucY[0] )
            addTXT( phrSet["next"], fntSet[0], (255,255,255), 332, instrucY[1])
            addSymm( instruction["Enter"], 378, instrucY[0] )
            addTXT( phrSet["select"], fntSet[0], (255,255,255), 425, instrucY[1])
            # 右上角p1p2 option.
            P1P2 = addSymm( pygame.transform.flip(pygame.image.load("image/option.png"),True,False), 460, -260 )
            
            if ( back.left < pos[0] < back.right ) and ( back.top < pos[1] < back.bottom ):
                back = addSymm( backImg[1], backPos[0], backPos[1] )
                if pygame.mouse.get_pressed()[0]:
                    soundList[2].play(0)
                    heroBook.pointer = heroBook.curHero[heroBook.playerNo]     # 索引重置为出战的英雄
                    page = "index"
            elif ( P1P2.left < pos[0] < P1P2.right ) and ( P1P2.top < pos[1] < P1P2.bottom ):
                P1P2 = addSymm( pygame.transform.flip(pygame.image.load("image/optionOn.png"),True,False), 420, -260 )

            if heroBook.playerNo == 0:
                addTXT( ("P1","角色1"), fntSet[1], (0,0,0), 430, 0.11 )
            elif heroBook.playerNo == 1:
                addTXT( ("P2","角色2"), fntSet[1], (0,0,0), 430, 0.11 )
            # Handle the key events.
            for event in pygame.event.get():  # 必不可少的部分，否则事件响应会崩溃
                if ( event.type == QUIT ):
                    pygame.quit()
                    sys.exit()
                elif ( event.type == KEYDOWN ):
                    if ( event.key == pygame.K_a ) or ( event.key == pygame.K_LEFT ):
                        heroBook.turnPage(-1)
                    elif ( event.key == pygame.K_d ) or ( event.key == pygame.K_RIGHT ):
                        heroBook.turnPage(1)
                    elif ( event.key == pygame.K_RETURN ):
                        if not heroBook.chooseHero(language):
                            controller.msgList.append( ["falseHero", 40] )
                elif event.type == pygame.MOUSEBUTTONUP:
                    # 检查若为alter player:
                    if ( P1P2.left < pos[0] < P1P2.right ) and ( P1P2.top < pos[1] < P1P2.bottom ):
                        soundList[2].play(0)
                        if heroBook.accList[1]==True:
                            heroBook.playerNo = ( heroBook.playerNo+1 ) % 2
                        else:
                            controller.msgList.append( ["false2P", 40] )
                    # 在有chosen Attribute Bar的情况下点击鼠标。只要attrPair不为空，就证明此时鼠标悬停在该bar上方。
                    elif heroBook.accList[heroBook.pointer] and attrPair[1]:
                        heroBook.heroList[heroBook.pointer].alloSP(attrPair[0])
        # ================================================
        # ================= 综合设置 ======================
        elif ( page == "settings" ):
            drawRect( 0, 0, bg_size[0], bg_size[1], stgManager.themeColor[0] )
            back = addSymm( backImg[0], backPos[0], backPos[1] )
            # 下方指示说明
            addSymm( instruction["click0"], 378, instrucY[0] )
            addTXT( ("select","选中"), fntSet[0], (210,210,200), 425, instrucY[1])

            # 7 项按键行
            key0 = addTXT( ("Player%d" %setManager.pNo,"玩家%d" %setManager.pNo), fntSet[1], (255,255,255), setManager.cols[1], 0.12 )

            key1 = addTXT( ("Left","左"), fntSet[1], (255,255,255), setManager.cols[0], 0.2 )
            addTXT( (setManager.keyNm["key1"],setManager.keyNm["key1"]), fntSet[1], (255,255,255), setManager.cols[1], 0.2 )

            key2 = addTXT( ("Right","右"), fntSet[1], (255,255,255), setManager.cols[0], 0.28 )
            addTXT( (setManager.keyNm["key2"],setManager.keyNm["key2"]), fntSet[1], (255,255,255), setManager.cols[1], 0.28 )

            key3 = addTXT( ("Downward","下跳"), fntSet[1], (255,255,255), setManager.cols[0], 0.36 )
            addTXT( (setManager.keyNm["key3"],setManager.keyNm["key3"]), fntSet[1], (255,255,255), setManager.cols[1], 0.36 )

            key4 = addTXT( ("Wrestle","近战攻击"), fntSet[1], (255,255,255), setManager.cols[0], 0.44 )
            addTXT( (setManager.keyNm["key4"],setManager.keyNm["key4"]), fntSet[1], (255,255,255), setManager.cols[1], 0.44 )

            key5 = addTXT( ("Jump","上跳"), fntSet[1], (255,255,255), setManager.cols[0], 0.52 )
            addTXT( (setManager.keyNm["key5"],setManager.keyNm["key5"]), fntSet[1], (255,255,255), setManager.cols[1], 0.52 )

            key6 = addTXT( ("Shoot","远程攻击"), fntSet[1], (255,255,255), setManager.cols[0], 0.6 )
            addTXT( (setManager.keyNm["key6"],setManager.keyNm["key6"]), fntSet[1], (255,255,255), setManager.cols[1], 0.6 )

            key7 = addTXT( ("Use Bag Item","使用背包物品"), fntSet[1], (255,255,255), setManager.cols[0], 0.68 )
            addTXT( (setManager.keyNm["key7"],setManager.keyNm["key7"]), fntSet[1], (255,255,255), setManager.cols[1], 0.68 )

            key8 = addTXT( ("Change Bag Item","切换背包物品"), fntSet[1], (255,255,255), setManager.cols[0], 0.76 )
            addTXT( (setManager.keyNm["key8"],setManager.keyNm["key8"]), fntSet[1], (255,255,255), setManager.cols[1], 0.76 )

            # 语言设置行
            lggRect = addTXT( ("Language","语言"), fntSet[1], (255,255,255), setManager.cols[2], 0.2 )
            if language == 0:
                addTXT( ("English","英语"), fntSet[1], (255,255,255), setManager.cols[3], 0.2 )
            elif language == 1:
                addTXT( ("Chinese","中文"), fntSet[1], (255,255,255), setManager.cols[3], 0.2 )
            # 音量设置行
            volRect = addTXT( ("Volume","音乐音量"), fntSet[1], (255,255,255), setManager.cols[2], 0.3 )
            addTXT( ("%d" % vol,"%d" % vol), fntSet[1], (255,255,255), setManager.cols[3], 0.3 )
            # 关卡内自然效果设置行
            natRect = addTXT( ("Ornament","自然效果"), fntSet[1], (255,255,255), setManager.cols[2], 0.4 )
            if natON == True:
                addTXT( ("ON","开启"), fntSet[1], (255,255,255), setManager.cols[3], 0.4 )
            elif natON == False:
                addTXT( ("OFF","关闭"), fntSet[1], (255,255,255), setManager.cols[3], 0.4 )

            if setManager.chosenRect:
                if setManager.currentKey == "language" or setManager.currentKey == "difficulty" or setManager.currentKey == "volume" or setManager.currentKey == "natOrnam" or setManager.currentKey == "wallPaper":      # 右侧系统设置
                    drawFrame( setManager.chosenRect, setManager.edges[1] )
                    addSymm( pygame.transform.smoothscale( instruction["leftOpt"], (20, 40) ), setManager.cols[3]-60, setManager.chosenRect.top+setManager.chosenRect.height//2-bg_size[1]//2 )
                    addSymm( pygame.transform.smoothscale( instruction["rightOpt"], (20, 40) ), setManager.cols[3]+60, setManager.chosenRect.top+setManager.chosenRect.height//2-bg_size[1]//2 )
                elif setManager.currentKey == "keyTitle":      # 左侧玩家键位选择
                    drawFrame( setManager.chosenRect, setManager.edges[0] )
                    addSymm( pygame.transform.smoothscale( instruction["leftOpt"], (20, 40) ), setManager.cols[1]-60, setManager.chosenRect.top+setManager.chosenRect.height//2-bg_size[1]//2 )
                    addSymm( pygame.transform.smoothscale( instruction["rightOpt"], (20, 40) ), setManager.cols[1]+60, setManager.chosenRect.top+setManager.chosenRect.height//2-bg_size[1]//2 )
                else:          # 左侧键位设置
                    drawFrame( setManager.chosenRect, setManager.edges[0] )
            # handle the mouse click events
            pos = pygame.mouse.get_pos()
            if ( back.left < pos[0] < back.right ) and ( back.top < pos[1] < back.bottom ):
                back = addSymm( backImg[1], backPos[0], backPos[1] )
                if pygame.mouse.get_pressed()[0]:
                    soundList[2].play(0)
                    page = "index"
                    setManager.chosenRect = None
            elif ( setManager.edges[0][0] < pos[0] < setManager.edges[0][1] ):  # 左侧一列
                if ( key0.top < pos[1] < key0.bottom ):
                    drawFrame( key0, setManager.edges[0] )
                    addTXT( ("Alter the current player to set his/her keys.","变更当前显示的玩家以修改其键位。"), fntSet[0], (255,255,255), -200, 0.9 )
                    if pygame.mouse.get_pressed()[0]:
                        setManager.currentKey = "keyTitle"
                        setManager.chosenRect = key0
                elif ( key1.top < pos[1] < key1.bottom ):
                    drawFrame( key1, setManager.edges[0] )
                    if pygame.mouse.get_pressed()[0]:
                        setManager.currentKey = "leftKey"
                        setManager.chosenRect = key1
                elif ( key2.top < pos[1] < key2.bottom ):
                    drawFrame( key2, setManager.edges[0] )
                    if pygame.mouse.get_pressed()[0]:
                        setManager.currentKey = "rightKey"
                        setManager.chosenRect = key2
                elif ( key3.top < pos[1] < key3.bottom ):
                    drawFrame( key3, setManager.edges[0] )
                    if pygame.mouse.get_pressed()[0]:
                        setManager.currentKey = "downKey"
                        setManager.chosenRect = key3
                elif  ( key4.top < pos[1] < key4.bottom ):
                    drawFrame( key4, setManager.edges[0] )
                    if pygame.mouse.get_pressed()[0]:
                        setManager.currentKey = "wrestleKey"
                        setManager.chosenRect = key4
                elif ( key5.top < pos[1] < key5.bottom ):
                    drawFrame( key5, setManager.edges[0] )
                    if pygame.mouse.get_pressed()[0]:
                        setManager.currentKey = "jumpKey"
                        setManager.chosenRect = key5
                elif ( key6.top < pos[1] < key6.bottom ):
                    drawFrame( key6, setManager.edges[0] )
                    if pygame.mouse.get_pressed()[0]:
                        setManager.currentKey = "shootKey"
                        setManager.chosenRect = key6
                elif ( key7.top < pos[1] < key7.bottom ):
                    drawFrame( key7, setManager.edges[0] )
                    if pygame.mouse.get_pressed()[0]:
                        setManager.currentKey = "itemKey"
                        setManager.chosenRect = key7
                elif ( key8.top < pos[1] < key8.bottom ):
                    drawFrame( key8, setManager.edges[0] )
                    if pygame.mouse.get_pressed()[0]:
                        setManager.currentKey = "bagKey"
                        setManager.chosenRect = key8
            elif ( setManager.edges[1][0] < pos[0] < setManager.edges[1][1] ):  # 右侧一列
                if (lggRect.top < pos[1] < lggRect.bottom ):
                    drawFrame( lggRect, setManager.edges[1] )
                    addTXT( ("Set both the written and verbal language of the game.","设置游戏的显示和语音语言。"), fntSet[0], (255,255,255), -200, 0.9 )
                    if pygame.mouse.get_pressed()[0]:
                        setManager.currentKey = "language"
                        setManager.chosenRect = lggRect
                elif (volRect.top < pos[1] < volRect.bottom ):
                    drawFrame( volRect, setManager.edges[1] )
                    addTXT( ("Set the BGM's volume of the game.","设置游戏背景音乐的音量。"), fntSet[0], (255,255,255), -200, 0.9 )
                    if pygame.mouse.get_pressed()[0]:
                        setManager.currentKey = "volume"
                        setManager.chosenRect = volRect
                elif (natRect.top < pos[1] < natRect.bottom ):
                    drawFrame( natRect, setManager.edges[1] )
                    addTXT( ("Switch on or off the effect of natural ornaments.","开启或关闭游戏中的自然装饰效果。"), fntSet[0], (255,255,255), -200, 0.9 )
                    if pygame.mouse.get_pressed()[0]:
                        setManager.currentKey = "natOrnam"
                        setManager.chosenRect = natRect
            # handle the key events
            for event in pygame.event.get():  # 必不可少的部分，否则事件响应会崩溃
                if ( event.type == QUIT ):
                    pygame.quit()
                    sys.exit()
                elif ( event.type == KEYDOWN ):
                    if setManager.currentKey == "language":
                        if ( event.key == pygame.K_a ) or ( event.key == pygame.K_LEFT ):
                            language = (language-1) % 2
                        elif ( event.key == pygame.K_d ) or ( event.key == pygame.K_RIGHT ):
                            language = (language+1) % 2
                        # 修改文件
                        m = readFile( "r", 6, None )
                        m[0] = str(language)
                        readFile( "w", 6, ";".join(m) )
                    elif setManager.currentKey == "volume":
                        if ( ( event.key == pygame.K_a ) or ( event.key == pygame.K_LEFT ) ) and ( vol > 0 ):
                            vol = vol - 10
                        elif ( ( event.key == pygame.K_d ) or ( event.key == pygame.K_RIGHT ) ) and ( vol < 100):
                            vol = vol +10
                        # adjust the volume
                        for snd in musicList:
                            snd.set_volume(vol/100)
                        for snd in soundList:
                            snd.set_volume(vol/100)
                        # 修改文件
                        m = readFile( "r", 6, None )
                        m[2] = str(vol)
                        readFile( "w", 6, ";".join(m) )
                    elif setManager.currentKey == "natOrnam":
                        if ( event.key == pygame.K_a ) or ( event.key == pygame.K_LEFT ) or ( event.key == pygame.K_d ) or ( event.key == pygame.K_RIGHT ):
                            natON = not natON
                        # 修改文件
                        m = readFile( "r", 6, None )
                        if natON == True:
                            m[3] = "1"
                        elif natON == False:
                            m[3] = "0"
                        readFile( "w", 6, ";".join(m) )
                    elif setManager.currentKey == "keyTitle":
                        if ( event.key == pygame.K_a ) or ( event.key == pygame.K_LEFT ) or ( event.key == pygame.K_d ) or ( event.key == pygame.K_RIGHT ):
                            setManager.alterPNo()
                    # 剩下的其他情况只有键位设置（如果已经选中rect的话）                          
                    elif setManager.chosenRect:
                        if ( event.key == pygame.K_RETURN ):   # return保留为暂停/继续，不能让玩家设置
                            controller.msgList.append( ["illegalKey", 40] )
                            continue
                        setManager.changeKey(event.key)
        
        # ====================================================
        # nature ornament effect. Varies according to curStg.
        if not nature:
            if curStg == 1 or curStg == 3:
                nature = mapManager.Nature(bg_size, curStg, 8, 1)
            elif curStg == 2:
                nature = mapManager.Nature(bg_size, curStg, 2, 0)
            elif curStg == 4 or curStg == 7:
                nature = mapManager.Nature(bg_size, curStg, 18, 0)
            elif curStg == 5:
                nature = mapManager.Nature(bg_size, curStg, 10, -1)
            elif curStg == 6:
                nature = mapManager.Nature(bg_size, curStg, 8, 1)
        nature.update(screen)
        
        controller.alert(language, screen)
        pygame.display.flip()
        clock.tick(40)
# end main

# ================================================================================
def addSymm(surface, x, y):       # Surface对象； x，y为正负（偏离中心点）像素值
    rect = surface.get_rect()
    rect.left = (width - rect.width) // 2 + x
    rect.top = (height - rect.height) // 2 + y
    screen.blit( surface, rect )
    return rect                   # 返回图片的位置信息以供更多操作

# ------------------------------
# txt文本内容(各语言的同义元组)；font字体（决定大小的元组，不用给到具体语言）；rgb颜色值（0，0，0）； x为正负（偏离中心线）像素值； y为0-1的百分数
def addTXT(txt, font, rgb, x, y):
    txt = font[language].render(txt[language], True, rgb)
    rect = txt.get_rect()
    rect.left = (width - rect.width) // 2 + x
    rect.top = height * y
    screen.blit( txt, rect )
    return rect                   # 返回文字的位置信息以供更多操作
# -------------------------
def drawFrame(key, edges):        # edges 是表示框架左右边缘的二元组，单位：像素
    canvas = pygame.Surface(bg_size).convert()
    canvasRect = canvas.get_rect()
    canvas.set_colorkey((0,0,0))
    canvas.fill((0,0,0))
    p1 = (edges[0], key.top-4)
    p2 = (edges[1], key.top-4)
    p3 = (edges[1], key.bottom+10)
    p4 = (edges[0], key.bottom+10)
    pygame.draw.line( canvas, (255,255,255), p1, p2, 2 )
    pygame.draw.line( canvas, (255,255,255), p2, p3, 2 )
    pygame.draw.line( canvas, (255,255,255), p3, p4, 2 )
    pygame.draw.line( canvas, (255,255,255), p4, p1, 2 )
    screen.blit( canvas, canvasRect )
# -------------------------
def readFile(method, lineNum, new):  # method 可以是字符串形式的"r"或"w"; lineNum 是要返回的行号
    lines = []
    if method == "r":
        with open("record.rec", "r") as f:   # 读取记录信息
            for line in f:                   # 根据换行符\n自动切分为数行
                lines.append( line.split(";") ) # 用";"将该行的信息分开
        return lines[lineNum]                # 返回值是一个列表，包含目标行中的信息
    elif method == "w":
        with open("record.rec", "r") as f:   # 读取记录信息
            for line in f:                   # 根据换行符\n自动切分为数行
                lines.append( line )
        lines[lineNum] = new                 # 用new行代替原来的行
        with open("record.rec", "w") as f:
            f.write( "".join(lines) ) # 重新写入文件
# --------------------------
def drawRect(x, y, width, height, rgba):
    surf = pygame.Surface( (width, height) ).convert_alpha()
    rect = surf.get_rect()
    rect.left = x
    rect.top = y
    surf.fill( rgba )
    screen.blit( surf, rect )
    return rect

# =================================================
# invoke main(), start the program
if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        pass
    except:
        traceback.print_exc()
        pygame.quit()
