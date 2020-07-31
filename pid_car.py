import sys
import time
import math
import pygame as pg  # install
from pygame.locals import *

pg.init()
size = width, height = 1200, 750  # 屏幕大小
screen = pg.display.set_mode(size)
pg.display.set_caption("Car tracking")
# car=pg.image.load('C:/Users/Ivan/Desktop/car.png')
# car_rect=Rect((400,150),(200,200)) # 小车初始位置所在矩形框
# move_car_rect=car_rect

count = 0
FPS = 60  # fps设定值
fps = 0
start = time.time()
clock = pg.time.Clock()

my_font = pg.font.Font(None, 25)

x, y = 555, 206  # 小车初始位置
speed = 20  # 速度标量
velocity = [0, 0]  # 速度矢量
angle = 0  # 初始角度

kp = 1.3
kd = 0.7
last_error = 0

path = [(x, y)]  # 轨迹

run = True  # 运行标志
pause = False  # 暂停标志


def color_binary(colors):
    # 颜色二值化 RGBA>>>0/1
    rval = []
    for color in colors:
        # 白色
        if color == (255, 255, 255, 255):
            rval.append(0)
        # 黑色
        elif color == (0, 0, 0, 255):
            rval.append(1)
    # print(rval)
    return rval


def get_gs_sensor_value(x, y, angle):
    # 获取灰度传感器值 并绘制传感器圆
    step1 = 11
    step2 = 19
    step3 = 15

    angle1 = math.pi * (angle + 90) / 180
    angle = math.pi * (angle) / 180

    x0 = x + step2 * math.cos(angle1) + step3 * math.cos(angle)
    y0 = y - step2 * math.sin(angle1) - step3 * math.sin(angle)

    pg.draw.circle(screen, (255, 0, 0), (int(x0), int(y0)), 3, 1)  # 绘制0号灰度

    x1 = x + step1 * math.cos(angle1) + step3 * math.cos(angle)
    y1 = y - step1 * math.sin(angle1) - step3 * math.sin(angle)
    pg.draw.circle(screen, (255, 0, 0), (int(x1), int(y1)), 3, 1)  # 绘制1号灰度

    x2, y2 = x + step3 * math.cos(angle), y - step3 * math.sin(angle)
    pg.draw.circle(screen, (255, 0, 0), (int(x2), int(y2)), 3, 1)  # 绘制2号（中间）灰度

    x3 = x - step1 * math.cos(angle1) + step3 * math.cos(angle)
    y3 = y + step1 * math.sin(angle1) - step3 * math.sin(angle)
    x4 = x - step2 * math.cos(angle1) + step3 * math.cos(angle)
    y4 = y + step2 * math.sin(angle1) - step3 * math.sin(angle)
    pg.draw.circle(screen, (255, 0, 0), (int(x3), int(y3)), 3, 1)  # 绘制3号灰度
    pg.draw.circle(screen, (255, 0, 0), (int(x4), int(y4)), 3, 1)  # 绘制4号灰度

    # 灰度传感器对应的像素值
    try:
        g0 = screen.get_at((int(x0), int(y0)))
        g1 = screen.get_at((int(x1), int(y1)))
        g2 = screen.get_at((int(x2), int(y2)))
        g3 = screen.get_at((int(x3), int(y3)))
        g4 = screen.get_at((int(x4), int(y4)))
    except:
        g0, g1, g2, g3, g4 = (255, 255, 255, 255)

    x5 = x + 100 * math.cos(angle)
    y5 = y - 100 * math.sin(angle)
    pg.draw.line(screen, (255, 0, 0), (x, y), (x5, y5), 1)  # 绘制方向指示线

    return color_binary([g0, g1, g2, g3, g4])


def pid_angle(gs):
    # pid 调速
    # :gs:灰度传感器数组
    global angle
    global last_error
    gs_black = 0  # 检测到黑色的灰度传感器数量
    sum_ = 0
    for i in range(len(gs)):
        if gs[i] == 1:
            gs_black += 1
            sum_ += i

    if gs_black != 0:
        sum_ = sum_ * 10 / gs_black - 20

    pid_p_out = kp * sum_  # p
    ed = sum_ - last_error  # 本次误差
    last_error = sum_  # 更新上次误差
    pid_d_out = kd * ed  # d

    pid_out = pid_p_out + pid_d_out
    angle = angle - pid_out

    if angle <= -180:
        angle = 180


def set_velocity(angle):
    # 设置速度矢量并更新x,y坐标
    global speed, velocity, x, y
    angle = math.pi * (-angle) / 180
    velocity[0] = speed * math.cos(angle)
    velocity[1] = speed * math.sin(angle)
    x += velocity[0]
    y += velocity[1]

    # 边界检测
    if x <= 0:
        x = 0
        speed = 0
    if x >= width:
        x = width
        speed = 0
    if y <= 0:
        y = 0
        speed = 0
    if y >= height:
        y = height
        speed = 0


def main_loop():
    # 主循环
    global run, pause, start, fps, count, x, y, angle
    while run:
        clock.tick(FPS)  # 设置fps
        for event in pg.event.get():
            if event.type == pg.QUIT:
                run = False
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_p:  # P键暂停
                    pause = not pause
                if event.key == pg.K_r:  # R键重新开始
                    x, y = 555, 206
                    angle = 0
                    path.clear()
                    path.append((x, y))

        if pause:
            continue

        mouse_pos_x, mouse_pos_y = pg.mouse.get_pos()  # 鼠标坐标

        set_velocity(angle)  # 设置速度

        # new_car=pg.transform.rotate(car,angle) # 转向
        if (x, y) not in path:
            path.append((x, y))
        # new_car_rect=new_car.get_rect()
        # move_car_rect.width=new_car_rect.width
        # move_car_rect.height=new_car_rect.height
        # move_car_rect=move_car_rect.move(velocity) # 小车矩形框移动
        # print(move_car_rect)

        # 计算fps
        count += 1
        now = time.time()
        if now - start > 0.1:
            fps = count / (now - start)
            start = now
            count = 0

        fps_img = my_font.render('fps:' + str(round(fps, 5)), True, (0, 0, 255))

        mouse_pos_img = my_font.render(
            'pos_x:' + str(mouse_pos_x) + '  pos_y:' + str(mouse_pos_y), True, (0, 0, 255))

        para_img = my_font.render(
            'kp:' + str(kp) + '  kd:' + str(kd) + '  speed:' + str(speed), True, (0, 0, 255))

        about_img = my_font.render(
            "press 'p' to pause, press 'r' to restart!", True, (0, 0, 255))
        # 绘图
        screen.fill((255, 255, 255))  # 绘制白色背景
        screen.blit(fps_img, (10, 10))  # 绘制fps
        screen.blit(mouse_pos_img, (10, 30))  # 绘制鼠标坐标
        screen.blit(para_img, (10, 50))  # 绘制参数
        screen.blit(about_img, (10, 80))  # 绘制注意事项
        pg.draw.ellipse(screen, (0, 0, 0), Rect((200, 200), (750, 400)), 20)  # 绘制跑道
        pg.draw.circle(screen, (255, 0, 0), (int(x), int(y)), 10, 1)  # 绘制圆代替小车

        gs = get_gs_sensor_value(x, y, angle)  # 获取灰度传感器值
        pid_angle(gs)  # pid调速

        pg.draw.lines(screen, (255, 0, 0), 0, path, 1)  # 绘制轨迹
        pg.display.flip()  # 重新绘制窗口

    pg.quit()


main_loop()
