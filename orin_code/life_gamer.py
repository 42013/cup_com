from tkinter import messagebox as msgbox
import tkinter as tk
import webbrowser
import random


class Lifes:
    def __init__(self, rows=36, cols=36):
        self.row = rows + 2
        self.col = cols + 2
        self.items = [[0] * self.col for _ in range(self.row)]
        self.histroy = []
        self.histroySize = 30
        self.running = False
        self.runningSpeed = 200

    def rndinit(self, rate=0.1):
        self.histroy = []
        for i in range(self.row):
            for j in range(self.col):
                rnd = random.random()
                if rnd > 1 - rate:
                    self.items[i][j] = 1

    def reproduce(self):
        new = [[0] * self.col for _ in range(self.row)]
        self.add_histroy()
        if len(self.histroy) > self.histroySize:
            self.histroy.pop(0)
        for i in range(self.row):
            for j in range(self.col):
                if i * j == 0 or i == self.row - 1 or j == self.col - 1:
                    new[i][j] = 0
                else:
                    lifes = 0
                    for m in range(i - 1, i + 2):
                        for n in range(j - 1, j + 2):
                            if m == i and n == j:
                                continue
                            lifes += self.items[m][n]
                    if self.items[i][j]:
                        if lifes == 2 or lifes == 3:
                            new[i][j] = 1
                        else:
                            new[i][j] = 0
                    else:
                        if lifes == 3:
                            new[i][j] = 1
        for idx, narray in enumerate(new):
            self.items[idx] = narray

    def is_stable(self):
        if len(self.histroy) < self.histroySize:
            return False
        arr = []
        for i in self.histroy:
            if i not in arr:
                arr.append(i)
        if len(arr) < 10:
            return True

    def add_histroy(self, Items=None):
        arr = []
        if Items == None:
            Items = self.items[:]
        for item in Items:
            b = 0
            for i, n in enumerate(item[::-1]):
                b += n * 2 ** i
            arr.append(b)
        self.histroy.append(arr)


def drawSpeedSlider():
    global speedScale
    speedScale = tk.Scale(win, from_=1, to=1000, orient="horizontal", label="运行速度(ms)", length=200)
    speedScale.set(200)  # 设置默认值为200毫秒
    speedScale.place(x=800, y=640)


def drawCanvas():
    global tv, rect
    tv = tk.Canvas(win, width=win.winfo_width(), height=win.winfo_height())
    tv.pack(side="top")
    for i in range(36):
        coord = 40, 40, 760, i * 20 + 40
        tv.create_rectangle(coord)
        coord = 40, 40, i * 20 + 40, 760
        tv.create_rectangle(coord)
    coord = 38, 38, 760, 760
    tv.create_rectangle(coord, width=2)
    coord = 39, 39, 760, 760
    tv.create_rectangle(coord, width=2)
    coord = 38, 38, 762, 762
    tv.create_rectangle(coord, width=2)
    R, XY = 8, [50 + i * 20 for i in range(36)]
    rect = [[0] * 36 for _ in range(36)]
    for i, x in enumerate(XY):
        for j, y in enumerate(XY):
            rect[i][j] = tv.create_rectangle(x - R, y - R, x + R, y + R, tags=('imgButton1'))
            tv.itemconfig(rect[i][j], fill='lightgray', outline='lightgray')
    tv.tag_bind('imgButton1', '<Button-1>', on_Click)
    drawSpeedSlider()  # 添加绘制滑块的函数


# def drawCanvas():
#     global tv, rect
#     tv = tk.Canvas(win, width=win.winfo_width(), height=win.winfo_height())
#     tv.pack(side="top")
#     for i in range(36):
#         coord = 40, 40, 760, i * 20 + 40
#         tv.create_rectangle(coord)
#         coord = 40, 40, i * 20 + 40, 760
#         tv.create_rectangle(coord)
#     coord = 38, 38, 760, 760
#     tv.create_rectangle(coord, width=2)
#     coord = 39, 39, 760, 760
#     tv.create_rectangle(coord, width=2)
#     coord = 38, 38, 762, 762
#     tv.create_rectangle(coord, width=2)
#     R, XY = 8, [50 + i * 20 for i in range(36)]
#     rect = [[0] * 36 for _ in range(36)]
#     for i, x in enumerate(XY):
#         for j, y in enumerate(XY):
#             rect[i][j] = tv.create_rectangle(x - R, y - R, x + R, y + R, tags=('imgButton1'))
#             tv.itemconfig(rect[i][j], fill='lightgray', outline='lightgray')
#     tv.tag_bind('imgButton1', '<Button-1>', on_Click)


def drawLifes():
    global Life
    Life.runningSpeed = speedScale.get()  # 获取滑块的当前值
    # 其他代码不变
    R, XY = 8, [50 + i * 20 for i in range(36)]
    if Life.running:
        for i, x in enumerate(XY):
            for j, y in enumerate(XY):
                if Life.items[i + 1][j + 1]:
                    tv.itemconfig(rect[i][j], fill='green', outline='green')
                else:
                    tv.itemconfig(rect[i][j], fill='lightgray', outline='lightgray')
        tv.update()
        Life.reproduce()
        if Life.is_stable():
            Life.running = False
            if sum(sum(Life.items, [])):
                msgbox.showinfo('Message', '生命繁殖与湮灭进入稳定状态！！！')
            else:
                msgbox.showinfo('Message', '生命全部湮灭，进入死亡状态！！！')
    win.after(Life.runningSpeed, drawLifes)  # 将滑块的当前值作为延迟参数


# def drawLifes():
#     R, XY = 8, [50 + i * 20 for i in range(36)]
#     if Life.running:
#         for i, x in enumerate(XY):
#             for j, y in enumerate(XY):
#                 if Life.items[i + 1][j + 1]:
#                     tv.itemconfig(rect[i][j], fill='green', outline='green')
#                 else:
#                     tv.itemconfig(rect[i][j], fill='lightgray', outline='lightgray')
#         tv.update()
#         Life.reproduce()
#         if Life.is_stable():
#             Life.running = False
#             if sum(sum(Life.items, [])):
#                 msgbox.showinfo('Message', '生命繁殖与湮灭进入稳定状态！！！')
#             else:
#                 msgbox.showinfo('Message', '生命全部湮灭，进入死亡状态！！！')
#     win.after(Life.runningSpeed, drawLifes)


def StartLife():
    if sum(sum(Life.items, [])):
        Life.histroy = []
        Life.running = True
    else:
        msgbox.showinfo('Message', '请点击小方块填入生命细胞，或者使用随机功能！')


def BreakLife():
    Life.running = not Life.running
    if Life.running:
        Life.histroy.clear()
        Life.add_histroy()


def RandomLife():
    Life.rndinit()
    Life.running = True


def ClearLife():
    Life.running = False
    Life.histroy = []
    Life.items = [[0] * 38 for _ in range(38)]
    for x in range(36):
        for y in range(36):
            tv.itemconfig(rect[x][y], fill='lightgray', outline='lightgray')


def btnCommand(i):
    if i == 0:
        return StartLife
    elif i == 1:
        return BreakLife
    elif i == 2:
        return RandomLife
    elif i == 3:
        return ClearLife


def on_Enter(event):
    tCanvas.itemconfig(tVisit, fill='magenta')


def on_Leave(event):
    tCanvas.itemconfig(tVisit, fill='blue')


def on_Release(event):
    url = 'https://blog.csdn.net/boysoft2002?type=blog'
    webbrowser.open(url, new=0, autoraise=True)


def on_Click(event):
    x, y = (event.x - 40) // 20, (event.y - 40) // 20
    if not Life.running:
        if Life.items[x + 1][y + 1]:
            tv.itemconfig(rect[x][y], fill='lightgray', outline='lightgray')
        else:
            tv.itemconfig(rect[x][y], fill='red', outline='red')
        Life.items[x + 1][y + 1] = not Life.items[x + 1][y + 1]


def on_Close():
    if msgbox.askokcancel("Quit", "Do you want to quit?"):
        Life.running = False
        print(Copyright())
        win.destroy()


def Introduce():
    txt = '''【生命游戏】\n\n生存定律：
    (1)当前细胞为湮灭状态时，当周围有３个存活细胞时，则迭代后该细胞变成存活状态(模拟繁殖)。
    (2)当前细胞为存活状态时，当周围的邻居细胞少于２个存活时，该细胞变成湮灭状态(数量稀少)。
    (3)当前细胞为存活状态时，当周围有３个以上的存活细胞时，该细胞变成湮灭状态(数量过多)。
    (4)当前细胞为存活状态时，当周围有２个或３个存活细胞时，该细胞保持原样。'''
    return txt


def Copyright():
    return 'Lifes Game Ver1.0\nWritten by HannYang, 2022/08/01.'


if __name__ == '__main__':

    win = tk.Tk()
    X, Y = win.maxsize()
    W, H = 1024, 800
    winPos = f'{W}x{H}+{(X - W) // 2}+{(Y - H) // 2}'
    win.geometry(winPos)
    win.resizable(False, False)
    win.title('生命游戏 Ver1.0')
    win.update()
    drawCanvas()
    Life = Lifes()
    drawLifes()

    tLabel = tk.Label(win, width=30, height=20, background='lightgray')
    tLabel.place(x=780, y=38)
    tLabel.config(text='\n\n\n'.join((Introduce(), Copyright())))
    tLabel.config(justify=tk.LEFT, anchor="nw", borderwidth=10, wraplength=210)

    tButton = [None] * 4
    bX, bY, dY = 835, 458, 50
    txt = ['开始', '暂停', '随机', '清空']
    for i in range(4):
        tButton[i] = tk.Button(win, text=txt[i], command=btnCommand(i))
        tButton[i].place(x=bX, y=bY + dY * i, width=120, height=40)

    tCanvas = tk.Canvas(win, width=200, height=45)
    tCanvas.place(x=800, y=716)
    tVisit = tCanvas.create_text((88, 22), text=u"点此访问Hann's CSDN主页!")
    tCanvas.itemconfig(tVisit, fill='blue', tags=('btnText'))
    tCanvas.tag_bind('btnText', '<Enter>', on_Enter)
    tCanvas.tag_bind('btnText', '<Leave>', on_Leave)
    tCanvas.tag_bind('btnText', '<ButtonRelease-1>', on_Release)
    win.protocol("WM_DELETE_WINDOW", on_Close)
    win.mainloop()
