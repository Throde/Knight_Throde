# plot manager
import pygame
from random import *

# 本模块是游戏的文字、图片、音频资源管理模块，共分为两类职能：
# 第一类负责全屏动画的播放；
# 第二类负责冒险模式中触发剧情对话的跟踪交互管理。
# ===========================================================================================================
# ===========================================================================================================
class Dialogue():

    # some properties of the Manager
    stg = 1
    yList = [240, 270, 300, 330]
    
    # Words of Pre Info part ----------------
    chp1_1 = [ ("Thank god you come!", "谢天谢地，你来救我了！"), \
        ("The whole tower's on fire,", "整座塔现在都是一片火光，"), \
        ("protect yourself when you up.", "请务必保护好自己。"), \
        ("You can get supplies from scattered chests.", "你可以从散落的宝箱中获得补给。") ]
    chp1_2 = [ ("Guy, you did quite good.", "你身手还不赖嘛。"), \
        ("but face more monsters from now on.", "但现在开始要面对更多怪物了。"), \
        ("Babydragons can fly and shoot fire,", "雏龙会喷火还会飞，"), \
        ("Try if you can shoot them down.", "试试你能不能把他们从空中击落？") ]
    chp1_3 = [ ("Prepared to fight the Boss?", "准备充足迎战巨龙了吗？"), \
        ("Don't get scared,", "不要慌张，"), \
        ("You've nice shield to defend its fire.", "你有强大的盾可以抵挡他的火焰。"), \
        ("Shoot its belly, Achilis' heel.", "射它的肚子，那是他的弱点所在。") ]

    chp2_1 = [ ("Watch your head, my sweetie...", "宝贝，当心你的头上……"), \
        ("These golems really tough I can't hurt them.", "这些石头人太硬了，我打不穿它们。"), \
        ("But not for your musket, I think. Besides,", "但对于你的火枪来说就不一样了。另外，"), \
        ("watch out the uneven path and jump ahead when stuck.", "有的路面崎岖不平，卡住的时候记住跳着前进。") ]
    chp2_2 = [ ("The most terrible creature is coming.", "最可怕的家伙才要出现。"), \
        ("We call these cave dwellers 'bowlers',", "穴居人常年生活在洞穴深处，"), \
        ("since they like to roll rocks.", "他们蛮不讲理，身材高大，"), \
        ("Never negotiate with these giants.", "小心他们扔来的巨大石头。") ]
    chp2_3 = [ ("You almost get me!", "就快到我这儿了！"), \
        ("Be quite, not to wake up the ", "轻轻地来，不要惊醒了这个洞穴的"), \
        ("lord of this cave- no.", "领主——不，千万不要。"), \
        ("Once you wake it... I don't know.", "万一它发现你了……我也不知道该怎么办。") ]

    chp3_1 = [ ("Thank you for coming, kid.", "谢谢你来救我，孩子。"), \
        ("But this is no fun at all.", "这片墓地里是尸骨和鬼魂的乐园,"), \
        ("Do stay away from the walking deads,", "记住那些行尸走肉保持一点距离，"), \
        ("or you may become one of them.", "否则，你也会变成他们中的一员。") ]
    chp3_2 = [ ("Forgot to tell you,", "忘记告诉你了，"), \
        ("deeper you in the yard, denser the mist.", "越往墓地深处，黑暗迷雾就越浓。"), \
        ("There're some torch accessible somewhere,", "这里或许有以往探险者遗落的火炬，"), \
        ("which will help you a lot.", "它们能照亮你前行的道路。") ]
    chp3_3 = [ ("Under the cover of darkness,", "在这黑暗之中，"), \
        ("something horrible is moving.", "有一些可怕的东西在游动，"), \
        ("I was deadly hurt by it.", "就是它袭击了我。"), \
        ("Watch your step, kid.", "每走一步，都注意周围！") ]
    
    chp4_1 = [ ("It's a complex and dangerous forest.", "这片林子很复杂，也很危险，"), \
        ("Beaware of the rising acid ooze beneath,", "时刻当心脚下那涨起的酸性沼泽，"), \
        ("It will kill all the lifes it contacts", "它会腐蚀它所接触到的一切生命，"), \
        ("except for the disgusting slimes.", "除了那些团恶心的软泥怪！") ]
    chp4_2 = [ ("Now watch your head...", "要继续打起精神了噢！"), \
        ("The sky is the battle field of gaint", "这里到处飞着巨大的硬壳甲虫，"), \
        ("bugs which will prey you from above.", "它们会从空中扑向你，"), \
        ("My advice, try to avoid them.", "我的建议是……精彩地躲开。") ]
    chp4_3 = [ ("Not bad, geezer.", "还真是厉害呢，老头儿。"), \
        ("I'm right here, trapped by the Python.", "我就在你上面，被一条蛇给困住了。"), \
        ("Keep that pace and burn these", "保持这气势呀，把一切"), \
        ("disgusting stuffs in your way!", "恶心的东西都给烧光，烧光！") ]
    
    chp5_1 = [ ("I'm the priest of the kingdom.", "我是王国的祭司，"), \
        ("I was with the king before apart.", "大家走散之前我一直和国王呆在一起。"), \
        ("Fists of Blizzard is a great impediment here.", "间歇的暴风雪是在这里行进的一大阻碍。"), \
        ("Aren't you skilled in coping with these wolves?", "你也应该很擅长对付这些狼吧？") ]
    chp5_2 = [ ("Looks like God stand by us.", "看来上帝站在我们这边。"), \
        ("the mountain is't that hard to conquest,", "这座雪山也没有人们说的那么"), \
        ("isn't it?", "难以征服，不是吗？"), \
        ("I don't often make rhetorical questions, do I?", "我不常问反问句，我有吗？") ]
    chp5_3 = [ ("The IceTroll is an ancient Titan.", "冰雪巨人是远古的泰坦巨人，"), \
        ("No prince dare to challenge him so far.", "历史上送来的王子没有一个敢挑战它。"), \
        ("But I'm afraid you will have to step on", "但你只有经过它的领地才能找到我。"), \
        ("his territory... Holy light bless you.", "圣光庇护你！") ]
    
    chp6_1 = [ ("I wanted to shelter here,", "我原想逃到这里避难，"), \
        ("But the factory has betrayed me.", "谁知整坐工厂的侏儒工人都叛变了。"), \
        ("Along with the dwarf workers,", "更严峻的是，他们操纵的机械装置，"), \
        ("the machines also turns against us.", "也成了我们的敌人。") ]
    chp6_2 = [ ("The factory is rather dangerous.", "兵工厂机关重重，"), \
        ("Please watch your head!", "你一定要小心啊。"), \
        ("We can't just stop here,", "我们绝不能在这里倒下，"), \
        ("My people in the capital are waiting...", "王国的子民等着我们回去！") ]
    chp6_3 = [ ("Damn it, the WarMachine is activated!", "糟了……侏儒工人启动了战争机器！"), \
        ("It was originally made to serve me!", "这原本是我命令打造的秘密武器！"), \
        ("He's on his way for you. If you come", "他正在找你，如果交手了，"), \
        ("across, attack his back first.", "率先打破它背上的火炮系统！") ]

    chp7_1 = [ ("I admire your gut, my brother.", "我敬畏你的勇气，哥哥。"), \
        ("You have lost your kingdom, your power,", "你已经失去了你的王国，你的权力，"), \
        ("your everything... But you returned.", "你已一无所有……但你竟然回来了。"), \
        ("Challenge me, then.", "那就来挑战我吧，哼哼哼……") ]
    chp7_2 = [ ("Don't you understand?", "你还不明白吗？"), \
        ("Days would never return, cause", "白昼将永不复返，"), \
        ("I'm the absolute power of Night.", "因为我就是黑夜的绝对力量。"), \
        ("Corrupt with me, Brother...", "和我一起加入长夜吧，哥哥……") ]
    chp7_3 = [ ("You will finally see...", "你终将会明白的……"), \
        ("Delicate human cannot master nothing...", "脆弱的人类什么也掌控不了……"), \
        ("You can not even controll your own fate.", "你连自己的命运也掌握不了。"), \
        ("Let me show you...", "我会让你彻底明白的……") ]
    
    tips = [ # general tip
        ("Hero's backpack can hold different items you find in chests.", "你的背包可以容纳从宝箱里获得的不同物品。按"),
        ("Press AlterItem Key to change and UseItem Key to use ", "切换键来切换当前的背包物品，按使用键来使用当前"),
        ("the current available item.", "的背包物品。")
    ], [
        ("It's a good habit to eat up your fruits as soon as you can in", "在墓地里及时把身上携带的水果都吃了是个好习惯。"),
        ("the graveyard. Once you get infected you will have to cry about", "因为一旦不慎感染成了丧尸，即使背包里装着十多个"),
        ("your life despite dozens of fruits in your bagpack.","水果，濒死的时候你也只能望果兴叹了。")
    ], [
        ("Every hero has his or her unique characteristics and strengths.", "每个英雄都有自己独特的属性和长处。"),
        ("They are always better at some certain cicumstances. It's hard", "他们也都有自己擅长应对的场合。很难说"),
        ("to say who's stronger-but it's good to have your favorite.","谁更厉害——但总有你最喜欢的。")
    ], [
        ("The Casual Model and the Practice Field both adopt the Normal", "休闲模式和训练场中的难度级别都是"),
        ("Difficulty of Adventure Model. ", "冒险模式中的“标准”难度。")
    ], [  # About Adventure Model
        ("In Adventure Model, only when all the Area Guardians are", "冒险模式中，只有所有被标记的敌人都被消灭后，才能解锁区域"),
        ("eliminated can you access the next area. Check how many Guardians", "门。可以通过左上角的数字来实时查看当前区域还剩下多少个"),
        ("remaining in the current area through upper-left indicator.", "怪物守卫。")
    ], [
        ("In Adventure Model, different tower may have different natural", "冒险模式中，不同的地域会有不同的自然阻碍。"),
        ("impediments. However, you can always find some helpful equipments", "但是你总能从宝箱中发现有用的工具来克服这些困难，"),
        ("from chests to fight against them. Be grateful to former adventurers.","这都要感谢你的前任冒险者们。")
    ], [  # About Casual Model
        ("In Casual Model, you can only head toward higher layers of","休闲模式中，你只能一往无前地向塔的高层跳跃，"),
        ("the tower-You can never go back. If you fall outside the screen,", "不能向下回去。如果你了掉落到屏幕范围之外，就会"),
        ("you will be dead.", "很快死亡。")
    ], [
        ("In Casual Model, for each new layer you gain 1 point.", "休闲模式中，你每跳上新的一层便能获得1分。"),
        ("Killing different enemy rewards you corresponding scores.", "杀死不同的敌人，可以额外获得不同的分数。")
    ], [  # About Practice Model
        ("In Practice Field, you get infinite ammunition and backpack","练习场中，你的弹药和背包物品是无限的，"),
        ("items. Thus, no supply chest or backpack info is provided.","因此不会提供任何的补给箱，也不显示背包信息。")
    ], [
        ("In Practice Field, when you get endangered you will immediately","练习场中，当你濒死时会立即回复所有体力值。"),
        ("get recovered. Of course, So does the trainer.","当然，训练师也是如此。")
    ], [
        ("In Practice Field, strawmen are generated all the time for you","练习场中，会源源不断地生成稻草人以供你攻击。"),
        ("to attack. You can practice your shooting and fighting skills","你可以不断练习你的射击精度、砍杀操作等等。"),
        ("with them. Also good for fun.", "当然，也可以纯属娱乐。")
    ]
    
    #字典，指向所有的关卡信息。
    allPre = { 1:[chp1_1, chp1_2, chp1_3], \
        2:[chp2_1, chp2_2, chp2_3], \
        3:[chp3_1, chp3_2, chp3_3], \
        4:[chp4_1, chp4_2, chp4_3], \
        5:[chp5_1, chp5_2, chp5_3], \
        6:[chp6_1, chp6_2, chp6_3], \
        7:[chp7_1, chp7_2, chp7_3] }
    preList = []    #只存储当前关卡pre的列表

    # Words of Interaction part -----------------
    chap1Msg = { 1:"这座哨塔共划分为三个区域，每个区域连接处有一道关门。",
        2:"每个区域均由一些怪物头目守卫，它们在其血条左侧具有头目标记。",
        3:"当前区域的剩余头目数量在屏幕左上方显示。" }
    chap2Msg = { 1:"注意被死尸的呕吐物溅射到之后，也会变成死尸。",
        2:"宝箱中有几率开出药剂，它能够治愈死尸的异变。",
        3:"墓地深处有浓雾弥漫，火炬能够在一定时间内扩大可视范围。" }
    chap3Msg = { 1:"雨林中每当下雨，便会涨起具有腐蚀性的绿色泥沼。",
        2:"除了那一团团软泥怪，其他生命都会受到伤害。",
        3:"附在砖块之下的虫卵之巢会不断掉落蠕虫，它们是硬壳甲虫的前身。" }
    
    # ====================================================================
    # Constructor of Dialogue Manager ------------------------------------------
    def __init__(self, stg):
        # initialize the properties of the object
        if stg:
            self.preList = self.allPre[stg]
        #self.tipImg = [ pygame.image.load("image/tipGoalie.png").convert_alpha(), pygame.image.load("image/tipBackpack.png").convert_alpha(), 
        #    pygame.image.load("image/tipUp.png").convert_alpha(), pygame.image.load("image/tipScore.png").convert_alpha(), 
        #    pygame.image.load("image/tipInfinite.png").convert_alpha(), pygame.image.load("image/tipImmune.png").convert_alpha(), 
        #    pygame.image.load("image/tipEndless.png").convert_alpha() ]
    
    def getPre(self, area):
        return self.preList[area]

# ===========================================================================================================
# ===========================================================================================================
class StgManager():

    nameList = [ ("Dragon Castle","恶龙城堡"), ("Underground Cave","地下洞穴"), ("Dead Yard","亡灵乐园"), ("Ooze Forest","软泥雨林"),
        ("Frozen Peak","冰雪孤峰"), ("Deserted Factory","古旧工厂"), ("Riot Capital","动荡王城") ]
    infoList = [ [("",""), ("","")],
        [("Used to be a fort of the kindom,","这座堡垒原本是王国边境的军事岗哨，"), ("until occupied by the rude dragon for dwelling.","后来被不讲道理的巨龙占去做了窝。")],
        [("They talk about diamonds in this cave,","人们谈论的都是这座山洞里的钻石、水晶，"), ("but the stones and the dwellers.","却只字不提那些诡异的石头和恐怖的穴居人……")],
        [("Only royal families can be buried here.","只有高贵的皇族才能埋葬在这块墓地中，"), ("Skeletons will imply the history of the kingdom.","数数骷髅的数量就知道王国的历史有多悠久了。")],
        [("Forest outside capital is perfect for hunting,","皇城郊外的这片密林是天然的狩猎场，"), ("only for those who are the best.","但只有最优秀的猎人才能安然归来。")],
        [("North of the kindom is high snow moutains.","王国最北边是常年冰雪的高山，"), ("Princes are sent here for a year before throned.","将任大位的王子一般都会送往这里历练一年。")],
        [("Before the terrible havoc it made weapons,","荒废前，是集造武器、造战车于一体的大型兵工厂，"), (" vehicles, and lovely toys for royal babies.","也会给皇城的小王子、小公主做玩具。")], 
        [("The Capital is built with silver-covered bricks.","皇城的城砖镀上了亮闪闪的白银，"), ("But it never shines in its dark time.","可在黑暗之时只剩下了冰凉与死寂。") ] ]
    # color (RGB)   中性：灰               关卡一：红           关卡二：深蓝           关卡三：紫            关卡四：绿          关卡五：浅蓝         关卡六：浅黄          关卡七：灰白
    alp = 210
    themeColor = [ (50, 50, 50, alp), (200, 100, 100, alp), (90, 90, 160, alp), (180, 90, 180, alp), (90, 180, 90, alp), (140, 140, 220, alp), (180, 180, 90, alp), (150, 150, 150, alp) ]
    compassPos = [ (0, 20), (-160, -180), (10, -120), (-210, -100), (-260, 220), (-360,40), (-220,0) ]
    curPos = [0, 20]
    star = [ 2, 1, 0, 0, 0, 0, 0 ]
    # Highest record:
    high = [ 0, 0, 0, 0, 0, 0, 0 ]

    # ====================================================================
    # Constructor of StgManager ------------------------------------------
    def __init__(self, stgInfo):
        # initialize the properties of the object
        # 初始化关卡封面
        self.coverList = [pygame.image.load("image/cover1.jpg").convert(), pygame.image.load("image/cover2.jpg").convert(), pygame.image.load("image/cover3.jpg").convert(), 
            pygame.image.load("image/cover4.jpg").convert(), pygame.image.load("image/cover5.jpg").convert(), pygame.image.load("image/cover6.jpg").convert(), 
            pygame.image.load("image/cover7.jpg").convert() ]
        # 封面缩略图
        self.coverAbb = []
        for each in self.coverList:
            coverAbb = pygame.transform.smoothscale(each, (90, 120))
            self.coverAbb.append( coverAbb )
        # compass
        self.compass = pygame.image.load("image/compass.png").convert_alpha()
        self.curPos = [0, 20]
        # 其他图标
        self.lock = pygame.image.load("image/lock.png").convert_alpha()
        self.option = [pygame.image.load("image/leftOpt.png").convert_alpha(), pygame.image.load("image/rightOpt.png").convert_alpha()]
        # 初始化通关信息（星星数和休闲模式下的最高分）
        i = 0
        for stg in stgInfo:
            self.star[i] = int( stg.split(",")[0] )
            self.high[i] = int( stg.split(",")[1] )
            i += 1
    
    def moveCompass(self, nxt):
        self.curPos[0] += (self.compassPos[nxt][0] - self.curPos[0])//8
        self.curPos[1] += (self.compassPos[nxt][1] - self.curPos[1])//8
    
    def renewRec(self, infoList, indx, newVal, gameMod):  # newVal is a list and return the new list
        # 冒险通关信息（负值），检查、更改信息
        if ( gameMod == 0 ): 
            if ( newVal > int( infoList[indx].split(",")[0] ) ):  # 这里newVal规定为难度级别值，故比原纪录大，则进行更新。否则不更新。
                infoList[indx] = str(newVal)+","+infoList[indx].split(",")[1]
                self.star[indx] = newVal   
        # 休闲模式，更新分数
        elif (gameMod == 1):
            self.high[indx] = newVal
            if (newVal < 10):
                val = "00"+str(newVal)
            elif (newVal < 100):
                val = "0"+str(newVal)
            else:
                val = str(newVal)
            infoList[indx] = infoList[indx].split(",")[0] + "," + val
        info = ";".join(infoList)
        return info

# ===========================================================================================================
# ===========================================================================================================
class Collection():

    # Monster Collection部分:------------------------
    monsList = [ None, {}, {}, {}, {}, {}, {}, {} ]   # 分关卡存储所有7关的怪物（访问序号1~7）；其中第0个是未解锁的虚怪兽模型
    card = None
    cardOn = None
    board = None
    quit = None
    quitOn = None

    stgName = []
    cardY = [ -140, 90, 320, 550, 780, 1010, 1240 ]
    cardRect = []      # 按序保存所有cardrect引用的列表（行优先）
    display = None       # 显示大图查看详情的标记，用于指示应当显示某个坐标的怪物。None表示不显示。

    # wallPaper Collection部分:----------------------
    paperNameList = [ ("???","？？？"), ("Fighting Dragon","鏖战巨龙"), ("Night Ruins","雨夜废墟"), ("Castle Escape","逃脱城堡"), ("Cave Lost","洞穴迷踪"), 
        ("Into Grave","踏入墓园"), ("Hunting Alone","独自狩猎") ]
    paperList = []     # 壁纸原画列表
    paperRect = []     # 壁纸原画的位置信息列表

    paperX = [ -220, 0, 220 ]
    paperY = [ -150, 30, 210, 390, 570 ]
    paperAbbList = []  # 壁纸缩略图列表
    paperAbbRect = []  # 壁纸缩略图位置列表
    activePaper = 0    # 当前正在使用的壁纸

    # 一些界面的参数，显示元素的窗口。------------------
    subject = { 0:("Monsters","怪物图鉴"), 1:("WallPapers","主页壁纸") }
    rollerY = { 0:0, 1:0 }  # 相应地，分别是monsters、wallpapers的roller纵坐标（相对）。
    liftY = { 0:10, 1:30 }
    window = None
    WDRect = None
    roller = None
    rollerRange = (-180, 180)    # 右侧滚轮的纵坐标范围

    # ====================================================================
    # Constructor of Collection ------------------------------------------ 
    def __init__(self, bg_size, stgName):
        # initialize the properties of the object
        self.curSub = 0
        self.roller = pygame.image.load("image/roller.png").convert_alpha()
        for each in self.rollerY:
            self.rollerY[each] = self.rollerRange[0]
        # 以下是怪物图鉴部分 --------------------------------------------------------
        self.stgName = stgName
        self.monsList[0] = VMons( ("Unknown","未知"),(0,0),(),[("Kill one to collect","在冒险模式中击杀"), ("in adventure model.","一只此怪物来收集它。")], "notFound.png" )
        # 第一关的怪物
        stg = self.monsList[1]
        stg["gozilla"] = VMons( ("Gozilla","小哥斯拉"),(1,0),("Health:30  Damage:6","生命值：30 伤害值：6"),[("Many wonder how can Gozilla walk in fire.","很多人好奇小哥斯拉为什么可以在火里行走，"), ("But no one has answer cause seekers are all eaten up.","但始终没有答案，因为去问的人都被吃了。")], "stg1/gozilla0.png" )
        stg["dragon"] = VMons( ("Baby Dragon","火龙宝宝"),(1,1),("Health:40  Damage:6.5","生命值：40 伤害值：6.5"),[("Never touch his head for his loveliness.","不要看火龙宝宝可爱就上去摸他的脑袋。"), ("If you insist doing so, tie up his smoking mouth first.","如果非要这么做，请先把他冒烟的嘴巴捆上。")], "stg1/dragonLeft1.png" )
        stg["megaGozilla"] = VMons( ("Mega Gozilla","超级哥斯拉"),(1,2),("Health:44  Damage:6","生命值：44 伤害值：6"),[("Mature but dull, and more homely-looking. Anyway,","成熟多了，却也变得行动迟缓。比起小时候还丑了许多。"), ("he would punch you hard if you dare comment on his nose.","如果你胆敢当面这么评论它的话，它会一拳头把你锤飞。")], "stg1/megaGozilla1.png" )
        stg["RedDragon"] = VMons( ("Crimson Dragon","猩红巨龙"),(1,3),("Health:200  Damage:12","生命值：200 伤害值：12"),[("You successfully draw her attention.","你成功引起了她的注意。"), ("That usually won't be longer than a few secs.","通常来说，这不会超过几秒钟。")], "stg1/RedDragon_All.png" )
        #第二关的怪物
        stg = self.monsList[2]
        stg["golem"] = VMons( ("Golem","戈仑石人"),(2,0),("Health:42  Damage:8","生命值：42 伤害值：8"),[("( Golemite  Health:21  Damage:4 )","（小戈仑石人 生命值：21 伤害值：4）"),  ("These stuffs are so hard that","这些家伙又结实又坚硬，"), ("they can be perfect construction materials.","可以当作建造别墅的好材料。")], "stg2/golemLeft0.png" )
        stg["bowler"] = VMons( ("Bowler","滚石巨人"),(2,1),("Health:45  Damage:0.5/hit","生命值：45 伤害值：0.5/碰撞"),[("His name well represents his two features:","滚石巨人这个名字很好的体现了他的两个特征："), ("Bowling, and Big.","滚石和巨人。")], "stg2/bowler0.png" )
        stg["GiantSpider"] = VMons( ("Giant Spider","巨型魔蛛"),(2,2),("Health:200  Damage:8","生命值：200 伤害值：8"),[("His name well represents his two features:","滚石巨人这个名字很好的体现了他的两个特征："), ("Bowling, and Big.","滚石和巨人。")], "stg2/spiderBody.png" )
        #第三关的怪物
        stg = self.monsList[3]
        stg["bat"] = VMons( ("Bat","蝙蝠"),(3,0),("Health:10  Damage:2","生命值：10 伤害值：2"),[("Lovely sprite of the night.","黑夜中可爱的小精灵。"), ("Perfect if they don't hurt you.","如果不伤人就完美了。")], "stg3/bat1.png" )
        stg["skeleton"] = VMons( ("Skeleton","骷髅兵"),(3,1),("Health:20  Damage:3","生命值：20 伤害值：3"),[("It is as vunerable as a pile of bones -well so is him.","小骷髅兵脆的像个骨架————好吧他们本来就是。"), ("But when you get hundreds of them,","但是他们源源不断地从地下冒出来时，"),("you end up there.","你想逃跑也逃不掉了。")], "stg3/skeletonLeft0.png" )
        stg["dead"] = VMons( ("Walking Dead","丧尸"),(3,2),("Health:30  Damage:0.5/hit","生命值：30 伤害值：0.5/碰撞"),[("They walk slowly and bite slowly...","一步两步，一口两口……"), ("and you ill quicly.","然后你也成了僵尸。")], "stg3/deadLeft0.png" )
        stg["Vampire"] = VMons( ("Vampire","吸血女巫"),(3,3),("Health:200  Damage:most 48/scrape","生命值：200 伤害值：至多 48/刮伤"),[("Steal Health: 50%","吸血：50%"), ("She lives by these souls and feeds the undead.","靠收割灵魂为生，养活不死生物。"), ("You may understand totally when she steals your blood","当她用镰刀挥向你并吸血时，"),("with her scythe.","你会体会的更深。")], "stg3/Vampire_All.png" )
        #第四关的怪物
        stg = self.monsList[4]
        stg["slime"] = VMons( ("Slime","软泥怪"),(4,0),("Health:28  Damage:6","生命值：28 伤害值：6"),[("You might feel disgusting, but they are great","你可能会感到很恶心，但它们为这片雨林的清洁"), ("cleaners of the forest. Once hitted through a fortunate","做出了巨大贡献。如果你攻击的角度合适，"), ("trajectory, you can see one split into two.","就有机会看到它们分裂出另一只软泥怪。")], "stg4/slime6.png" )
        stg["nest"] = VMons( ("Eggs","虫卵"),(4,1),("Health:60","生命值：60"),[("( Worm  Health:5  Damage:4.5 )","（蠕虫 生命值：5 伤害值：4.5）"), ("It gives birth to worms continuously,","这堆虫卵会源源不断地孵出小蠕虫，"), ("which may drop on your head...","冷不丁掉在你的头上，然后炸开……"),("Surprise, hah?","惊不惊喜，意不意外？")], "stg4/nest0.png" )
        stg["fly"] = VMons( ("Crusty Coleopter","硬壳甲虫"),(4,2),("Health:38  Damage:5.5","生命值：38 伤害值：5.5"),[("The Coleopter has the hardest shell,","硬壳甲虫有世界上最硬的壳，"), ("do you have the finest weapon?","你有世界上最锋利的箭吗？")], "stg4/flyLeft0.png" )
        #第五关的怪物
        stg = self.monsList[5]
        stg["wolf"] = VMons( ("Snow Wolf","雪狼"),(5,0),("Health:32  Damage:8.5","生命值：32 伤害值：8.5"),[("Aggressive Snow Wolf lives in the north peak.","北方雪山上攻击性极强的雪狼，"), ("His fur is very favored by bold hunters.","胆大的猎人最喜欢它那暖和的皮毛。")], "stg5/wolf0.png" )
        stg["iceTroll"] = VMons( ("Ice Troll","雪怪"),(5,1),("Health:38  Damage:0.01/hit","生命值：38 伤害值：0.01/碰撞"),[("Clumsy and cool","笨拙而冷酷，无情又强壮。"), ("Piercing and powerful.","")], "stg5/iceTroll0.png" )
        #第六关的怪物
        stg = self.monsList[6]
        stg["dwarf"] = VMons( ("Dwarf Worker","侏儒工人"),(6,0),("Health:28  Damage:4.5","生命值：28 伤害值：4.5"),[("They are small, and they are angry.","他们身材虽小，却满脸戾气，"), ("It's the rigid boss to be blame.","这都是因为那严苛的工头导致的。")], "stg6/dwarf0.png" )
        stg["gunner"] = VMons( ("Gunner","机枪守卫"),(6,1),("Health:50  Damage:3/hit","生命值：50 伤害值：3/碰撞"),[("Basically made out of offcuts,","原料基本都是废铜烂铁，"), ("so some are not very reliable.","所以并非总是那么牢靠。")], "stg6/gunner0.png" )
        stg["WarMachine"] = VMons( ("War Machine","战争机器"),(6,2),("Health:200","生命值：200"),[("Grenade Damage:6.5  Laser Damage:1/hit","榴弹伤害：6.5 激光伤害：1/碰撞"), ("Designed by the best mechanic of the kingdom,","由全王国最优秀的技工设计完成，"), ("but never practice in a war yet.","但还从来没有投入到战场上使用过。")], "stg6/WarMachine_All.png" )
        # 第七关的怪物
        stg = self.monsList[7]
        stg["guard"] = VMons( ("Royal Guard","王城卫兵"),(7,0),("Health:30  Damage:6.5","生命值：30 伤害值：6.5"),[("Cladded with heavy armors. With","身披重甲，手执长矛和大盾，"), ("spear and shield in hand,","能防御来自正面的任何攻击！"), ("he can defend any attack to him.","")], "stg7/guard_All.png" )
        
        self.card = pygame.image.load("image/card.png").convert_alpha()
        self.cardOn = pygame.image.load("image/cardOn.png").convert_alpha()
        self.board = pygame.image.load("image/cardBoard.png").convert_alpha()
        self.quit = pygame.image.load("image/quit.png").convert_alpha()
        self.quitOn = pygame.image.load("image/quitOn.png").convert_alpha()
        # create the window to display cards.
        self.window = pygame.Surface( (bg_size[0]-80, bg_size[1]-180) ).convert_alpha()
        self.WDRect = self.window.get_rect()
        self.WDRect.left = 40
        self.WDRect.top = 120
        self.window.fill( (20, 20, 20, 160) )
        # initialize all cards and their rects.
        for i in (1,2,3,4,5,6,7):     # 逐关地初始化VMons的rect信息。
            x = -240
            for each in self.monsList[i]:
                self.monsList[i][each].rect = self.addSymm( self.card, x, self.cardY[i-1] )
                x += 156
        
        # 以下是墙纸About wallPaper part: -------------------------------------------------------------
        self.activePaper = int( readFile( "r", 6, None)[4] ) # wallPaper No初始默认为0
        k = 0
        while k<=5:
            ppr = pygame.image.load("image/titleBG/titleBG"+str(k)+".jpg")
            self.paperList.append( ppr )
            rect = ppr.get_rect()
            rect.left = (bg_size[0] - rect.width) // 2
            rect.top = (bg_size[1] - rect.height) // 2
            self.paperRect.append( rect )
            k += 1
        self.paperAbbRect = []
        # for each in self.paperList:
        for j in (0, 1, 2, 3):
            for i in (0, 1, 2):
                if i+j*3<=5:
                    bigP = pygame.image.load("image/titleBG/titleBG"+str(i+j*3)+"Abb.jpg")
                    self.paperAbbList.append( pygame.transform.smoothscale( bigP, (200, 150) ) )
                    self.paperAbbRect.append( self.addSymm( pygame.transform.smoothscale( bigP, (200, 150) ), self.paperX[i], self.paperY[j] ) )
                else:
                    self.paperAbbList.append( pygame.transform.smoothscale( self.card, (200, 150) ) )
                    self.paperAbbRect.append( self.addSymm( pygame.transform.smoothscale( self.card, (200, 150) ), self.paperX[i], self.paperY[j] ) )

    # roll函数：用于改变图鉴的竖直方向显示。两个参数，取值只能为1或-1.
    # (-1, 1)表示页面向下滑动；(1,-1)表示页面向上滑动。
    def roll(self, coeffRoll, coeffRect):
        self.rollerY[self.curSub] += ( coeffRoll * self.liftY[self.curSub] )
        if self.curSub==0:
            for i in (1,2,3,4,5,6,7):     # 逐关地初始化VMons的rect信息。
                self.cardY[i-1] += ( coeffRect * 32 )
                for each in self.monsList[i]:
                    self.monsList[i][each].rect.top += ( coeffRect * 32 )
        elif self.curSub==1:
            for i in ( 0, 1, 2, 3 ):
                self.paperY[i] += ( coeffRect * 20 )

    def renderWindow(self, pos, font, lgg):
        # clear the window canvas.
        self.window.fill( (0,0,0,0) )
        self.window.fill( (20, 20, 20, 160) )
        if not self.display:
            for i in (1,2,3,4,5,6,7):          # 逐关地打印
                drawRect( self.window, self.WDRect.width//2-320, self.cardY[i-1]+150, 640, 20, (180,180,180,60) )
                self.addTXT(self.stgName[i-1][lgg], font[lgg], (250,250,250), self.WDRect.width//2, self.cardY[i-1]+160)
                for each in self.monsList[i]:  # 处理每一关中的所有VMons
                    c = self.monsList[i][each].rect
                    if ( c.left+40 < pos[0] < c.right+40 ) and ( c.top+120 < pos[1] < c.bottom+120 ):
                        self.window.blit( self.cardOn, c )  # 若在等待选中时鼠标悬停，替换打底图片
                        hangover = True
                    else:
                        self.window.blit( self.card, c )
                        hangover = False
                    # 把monster图片blit到cardbase上。
                    if self.monsList[i][each].acc:
                        self.addSymm( self.monsList[i][each].image, c.left+c.width//2-self.WDRect.width//2, c.top+c.height//2-self.WDRect.height//2 )
                        if hangover:
                            drawRect( self.window, c.left, c.bottom-40, c.width, 20, (255,255,255,180) )
                            self.addTXT(self.monsList[i][each].name[lgg], font[lgg], (0,0,0), c.left+c.width//2, c.bottom-30)
                    else:
                        self.addSymm( self.monsList[0].image, c.left+c.width//2-self.WDRect.width//2, c.top+c.height//2-self.WDRect.height//2 )
        else:  # 已经选中某个monster，现只显示其详细信息。
            self.addSymm( self.board, 0, 0 )
            # IMAGE & NAME.
            self.addSymm( self.display.image, -160, 0 )
            drawRect( self.window, self.WDRect.width//2-240, self.WDRect.height//2+80, 160, 20, (240,210,180,210) )
            self.addTXT( self.display.name[lgg], font[lgg], (0,0,0), self.WDRect.width//2-160, self.WDRect.height//2+90 )
            # Right Side Description.
            self.addTXT( self.display.attr[lgg], font[lgg], (0,0,0), self.WDRect.width//2+100, self.WDRect.height*0.4)
            x = self.WDRect.height*0.45
            for each in self.display.desc:
                x += 30
                self.addTXT( each[lgg], font[lgg], (0,0,0), self.WDRect.width//2+100, x)
            
            q = self.addSymm( self.quit, -274, -132 )
            if ( q.left+40 < pos[0] < q.right+40 ) and ( q.top+120 < pos[1] < q.bottom+120 ):
                q = self.addSymm( self.quitOn, -274, -132 )
                txt = "Back" if lgg==0 else "返回"
                self.addTXT( txt, font[lgg], (0,0,0), self.WDRect.width//2-274, self.WDRect.height//2-92 )
                return q         # 若mouse hang over the quit rect, 返回之。
            return None          # 否则，返回None已告知mouse不在其上。

    def renderGallery(self, pos, font, lgg):
        # clear the window canvas.
        self.window.fill( (0,0,0,0) )
        self.window.fill( (20, 20, 20, 160) )
        for j in (0, 1, 2, 3):
            for i in (0, 1, 2):
                self.paperAbbRect[i+j*3] = self.addSymm( self.paperAbbList[i+j*3], self.paperX[i], self.paperY[j] )
                p = self.paperAbbRect[i+j*3]
                if ( p.left+40 < pos[0] < p.right+40 ) and ( p.top+120 < pos[1] < p.bottom+120 ):
                    pygame.draw.rect( self.window, (255,255,255,160), p, 3 )  # 鼠标悬停，加框
                    # 加壁纸名字
                    drawRect( self.window, p.left, p.bottom-20, p.width, 20, (255,255,255,140) )
                    if i+j*3<=5:
                        txt = self.paperNameList[i+j*3+1][lgg]
                    else:
                        txt = self.paperNameList[0][lgg]
                    self.addTXT( txt, font[lgg], (0,0,0), self.WDRect.width//2 + self.paperX[i], self.WDRect.height*0.62 + self.paperY[j] )
                # 显示是否是当前正在使用的壁纸。
                if i+j*3==self.activePaper:
                    self.addSymm( pygame.image.load("image/active.png").convert_alpha(), self.paperX[i]+80, self.paperY[j]+60 )
    
    def addRoller(self):
        # 右侧拉条
        pygame.draw.line( self.window, (210,210,200), (838,self.WDRect.height//2+self.rollerRange[0]), (838,self.WDRect.height//2+self.rollerRange[1]), 4)
        self.addSymm( self.roller, 400, self.rollerY[self.curSub])

    # --------------------------------------
    def addSymm(self, image, x, y):    # Surface对象； x，y为正负（偏离中心点）像素值
        rect = image.get_rect()
        rect.left = (self.WDRect.width - rect.width) // 2 + x
        rect.top = (self.WDRect.height - rect.height) // 2 + y
        self.window.blit( image, rect )
        return rect                    # 返回图片的位置信息以供更多操作
    
    # 本函数是以整个window为坐标（非中点）,这么做是为了能够更直接地在添加图片后对图片进行文字添加。但是x,y坐标是绘画的文本rect的中心。
    def addTXT(self, txt, fnt, color, x, y):
        txt = fnt.render(txt, True, color)
        rect = txt.get_rect()
        rect.left = x - rect.width//2
        rect.top = y - rect.height//2
        self.window.blit( txt, rect )

# ------------------------------------
class VMons():
    def __init__( self, name, coord, attr, desc, src ):
        self.name = name
        self.attr = attr
        self.desc = desc
        self.image = pygame.image.load("image/"+src).convert_alpha()
        self.rect = None
        # accessiblity (coord 表明了怪物在记录文件中的坐标：第几关（行）、该关内第几个（行内偏移）)
        if readFile( "r", 16+coord[0], None )[coord[1]] == "1":
            self.acc = True
        else:
            self.acc = False
        self.coord = coord

    def collec( self ):
        if self.acc:  # 已经收集则直接返回
            return False
        self.acc = True
        mo = readFile( "r", 16+self.coord[0], None)
        mo[self.coord[1]] = "1"
        readFile( "w", 16+self.coord[0], ";".join(mo) )
        return True   # 修改成功，返回真值

# ===========================================================================================================
# ===========================================================================================================
class HeroBook():

    #英雄解锁：  骑士   公主   王子   法师   猎人   牧师    国王
    accList = [ True, False, False, False, False, False, False ]
    # 按序存储所有VHero，因为编译时还没初始化pygame.display，所以具体构造对象的过程要到代码执行阶段，即放到init函数中去。
    heroList = []
    notFound = None
    lvList = [ (1,0,100), (1,0,100), (1,0,100), (1,0,100), (1,0,100), (1,0,100), (1,0,100) ]    # (当前等级，已有经验值，升到下一级所需经验值)
    skillList = [ [], [], [], [], [], [], [] ]

    # 一系列指针。
    playerNo = 0         # 0表示指示P1，1表示指示P2
    curHero = []
    bkCnt = 0            # book count: help the animation of turning page
    pointer = 0          # book pointer: help point to the current hero (maybe not decided yet)
    pageSnd = None
    chosenSnd = None

    bg_size = []
    xAlign = 50

    # ====================================================================
    # Constructor of HeroManager ------------------------------------------
    def __init__(self, bg_size):
        self.bg_size = bg_size
        # initialize the properties of the object
        # 检测英雄可用性
        accInfo = readFile( "r", 1, None )
        i = 0   # 辅助变量，用于指示当前的英雄在accList中的位置。如，1表示公主是否解锁。注意accInfo列表是按关卡顺序排列的。
        for stgInfo in accInfo:
            i += 1
            if int( stgInfo.split(",")[0] ) >= 0 and i < len(accInfo): # 如果该关已通过，则该关卡对应的英雄设为True（已解锁）
                self.accList[i] = True
        self.heroList = []
        # name, acc,   hp, dmg, rDmg,   desc, note, script
        self.heroList.append( VHero( 0, ("Knight","骑士"), self.accList[0], (100,4), (9,1), (15,1), ( ("He's a speechless man who","沉默寡言的骑士，把他一生"), ("hides all his words in the","的话都藏在那颗爱公主的心"), ("buried love towards Princess.","当中。") ), ("Basic hero.","基本英雄。"), ("-I will do my best!","——我保证完成任务！") ) )
        self.heroList.append( VHero( 1, ("Princess","公主"), self.accList[1], (80,3), (8,0.5), (22,2), ( ("Beautiful Princess is not only","美丽的公主可不只负责美丽，"), ("good-looking, but also a good","她手里的火枪会让你知道痛字"), ("teacher of pain with her rifle.","怎么写。") ), ("Unlock by completing Stage 1 Dragon Castle.","通过第一关恶龙城堡解锁此英雄。"), ("-Get away from my Prince!","——离我的王子远点儿！") ) )
        self.heroList.append( VHero( 2, ("Prince","王子"), self.accList[2], (120,5), (9,0.5), (13,1), ( ("Prince loves his pony best,","小马是王子的最爱，"), ("as well as Princess.","公主也是王子的最爱。") ), ("Unlock by completing Stage 2 Stone Cave.","通过第二关地下洞穴解锁此英雄。"), ("-Do you know you are bothering the Prince?","——有什么事用得着本王子出马？") ) )
        self.heroList.append( VHero( 3, ("Wizard","大法师"), self.accList[3], (90,4), (8,0.5), (16,1), ( ("A master of natural elements,","运用大自然元素力量的大师，"), ("and is favored by the king for","有时也会炼炼丹，因此很受国"), ("his modest knowledge of","王的待见。他的火球能造成范"), ("alchemy. His fireball deals","围伤害。"), ("extensive damage.","") ), ("Unlock by completing Stage 3 Dead Yard.","通过第三关亡灵乐园解锁此英雄。"), ("-Fear the power of nature.","——敬畏自然之力吧。") ) )
        self.heroList.append( VHero( 4, ("Huntress","女猎手"), self.accList[4], (85,3), (7.5,0.5), (4,0.2), ( ("A dart master and skilled","一位飞镖大师、攀岩高手，也是"), ("climber, and good friend of","流浪动物的爱心伙伴。她的飞镖"), ("strayed animals. Her dart","会穿透敌人，造成出乎意料的效"), ("penetrates enemies' body,","果！") ), ("Unlock by completing Stage 4 Ooze Underground.","通过第四关软泥雨林解锁此英雄。"), ("-Leave it to me. Prepare your money.","——交给我了，准备钱吧。") ) )
        self.heroList.append( VHero( 5, ("Priest","牧师"), self.accList[5], (100,4), (8,0.5), (12,1), ( ("The youngest but best priest","她是全王国最年轻却最优秀"), ("throughout the kingdom.","的女牧师。她的力量来自于"), ("Her power comes from the","信仰，也来自于圣之玉石。") ), ("Unlock by completing Stage 5 Frozen Peak.","通过第五关冰雪孤峰解锁此英雄。"), ("-My destiny is to purify everything.","——我的使命是净化一切。") ) )
        self.heroList.append( VHero( 6, ("King","国王"), self.accList[6], (95,4), (8.5,1), (4,0.6), ( ("Though elder and fatter now,","虽然有些老了，有些胖了，"), ("he's still awesome in battle.","但他仍然是战场上令人敬畏"), ("He's good at axe and rifle.","的对手。他最擅用短斧和"), ("","火枪。") ), ("Unlock by completing Stage 6 Antique Factory.","通过第六关古旧工厂解锁此英雄。"), ("-You are not welcomed.","——我的王国，不容异端。") ) )
        self.notFound = pygame.image.load("image/notFound.png").convert_alpha()
        # 初始化背景古书的图像
        self.book = ( pygame.image.load("image/book0.png").convert_alpha(), pygame.image.load("image/book1.png").convert_alpha(), pygame.image.load("image/book2.png").convert_alpha(), 
            pygame.image.load("image/book3.png").convert_alpha(), pygame.image.load("image/book4.png").convert_alpha(), pygame.image.load("image/book5.png") )
        # curHero (heroNo):初始默认为0：骑士; 1：公主
        self.curHero = [ int( readFile( "r", 6, None)[5] ), int( readFile( "r", 6, None)[6] ) ]
        self.pointer = self.curHero[self.playerNo] # set pointer to the player1's hero
        self.pageSnd = pygame.mixer.Sound("audio/page.wav")
        self.chosenSnd = pygame.mixer.Sound("audio/victoryHorn.wav")

    def printAttri(self, surface, fontBig, fontSmall, language, pos):
        hero = self.heroList[self.pointer]
        # level.
        lvlLine = ( ("Level"+str(hero.lvl)),("等级"+str(hero.lvl)) )
        lvlRect = self.addTXT( surface, lvlLine, fontBig, language, (80,0,0), -20, -240 )
        self.drawExp( surface, lvlRect.right+8, 130, int(hero.exp), int(hero.nxtLvl), 2 )
        # progress Text & SP number.
        self.addTXT( surface, (str(hero.exp)+"/"+str(hero.nxtLvl),str(hero.exp)+"/"+str(hero.nxtLvl) ), fontSmall, language, (10,10,10), 120, -230 )
        self.addTXT( surface, ( ("Skill Points: "+str(hero.SP)),("剩余技能点："+str(hero.SP)) ), fontSmall, language, (80,40,40), 200, -200 )
        # Attributes.
        # Firstly, Draw BG Rects.
        AttBars = {"HP":None, "PW":None, "DMG":None, "NULL":None}
        recLeft = self.bg_size[0]//2 +self.xAlign
        AttBars["HP"] = drawRect( surface, recLeft-2, self.bg_size[1]//2-162, 260, 36, (210,180,120,120) )
        AttBars["PW"] = drawRect( surface, recLeft-2, self.bg_size[1]//2-122, 260, 36, (210,180,120,120) )
        AttBars["DMG"] = drawRect( surface, recLeft-2, self.bg_size[1]//2-82, 260, 36, (210,180,120,120) )
        # Then, Check Mouse Hanging-overs.
        chosenAtt = "NULL"
        for each in AttBars:
            if AttBars[each] and ( AttBars[each].left < pos[0] < AttBars[each].right ) and ( AttBars[each].top < pos[1] < AttBars[each].bottom ):
                chosenAtt = each              # 记录选中的属性项名称.
                if each=="HP":
                    drawRect( surface, recLeft, self.bg_size[1]//2-160, 256, 32, (240,210,150,120) )  # 选中的颜色覆盖
                    self.addTXT( surface, ("+"+str(hero.hpInc),"+"+str(hero.hpInc)), fontBig, language, (80,40,40), 200, -160 )
                elif each=="PW":
                    drawRect( surface, recLeft, self.bg_size[1]//2-120, 256, 32, (240,210,150,120) )
                    self.addTXT( surface, ("+"+str(hero.pwInc),"+"+str(hero.pwInc)), fontBig, language, (80,40,40), 200, -120 )
                elif each=="DMG":
                    drawRect( surface, recLeft, self.bg_size[1]//2-80, 256, 32, (240,210,150,120) )
                    self.addTXT( surface, ("+"+str(hero.dmgInc),"+"+str(hero.dmgInc)), fontBig, language, (80,40,40), 200, -80 )
                break
        # Finally, Write Attributes Infos.
        self.addTXT( surface, ( ("Health: "+str(hero.hp)),("体力上限："+str(hero.hp)) ), fontBig, language, (0,0,0), 0, -160 )
        self.addTXT( surface, ( ("Power: "+str(hero.pw)),("近战伤害："+str(hero.pw)) ), fontBig, language, (0,0,0), 0, -120 )
        self.addTXT( surface, ( ("Ranged Damage: "+str(hero.dmg)),("远程伤害："+str(hero.dmg)) ), fontBig, language, (0,0,0), 0, -80 )

        return (chosenAtt, AttBars[chosenAtt]) # 返回选中的属性项名称和其rect.

    def chooseHero(self, language):
        if self.accList[self.pointer]: # 选中英雄的情况
            self.chosenSnd.play(0)
            self.heroList[self.pointer].voice[language].play(0)
            h = readFile( "r", 6, None )
            if self.pointer == self.curHero[1-self.playerNo]:           # 如果选中了另一个玩家选的角色
                self.curHero[1-self.playerNo] = self.curHero[self.playerNo]  # 那就将两个角色互换（不能相同！）
                h[5+(1-self.playerNo)] = str(self.curHero[1-self.playerNo])
            self.curHero[self.playerNo] = self.pointer                  # 设为出战
            h[5+self.playerNo] = str(self.curHero[self.playerNo])       # 修改记录
            readFile( "w", 6, ";".join(h) )
            return True
        return False

    # next值取1或-1，分别表示下一个或前一个。
    def turnPage(self, next):
        if (self.pointer>=6 and next>0) or (self.pointer<=0 and next<0):
            return
        self.pageSnd.play(0)
        self.bkCnt = 10*next
        self.pointer += next

    def turnAnimation(self):
        if self.bkCnt > 0:
            self.bkCnt -= 1
            if self.bkCnt >= 8:
                return( self.book[1], 0, -45 )
            elif self.bkCnt >= 6:
                return( self.book[2], 0, -42 )
            elif self.bkCnt >= 4:
                return( self.book[3], 0, -46 )
            elif self.bkCnt >= 2:
                return( self.book[4], 0, -45 )
            elif self.bkCnt >= 0:
                return( self.book[5], 0, -28 )
        elif self.bkCnt < 0:
            self.bkCnt += 1
            if self.bkCnt <= -8:
                return( self.book[5], 0, -28 )
            elif self.bkCnt <= -6:
                return( self.book[4], 0, -45 )
            elif self.bkCnt <= -4:
                return( self.book[3], 0, -46 )
            elif self.bkCnt <= -2:
                return( self.book[2], 0, -42 )
            elif self.bkCnt <= 0:
                return( self.book[1], 0, -45 )
        return None

    # y为正负（偏离屏幕中心点）像素值，x为正负偏离self.xAlign的像素值。确定了文字行的左上角坐标。
    def addTXT(self, surface, txtList, font, language, color, x, y):
        txt = font[language].render( txtList[language], True, color )
        rect = txt.get_rect()
        rect.left = self.bg_size[0]//2 + self.xAlign+x
        rect.top = self.bg_size[1]//2 + y
        surface.blit( txt, rect )
        return rect

    def drawExp(self, surface, x, y, exp, full, gap):
        color = (180, 60, 60)
        shadeColor = (90, 30, 30)   # 经验条下方的条形阴影的颜色
        # 画外边框（白色底框）
        outRect = pygame.Rect( x, y, 200, 20 )
        pygame.draw.rect( surface, (240,230,230), outRect )
        # 经验值的长度
        length = (exp/full)*(200-gap*2)
        exp = pygame.Rect( x+gap, y+gap, int(length), 20-gap*2 )
        pygame.draw.rect( surface, color, exp )
        shadow = pygame.Rect( x+gap, exp.bottom-gap, int(length), gap )
        pygame.draw.rect( surface, shadeColor, shadow )
        return outRect

# ------------------------------------
class VHero():
    def __init__( self, no, name, acc, hp, pw, dmg, desc, note, script ):
        self.no = int(no)
        self.name = name
        self.hp = hp[0]     # health
        self.hpInc = hp[1]
        self.pw = pw[0]     # power
        self.pwInc = pw[1]
        self.dmg = dmg[0]   # ranged damage
        self.dmgInc = dmg[1]
        self.desc = desc
        self.note = note
        self.script = script
        tag = name[0].lower()
        self.image = pygame.image.load("image/"+tag+"/"+tag+".png").convert_alpha()
        self.brand = pygame.image.load("image/"+tag+"/brand.png").convert_alpha()
        self.voice = ( pygame.mixer.Sound("audio/"+tag+"/"+tag+"E.wav"),pygame.mixer.Sound("audio/"+tag+"/"+tag+"C.wav") )
        self.alloSnd = pygame.mixer.Sound("audio/exp.wav")
        # accessiblity
        self.acc = acc
        # exp & level information
        lvex = readFile( "r", 8+self.no, None )  # no=0时，即记录第5行，是骑士。
        self.lvl = int(lvex[0])
        self.exp = int(lvex[1])
        self.SP = int(lvex[2])
        self.hp += int(lvex[3])
        self.pw += float(lvex[4])
        self.dmg += float(lvex[5])
        self.nxtDic = {1:100, 2:200, 3:400, 4:800, 5:1200, 6:1600, 7:2000, 8:0} # 当前级升到下一级所需的经验值
        self.nxtLvl = self.nxtDic[int(self.lvl)]

    def increaseExp(self, num):    # 处理经验增加
        self.exp += num
        if self.exp>=self.nxtLvl:
            self.lvl += 1
            self.SP += 1
            self.exp -= self.nxtLvl
            self.nxtLvl = self.nxtDic[int(self.lvl)]
        # 处理满级
        if self.lvl>=len(self.nxtDic):
            self.lvl = len(self.nxtDic)
            self.exp = 0
        # 更新文件中的信息
        # 英雄等级系统部分的信息格式：等级，exp，SP，体力加成，武力加成，远程加成
        lvex = readFile( "r", 8+self.no, None )
        lvex[0] = str(self.lvl)  # 更新等级
        lvex[1] = str(self.exp)  # 更新经验
        lvex[2] = str(self.SP)   # 更新技能点
        readFile( "w", 8+self.no, ";".join(lvex) )

    def alloSP(self, attri):       # 处理技能点分配
        if self.SP<=0:
            return
        self.alloSnd.play(0)
        lvex = readFile( "r", 8+self.no, None )
        if attri=="HP":
            self.hp += self.hpInc
            lvex[3] = str(int(lvex[3])+self.hpInc)
        elif attri == "PW":
            self.pw += self.pwInc
            lvex[4] = str(float(lvex[4])+self.pwInc)
        elif attri == "DMG":
            self.dmg += self.dmgInc
            lvex[5] = str(float(lvex[5])+self.dmgInc)+"\n"
        # 技能点-1
        self.SP -= 1
        lvex[2] = str(int(lvex[2])-1)
        readFile( "w", 8+self.no, ";".join(lvex) )

# ===========================================================================================================
# ===========================================================================================================
class Settings():

    currentKey = ""     # 调整按键设置时用到的两个变量（指针）
    chosenRect = None
    pNo = 1             # 初始为显示玩家1的键位设置

    cols = [-240, -120, 120, 240]       # 四列相对中线的横坐标值
    edges = [ (150, 440), (520, 810) ]  # 两列设置的框框边界
    # Dictionary for storing the key info of two players
    keyDic1 = {}
    keyDic2 = {}
    keyNm = {}          # 当前的keyDic里的对应键名。初始化为玩家1的键位。

    # ====================================================================
    # Constructor of HeroManager ------------------------------------------
    def __init__(self, keyDic1, keyDic2):
        # initialize the properties of the object
        self.keyDic1 = keyDic1
        self.keyDic2 = keyDic2
        self.renewKeyNm()

    def alterPNo(self):
        if self.pNo==1:
            self.pNo = 2
        elif self.pNo==2:
            self.pNo = 1
        self.renewKeyNm()

    def changeKey(self, key):
        kList = []
        if self.pNo == 1:
            #print(keyDic1[setManager.currentKey])
            self.keyDic1[self.currentKey] = key
            self.renewKeyNm()
            for each in self.keyDic1:
                kList.append( str(self.keyDic1[each]) )
            readFile( "w", 3, ";".join(kList)+"\n" )  # 补了换行符
        elif self.pNo == 2:
            self.keyDic2[self.currentKey] = key
            self.renewKeyNm()
            for each in self.keyDic2:
                kList.append( str(self.keyDic2[each]) )
            readFile( "w", 4, ";".join(kList)+"\n" )  # 补了换行符

    def renewKeyNm(self):
        if self.pNo==1:
            self.keyNm = { "key1":pygame.key.name(self.keyDic1["leftKey"]).upper(), "key2":pygame.key.name(self.keyDic1["rightKey"]).upper(), 
                "key3":pygame.key.name(self.keyDic1["downKey"]).upper(), "key4":pygame.key.name(self.keyDic1["wrestleKey"]).upper(), 
                "key5":pygame.key.name(self.keyDic1["jumpKey"]).upper(), "key6":pygame.key.name(self.keyDic1["shootKey"]).upper(), 
                "key7":pygame.key.name(self.keyDic1["itemKey"]).upper(), "key8":pygame.key.name(self.keyDic1["bagKey"]).upper() }
        elif self.pNo==2:
            self.keyNm = { "key1":pygame.key.name(self.keyDic2["leftKey"]).upper(), "key2":pygame.key.name(self.keyDic2["rightKey"]).upper(), 
                "key3":pygame.key.name(self.keyDic2["downKey"]).upper(), "key4":pygame.key.name(self.keyDic2["wrestleKey"]).upper(), 
                "key5":pygame.key.name(self.keyDic2["jumpKey"]).upper(), "key6":pygame.key.name(self.keyDic2["shootKey"]).upper(), 
                "key7":pygame.key.name(self.keyDic2["itemKey"]).upper(), "key8":pygame.key.name(self.keyDic2["bagKey"]).upper() }
            
# ===========================================================================================================
# The Controller is an integrated class that provides the ability to add alert warnings, fancy words, image effects and so on.
# ===========================================================================================================
class Controller():

    bg_size = ()
    # about message and alerts
    msgList = []
    fntSet = []
    alertDic = { "falseHero":("This Hero is locked.","此英雄尚未解锁。"), 
        "notFound":("Kill one to collect in adventure model.","在冒险模式中击杀一只此怪物来收集它。"), 
        "falseStg":("This Stage is locked.","此关卡尚未解锁。"), 
        "false2P":("You have only one hero accessible.","你目前只有一个可用的英雄。"),
        "illegalKey":("RETURN Key should not be set freely.","回车键不能被设置为玩家按键。"),
        "comingSoon":("The module coming soon!","该模块正在开发中，敬请期待！"),
        "banHero":("Hero of P1 can't join this stage.","玩家1所选的英雄不能参加本关战斗。") }
        #"newHero":("The new hero is already accessible.","新英雄已经解锁。") }
    SSList = []

    def __init__(self, bg_size):
        self.bg_size = bg_size
        self.masgList = []
        self.fntSet = [ ( pygame.font.Font("font/ebangkok.ttf", 16), pygame.font.Font("font/hanSerif.otf", 16) ), 
            ( pygame.font.Font("font/ebangkok.ttf", 24), pygame.font.Font("font/hanSerif.otf", 24) ), 
            ( pygame.font.Font("font/ebangkok.ttf", 36), pygame.font.Font("font/hanSerif.otf", 36) ), 
            ( pygame.font.Font("font/ebangkok.ttf", 48), pygame.font.Font("font/hanSerif.otf", 48) ) ]

    # 为了降低保存图片平滑切换元素的存储开销，添加时进行一系列简单的处理，将起止地址、切换时间转换为增量。
    def addSmoothSwitch(self, image, rect, endSize, dx, dy, time):  # endSize为以百分数，以1为原大小；dx，dy是相对位移
        scaleX = int( (endSize-1)*rect.width//time )  # 尺寸大小的缩放量
        scaleY = int( (endSize-1)*rect.height//time )
        dx = int(dx//time)   # 距离的每次偏移量
        dy = int(dy//time)
        self.SSList.append( [image, rect, (scaleX, scaleY), (dx,dy), time] )

    def doSwitch(self, screen):
        for each in self.SSList:
            newW = each[1].width + each[2][0]
            newH = each[1].height + each[2][1]
            newImg = pygame.transform.smoothscale(each[0], (newW, newH))
            rect = newImg.get_rect()
            newCtr = (each[1].left+each[1].width//2-rect.width//2, each[1].top+each[1].height//2-rect.height//2)
            rect.left = newCtr[0] + each[3][0]
            rect.top = newCtr[1] + each[3][1]
            each[1] = rect
            each[4] -= 1
            screen.blit( newImg, rect )
            if each[4]<=0:
                self.SSList.remove(each)
    
    def alert(self, language, screen):
        for msg in self.msgList:
            if msg[1] <= -40: # 倒计时减为0时从列表删除
                self.msgList.remove(msg)
                continue
            self.shadowTXT( self.alertDic[msg[0]][language], self.fntSet[1][language], (255,0,0), (255,255,255), 0, msg[1], screen )
            msg[1] -= 1       # 消息显示倒计时-1
    
    # ------------------------------
    # txt文本内容(各语言的同义元组)；font字体（决定大小的元组，不用给到具体语言）；rgb颜色值（0，0，0）:1是底色，即阴影颜色；2是文字颜色。
    def shadowTXT(self, text, font, rgb1, rgb2, offX, offY, surface ):
        # Shadow Part.
        txt = font.render(text, True, rgb1)
        rect = txt.get_rect()
        rect.left = (self.bg_size[0] - rect.width) // 2 + offX
        rect.top = (self.bg_size[1] - rect.height) // 2 + offY + 3
        surface.blit( txt, rect )
        # Upper Part.
        txt = font.render(text, True, rgb2)
        rect = txt.get_rect()
        rect.left = (self.bg_size[0] - rect.width) // 2 + offX
        rect.top = (self.bg_size[1] - rect.height) // 2 + offY
        surface.blit( txt, rect )
        return rect                   # 返回文字的位置信息以供更多操作

# 绘制rect的辅助函数：------------------------
def drawRect(base, x, y, width, height, rgba):  # base should be surface.
    surf = pygame.Surface( (width, height) ).convert_alpha()
    surf.fill( rgba )
    rect = surf.get_rect()
    rect.left = x
    rect.top = y
    base.blit( surf, rect )
    return rect
    
# 读写文件的辅助函数：-------------------------
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