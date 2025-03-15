import time
import threading
import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
import serial.tools.list_ports
import serial
import xml.etree.ElementTree as ET
import os

global ser
listener_thread = None
stop_thread = threading.Event()

# 初始化主窗口
root = tk.Tk()
root.title("cup-com v_1.0")
root.geometry("800x600")
style = ttk.Style()
style.configure("Red.TButton", foreground="blue", background="red")


def get_ports():
    return [port.device for port in serial.tools.list_ports.comports()]


def save_settings():
    root = ET.Element("Settings")
    ET.SubElement(root, "BaudRate").text = combo2.get()
    ET.SubElement(root, "EncodingMode").text = combo3.get()
    ET.SubElement(root, "stop_mode").text = combo4.get()
    ET.SubElement(root, "ParityMode").text = combo5.get()
    tree = ET.ElementTree(root)
    tree.write("settings.xml")


def load_settings():
    if os.path.exists("settings.xml") and os.path.getsize("settings.xml") > 0:
        tree = ET.parse("settings.xml")
        root = tree.getroot()
        combo2.set(root.find("BaudRate").text)
        combo3.set(root.find("EncodingMode").text)
        stop_mode = root.find("stop_mode")
        if stop_mode is not None:
            combo4.set(stop_mode.text)
        parity_mode = root.find("ParityMode")
        if parity_mode is not None:
            combo5.set(parity_mode.text)


ports = get_ports()
RateTypes = [1200, 2400, 4800, 9600, 115200, 19200, 38400, 56000, 57600, 128000, 256000]
text_Types = ['GBK', 'GB2312', 'utf-8']
stop_bits = [1, 2]
parity_types = ["NONE", "EVEN", "ODD", "MARK", "SPACE"]

# 创建下拉列表框
frame1 = ttk.LabelFrame(root, text="串口选择")
frame1.place(x=600, y=10, width=140, height=60)
combo1 = ttk.Combobox(frame1, values=ports)
combo1.place(x=10, y=10, width=100, height=20)

frame2 = ttk.LabelFrame(root, text="波特率")
frame2.place(x=600, y=80, width=140, height=60)
combo2 = ttk.Combobox(frame2, values=RateTypes)
combo2.place(x=10, y=10, width=100, height=20)

frame3 = ttk.LabelFrame(root, text="文本编码格式")
frame3.place(x=600, y=400, width=180, height=60)
combo3 = ttk.Combobox(frame3, values=text_Types)
combo3.place(x=10, y=10, width=140, height=20)

label_stop_bits = ttk.Label(text="停止位")
label_stop_bits.place(x=600, y=160, width=40, height=20)
combo4 = ttk.Combobox(values=stop_bits)
combo4.place(x=650, y=160, width=70, height=20)

label_parity = ttk.Label(text="校验位")
label_parity.place(x=600, y=200, width=40, height=20)
combo5 = ttk.Combobox(values=parity_types)
combo5.place(x=650, y=200, width=70, height=20)

# 创建勾选框
hex_mode_send = tk.BooleanVar()
hex_mode_receive = tk.BooleanVar()
Line_breaks = tk.BooleanVar()
send_cl = tk.BooleanVar()
receive_cl = tk.BooleanVar()


def clear_sends():
    send_textbox.delete("1.0", tk.END)


def clear_receives():
    receive_textbox.delete("1.0", tk.END)


clear_send = tk.Checkbutton(root, text="清除发送", variable=send_cl, command=clear_sends)
clear_send.place(x=600, y=500)
clear_receive = tk.Checkbutton(root, text="清除接收", variable=receive_cl, command=clear_receives)
clear_receive.place(x=600, y=300)

checkbutton2 = tk.Checkbutton(root, text="Hex 模式显示", variable=hex_mode_receive, command=save_settings)
checkbutton2.place(x=600, y=340)

checkbutton3 = tk.Checkbutton(root, text="发送新行", variable=Line_breaks, command=save_settings)
checkbutton3.place(x=600, y=520)

checkbutton1 = tk.Checkbutton(root, text="Hex 模式发送", variable=hex_mode_send, command=save_settings)
checkbutton1.place(x=600, y=550)


def send_packet(ser0, data):
    ser0.write(data)
    time.sleep(0.02)  # 添加延时，以确保 STM32 单片机能够正确接收


def open_button_action():
    global ser, listener_thread, stop_thread
    selected_option = combo1.get()
    selected_choice = combo2.get()
    stop_bits_choice = combo4.get()
    parity_choice = combo5.get()

    if not selected_option:
        ports = get_ports()
        if ports:
            selected_option = ports[0]
        else:
            receive_textbox.insert(tk.END, "未找到串口\n")
            return

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
                baudrate=int(selected_choice) if selected_choice else 38400,
                bytesize=8,
                stopbits=int(stop_bits_choice) if stop_bits_choice else 1,
                parity=parity_mapping[parity_choice] if parity_choice else serial.PARITY_NONE,
                timeout=0.05
            )
            stop_thread.clear()
            listener_thread = threading.Thread(target=listen_serial, daemon=True)
            listener_thread.start()
            open_button.config(text="串口关闭", style="Red.TButton")
        except Exception as e:
            receive_textbox.delete("1.0", tk.END)
            receive_textbox.insert(tk.END, f"Error: {e}")
    else:
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
            if Line_breaks.get():
                message += "\r\n"
            ms = message.encode(selected)
            send_packet(ser, ms)
        else:
            receive_textbox.insert(tk.END, "\n请选择文本编码")
            return


# 创建按钮
send_button = ttk.Button(root, text="发送", command=lambda: [send_button_action(), save_settings()])
send_button.place(x=610, y=460, width=100, height=30)

open_button = ttk.Button(root, text="串口打开", command=lambda: [open_button_action(), save_settings()])
open_button.place(x=610, y=240, width=100, height=30)

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
                        receive_textbox.insert(tk.END, "请选择文本编码\n")
                        return
                    try:
                        formatted_data = data.decode(selected)
                    except UnicodeDecodeError:
                        formatted_data = f"解码错误: {data}"
                receive_textbox.insert(tk.END, formatted_data + "\n")
        time.sleep(0.1)  # 降低 CPU 占用率


# 蓝牙配置功能
def configure_bluetooth():
    ser = serial.Serial(
        ports[0],
        baudrate=38400,
        bytesize=8,
        stopbits=1,
        parity=serial.PARITY_NONE,
        timeout=0.05
    )
    config_window = tk.Toplevel(root)
    config_window.title("蓝牙配置")
    config_window.geometry("300x400")

    role_var = tk.StringVar(value="0")
    password_var = tk.StringVar(value="1234")
    name_var = tk.StringVar(value="20")
    bit_var = tk.IntVar()
    bind_var = tk.StringVar()

    ttk.Label(config_window, text="主从模式 (1: 主, 0: 从):").pack(pady=5)
    ttk.Entry(config_window, textvariable=role_var).pack(pady=5)

    ttk.Label(config_window, text="密码:").pack(pady=5)
    ttk.Entry(config_window, textvariable=password_var).pack(pady=5)

    ttk.Label(config_window, text="名字:").pack(pady=5)
    ttk.Entry(config_window, textvariable=name_var).pack(pady=5)

    ttk.Label(config_window, text="蓝牙波特率:").pack(pady=5)
    ttk.Entry(config_window, textvariable=bit_var).pack(pady=5)

    ttk.Label(config_window, text="绑定主机蓝牙地址 (可选):").pack(pady=5)
    ttk.Entry(config_window, textvariable=bind_var).pack(pady=5)



    def apply_bluetooth_config():
        role = role_var.get()
        password = password_var.get()
        name = name_var.get()
        bits = bit_var.get()
        bind_address = bind_var.get()

        if ser and ser.is_open:
            commands = [
                f"AT+ROLE={role}\r\n",
                f"AT+PSWD=\"{password}\"\r\n",
                f"AT+NAME={name}\r\n",
                f"AT+UART={bits},0,0\r\n"
            ]
            if bind_address:
                commands.append(f"AT+BIND={bind_address}\r\n")
            commands.append("AT+ADDR?\r\n")

            for cmd in commands:
                ser.write(cmd.encode('GBK'))
                time.sleep(0.1)
                response = ser.readline().decode('GBK').strip()
                receive_textbox.insert(tk.END, f"Sent: {cmd.strip()}\nReceived: {response}\n")

        config_window.destroy()

    ttk.Button(config_window, text="应用", command=apply_bluetooth_config).pack(pady=20)


# 添加蓝牙配置按钮
bluetooth_button = ttk.Button(root, text="配置蓝牙", command=configure_bluetooth)
bluetooth_button.place(x=610, y=270, width=100, height=30)

root.mainloop()
