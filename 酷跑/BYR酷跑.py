import pygame
from pygame.locals import *
import random
import time


# 地图
class GameBackground:
    image1 = None
    image2 = None
    main_scene = None
    speed = 8  # 滚动速度
    x1 = None
    x2 = None

    # 初始化地图
    def __init__(self, scene):
        # 加载相同张图片资源,做交替实现地图滚动
        self.image1 = pygame.image.load("images/images/map.png")
        self.image2 = self.image1
        self.main_scene = scene
        # 辅助移动地图
        self.x1 = 0
        self.x2 = self.main_scene.size[0]

    # 计算地图图片坐标
    def action(self):
        self.x1 = self.x1 - self.speed
        self.x2 = self.x2 - self.speed
        if self.x1 <= -self.main_scene.size[0]:
            self.x1 = 0
        if self.x2 <= 0:
            self.x2 = self.main_scene.size[0]

    # 绘制地图的两张图片
    def draw(self):
        map_y = self.main_scene.size[1] - self.image1.get_height()
        self.main_scene.scene.blit(self.image1, (self.x1, map_y))
        self.main_scene.scene.blit(self.image2, (self.x2, map_y))


# 背景移动物
class Cloud:
    speed = 1
    image = None
    x = None
    y = None

    def __init__(self, x, y, image):
        self.x = x
        self.y = y
        self.image = image

    def move(self):
        self.x -= self.speed


# 地面障碍
class EarthObstacles:
    speed = 8
    image = None
    x = None
    y = None
    width = None
    height = None

    def __init__(self, x, y, image):
        self.x = x
        self.y = y
        self.image = image
        self.width = image.get_width()
        self.height = image.get_height()

    def move(self):
        self.x -= self.speed

# 空中障碍
class AirObstacle:
    speed = 10
    image = None
    x = None
    y = None
    width = None
    height = None
    index = 0
    main_scene = None
    ret = 1

    def __init__(self, x, y, image, main_scene):
        self.x = x
        self.y = y
        self.image = image
        self.main_scene = main_scene
        image = self.image[self.index]
        self.width = image.get_width()
        self.height = image.get_height()

    def move(self):
        self.x -= self.speed

    def draw(self):
        if self.ret <= 4:
            self.index = 0
        else:
            self.index = 1

        if self.ret == 8:
            self.ret = 0

        image = self.image[self.index]
        self.main_scene.scene.blit(image, (self.x, self.y))
        self.ret += 1


# byr小人
class Byr:
    speed = 10
    image = None
    x = None
    y = None
    width = None
    height = None
    index = 0
    main_scene = None
    ret = 0
    style = 0  # 0：站立，1：蹲下
    jump = 0  # 0: 未起跳，1：开始上升，2：开始下降
    jump_y_add = 0
    is_hit = 0

    def __init__(self, x, y, image, main_scene):
        self.x = x
        self.y = y
        self.image = image
        self.main_scene = main_scene

    def set_jump(self):
        if self.style == 0 and self.jump == 0:
            self.jump = 1
            self.main_scene.jump_sound.play()
        if self.style == 0 and self.jump == 2:
            self.jump = 4
            self.main_scene.jump_sound.play()

    def move(self):
        if self.jump == 1:
            self.y -= 10
            self.jump_y_add += 10
            if self.jump_y_add == 180:
                self.jump = 2

        if self.jump == 4:
            self.y -= 10
            self.jump_y_add += 10
            if self.jump_y_add == 280:
                self.jump = 5

        if self.jump == 5:
            self.y += 10
            self.jump_y_add -= 10
            if self.jump_y_add == 0:
                self.jump = 0

        if self.jump == 2:
            self.y += 10
            self.jump_y_add -= 10
            if self.jump_y_add == 0:
                self.jump = 0

    def draw(self):
        if self.ret >= 40:
            self.ret = 0
        self.index = int(self.ret / 5)

        image = self.image[self.index]
        self.width = image.get_width()
        self.height = image.get_height()
        self.main_scene.scene.blit(image, (self.x, self.y))
        self.ret += 1

        image = self.image[self.index]
        self.width = image.get_width()
        self.height = image.get_height()
        self.main_scene.scene.blit(image, (self.x, self.y))
        self.ret += 1


# 主场景
class MainScene:
    running = True
    size = None
    scene = None
    bg = None

    clouds = []
    cloud_image = None

    items = []
    item_images = []
    item_ret = 1
    item_ret_num = 100

    airobstacle_images = []
    airobstacles = []
    airobstacle_ret = 1
    airobstacle_ret_num = 150

    byr = None
    byr_images = []

    gameover_image = None
    restart_image = None
    restart_x = None
    restart_y = None
    score = 0.0

    jump_sound = None
    gameover_sound = None

    # 初始化主场景
    def __init__(self):
        pygame.init()
        # 场景尺寸
        self.size = (800, 350)
        # 场景对象
        self.scene = pygame.display.set_mode([self.size[0], self.size[1]])
        # 设置标题
        pygame.display.set_caption("BYR酷跑")
        # 创建clock对象控制帧数
        self.timer = pygame.time.Clock()

        # 创建地图
        self.bg = GameBackground(self)

        # 创建云
        self.cloud_image = pygame.image.load("images/images/cloud.png")
        self.create_cloud()

        # 创建地面障碍
        for n in range(7):
            self.item_images.append(pygame.image.load("images/images/item_" + str(n + 1) + ".png"))

        # 创建空中障碍
        self.airobstacle_images.append(pygame.image.load("images/images/bird_1.png"))
        self.airobstacle_images.append(pygame.image.load("images/images/bird_2.png"))

        # 创建byr小人
        self.byr_images.append(pygame.image.load("images/images/zhu_1.png"))
        self.byr_images.append(pygame.image.load("images/images/zhu_2.png"))
        self.byr_images.append(pygame.image.load("images/images/zhu_3.png"))
        self.byr_images.append(pygame.image.load("images/images/zhu_4.png"))
        self.byr_images.append(pygame.image.load("images/images/zhu_5.png"))
        self.byr_images.append(pygame.image.load("images/images/zhu_6.png"))
        self.byr_images.append(pygame.image.load("images/images/zhu_7.png"))
        self.byr_images.append(pygame.image.load("images/images/zhu_8.png"))

        d_x = 50
        d_y = self.size[1] - self.byr_images[0].get_height()
        self.byr = Byr(d_x, d_y, self.byr_images, self)

        # gameover
        self.gameover_image = pygame.image.load("images/images/gameover.png")
        self.restart_image = pygame.image.load("images/images/restart.png")

        # 音效加载
        self.jump_sound = pygame.mixer.Sound("sounds/sounds/jump.wav")
        self.gameover_sound = pygame.mixer.Sound("sounds/sounds/gameover.wav")

    #  生成背景移动物
    def create_cloud(self):
        self.clouds.append(Cloud(350, 30, self.cloud_image))
        self.clouds.append(Cloud(650, 100, self.cloud_image))

    # 绘制
    def draw_elements(self):
        if self.byr.is_hit == 1:
            g_x = self.size[0] // 2 - self.gameover_image.get_width() // 2
            self.scene.blit(self.gameover_image, (g_x, 120))

            self.restart_x = self.size[0] // 2 - self.restart_image.get_width() // 2
            self.restart_y = 170
            self.scene.blit(self.restart_image, (self.restart_x, self.restart_y))
            return

        self.scene.fill((255, 255, 255))  # 填充背景色为白色
        self.bg.draw()  # 绘制背景

        # 绘制背景移动物（以云为例）
        for c in self.clouds[:]:
            self.scene.blit(c.image, (c.x, c.y))

        # 绘制地面障碍
        for i in self.items[:]:
            self.scene.blit(i.image, (i.x, i.y))

        # 绘制空中障碍
        for b in self.airobstacles[:]:
            b.draw()

        # 绘制byr小人
        self.byr.draw()

        # 显示跑动距离
        self.score += 0.1
        font = pygame.font.Font("freesansbold.ttf", 20)
        text = font.render(str(int(self.score)) + "m", True, (83, 83, 83))
        text_rect = text.get_rect()
        text_rect.right = self.size[0] - 10
        text_rect.top = 10
        self.scene.blit(text, text_rect)

    # 计算元素坐标及生成元素
    def action_elements(self):
        if self.byr.is_hit == 1:
            return

        # 地图
        self.bg.action()

        # 云
        for c in self.clouds[:]:
            c.move()

            if c.x < - self.cloud_image.get_width():
                self.clouds.remove(c)

        if len(self.clouds) == 0:
            self.create_cloud()

        # 地面障碍
        if self.item_ret % self.item_ret_num == 0:
            image = self.item_images[random.randint(0, len(self.item_images) - 1)]
            x = self.size[0]
            y = self.size[1] - image.get_height()
            self.items.append(EarthObstacles(x, y, image))
        self.item_ret += 1
        if self.item_ret == self.item_ret_num:
            self.item_ret = 0
            self.item_ret_num = random.randint(60, 110)

        for i in self.items[:]:
            i.move()

            if i.x < -i.width:
                self.items.remove(i)

        # 空中障碍
        if int(self.score) > 100:
            if self.airobstacle_ret % self.airobstacle_ret_num == 0:
                x = self.size[0]
                y = 210
                self.airobstacles.append(AirObstacle(x, y, self.airobstacle_images, self))
            self.airobstacle_ret += 1
            if self.airobstacle_ret == self.airobstacle_ret_num:
                self.airobstacle_ret = 0
                self.airobstacle_ret_num = random.randint(150, 300)

            for b in self.airobstacles[:]:
                b.move()

                if b.x < -b.width:
                    self.airobstacles.remove(b)

        # byr小人
        self.byr.move()

    # 处理事件
    def handle_event(self):
        for event in pygame.event.get():
            # 检测松开键盘事件
            if event.type == pygame.KEYUP:
                if event.key == K_DOWN:
                    if self.byr.style == 1:
                        self.byr.style = 0
                        self.byr.y -= 34

            # 检测按下鼠标事件
            if event.type == pygame.MOUSEBUTTONDOWN:
                if pygame.mouse.get_pressed()[0]:
                    if self.byr.is_hit == 1:
                        pos = event.pos  # 点击位置坐标

                        # 判断点击热区
                        x1 = self.restart_x
                        x2 = self.restart_x + self.restart_image.get_width()

                        y1 = self.restart_y
                        y2 = self.restart_y + self.restart_image.get_height()

                        if pos[0] >= x1 and pos[0] <= x2 and pos[1] >= y1 and pos[1] <= y2:
                            self.byr.is_hit = 0
                            self.score = 0
                            self.items.clear()
                            self.airobstacles.clear()

            # 检测到事件为退出时
            if event.type == pygame.QUIT:
                self.running = False

    # 碰撞检测
    def detect_collision(self):
        if self.byr.is_hit == 0:
            for i in self.items[:]:
                if self.collision(self.byr, i) or self.collision(i, self.byr):
                    self.byr.is_hit = 1
                    break

            for b in self.airobstacles[:]:
                if self.collision(self.byr, b) or self.collision(b, self.byr):
                    self.byr.is_hit = 1
                    break

            if self.byr.is_hit == 1:
                self.gameover_sound.play()

    # 验证是否碰撞
    def collision(self, a, b):
        offset = 20  # 增加误差，降低难度
        temp1 = (b.x + offset <= a.x + a.width <= b.x + offset + b.width)
        temp2 = (b.y + offset <= a.y + a.height <= b.y + offset + b.height)
        return temp1 and temp2

    # 处理按键
    def key_pressed(self):
        # 获取键盘按键信息
        key_pressed = pygame.key.get_pressed()

        if key_pressed[K_DOWN]:
            if self.byr.jump == 0:
                if self.byr.style == 0:
                    self.byr.style = 1
                    self.byr.y += 35

        if key_pressed[K_SPACE]:
            self.byr.set_jump()

    # 处理帧数
    def set_fps(self):
        # 刷新显示
        pygame.display.update()
        # 设置帧率为60fps
        self.timer.tick(60)

    # 主循环 处理各种事件
    def run_scene(self):

        while self.running:
            # 计算元素坐标及生成元素
            self.action_elements()
            # 绘制元素图片
            self.draw_elements()
            # 处理事件
            self.handle_event()
            # 碰撞检测
            self.detect_collision()
            # 按键处理
            self.key_pressed()
            # 画布fps
            self.set_fps()


# 创建主场景
mainScene = MainScene()
# 开始游戏
mainScene.run_scene()
