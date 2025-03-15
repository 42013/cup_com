from tkinter import messagebox as msgbox
import tkinter as tk
import webbrowser
import random

ROW = 38
entry = 10


class Lifes:
    def __init__(self, rows=ROW, cols=ROW):
        self.row = rows + 2
        self.col = cols + 2
        self.items = [[0] * self.col for _ in range(self.row)]
        self.histroy = []
        self.histroySize = 30
        self.running = False
        self.runningSpeed = 200
        self.iterations = 0  # 迭代次数

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
    speedScale.place(x=880, y=700)


# 40方格数目
def drawCanvas():
    global tv, rect
    tv = tk.Canvas(win, width=win.winfo_width(), height=win.winfo_height())
    tv.pack(side="top")
    for i in range(ROW):  # Change the range to 40
        coord = ROW, ROW, 20 * ROW + 40, i * 20 + 40  # Adjust the coordinates for a 40x40 grid
        tv.create_rectangle(coord)
        coord = ROW, ROW, i * 20 + 40, 20 * ROW + 40  # Adjust the coordinates for a 40x40 grid
        tv.create_rectangle(coord)
    coord = ROW, ROW, 20 * ROW + 40, 20 * ROW + 40
    tv.create_rectangle(coord, width=2)
    coord = ROW + 1, ROW + 1, 20 * ROW + 40, 20 * ROW + 40
    tv.create_rectangle(coord, width=2)
    coord = ROW, ROW, 20 * ROW + 42, 20 * ROW + 42
    tv.create_rectangle(coord, width=2)
    R, XY = 8, [50 + i * 20 for i in range(ROW)]  # Adjust the range to 40
    rect = [[0] * ROW for _ in range(ROW)]  # Change the range to 40
    for i, x in enumerate(XY):
        for j, y in enumerate(XY):
            rect[i][j] = tv.create_rectangle(x - R, y - R, x + R, y + R, tags=('imgButton1'))
            tv.itemconfig(rect[i][j], fill='lightgray', outline='lightgray')
    tv.tag_bind('imgButton1', '<Button-1>', on_Click)
    drawSpeedSlider()


# 40方格数目
def drawLifes():
    global Life, iterationLabel
    Life.runningSpeed = speedScale.get()  # 获取滑块的当前值
    # 其他代码不变
    R, XY = 8, [50 + i * 20 for i in range(ROW)]
    if Life.running:
        for i, x in enumerate(XY):
            for j, y in enumerate(XY):
                if Life.items[i + 1][j + 1]:
                    tv.itemconfig(rect[i][j], fill='green', outline='green')
                else:
                    tv.itemconfig(rect[i][j], fill='lightgray', outline='lightgray')
        tv.update()
        Life.iterations += 1  # 每次迭代增加迭代次数
        iterationLabel.config(text=f'迭代次数: {Life.iterations}')
        Life.reproduce()
        if Life.is_stable():
            Life.running = False
            if sum(sum(Life.items, [])):
                msgbox.showinfo('Message', '生命繁殖与湮灭进入稳定状态！！！')
            else:
                msgbox.showinfo('Message', '生命全部湮灭，进入死亡状态！！！')
    win.after(Life.runningSpeed, drawLifes)  # 将滑块的当前值作为延迟参数


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
    Life.items = [[0] * (ROW + 2) for _ in range(ROW + 2)]  # 40方格数目 # items=方格加二
    for x in range(ROW):
        for y in range(ROW):
            tv.itemconfig(rect[x][y], fill='lightgray', outline='lightgray')
    Life.iterations = 0  # 清零迭代次数
    iterationLabel.config(text=f'迭代次数: {Life.iterations}')  # 更新迭代次数显示


def btnCommand(i):
    if i == 1:
        return StartLife
    elif i == 2:
        return BreakLife
    elif i == 3:
        return RandomLife
    elif i == 4:
        return ClearLife

def on_Enter(event):
    tCanvas.itemconfig(tVisit, fill='magenta')


def on_Leave(event):
    tCanvas.itemconfig(tVisit, fill='blue')


def on_Release(event):
    url = 'https://cup-2cq.pages.dev/'
    webbrowser.open(url, new=0, autoraise=True)


# 40方格数目+4 点击事件接受
def on_Click(event):
    x, y = (event.x - ROW - 4) // 20, (event.y - ROW - 4) // 20
    if not Life.running:
        if Life.items[x + 1][y + 1]:
            tv.itemconfig(rect[x][y], fill='lightgray', outline='lightgray')
        else:
            tv.itemconfig(rect[x][y], fill='red', outline='red')
        Life.items[x + 1][y + 1] = not Life.items[x + 1][y + 1]


def on_Close():
    if msgbox.askokcancel("退出", "请选是或否"):
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
    return 'Lifes Game Ver2.0\nWritten by rwr,2024/5/3.'

def Button_event():
    tButton = [None] * 5
    bX, bY, dY = 880, 500, 40
    txt = ['修改', '开始', '暂停', '随机', '清空']
    for i in range(5):
        tButton[i] = tk.Button(win, text=txt[i], command=btnCommand(i))
        tButton[i].place(x=bX, y=bY + dY * i, width=100, height=30)

if __name__ == '__main__':

    win = tk.Tk()
    X, Y = win.maxsize()
    W, H = 1200, 880
    winPos = f'{W}x{H}+{(X - W) // 2}+{(Y - H) // 2}'
    win.geometry(winPos)
    win.resizable(False, False)
    win.title('生命游戏 测试')
    win.iconbitmap("D:\\Word_detect\\life.ico")

    win.update()
    drawCanvas()
    Life = Lifes()
    drawLifes()
    tLabel = tk.Label(win, width=30, height=20, background='#FF0000')
    tLabel.place(x=880, y=38)
    tLabel.config(text='\n\n\n'.join((Introduce(), Copyright())))
    tLabel.config(justify=tk.LEFT, anchor="nw", borderwidth=10, wraplength=210)

    Button_event()

    tCanvas = tk.Canvas(win, width=200, height=45)
    tCanvas.place(x=880, y=770)
    iterationLabel = tk.Label(win, text=f'迭代次数: {Life.iterations}')
    iterationLabel.place(x=880, y=840)
    tVisit = tCanvas.create_text((88, 22), text=u"点此访问robocup主页!")
    tCanvas.itemconfig(tVisit, fill='blue', tags=('btnText'))
    tCanvas.tag_bind('btnText', '<Enter>', on_Enter)
    tCanvas.tag_bind('btnText', '<Leave>', on_Leave)
    tCanvas.tag_bind('btnText', '<ButtonRelease-1>', on_Release)
    win.protocol("WM_DELETE_WINDOW", on_Close)
    win.mainloop()
