import os
import time
import serial
import threading
import tkinter as tk
import serial.tools.list_ports
import xml.etree.ElementTree as ET
from tkinter import ttk, simpledialog, messagebox

global ser
global sending
listener_thread = None
stop_thread = threading.Event()

# 初始化主窗口
root = tk.Tk()
style = ttk.Style()
root.geometry("800x600")
root.title("cup-com v_1.0")
style.configure("Red.TButton", foreground="blue", background="red")


def get_ports():
    return [port.device for port in serial.tools.list_ports.comports()]


def save_settings():
    root = ET.Element("Settings")
    baud_rate = ET.SubElement(root, "BaudRate")
    baud_rate.text = combo2.get()
    encoding_mode = ET.SubElement(root, "EncodingMode")
    encoding_mode.text = combo3.get()
    stop_mode = ET.SubElement(root, "stop_mode")
    stop_mode.text = combo4.get()
    parity_mode = ET.SubElement(root, "ParityMode")
    parity_mode.text = combo5.get()

    tree = ET.ElementTree(root)
    tree.write("settings.xml")


# Function to load default settings from XML
def load_settings():
    global combo3
    global combo2
    try:
        if os.path.exists("settings.xml") and os.path.getsize("settings.xml") > 0:
            tree = ET.parse("settings.xml")
            root = tree.getroot()
            baud_rate = root.find("BaudRate").text
            encoding_mode = root.find("EncodingMode").text
            stop_mode = root.find("stop_mode")
            parity_mode = root.find("ParityMode")

            combo2.set(baud_rate)
            combo3.set(encoding_mode)
            combo4.set(stop_mode.text)
            combo5.set(parity_mode.text)
    except FileNotFoundError:
        pass  # No settings file found, use defaults


ports = get_ports()
RateTypes = [1200, 2400, 4800, 9600, 115200, 19200, 38400, 56000, 57600, 128000, 256000]
text_Types = ['GBK', 'GB2312', 'utf-8']
stop_bits = [1, 2]
parity_types = ["NONE", "EVEN", "ODD", "MARK", "SPACE"]
standard_x = 600
# 创建下拉列表框
frame1 = ttk.LabelFrame(root, text="串口选择")
frame1.place(x=standard_x, y=10, width=140, height=60)

combo1 = ttk.Combobox(frame1, values=ports)
combo1.place(x=10, y=10, width=100, height=20)

frame2 = ttk.LabelFrame(root, text="波特率")
frame2.place(x=standard_x, y=80, width=140, height=60)

combo2 = ttk.Combobox(frame2, values=RateTypes)
combo2.place(x=10, y=10, width=100, height=20)

frame3 = ttk.LabelFrame(root, text="文本编码格式")
frame3.place(x=standard_x, y=400, width=180, height=60)

combo3 = ttk.Combobox(frame3, values=text_Types)
combo3.place(x=10, y=10, width=140, height=20)

label_stop_bits = ttk.Label(text="停止位")
label_stop_bits.place(x=standard_x, y=160, width=40, height=20)

combo4 = ttk.Combobox(values=stop_bits)
combo4.place(x=650, y=160, width=70, height=20)

label_parity = ttk.Label(text="校验位")
label_parity.place(x=standard_x, y=200, width=40, height=20)

combo5 = ttk.Combobox(values=parity_types)
combo5.place(x=650, y=200, width=70, height=20)

# 创建勾选框
hex_mode_send = tk.BooleanVar()
hex_mode_receive = tk.BooleanVar()
Line_breaks = tk.BooleanVar()
send_cl = tk.BooleanVar()
receive_cl = tk.BooleanVar()


def on_hex_mode_selected():
    if hex_mode_send.get():
        hex_mode_send.set(True)
        save_settings()
    else:
        hex_mode_send.set(False)
        save_settings()


def on_hex_mode_selected2():
    if hex_mode_receive.get():
        hex_mode_send.set(True)
        save_settings()
    else:
        hex_mode_receive.set(False)
        save_settings()


def Line_break():
    if Line_breaks.get():
        Line_breaks.set(True)
        save_settings()
    else:
        Line_breaks.set(False)
        save_settings()


def clear_sends():
    send_textbox.delete("1.0", tk.END)


def clear_receives():
    receive_textbox.delete("1.0", tk.END)


clear_send = tk.Checkbutton(root, text="清除发送", variable=send_cl, command=clear_sends)
clear_send.place(x=standard_x, y=490)
clear_receive = tk.Checkbutton(root, text="清除接收", variable=receive_cl, command=clear_receives)
clear_receive.place(x=standard_x, y=280)

checkbutton2 = tk.Checkbutton(root, text="Hex 模式显示", variable=hex_mode_receive,
                              command=lambda: [on_hex_mode_selected2(), save_settings()])
checkbutton2.place(x=standard_x, y=320)

checkbutton3 = tk.Checkbutton(root, text="发送新行", variable=Line_breaks,
                              command=lambda: [Line_break(), save_settings()])
checkbutton3.place(x=standard_x, y=520)

checkbutton1 = tk.Checkbutton(root, text="Hex 模式发送", variable=hex_mode_send,
                              command=lambda: [on_hex_mode_selected(), save_settings()])
checkbutton1.place(x=standard_x, y=550)


def recv(ser0):
    while True:
        data = ser0.read_all()
        if data == '':
            continue
        else:
            break
    return data


def send_packet(ser0, data):
    ser0.write(data)
    time.sleep(0.02)  # 添加延时，以确保 STM32 单片机能够正确接收


# 打开按钮的功能
def open_button_action():
    global ser, listener_thread, stop_thread
    selected_option = combo1.get()
    selected_choice = combo2.get()
    stop_bits_choice = combo4.get()
    parity_choice = combo5.get()

    parity_mapping = {
        "NONE": serial.PARITY_NONE,
        "EVEN": serial.PARITY_EVEN,
        "ODD": serial.PARITY_ODD,
        "MARK": serial.PARITY_MARK,
        "SPACE": serial.PARITY_SPACE
    }

    if open_button.cget("text") == "串口打开":
        try:
            ser = serial.Serial(
                selected_option,
                baudrate=int(selected_choice),
                bytesize=8,
                stopbits=int(stop_bits_choice),
                parity=parity_mapping[parity_choice],
                timeout=0.05
            )
            stop_thread.clear()
            listener_thread = threading.Thread(target=listen_serial, daemon=True)
            listener_thread.start()
            open_button.config(text="串口关闭", style="Red.TButton")
        except Exception as e:
            receive_textbox.delete("1.0", tk.END)
            receive_textbox.insert(tk.END, f"Error: {e}")
    elif open_button.cget("text") == "串口关闭":
        stop_thread.set()
        ser.close()
        open_button.config(text="串口打开", style="TButton")


def send_button_action():
    selected = combo3.get()
    message = send_textbox.get("1.0", tk.END).strip()
    if hex_mode_send.get():
        try:
            data = int(message)
            if data > 255:
                receive_textbox.insert(tk.END, "\n无效字节输入: 字节在0-255之间")
                return
            hex_data = bytes([data])
            send_packet(ser, hex_data)
        except ValueError:
            receive_textbox.insert(tk.END, "格式不符，本软件文本与其他串口助手不同，不会强转字节发送\n")
            return
    else:
        if selected:
            if Line_breaks.get():  # Use get() to retrieve the value of Line_breaks
                message += "\r\n"  # Add "\r\n" if Line_breaks is checked
            ms = message.encode(selected)
            send_packet(ser, ms)
        else:
            receive_textbox.insert(tk.END, "\n请选择文本编码")
            return


# 创建按钮
send_button = ttk.Button(root, text="发送", command=lambda: [send_button_action(), save_settings()])
send_button.place(x=standard_x+10, y=460, width=100, height=30)

open_button = ttk.Button(root, text="串口打开", command=lambda: [open_button_action(), save_settings()])
open_button.place(x=standard_x+10, y=240, width=100, height=30)

# 创建接收文本框和滚动条
receive_frame = ttk.Frame(root)
receive_frame.place(x=20, y=10, width=550, height=320)

receive_scrollbar = tk.Scrollbar(receive_frame)
receive_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

receive_textbox = tk.Text(receive_frame, height=15, width=550, yscrollcommand=receive_scrollbar.set)
receive_textbox.pack(side=tk.LEFT, fill=tk.BOTH)

receive_scrollbar.config(command=receive_textbox.yview)

# 创建发送文本框
send_textbox = tk.Text(root, height=15, width=60)
send_textbox.place(x=20, y=400, width=570, height=170)
send_textbox.insert(tk.END, "本串口为学习测试用，如有问题，请发送详情至个人邮箱3109613603@qq.com")

if os.path.exists("settings.xml") and os.path.getsize("settings.xml") > 0:
    load_settings()


def listen_serial():
    global ser
    while not stop_thread.is_set():
        selected = combo3.get()
        if ser.is_open:
            data = ser.read_all()
            if data:
                if hex_mode_receive.get():
                    formatted_data = ' '.join(f'{byte:02x}' for byte in data)
                else:
                    if selected is None:
                        receive_textbox.insert(tk.END, "\n请选择文本编码格式")
                        return
                    formatted_data = data.decode(selected, errors='replace')
                receive_textbox.insert(tk.END, f"\n{formatted_data}")
                receive_textbox.see(tk.END)  # 自动滚动到最后


def update_ports():
    current_ports = get_ports()
    if current_ports != combo1['values']:
        combo1['values'] = current_ports
        if combo1.get() not in current_ports:
            combo1.set('')  # 清除当前选择，如果它已经不存在
    root.after(500, update_ports)  # 每秒更新一次


def bluetooth_config():
    ser = serial.Serial(
        ports[0],
        baudrate=38400,
        bytesize=8,
        stopbits=1,
        parity=serial.PARITY_NONE,
        timeout=0.05
    )
    role = simpledialog.askinteger("蓝牙配置", "输入主从机模式（0为从机，1为主机）:")
    password = simpledialog.askstring("蓝牙配置", "输入蓝牙密码:")
    name = simpledialog.askstring("蓝牙配置", "输入蓝牙代号:")
    bits = simpledialog.askstring("蓝牙配置", "输入蓝牙波特率:")

    if role == 0:
        bind_address = messagebox.askyesno("蓝牙配置", "从机设置：是否连接主机蓝牙?")
        if bind_address:
            bind_address = simpledialog.askstring("蓝牙配置", "输入主机蓝牙地址:")

    # 发送AT指令到蓝牙模块 每条之间添加延时以确保蓝牙模块正确
    if ser.is_open:
        ser.write(f"AT+ROLE={role}\r\n".encode('GBK'))
        time.sleep(0.02)
        ser.write(f"AT+PSWD=\"{password}\"\r\n".encode('GBK'))
        time.sleep(0.02)
        ser.write(f"AT+NAME={name}\r\n".encode('GBK'))
        time.sleep(0.02)
        ser.write(f"AT+UART={int(bits)},0,0\r\n".encode('GBK'))
        time.sleep(0.02)
        ser.write(f"AT+ADDR?\r\n".encode('GBK'))
        time.sleep(0.02)
        if role == 0 and bind_address:
            ser.write(f"AT+BIND={bind_address}\r\n".encode('GBK'))
            time.sleep(0.02)


# 创建蓝牙配置按钮
# bluetooth_button = ttk.Button(root, text="蓝牙配置", command=bluetooth_config)
# bluetooth_button.place(x=standard_x+10, y=360, width=100, height=30)

# 启动端口更新
root.after(500, update_ports)

# 运行主循环
root.mainloop()
