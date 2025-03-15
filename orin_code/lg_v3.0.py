import tkinter as tk
from tkinter import messagebox as msgbox
import webbrowser
import random

# Pyinstaller -F -i life.ico lg_v3.0.py
# pyi-makespec -F -i life.ico  name.py
# Pyinstaller lg_v3.0.spec
class Lifes:
    def __init__(self, rows=10, cols=10):
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


def drawCanvas(rows):
    global tv, rect, ROW, Life
    ROW = rows
    if 'tv' in globals():
        tv.destroy()
    canvas_width = 20 * rows + 40
    canvas_height = 20 * rows + 40
    tv = tk.Canvas(win, width=canvas_width, height=canvas_height)  # 根据行数调整画布大小
    tv.place(x=20, y=20)  # Place the canvas in the top left corner of the window

    # Calculate the size of individual cells
    cell_size = min(canvas_width // (rows + 2), canvas_height // (rows + 2))

    for i in range(rows + 1):
        # Draw horizontal lines
        x0 = cell_size
        y0 = i * cell_size + cell_size
        x1 = canvas_width - cell_size
        y1 = i * cell_size + cell_size
        tv.create_line(x0, y0, x1, y1)

        # Draw vertical lines
        x0 = i * cell_size + cell_size
        y0 = cell_size
        x1 = i * cell_size + cell_size
        y1 = canvas_height - cell_size
        tv.create_line(x0, y0, x1, y1)

    # Draw outer rectangle
    tv.create_rectangle(cell_size, cell_size, canvas_width - cell_size, canvas_height - cell_size, width=2)

    R = 8
    rect = []
    for i in range(rows):
        row_rect = []
        for j in range(rows):
            x = (j + 1) * cell_size + cell_size // 2
            y = (i + 1) * cell_size + cell_size // 2
            rect_id = tv.create_rectangle(x - R, y - R, x + R, y + R, tags=('imgButton1'))
            tv.itemconfig(rect_id, fill='lightgray', outline='lightgray')
            row_rect.append(rect_id)
        rect.append(row_rect)

    tv.tag_bind('imgButton1', '<Button-1>', on_Click)
    drawSpeedSlider()


# 绘制生命状态
def drawLifes():
    global Life, iterationLabel
    Life.runningSpeed = speedScale.get()  # 获取滑块的当前值
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
    global rows_entry, Life
    rows = int(rows_entry.get())  # 获取行数输入框的值
    Life = Lifes(rows, rows)  # 创建 Lifes 实例时传入行数作为参数
    drawCanvas(rows)  # 绘制画布


def StartLife0():
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
    global Life
    Life.running = False
    Life.histroy = []
    Life.items = [[0] * (ROW + 2) for _ in range(ROW + 2)]  # 40方格数目 # items=方格加二
    for x in range(ROW):
        for y in range(ROW):
            tv.itemconfig(rect[x][y], fill='lightgray', outline='lightgray')
    Life.iterations = 0  # 清零迭代次数
    iterationLabel.config(text=f'迭代次数: {Life.iterations}')  # 更新迭代次数显示


def btnCommand(i):
    if i == 0:
        return StartLife0
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
    url = 'https://cup-2cq.pages.dev/'
    webbrowser.open(url, new=0, autoraise=True)


# 点击事件接受
def on_Click(event):
    canvas_width = 20 * ROW + 40
    canvas_height = 20 * ROW + 40
    cell_size = min(canvas_width // (ROW + 2), canvas_height // (ROW + 2))

    x, y = (event.x - 20) // cell_size, (event.y - 20) // cell_size
    if 0 <= x < ROW and 0 <= y < ROW:
        if not Life.running:
            if Life.items[y + 1][x + 1]:
                tv.itemconfig(rect[y][x], fill='lightgray', outline='lightgray')
            else:
                tv.itemconfig(rect[y][x], fill='red', outline='red')
            Life.items[y + 1][x + 1] = not Life.items[y + 1][x + 1]


def on_Close():
    if msgbox.askokcancel("退出", "请选择"):
        Life.running = False
        print(Copyright())
        win.destroy()


def Introduce():
    txt = '''【生命游戏】\n\n生存定律：
    (1)当前细胞为湮灭状态时，周围有３个存活细胞时，则迭代后该细胞变成存活状态(模拟繁殖)。
    (2)当前细胞为存活状态时，周围的邻居细胞少于２个存活时，该细胞变成湮灭状态(数量稀少)。
    (3)当前细胞为存活状态时，周围有３个以上的存活细胞时，该细胞变成湮灭状态(数量过多)。
    (4)当前细胞为存活状态时，周围有２个或３个存活细胞时，该细胞保持原样。''
    (5)输入行数修改棋盘大小，范围10到40'''
    return txt


def Copyright():
    return 'Lifes Game Ver3.0\nWritten by rwr,2024/5/4.'


def Button_event():
    tButton = [None] * 4
    bX, bY, dY = 880, 540, 40  # Adjust the starting position of the buttons
    txt = ['开始', '暂停', '随机', '清空']
    for i in range(4):  # Skip the "Start" button
        tButton[i] = tk.Button(win, text=txt[i], command=btnCommand(i))
        tButton[i].place(x=bX, y=bY + dY * i, width=80, height=20)


if __name__ == '__main__':
    global win, rows_entry, iterationLabel, tCanvas, tVisit
    win = tk.Tk()
    X, Y = win.maxsize()
    W, H = 1200, 880
    winPos = f'{W}x{H}+0+0'  # 放置在左上角
    win.geometry(winPos)
    win.resizable(False, False)
    win.title('生命游戏 测试')
    start_button = tk.Button(win, text="修改", command=StartLife)
    start_button.place(x=880, y=470, width=100, height=30)  # Adjust the position of the Start button

    rows_entry = tk.Entry(win, width=10)
    rows_entry.place(x=880, y=430, width=100, height=30)
    # rows_entry.pack(pady=5)
    win.update()

    tLabel = tk.Label(win, width=30, height=20, background='gray')
    tLabel.place(x=900, y=38)
    tLabel.config(text='\n\n\n'.join((Introduce(), Copyright())))
    tLabel.config(justify=tk.LEFT, anchor="nw", borderwidth=20, wraplength=220)


    tCanvas = tk.Canvas(win, width=200, height=45)
    tCanvas.place(x=880, y=770)

    tVisit = tCanvas.create_text((88, 22), text=u"点此访问robocup主页!")
    tCanvas.tag_bind('btnText', '<Enter>', on_Enter)
    tCanvas.tag_bind('btnText', '<Leave>', on_Leave)
    tCanvas.tag_bind('btnText', '<ButtonRelease-1>', on_Release)

    win.protocol("WM_DELETE_WINDOW", on_Close)

    Button_event()
    iterationLabel = tk.Label(win, text='迭代次数: 0')
    iterationLabel.place(x=880, y=840)
    Life = Lifes()
    drawSpeedSlider()
    drawCanvas(10)  # 初始行数为 10
    drawLifes()

    win.mainloop()
