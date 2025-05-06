"""
**What Users Can Do**:
1. **Use for Personal and Non-Commercial Purposes:**  
   Users can download and use the Software for personal projects, non-commercial projects, or educational purposes, as long as it's not for profit or commercial gain.

2. **Incorporate into Larger Projects:**  
   Users can include the Software in larger projects, either public or private, but **with proper attribution** (e.g., crediting the original author, "ByteLightDev").

3. **Modify for Personal Use:**  
   Users can modify the Software for their own use within a larger project, as long as any modifications are clearly documented (e.g., note which parts were changed).

4. **Publicly Distribute:**  
   Users can distribute their projects that use the Software publicly, but **U must provide proper attribution** to the original author and include the required notice ("This project includes software developed by [ByteLightDev], © 2025...").

---

**What Users Can't Do:**
1. **Commercial Use Without Permission:**  
   Users cannot use the Software for commercial purposes (e.g., selling it, using it in a product sold for profit) without any **consent** from the Licensor.

2. **Resell or Sublicense the Software:**  
   Users cannot sell, lease, or sublicense the Software as a standalone product. The Software cannot be distributed as-is for a fee or bundled with another product for resale.

3. **Alter or Copy the Original Software (or parts of it) Without Permission:**  
   Users cannot modify the core form of the Software and then redistribute it as part of their project, unless U clearly state any changes made. Copying portions of the Software for redistribution or use in other projects **without the necessary modifications** is prohibited.

4. **Failing to Give Proper Attribution:**  
   If a user integrates the Software into any project that is shared or published, U must ensure the correct **attribution** notice is visible and readable, as specified in the agreement.

---

**How U Can Use the Software:**
**1. Permission for Commercial Use or Profit**  
If you want to use the Software for **commercial purposes** (e.g., selling a product that includes it or using it in a business), you **must get permission** from the Licensor.  

Alternatively, you can use the Software commercially **without prior permission** if you **credit "ByteLightDev" properly** by:  
- Displaying the **ByteLightDev logo** in your commercial content.  
- Ensuring the logo appears **clearly** in the video for **at least 3 seconds** in **HD quality** and is **easily visible** (not hidden or covered).  

© 2025 [ByteLightDev]
"""




from http.server import SimpleHTTPRequestHandler, HTTPServer
import socketserver
import logging
import socket
import http
import json
import io
import shutil
import subprocess
import os
import time
import random
import uuid
import inspect
import smtplib
from email.message import EmailMessage
import threading
import sys
import requests
import datetime
import re
import pyperclip
import tkinter as tk
import numpy as np
import sounddevice as sd
import string
import hashlib
import ast
import heapq
from functools import lru_cache
from collections import defaultdict
from difflib import get_close_matches
import platform
import ctypes
from urllib.request import urlopen
from base64 import b64encode
import hmac



def Easterbun():
    if check_internet_connection():
        def get_easter_date(year):
            a = year % 19
            b = year // 100
            c = year % 100
            d = b // 4
            e = b % 4
            f = (b + 8) // 25
            g = (b - f + 1) // 3
            h = (19 * a + b - d - g + 15) % 30
            i = c // 4
            k = c % 4
            l = (32 + 2 * e + 2 * i - h - k) % 7
            m = (a + 11 * h + 22 * l) // 451
            month = (h + l - 7 * m + 114) // 31
            day = ((h + l - 7 * m + 114) % 31) + 1
            return datetime.date(year, month, day)
        today = datetime.date.today()
        easter = get_easter_date(today.year)
        if today == easter:
            def get_screen_size():
                temp = tk.Tk()
                temp.withdraw()
                w, h = temp.winfo_screenwidth(), temp.winfo_screenheight()
                temp.destroy()
                return w, h
            screen_width, screen_height = get_screen_size()
            url = "https://raw.githubusercontent.com/GoodByeSyntax/GBSassets/main/Easter.png"
            with urlopen(url) as response:
                image_data = response.read()
            b64_data = b64encode(image_data)
            root = tk.Tk()
            root.overrideredirect(True)
            root.geometry(f"{screen_width}x{screen_height}+0+0")
            root.configure(bg='black')
            root.bind("<Escape>", lambda e: root.destroy())
            photo = tk.PhotoImage(data=b64_data)
            label = tk.Label(root, image=photo, bg='black')
            label.place(relx=0.5, rely=0.5, anchor='center')
            root.mainloop()
        else:print("Today is not Easter 🐰")
    else:print("No internet no bun!")
def Halloween():
    if check_internet_connection():
        today = datetime.date.today()
        if today.month == 10 and today.day == 31:
            def get_screen_size():
                temp = tk.Tk()
                temp.withdraw()
                w, h = temp.winfo_screenwidth(), temp.winfo_screenheight()
                temp.destroy()
                return w, h
            screen_width, screen_height = get_screen_size()
            url = "https://raw.githubusercontent.com/GoodByeSyntax/GBSassets/main/Halloween.png"
            with urlopen(url) as response:
                image_data = response.read()
            b64_data = b64encode(image_data)
            root = tk.Tk()
            root.overrideredirect(True)
            root.geometry(f"{screen_width}x{screen_height}+0+0")
            root.configure(bg='black')
            root.bind("<Escape>", lambda e: root.destroy())
            photo = tk.PhotoImage(data=b64_data)
            label = tk.Label(root, image=photo, bg='black')
            label.place(relx=0.5, rely=0.5, anchor='center')
            root.mainloop()
        else:print("It's not Halloween yet 🎃")
    else:print("No internet, no pumpkin! 👻")
def Valentine():
    if check_internet_connection():
        today = datetime.date.today()
        if today.month == 2 and today.day == 14:
            def get_screen_size():
                temp = tk.Tk()
                temp.withdraw()
                w, h = temp.winfo_screenwidth(), temp.winfo_screenheight()
                temp.destroy()
                return w, h
            screen_width, screen_height = get_screen_size()
            url = "https://raw.githubusercontent.com/GoodByeSyntax/GBSassets/main/Valentines%20Day.png"
            with urlopen(url) as response:
                image_data = response.read()
            b64_data = b64encode(image_data)
            root = tk.Tk()
            root.overrideredirect(True)
            root.geometry(f"{screen_width}x{screen_height}+0+0")
            root.configure(bg='black')
            root.bind("<Escape>", lambda e: root.destroy())
            photo = tk.PhotoImage(data=b64_data)
            label = tk.Label(root, image=photo, bg='black')
            label.place(relx=0.5, rely=0.5, anchor='center')
            root.mainloop()
        else: print("It's not Valentine's Day yet 💘")
    else:print("No internet, no love! 💔")
def Christmas():
    if check_internet_connection():
        today = datetime.date.today()
        if today.month == 12 and today.day == 25:
            def get_screen_size():
                temp = tk.Tk()
                temp.withdraw()
                w, h = temp.winfo_screenwidth(), temp.winfo_screenheight()
                temp.destroy()
                return w, h
            screen_width, screen_height = get_screen_size()
            url = "https://raw.githubusercontent.com/GoodByeSyntax/GBSassets/main/Christmas.png"
            with urlopen(url) as response:image_data = response.read()
            b64_data = b64encode(image_data)
            root = tk.Tk()
            root.overrideredirect(True)
            root.geometry(f"{screen_width}x{screen_height}+0+0")
            root.configure(bg='black')
            root.bind("<Escape>", lambda e: root.destroy())
            photo = tk.PhotoImage(data=b64_data)
            label = tk.Label(root, image=photo, bg='black')
            label.place(relx=0.5, rely=0.5, anchor='center')
            root.mainloop()
        else:print("It's not Christmas yet 🎅")
    else:print("No internet, no ho-ho-ho! ❄️")

def wait(key="s", num=1):
    if key.lower() == "s":
        time.sleep(num)
    elif key.lower() == "m":
        time.sleep(num * 60)
    elif key.lower() == "h":
        time.sleep(num * 3600)
    else:
        print("Error: Use 's' for seconds, 'm' for minutes, or 'h' for hours.")

def ifnull(value, default):
    return default if value is None or value == "" else value

def switch_case(key, cases, default=None):
    result = cases.get(key, default)
    return result() if callable(result) else result

def timer_function(func, seconds):
    time.sleep(seconds)
    func()

def iftrue(var, function):
    if var:
        function()

def iffalse(var, function):
    if not var:
        function()
        
def isequal(text,atext):
    if text.lower() == atext:return True
    else:return False

def until(function, whattodo):
    function()
    while True:
        whattodo()
        if function():break

def repeat(function, times):
    for _ in range(times):
        function()

def oncondit(condition, function_true, function_false):
    if condition:
        function_true()
    else:
        function_false()

def repeat_forever(function):
    while True:
        function()

def safe_run(func, *args, **kwargs):
    try:
        func(*args, **kwargs)
    except Exception as e:
        print(f"Error occurred in function {func.__name__}: {e}")
        return None

def start_timer(seconds, callback):
    time.sleep(seconds)
    callback()

def generate_random_string(length=15):
    characters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@/-*_'
    return ''.join(random.choices(characters, k=length))

def get_ip_address():
    return socket.gethostbyname(socket.gethostname())

def send_email(subject, body, to_email, mailname, mailpass):
    msg = EmailMessage()
    msg.set_content(body)
    msg["Subject"] = subject
    msg["From"] = mailname
    msg["To"] = to_email
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(mailname, mailpass)
            server.send_message(msg)
            print("Email sent successfully.")
    except Exception as e:
        print(f"Error sending email: {e}")

def generate_unique_id():
    return str(uuid.uuid4())

def start_background_task(backtask):
    thread = threading.Thread(target=backtask)
    thread.start()

def nocrash(func):
    def wrapper(*args, **kwargs):
        return safe_run(func, *args, **kwargs)
    return wrapper

def parallel(*functions):
    threads = []
    for func in functions:
        thread = threading.Thread(target=func)
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()

def gs(func):
    return inspect.getsource(func)

def Jctb(input_string):
    def char_to_binary(c):
        if c == ' ':
            return '0000000001'
        elif c == '\n':
            return '0000000010'
        alphabet_upper = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        alphabet_lower = 'abcdefghijklmnopqrstuvwxyz'
        if c in alphabet_upper:
            return format(alphabet_upper.index(c), '010b')
        elif c in alphabet_lower:
            return format(alphabet_lower.index(c) + 26, '010b')
        return None

    binary_string = ''.join(char_to_binary(char) for char in input_string if char_to_binary(char))
    return binary_string


def Jbtc(binary_input):
    def binary_to_char(binary_vector):
        if binary_vector == '0000000001':
            return ' '
        elif binary_vector == '0000000010':
            return '\n'
        alphabet_upper = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        alphabet_lower = 'abcdefghijklmnopqrstuvwxyz'
        num = int(binary_vector, 2)
        if 0 <= num <= 25:
            return alphabet_upper[num]
        elif 26 <= num <= 51:
            return alphabet_lower[num - 26]
        return None

    char_list = [binary_to_char(binary_input[i:i+10]) for i in range(0, len(binary_input), 10)]
    return ''.join(char_list)

class Jwin:
    def __init__(self, layout, widgets_config, user_callbacks=None):
        self.root = tk.Tk()
        self.root.title("Dynamic Window")
        self.widgets = {}
        self.user_callbacks = user_callbacks or {}
        self.layout_lines = [line.strip() for line in layout.strip().split("\n") if line.strip()]
        self.num_rows = len(self.layout_lines)
        self.num_cols = max(len(line) for line in self.layout_lines)
        for r in range(self.num_rows):
            self.root.grid_rowconfigure(r, weight=1)
        for c in range(self.num_cols):
            self.root.grid_columnconfigure(c, weight=1)
        self._create_widgets(widgets_config)
        self._create_layout()

    def _create_widgets(self, widgets_config):
        for widget_config in widgets_config:
            row, col = widget_config['position']
            widget_type = widget_config['type']
            options = widget_config.get('options', {})
            widget = self._create_widget(widget_type, options)
            if widget:
                widget.grid(row=row, column=col, padx=5, pady=5)
                widget_id = options.get("id")
                if widget_id:
                    self.widgets[widget_id] = widget

    def _create_widget(self, widget_type, options):
        if widget_type == "button":
            return tk.Button(self.root, text=options.get("text", "Button"),
                             command=lambda: self._execute_callback(options.get("id")))
        elif widget_type == "label":
            return tk.Label(self.root, text=options.get("text", "Label"))
        elif widget_type == "input":
            return tk.Entry(self.root)
        elif widget_type == "password":
            return tk.Entry(self.root, show="*")
        elif widget_type == "checkbox":
            return tk.Checkbutton(self.root, text=options.get("text", "Checkbox"))
        elif widget_type == "textarea":
            return tk.Text(self.root, height=5, width=20)
        else:
            return tk.Label(self.root, text=f"Unsupported: {widget_type}")

    def _create_layout(self):
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                if self.layout_lines[r][c] == " ":
                    continue

    def _execute_callback(self, widget_id):
        if widget_id and widget_id in self.user_callbacks:
            callback = self.user_callbacks[widget_id]
            if callable(callback):
                callback()

    def run(self):
        self.root.mainloop()


    def show_error_messagebox(message):
        root = tk.Tk()
        root.withdraw()
        tk.messagebox.showerror("Error", message)

def encode_base64(data):
    base64_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
    binary_data = ''.join([f"{ord(c):08b}" for c in data])
    padding = len(binary_data) % 6
    if padding != 0:
        binary_data += '0' * (6 - padding)
    encoded = ''.join([base64_chars[int(binary_data[i:i+6], 2)] for i in range(0, len(binary_data), 6)])
    encoded += "=" * ((4 - len(encoded) % 4) % 4)
    return encoded

def decode_base64(encoded_data):
    base64_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
    encoded_data = encoded_data.rstrip("=")
    binary_data = ''.join([f"{base64_chars.index(c):06b}" for c in encoded_data])
    decoded = ''.join([chr(int(binary_data[i:i+8], 2)) for i in range(0, len(binary_data), 8)])
    return decoded

def reverse_string(string):
    return string[::-1]

def calculate_factorial(number):
    if number == 0:
        return 1
    return number * calculate_factorial(number - 1)

def generate_random_string(length=15):
    charset = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@/-*_'
    random_string = ''
    for _ in range(length):
        random_string += charset[calculate_factorial(len(charset)) % len(charset)]
    return random_string

def swap_values(a, b):
    return b, a

def replace(string,replacement,replacment):return string.replace(replacement,replacment)

def find_maximum(numbers):
    max_val = numbers[0]
    for num in numbers:
        if num > max_val:
            max_val = num
    return max_val

def find_minimum(numbers):
    min_val = numbers[0]
    for num in numbers:
        if num < min_val:
            min_val = num
    return min_val

def sum_list(lst):
    total = 0
    for num in lst:
        total += num
    return total

def reverse_list(lst):
    return lst[::-1]

def is_prime(n):
    if n <= 1:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True

def split_into_chunks(text, chunk_size):
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

def unique_elements(lst):
    unique_lst = []
    for item in lst:
        if item not in unique_lst:
            unique_lst.append(item)
    return unique_lst

def calculate_average(numbers):
    if not numbers:
        return 0
    return sum_list(numbers) / len(numbers)

def calculate_median(numbers):
    sorted_numbers = sorted(numbers)
    n = len(sorted_numbers)
    mid = n // 2
    if n % 2 == 0:
        return (sorted_numbers[mid - 1] + sorted_numbers[mid]) / 2
    return sorted_numbers[mid]

def count_words(text):
    return len(text.split())

def count_sentences(text):
    sentences = text.split('.')
    return len([s for s in sentences if s.strip()])

def add_commas(input_string):
    return ','.join(input_string)

def remove_spaces(text):
    return ''.join([char for char in text if char != ' '])

def calculate_square_root(number):
    if number < 0:
        return None
    guess = number / 2.0
    for _ in range(20):
        guess = (guess + number / guess) / 2.0
    return guess

def find_files_by_extension(directory, extension):
    return [f for f in os.listdir(directory) if f.endswith(extension)]

def get_curr_dir():
    return os.getcwd()

def check_if_file_exists(file_path):
    return os.path.exists(file_path)

def monitor_new_files(directory, callback):
    known_files = set(os.listdir(directory))
    while True:
        current_files = set(os.listdir(directory))
        new_files = current_files - known_files
        if new_files:
            callback(new_files)
        known_files = current_files
        time.sleep(1)


def monitor_file_changes(file_path, callback):
    last_modified = os.path.getmtime(file_path)
    while True:
        current_modified = os.path.getmtime(file_path)
        if current_modified != last_modified:
            last_modified = current_modified
            callback()
        time.sleep(1)

def write_to_file(filename, content):
    with open(filename, 'w') as file:
        file.write(content)

def read_from_file(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        return file.read()

def parse_json(json_string):
    return json.loads(json_string)

def create_file_if_not_exists(filename):
    if not os.path.exists(filename):
        with open(filename, 'w') as file:
            file.write('')

def create_directory(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def create_zip_file(source_dir, output_zip):
    shutil.make_archive(output_zip, 'zip', source_dir)

def extract_zip_file(zip_file, extract_dir):
    shutil.unpack_archive(zip_file, extract_dir)

def move_file(source, destination):
    shutil.move(source, destination)

def copy_file(source, destination):
    shutil.copy(source, destination)

def show_file_properties(file_path):
    stats = os.stat(file_path)
    return f"Size: {stats.st_size} bytes, Last Modified: {time.ctime(stats.st_mtime)}"


def start_http_server(ip="0.0.0.0", port=8000):
    server_address = (ip, port)
    httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
    print(f"Server started on {ip}:{port}")
    httpd.serve_forever()

def stop_http_server():
    print("Stopping server...")
    exit(0)

def get_server_status(url="http://localhost:8000"):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            print("Server is up and running.")
        else:
            print(f"Server is down. Status Code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to server: {e}")

def set_server_timeout(timeout=10):
    socket.setdefaulttimeout(timeout)
    print(f"Server connection timeout set to {timeout} seconds.")

def upload_file_to_server(file_path, url="http://localhost:8000/upload"):
    with open(file_path, 'rb') as file:
        response = requests.post(url, files={'file': file})
        if response.status_code == 200:
            print(f"File successfully uploaded: {file_path}")
        else:
            print(f"File upload failed. Status Code: {response.status_code}")

def download_file_from_server(file_url, save_path):
    response = requests.get(file_url)
    if response.status_code == 200:
        with open(save_path, 'wb') as file:
            file.write(response.content)
        print(f"File downloaded: {save_path}")
    else:
        print(f"File download failed. Status Code: {response.status_code}")

class CustomRequestHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"Welcome! Server is running.")
        elif self.path == "/status":
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"status": "online"}')
        else:
            self.send_response(404)
            self.end_headers()

def start_custom_http_server(ip="0.0.0.0", port=8000):
    server_address = (ip, port)
    httpd = HTTPServer(server_address, CustomRequestHandler)
    print(f"Custom server started on {ip}:{port}")
    httpd.serve_forever()

def set_server_access_logs(log_file="server_access.log"):
    logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s - %(message)s')
    print(f"Access logs are being saved to {log_file}")

def get_server_logs(log_file="server_access.log"):
    try:
        with open(log_file, 'r') as log:
            logs = log.readlines()
            print("".join(logs))
    except FileNotFoundError:
        print(f"{log_file} not found.")

def restart_http_server():
    print("Restarting server...")
    os.execv(sys.executable, ['python'] + sys.argv)

def check_internet_connection():
    try:
        param = "-n" if platform.system().lower() == "windows" else "-c"
        subprocess.run(["ping", param, "1", "google.com"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except:
        return False

def create_web_server(directory, port=8000):
    os.chdir(directory)
    handler = SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"Serving {directory} at http://localhost:{port}")
        httpd.serve_forever()

def create_custom_web_server(html, port=8000):
    html_content = html

    class CustomHandler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(html_content.encode('utf-8'))

    with socketserver.TCPServer(("", port), CustomHandler) as httpd:
        print(f"Serving custom HTML page at http://0.0.0.0:{port}")
        print("Anyone on the same network can access this. (if not work use this http://127.0.0.1:8000)")
        httpd.serve_forever()
def JynParser(rep):
    inj= """
    global main
    main = rep
    """
    exec()

def contains(input, str):
    return str in input

def Jusbcam(Device_Name):
    try:
        result = subprocess.run(
            ['wmic', 'path', 'Win32_PnPEntity', 'where', 'DeviceID like "USB%"', 'get', 'Name'],
            capture_output=True, text=True, encoding="utf-8", errors="ignore"
        )
        if result.stdout:
            output = result.stdout.strip().split("\n")[1:]
            devices = [line.strip() for line in output if line.strip()]
            return contains(devices,Device_Name)
        else:
            return []
    except Exception as e:
        print(f"Error detecting devices: {e}")
        return []

def defseprator(option_count, *options):
    if len(options) != option_count:
        raise ValueError(f"Expected {option_count} options, but got {len(options)}.")
    result = [1 if option else 0 for option in options]
    return ",".join(map(str, result))


def claw(html_option, html, ip, port, subdomain_option, subdomain_count, subdomains, return_server_logs_option):
    class CustomHandler(http.server.SimpleHTTPRequestHandler):
        MAIN_HTML = "<h1>Default Page</h1>"
        SUBDOMAINS = {}
        def do_GET(self):
            if self.path == "/":
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(self.MAIN_HTML.encode("utf-8"))
            elif self.path in self.SUBDOMAINS:
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(self.SUBDOMAINS[self.path].encode("utf-8"))
            else:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b"404 Not Found")
            if self.server.log_requests:logging.info(f"Request: {self.command} {self.path} from {self.client_address}")
    if return_server_logs_option:logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
    if html_option:CustomHandler.MAIN_HTML = html
    if subdomain_option:
        for i in range(1, subdomain_count + 1):
            sub_path = f"/sub{i}"
            CustomHandler.SUBDOMAINS[sub_path] = subdomains.get(sub_path, f"<h1>Subdomain {i}</h1>")
    server = socketserver.TCPServer((ip, port), CustomHandler)
    server.log_requests = return_server_logs_option
    thread = threading.Thread(target=server.serve_forever)
    thread.daemon = True
    thread.start()
    print(f"Server started at http://{ip}:{port}")
    return server

class ConsoleCam:
    def __init__(self):
        self._original_stdout = sys.stdout
        self._buffer = io.StringIO()
        sys.stdout = self._buffer
    @classmethod
    def start(cls):
        instance = cls()
        instance._buffer.truncate(0)
        instance._buffer.seek(0)
        return instance
    def get_new(self):return self._buffer.getvalue()
    def stop(self):sys.stdout = self._original_stdout

def prn(str):print(str)

def copy_to_clipboard(text):
    pyperclip.copy(text)

class Key:
    def __init__(self, key):
        VK_CODE = {
            **{chr(i): i - 32 for i in range(ord('a'), ord('z') + 1)},
            **{str(i): 0x30 + i for i in range(10)},
            **{f'f{i}': 0x6F + i for i in range(1, 13)},
            'left': 0x25, 'up': 0x26, 'right': 0x27, 'down': 0x28,
            'home': 0x24, 'end': 0x23, 'insert': 0x2D, 'delete': 0x2E,
            'pageup': 0x21, 'pagedown': 0x22,
            'shift': 0x10, 'ctrl': 0x11, 'alt': 0x12,
            'tab': 0x09, 'capslock': 0x14, 'enter': 0x0D,
            'space': 0x20, 'backspace': 0x08, 'esc': 0x1B,
            ';': 0xBA, '=': 0xBB, ',': 0xBC, '-': 0xBD,
            '.': 0xBE, '/': 0xBF, '`': 0xC0,
            '[': 0xDB, '\\': 0xDC, ']': 0xDD, "'": 0xDE,
            'num0': 0x60, 'num1': 0x61, 'num2': 0x62, 'num3': 0x63,
            'num4': 0x64, 'num5': 0x65, 'num6': 0x66,
            'num7': 0x67, 'num8': 0x68, 'num9': 0x69,
            'multiply': 0x6A, 'add': 0x6B, 'separator': 0x6C,
            'subtract': 0x6D, 'decimal': 0x6E, 'divide': 0x6F,
        }
        self.key = key.lower()
        self.vk = VK_CODE.get(self.key)

    def press(self):
        if self.vk is not None:
            ctypes.windll.user32.keybd_event(self.vk, 0, 0, 0)

    def release(self):
        KEYEVENTF_KEYUP = 0x0002
        if self.vk is not None:
            ctypes.windll.user32.keybd_event(self.vk, 0, KEYEVENTF_KEYUP, 0)

    def tap(self, delay=0.05):
        self.press()
        time.sleep(delay)
        self.release()
    
    def type_text(text):
        def press_combo(*keys, delay=0.05):
            key_objs = [Key(k) for k in keys]
            for k in key_objs:
                k.press()
                time.sleep(delay)
            for k in reversed(key_objs):
                k.release()
                time.sleep(delay)
        for char in text:
            if char.isupper():
                press_combo('shift', char.lower())
            else:
                Key(char).tap()

    def press_combo(*keys, delay=0.05):
        key_objs = [Key(k) for k in keys]
        for k in key_objs:
            k.press()
            time.sleep(delay)
        for k in reversed(key_objs):
            k.release()
            time.sleep(delay)

def count_occurrences(lst, element):return lst.count(element)

def get_curr_time():now = datetime.datetime.now();return now.strftime("%Y-%m-%d %H:%M:%S")

def is_palindrome(s):return s == s[::-1]

def get_min_max(list):return min(list),max(list)

def is_digits(input):return input.isdigit()

def create_dict(keys, values):return dict(zip(keys, values))

def square_number(input):return input ** 2

def get_file_size(file_path):return os.path.getsize(file_path)

def find_duplicates(lst):
    seen = set()
    duplicates = []
    for item in lst:
        if item in seen:duplicates.append(item)
        else:seen.add(item)
    return duplicates

def get_average(list):
    if not list:return 0
    return sum(list) / len(list)

def divide(a, b):
    if b == 0:return None
    return a / b

def extract_numbers(s):return [int(x) for x in re.findall(r'\d+', s)]

class BinTrig:
    @classmethod
    def exit(cls, winroot, trig):
        def close_and_destroy():
            trig()
            winroot.destroy()
        winroot.protocol("WM_DELETE_WINDOW", close_and_destroy)

    def mouse_in(self, winroot, trig):
        winroot.bind("<Enter>", trig)

    def mouse_out(self, winroot, trig):
        winroot.bind("<Leave>", trig)

    def fullscreen(self, winroot, trig):
        def check_fullscreen(event=None):
            screen_width = winroot.winfo_screenwidth()
            screen_height = winroot.winfo_screenheight()
            window_width = winroot.winfo_width()
            window_height = winroot.winfo_height()
            if window_width == screen_width and window_height == screen_height:
                trig(event)
        winroot.bind("<Configure>", check_fullscreen)

    def minimized(self, winroot, trig):
        def check_minimized(event=None):
            if winroot.state() in ['iconic', 'withdrawn']:
                trig(event)
        winroot.bind("<Visibility>", check_minimized)

    def width_height(self, winroot, widmin, heimin, trig):
        def check_size(event=None):
            width = winroot.winfo_width()
            height = winroot.winfo_height()
            if width > widmin or height > heimin:
                trig(event)
        winroot.bind("<Configure>", check_size)

    def key_press(self, winroot, key, trig):
        winroot.bind(f"<KeyPress-{key}>", trig)

    def focus_gain(self, winroot, trig):
        winroot.bind("<FocusIn>", trig)

    def focus_loss(self, winroot, trig):
        winroot.bind("<FocusOut>", trig)

    def window_move(self, winroot, trig):
        winroot.bind("<Configure>", trig)

    def resize(self, winroot, trig):
        winroot.bind("<Configure>", trig)

    def close_shortcut(self, winroot, trig):
        winroot.bind("<Alt-F4>", trig)

    def mouse_button_press(self, winroot, button, trig):
        winroot.bind(f"<Button-{button}>", trig)

    def mouse_button_release(self, winroot, button, trig):
        winroot.bind(f"<ButtonRelease-{button}>", trig)

    def double_click(self, winroot, trig):
        winroot.bind("<Double-1>", trig)

    def mouse_motion(self, winroot, trig):
        winroot.bind("<Motion>", trig)

    def window_minimized(self, winroot, trig):
        def check_minimized(event=None):
            if winroot.state() == 'iconic':
                trig(event)
        winroot.bind("<Unmap>", check_minimized)

    def window_maximized(self, winroot, trig):
        def check_maximized(event=None):
            winroot.update_idletasks()
            if winroot.state() == 'zoomed':
                trig(event)
        winroot.bind("<Map>", check_maximized)
        winroot.bind("<Configure>", check_maximized)

    def window_restored(self, winroot, trig):
        def check_restored(event=None):
            if winroot.state() == 'normal':
                trig(event)
        winroot.bind("<Configure>", check_restored)

    def mouse_wheel_scroll(self, winroot, trig):
        winroot.bind("<MouseWheel>", trig)

    def text_change(self, widget, trig):
        widget.bind("<KeyRelease>", trig)

    def focus_on_widget(self, widget, trig):
        widget.bind("<FocusIn>", trig)

    def focus_off_widget(self, widget, trig):
        widget.bind("<FocusOut>", trig)

class ByteJar:
    def __init__(self, host="127.0.0.1", port=8090):
        self.host = host
        self.port = port
        self.client_socket = None

    def start(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.client_socket.connect((self.host, self.port))
            response = self.client_socket.recv(1024).decode().strip()
            print(f"DEBUG: Server response: {response}")  
            return response
        except Exception as e:
            return f"Error connecting to server: {e}"

    def stop(self):
        if self.client_socket:
            self.client_socket.close()
            self.client_socket = None
            return "Connection closed."
        return "No active connection."

    def send_command(self, command):
        if not self.client_socket:
            return "Error: No active connection. Please start the connection first."

        try:
            self.client_socket.sendall(command.encode())
            response = self.client_socket.recv(1024).decode().strip()
            print(f"DEBUG: Server response: {response}")  
            return response
        except Exception as e:
            return f"Error while sending command: {e}"

def letterglue(str="", *substr, str2=""):return str + ''.join(substr) + str2

def letterglue_creator(word):
    alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    original_vars = [(alphabet[i % 26] * ((i // 26) + 1), letter) for i, letter in enumerate(word)]
    shuffled_vars = original_vars[:]
    random.shuffle(shuffled_vars)
    defs_line = "; ".join([f'{var}="{ch}"' for var, ch in shuffled_vars]) + ";"
    glue_order = ", ".join([var for var, _ in original_vars])
    code = defs_line + "\n"
    code += "result = letterglue(" + glue_order + ")\n"
    code += "print(result)"
    return code

def Baudio(filename="audio_data", mode="Write", duration=5, Warn=True):
    def BprecAU(fname, Warn=Warn):
        if Warn:
            print("Playing audio...")
        samplerate = 44100
        with open(letterglue(fname, ".Bau"), 'rb') as f:
            audio_data = f.read()
        audio_data_np = np.frombuffer(audio_data, dtype='float32')
        sd.play(audio_data_np, samplerate=samplerate)
        sd.wait()
        if Warn:
            print(f"Audio playback from {fname}.Bau finished.")

    host = "127.0.0.1"
    port = 65432
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))
    
    client_socket.sendall("record".encode())
    client_socket.sendall(duration.to_bytes(4, 'big'))
    
    audio_length = int.from_bytes(client_socket.recv(4), 'big')
    audio_data = b""
    while len(audio_data) < audio_length:
        audio_data += client_socket.recv(1024)
    
    client_socket.close()
    
    if mode.lower() == "write":
        with open(letterglue(filename, ".Bau"), 'wb') as f:
            f.write(audio_data)
        if Warn:
            print(f"Audio recorded and saved to {filename}.Bau.")
            
    elif mode.lower() == "return":
        audio_np = np.frombuffer(audio_data, dtype='float32')
        if Warn:
            print("Audio recorded and returned as a numpy array.")
        return audio_np
    elif mode.lower() == "play":
        BprecAU(filename)
    else:
        raise ValueError("Invalid mode. Please use 'Write', 'Return' or 'Play'.")

class Btuple:
    @classmethod
    def count(cls, *words):
        return len(words)
    @classmethod
    def get(cls, index, *words):
        if 0 <= index < len(words):
            return words[index-1]
        return "Error: Please choose a number within range."
    @classmethod
    def exists(cls, item, *words):
        return item in words

    @classmethod
    def first(cls, *words):
        return words[0] if words else "Error: Tuple is empty."

    @classmethod
    def last(cls, *words):
        return words[-1] if words else "Error: Tuple is empty."

def isgreater(*nums):
    tc = Btuple.count(*nums)
    t1 = Btuple.get(*nums, 1)
    t2 = Btuple.get(*nums, 2)
    if tc != 2:
        print("There should be 2 numbers inputted!")
        return False
    elif tc == 0:
        print("Input can't be empty!")
        return False
    elif t1 > t2:return True
    else:return False

def runwfallback(func, fallback_func):
    try:return func()
    except Exception as e:return fallback_func()

def retry(func, retries=3, delay=1):
    for attempt in range(retries):
        try:
            return func()
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            time.sleep(delay)
    print("All attempts failed.")
    return None

def fftime(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__} took {end - start:.4f} seconds")
        return result
    return wrapper

def debug(func):
    def wrapper(*args, **kwargs):
        print(f"Calling {func.__name__} with args={args}, kwargs={kwargs}")
        result = func(*args, **kwargs)
        print(f"{func.__name__} returned {result}")
        return result
    return wrapper

def paste_from_clipboard():return pyperclip.paste()

def watch_file(filepath, callback):
    last_modified = os.path.getmtime(filepath)
    while True:
        time.sleep(1)
        if os.path.getmtime(filepath) != last_modified:
            last_modified = os.path.getmtime(filepath)
            callback(filepath)

def is_website_online(url):
    try:
        response = requests.get(url, timeout=5)
        return response.status_code == 200
    except requests.RequestException:return False

def shorten_url(long_url):
    response = requests.get(f"http://tinyurl.com/api-create.php?url={long_url}")
    return response.text

def celsius_to_fahrenheit(c):return (c * 9/5) + 32

def fahrenheit_to_celsius(f):return (f - 32) * 5/9

def efv(code: str):
    fc = code.replace(",", ";")
    local_vars = {}
    exec(fc, {}, local_vars)
    return local_vars

def Hpass(lIlllIlIIllllIIIll=30):
    lllllllllllllll, llllllllllllllI, lllllllllllllIl, lllllllllllllII, llllllllllllIll, llllllllllllIlI, llllllllllllIIl, llllllllllllIII = len, exec, chr, str, bool, int, globals, ord
    def lllIIIIllllllIIIlI(IllllllIllIllIlIll=8):
        return ''.join(random.choices(string.ascii_letters + string.digits, k=IllllllIllIllIlIll))
    def llIlIIIIIlIIIllIII(lIIIIlllIIIlIllIlI, llIllIIIlIIIllIIlI):
        lllllIIIIlIIIlllIl = lllllllllllllII(llllllllllllIlI(time.time()))
        IIlIIlIlIIIIIIIIll = ''.join(random.sample(lIIIIlllIIIlIllIlI + llIllIIIlIIIllIIlI + lllllIIIIlIIIlllIl, lllllllllllllll(lIIIIlllIIIlIllIlI + llIllIIIlIIIllIIlI + lllllIIIIlIIIlllIl)))
        return IIlIIlIlIIIIIIIIll
    def lllllIllIlIIIlIIlI(lIlIIIIlIllIIlllIl):
        return hashlib.sha256(lIlIIIIlIllIIlllIl.encode('utf-8')).hexdigest()
    def IIIIIIlIIIllIlIlIl(IIlIIlllIllllIIIlI):
        IIIlllIlIllIlIllll = []
        for lllIlIIllllllIllII in IIlIIlllIllllIIIlI:
            IIIIlllIIIIIIIlIll = llllllllllllIII(lllIlIIllllllIllII) * 10 % 256
            IIIlllIlIllIlIllll.append(lllllllllllllIl(IIIIlllIIIIIIIlIll))
        return ''.join(IIIlllIlIllIlIllll)
    IIllIlIlIIlllIIIlI = lIlllIlIIllllIIIll
    def llIlllIIlIIllIllIl(lIIIIlllIIIlIllIlI, llIllIIIlIIIllIIlI):
        IlIIllIIlIlIlIIlIl = llIlIIIIIlIIIllIII(lIIIIlllIIIlIllIlI, llIllIIIlIIIllIIlI)
        IIIlIIIlIlllIIIlII = lllllIllIlIIIlIIlI(IlIIllIIlIlIlIIlIl)
        IIIlIIlIllIlIIlIll = IIIIIIlIIIllIlIlIl(IIIlIIIlIlllIIIlII)
        lIllIlIlIIllIIIlIl = llIlIIIIIlIIIllIII(lIIIIlllIIIlIllIlI, llIllIIIlIIIllIIlI + IIIlIIlIllIlIIlIll)
        IIIlIIIllIIIlIIlII = lllllIllIlIIIlIIlI(lIllIlIlIIllIIIlIl)
        llIIIIIlIIIIlllIll = IIIIIIlIIIllIlIlIl(IIIlIIIllIIIlIIlII)
        return llIIIIIlIIIIlllIll
    def IIIlllllIlllIIllII(lIIIIlllIIIlIllIlI, llIllIIIlIIIllIIlI):
        llIlIIlIIllIIIlIII = llIlllIIlIIllIllIl(lIIIIlllIIIlIllIlI, llIllIIIlIIIllIIlI)
        lllIlIllllIllllllI = llIlllIIlIIllIllIl(lIIIIlllIIIlIllIlI, llIllIIIlIIIllIIlI)
        lllllIIIIlIIIlllIl = lllllllllllllII(llllllllllllIlI(time.time()))
        lIllIIIIlIIllIlIlI = llIlIIlIIllIIIlIII + lllIlIllllIllllllI + lllllIIIIlIIIlllIl
        return lIllIIIIlIIllIlIlI
    def llIlllIlllIlIIlIll(llIlIIIlIllIllIlll):
        IIIlllIlIllIlIllll = []
        for lllIlIIllllllIllII in llIlIIIlIllIllIlll:
            IIIlllIlIllIlIllll.append(lllllllllllllII(llllllllllllIII(lllIlIIllllllIllII)))
        return ''.join(IIIlllIlIllIlIllll)
    def lllllIllIlIIlIIlll(IlIIIIIIIIlIlIlIII):
        llIIIIIIIlllIIIIlI = lllllllllllllII(IlIIIIIIIIlIlIlIII)
        IIIlllIlIllIlIllll = []
        for lllIIlIIIIllIlIIll in llIIIIIIIlllIIIIlI:
            lllIlIIllllllIllII = lllllllllllllIl(96 + llllllllllllIlI(lllIIlIIIIllIlIIll))
            if random.choice([llllllllllllIll(((1 & 0 ^ 0) & 0 ^ 1) & 0 ^ 1 ^ 1 ^ 0 | 1), llllllllllllIll(((1 & 0 ^ 0) & 0 ^ 1) & 0 ^ 1 ^ 1 ^ 0 | 0)]):
                lllIlIIllllllIllII = lllIlIIllllllIllII.upper()
            IIIlllIlIllIlIllll.append(lllIlIIllllllIllII)
        return ''.join(IIIlllIlIllIlIllll)
    def IllIlllIlIlIlllIIl(IIIIIlIIllIlIlllIl, IlIllllllIlIIllllI):
        return IIIIIlIIllIlIlllIl[:IlIllllllIlIIllllI]
    lIIIIlllIIIlIllIlI = lllIIIIllllllIIIlI()
    llIllIIIlIIIllIIlI = lllIIIIllllllIIIlI()
    IIlllIIllIlIIlIIlI = 'w'
    IIllIIIlIIIIlIlIlI = 'r'
    IllIllIIIlIlllIIll = 'o'
    llIIllIIIIIlIIlIIl = '='
    IlIlIIIlllIIllIlII = ' '
    IIIIIlllIIIlIlIIII = '('
    llllIIIIlIlllIIIIl = 'o'
    llllIllIIIllllIIII = '2'
    llIllllIlIIIIlIllI = ','
    IlIllllIIllIIIIIll = '1'
    lIIllIllIIIlIlllIl = 'o'
    lIIlllIIIIlIllIllI = 'd'
    lllIIIIIIIIllllIII = ' '
    IllIIlIIIIlllIlIll = 'o'
    lIllIIIllIIIllIIIl = ')'
    lllllIIllIlIllIIll = 'o'
    IlIIlIIIIlIIlIIIIl = 'r'
    lIllIlllllIllIlIIl = 'd'
    llIIlIllllIllIIlll = 'w'
    IIIlllIlIllIlIllll = letterglue(llllIIIIlIlllIIIIl, IllIIlIIIIlllIlIll, llIIllIIIIIlIIlIIl, IlIlIIIlllIIllIlII, lIIllIllIIIlIlllIl, IIIIIlllIIIlIlIIII, llIIlIllllIllIIlll, IllIllIIIlIlllIIll, IlIIlIIIIlIIlIIIIl, lIllIlllllIllIlIIl, IlIllllIIllIIIIIll, llIllllIlIIIIlIllI, lllIIIIIIIIllllIII, IIlllIIllIlIIlIIlI, lllllIIllIlIllIIll, IIllIIIlIIIIlIlIlI, lIIlllIIIIlIllIllI, llllIllIIIllllIIII, lIllIIIllIIIllIIIl)
    lIIIIlIllIIIlIlIIl = {'word1': lIIIIlllIIIlIllIlI, 'word2': llIllIIIlIIIllIIlI, 'o': IIIlllllIlllIIllII}
    llllllllllllllI(IIIlllIlIllIlIllll, llllllllllllIIl(), lIIIIlIllIIIlIlIIl)
    IIllllIIlIIlIllIII = llIlllIlllIlIIlIll(lIIIIlIllIIIlIlIIl.get('oo'))
    lIIllIIlIlIllIlllI = lllllIllIlIIlIIlll(IIllllIIlIIlIllIII)
    return IllIlllIlIlIlllIIl(replace(lIIllIIlIlIllIlllI, '`', ''), IIllIlIlIIlllIIIlI)

def l(input):return list(input)

def dl(input):return ''.join(input)

def mix(input):
    IIlIIIIllIlIIlIlll = l(input)
    random.shuffle(IIlIIIIllIlIIlIlll)
    return dl(IIlIIIIllIlIIlIlll)

def sugar(input):
    lllllllllllllll, llllllllllllllI, lllllllllllllIl = str, len, list
    lIlIllIIIIIIIlllIl = random.randint(1, llllllllllllllI(input))
    llIIlIllllllIlIlII = ''.join(random.choices('01243213132112576635439769813224562133489', k=5))
    lIlIllIIllIllIIIlI = llllllllllllllI(input) - 1
    IlIlllIlIIIIlllIIl = lllllllllllllIl(add_commas(input))
    random.shuffle(IlIlllIlIIIIlllIIl)
    IIlIIlIIIIllIlllII = generate_random_string(lIlIllIIllIllIIIlI)
    IlIIIllllllIllllIl = letterglue(''.join(IlIlllIlIIIIlllIIl), IIlIIlIIIIllIlllII)
    IlIllIlIlllIllIIlI = lllllllllllllIl(IlIIIllllllIllllIl)
    random.shuffle(IlIllIlIlllIllIIlI)
    IlllllllIlIIlIIlll = ''.join(IlIllIlIlllIllIIlI)
    IIlllllIIIllIIlllI = IlllllllIlIIlIIlll.replace(',', '')
    IIllIlIIIlIIllIllI = lllllllllllllIl(IIlllllIIIllIIlllI)
    random.shuffle(IIllIlIIIlIIllIllI)
    lIllIIIIlllIIlllIl = ''.join(IIllIlIIIlIIllIllI)
    IIlllIIIIllIlllIIl = add_commas(lllllllllllllll(lIlIllIIIIIIIlllIl))
    IIlllIlllllIllIlIl = lllllllllllllIl(IIlllIIIIllIlllIIl)
    random.shuffle(IIlllIlllllIllIlIl)
    IIlIlIlIIlIIlllllI = ''.join(IIlllIlllllIllIlIl)
    lIlIlIIllIIIlIIIII = letterglue(llIIlIllllllIlIlII, IIlIlIlIIlIIlllllI + lIllIIIIlllIIlllIl)
    IllIlIIlIllllllIlI = lllllllllllllIl(lIlIlIIllIIIlIIIII)
    random.shuffle(IllIlIIlIllllllIlI)
    llIIlIlIIlllIIIIlI = ''.join(IllIlIIlIllllllIlI)
    return replace(mix(llIIlIlIIlllIIIIlI), ',', '')

def get_type(value):return f"{type(value).__name__} - {repr(value)}"

class Cache:
    def __init__(self):self.cached = {}
    def add(self, key, value):self.cached[key] = value
    def get(self, key):return self.cached.get(key, None)


def cantint(egl="Equal,Greater,Lower", ftw="From/To What", tw="Tuple of ints"):
    if egl == "e":
        if ftw in tw:tw.clear()
    elif egl == "g":
        if any(ftw > item for item in tw):tw.clear()
    elif egl == "l":
        if any(ftw < item for item in tw):tw.clear()
    else:return

def flatten(obj):
    if isinstance(obj, list):
        for item in obj:
            yield from flatten(item)
    else:
        yield obj

def memoize(func):
    cache = {}
    def wrapper(*args):
        if args not in cache:
            cache[args] = func(*args)
        return cache[args]
    return wrapper

def chunk(iterable, size):
    for i in range(0, len(iterable), size):
        yield iterable[i:i + size]

def merge_dicts(*dicts):
    result = {}
    for d in dicts:
        result.update(d)
    return result

def deep_equal(a, b):
    if isinstance(a, dict) and isinstance(b, dict):
        if a.keys() != b.keys():
            return False
        return all(deep_equal(a[k], b[k]) for k in a)
    elif isinstance(a, list) and isinstance(b, list):
        return len(a) == len(b) and all(deep_equal(i, j) for i, j in zip(a, b))
    return a == b

def split_by(text, size):
    return [text[i:i + size] for i in range(0, len(text), size)]

class GoodBye2Spy:
    class Passworded:
        lllllllllllllll, llllllllllllllI, lllllllllllllIl, lllllllllllllII, llllllllllllIll, llllllllllllIlI = len, str, classmethod, bool, list, range
        @lllllllllllllIl
        def create(cls, data, key, seed=42):
            def lllIllIIlIlIllIIll(data, key, seed=42):
                lllllllllllllll, llllllllllllllI, lllllllllllllIl, lllllllllllllII, llllllllllllIll, llllllllllllIlI = len, str, classmethod, bool, list, range
                IlllIIlIlIIIlIIlII = llllllllllllIll(data)
                lIlIlIlIIllIllIIll = 0
                random.seed(seed)
                for llIllIIIIllllIIIII in llllllllllllIlI(lllllllllllllll(IlllIIlIlIIIlIIlII)):
                    if random.choice([lllllllllllllII(((1 & 0 ^ 0) & 0 ^ 1) & 0 ^ 1 ^ 1 ^ 0 | 1), lllllllllllllII(((1 & 0 ^ 0) & 0 ^ 1) & 0 ^ 1 ^ 1 ^ 0 | 0)]):
                        IlllIIlIlIIIlIIlII[llIllIIIIllllIIIII] = key[lIlIlIlIIllIllIIll % lllllllllllllll(key)]
                        lIlIlIlIIllIllIIll += 1
                IIlIlIllllllllIIlI = ''.join(IlllIIlIlIIIlIIlII)
                return IIlIlIllllllllIIlI
            IIlIlIllllllllIIlI = lllIllIIlIlIllIIll(data, key, seed)
            IlIIIIlIIlllIIIIll = hashlib.sha256(IIlIlIllllllllIIlI.encode()).hexdigest()
            return IlIIIIlIIlllIIIIll
        @lllllllllllllIl
        def verify(cls, data, key, given_hash, seed=42):
            IlIIIlIIIlIIIlIlll = cls.create(data, key, seed)
            return IlIIIlIIIlIIIlIlll == given_hash
    class Oneway:
        lllllllllllllll, llllllllllllllI, lllllllllllllIl, lllllllllllllII, llllllllllllIll, llllllllllllIlI = len, str, classmethod, bool, list, range
        @lllllllllllllIl
        def OW(cls, data='Input a string', IlIlIlIllIlllIIIII=5):
            class IIlIIIlIllllIlIlII:
                lllllllllllllll, llllllllllllllI, lllllllllllllIl, lllllllllllllII, llllllllllllIll, llllllllllllIlI = len, str, classmethod, bool, list, range
                @lllllllllllllIl
                def create(cls, data, key, seed=42):
                    def lllIllIIlIlIllIIll(data, key, seed=42):
                        lllllllllllllll, llllllllllllllI, lllllllllllllIl, lllllllllllllII, llllllllllllIll, llllllllllllIlI = len, str, classmethod, bool, list, range
                        IlllIIlIlIIIlIIlII = llllllllllllIll(data)
                        lIlIlIlIIllIllIIll = 0
                        random.seed(seed)
                        for llIllIIIIllllIIIII in llllllllllllIlI(lllllllllllllll(IlllIIlIlIIIlIIlII)):
                            if random.choice([lllllllllllllII(((1 & 0 ^ 0) & 0 ^ 1) & 0 ^ 1 ^ 1 ^ 0 | 1), lllllllllllllII(((1 & 0 ^ 0) & 0 ^ 1) & 0 ^ 1 ^ 1 ^ 0 | 0)]):
                                IlllIIlIlIIIlIIlII[llIllIIIIllllIIIII] = key[lIlIlIlIIllIllIIll % lllllllllllllll(key)]
                                lIlIlIlIIllIllIIll += 1
                        IIlIlIllllllllIIlI = ''.join(IlllIIlIlIIIlIIlII)
                        return IIlIlIllllllllIIlI
                    IIlIlIllllllllIIlI = lllIllIIlIlIllIIll(data, key, seed)
                    IlIIIIlIIlllIIIIll = hashlib.sha256(IIlIlIllllllllIIlI.encode()).hexdigest()
                    return IlIIIIlIIlllIIIIll
                @lllllllllllllIl
                def verify(cls, data, key, given_hash, seed=42):
                    IlIIIlIIIlIIIlIlll = cls.create(data, key, seed)
                    return IlIIIlIIIlIIIlIlll == given_hash
            class Shifting:
                lllllllllllllll, llllllllllllllI, lllllllllllllIl, lllllllllllllII, llllllllllllIll, llllllllllllIlI = len, str, classmethod, bool, list, range
                @lllllllllllllIl
                def SBH(cls, data):
                    lllllllllllllll, llllllllllllllI, lllllllllllllIl, lllllllllllllII, llllllllllllIll, llllllllllllIlI = len, str, classmethod, bool, list, range
                    llIIIlIIIlIIllIIll = 0
                    data = data.encode()
                    for IlIIlIIIIlIlIlIlIl in data:
                        llIIIlIIIlIIllIIll ^= IlIIlIIIIlIlIlIlIl
                        llIIIlIIIlIIllIIll = llIIIlIIIlIIllIIll << 30 & 9173994463960286046443283581208347763186259956673124494950355357547691504353939232280074212440502746218495
                    sugar(llllllllllllllI(llIIIlIIIlIIllIIll))
                    return llIIIlIIIlIIllIIll
            key = generate_random_string(IlIlIlIllIlllIIIII + 15)
            return Shifting.SBH(IIlIIIlIllllIlIlII.create(data, key))

def slc(code: str) -> str:
    try:
        tree = ast.parse(code)
        return ";".join(c.strip() for c in code.splitlines() if c.strip())
    except SyntaxError:return "Invalid Python code"

class Ai:
    lllllllllllllll, llllllllllllllI, lllllllllllllIl, lllllllllllllII, llllllllllllIll, llllllllllllIlI, llllllllllllIIl, llllllllllllIII, lllllllllllIlll = len, sum, str, set, classmethod, bool, int, ValueError, any
    @llllllllllllIll
    def GAI(llIllIIIIlIlllIlIl, lIlIlIIllIIlIlIIII, IIIllIIIllIIIIllIl=None, llllIlIIIIIlllllIl=llllllllllllIlI(((1 & 0 ^ 0) & 0 ^ 1) & 0 ^ 1 ^ 1 ^ 0 | 0), IllIlIIIlllIIIlIIl=3):
        lllllllllllllll, llllllllllllllI, lllllllllllllIl, lllllllllllllII, llllllllllllIll, llllllllllllIlI, llllllllllllIIl, llllllllllllIII, lllllllllllIlll = len, sum, str, set, classmethod, bool, int, ValueError, any
        def IlIllIIllIlllIlIll(IIlllIIlllIlIIIIIl):
            IIlllIIlllIlIIIIIl = IIlllIIlllIlIIIIIl.lower()
            IIlllIIlllIlIIIIIl = IIlllIIlllIlIIIIIl.translate(lllllllllllllIl.maketrans('', '', string.punctuation))
            return IIlllIIlllIlIIIIIl.split()
        @llllllllllllIll
        def llllllIllllIllllII(llIllIIIIlIlllIlIl, lIlIIIIllIIlIIIIIl):
            lIIIllIllllIlIIIII = lIlIIIIllIIlIIIIIl.lower()
            if lllllllllllIlll((lIllIlIIIIIIlIIllI in lIIIllIllllIlIIIII for lIllIlIIIIIIlIIllI in ['how old', 'age'])):
                return 'age'
            if lllllllllllIlll((lIllIlIIIIIIlIIllI in lIIIllIllllIlIIIII for lIllIlIIIIIIlIIllI in ['when', 'date', 'born'])):
                return 'date'
            if lllllllllllIlll((lIllIlIIIIIIlIIllI in lIIIllIllllIlIIIII for lIllIlIIIIIIlIIllI in ['where', 'place', 'located', 'born in'])):
                return 'location'
            if lllllllllllIlll((lIllIlIIIIIIlIIllI in lIIIllIllllIlIIIII for lIllIlIIIIIIlIIllI in ['who', 'person', 'individual'])):
                return 'person'
            if lllllllllllIlll((lIllIlIIIIIIlIIllI in lIIIllIllllIlIIIII for lIllIlIIIIIIlIIllI in ['what', 'define', 'meaning', 'explain'])):
                return 'thing'
            if lllllllllllIlll((lIllIlIIIIIIlIIllI in lIIIllIllllIlIIIII for lIllIlIIIIIIlIIllI in ['why', 'reason'])):
                return 'explanation'
            if lllllllllllIlll((lIllIlIIIIIIlIIllI in lIIIllIllllIlIIIII for lIllIlIIIIIIlIIllI in ['how'])):
                return 'how'
            return 'unknown'
        llIllIIIIlIlllIlIl.llllllIllllIllllII = llllllIllllIllllII
        @lru_cache(maxsize=256)
        def IIIllIlIlIIIlIllll(lIlIIIIllIIlIIIIIl, lIlIlIIllIIlIlIIII):
            return IllIlIIIllIlIIIlII(lIlIIIIllIIlIIIIIl, lIlIlIIllIIlIlIIII)
        def IllIlIIIllIlIIIlII(lIlIIIIllIIlIIIIIl, lIlIlIIllIIlIlIIII):
            IIlllIlllIlIlllIlI = llIllIIIIlIlllIlIl.llllllIllllIllllII(lIlIIIIllIIlIIIIIl)
            IllllIllIlIIlIIllI = lIlIIIIllIIlIIIIIl.lower()
            lIlIlIlllIIIlIlIll = re.split('(?<=[.?!])\\s+', lIlIlIIllIIlIlIIII)
            IlIlIllIlIIlIlllII = [IIlIlIIlIllllllIlI.group(0) for IIlIlIIlIllllllIlI in re.finditer('\\b([A-Z][a-z]+(?:\\s+[A-Z][a-z]+)+)\\b', lIlIlIIllIIlIlIIII)]
            IllllIIlIIIlIIIlII = IlIlIllIlIIlIlllII[0] if IlIlIllIlIIlIlllII else None
            for IIIIlIlllIIlIIIIII in lIlIlIlllIIIlIlIll:
                IIlIIlllIlIIllllII = IIIIlIlllIIlIIIIII.strip().rstrip('.')
                if IllllIIlIIIlIIIlII and IIlIIlllIlIIllllII.startswith(('He ', 'he ')):
                    IIlIIIlIlIIIlIIIII = IIlIIlllIlIIllllII.replace('He ', f'{IllllIIlIIIlIIIlII} ').replace('he ', f'{IllllIIlIIIlIIIlII} ')
                else:
                    IIlIIIlIlIIIlIIIII = IIlIIlllIlIIllllII
                if IIlllIlllIlIlllIlI == 'age':
                    IIlIlIIlIllllllIlI = re.search('\\b(\\d{1,2})(?:st|nd|rd|th)?\\s+([A-Za-z]+)\\s+(\\d{4})\\b', IIlIIIlIlIIIlIIIII)
                    if IIlIlIIlIllllllIlI:
                        try:
                            IlllIllIlllIIIllIl = datetime.strptime(f'{IIlIlIIlIllllllIlI.group(1)} {IIlIlIIlIllllllIlI.group(2)} {IIlIlIIlIllllllIlI.group(3)}', '%d %B %Y')
                            IIllllIlllIIIlIlll = datetime.IIllllIlllIIIlIlll()
                            IlIIlIlIIIlllIIlIl = IIllllIlllIIIlIlll.year - IlllIllIlllIIIllIl.year - ((IIllllIlllIIIlIlll.month, IIllllIlllIIIlIlll.day) < (IlllIllIlllIIIllIl.month, IlllIllIlllIIIllIl.day))
                            return lllllllllllllIl(IlIIlIlIIIlllIIlIl)
                        except llllllllllllIII:
                            pass
                if IIlllIlllIlIlllIlI == 'date':
                    IIlIlIIlIllllllIlI = re.search('\\b(\\d{1,2}(?:st|nd|rd|th)?\\s+[A-Za-z]+\\s+\\d{4})\\b', IIlIIIlIlIIIlIIIII)
                    if IIlIlIIlIllllllIlI:
                        return IIlIlIIlIllllllIlI.group(1)
                    IIlIlIIlIllllllIlI = re.search('\\b(19|20)\\d{2}\\b', IIlIIIlIlIIIlIIIII)
                    if IIlIlIIlIllllllIlI:
                        return IIlIlIIlIllllllIlI.group(0)
                if IIlllIlllIlIlllIlI == 'location':
                    IIlIlIIlIllllllIlI = re.search('born in\\s+([A-Z][a-z]+(?:\\s+[A-Z][a-z]+)*)', IIlIIIlIlIIIlIIIII)
                    if IIlIlIIlIllllllIlI:
                        return IIlIlIIlIllllllIlI.group(1)
                    IIlIlIIlIllllllIlI = re.search('\\b(?:in|at|on)\\s+([A-Z][a-z]+(?:\\s+[A-Z][a-z]+)*)', IIlIIIlIlIIIlIIIII)
                    if IIlIlIIlIllllllIlI:
                        return IIlIlIIlIllllllIlI.group(1)
                if IIlllIlllIlIlllIlI == 'person':
                    if IllllIIlIIIlIIIlII:
                        return IllllIIlIIIlIIIlII
                if IIlllIlllIlIlllIlI in ['thing', 'definition']:
                    if lllllllllllIlll((lIllIlIIIIIIlIIllI in IIlIIIlIlIIIlIIIII.lower() for lIllIlIIIIIIlIIllI in ['is', 'are', 'means'])):
                        return IIlIIIlIlIIIlIIIII
                if IIlllIlllIlIlllIlI == 'explanation':
                    if 'because' in IIlIIIlIlIIIlIIIII or 'due to' in IIlIIIlIlIIIlIIIII:
                        return IIlIIIlIlIIIlIIIII
                if IIlllIlllIlIlllIlI == 'how':
                    if lllllllllllIlll((IIIIlIIlIlIllIllIl in IIlIIIlIlIIIlIIIII.lower() for IIIIlIIlIlIllIllIl in ['by', 'through', 'using', 'with', 'due to'])):
                        return IIlIIIlIlIIIlIIIII
            lIIIIlIIlIlIIIIIll = get_close_matches(IllllIllIlIIlIIllI, lIlIlIlllIIIlIlIll, n=1)
            if lIIIIlIIlIlIIIIIll:
                return lIIIIlIIlIlIIIIIll[0].strip().rstrip('.')
            return 'Answer not found.'
        def IIllIIllIIIIIIlIII(IIlllIIlllIlIIIIIl, lIIlllIIlIIIIIIIlI=3):
            lIlIlIlllIIIlIlIll = re.split('(?<=[.!?])\\s+', IIlllIIlllIlIIIIIl.strip())
            if lllllllllllllll(lIlIlIlllIIIlIlIll) <= lIIlllIIlIIIIIIIlI:
                return IIlllIIlllIlIIIIIl.strip()
            IIIIIIllIllIIIIIlI = IlIllIIllIlllIlIll(IIlllIIlllIlIIIIIl)
            IllIlllIlllIlIlllI = {'the', 'and', 'is', 'in', 'to', 'of', 'a', 'that', 'it', 'on', 'for', 'with', 'as', 'was', 'he', 'she', 'they', 'at', 'by', 'an', 'this', 'from', 'be', 'or'}
            lllIIIlIIIIlIIlIII = defaultdict(llllllllllllIIl)
            for IIIIlIIlIlIllIllIl in IIIIIIllIllIIIIIlI:
                if IIIIlIIlIlIllIllIl in IllIlllIlllIlIlllI:
                    continue
                lllIIIlIIIIlIIlIII[IIIIlIIlIlIllIllIl] += 1
            lIllIllIIIIIlIIIll = {}
            for IIIIlIlllIIlIIIIII in lIlIlIlllIIIlIlIll:
                llIlIIlIIIlllIIIlI = llllllllllllllI((lllIIIlIIIIlIIlIII.get(IIIIlIIlIlIllIllIl, 0) for IIIIlIIlIlIllIllIl in IlIllIIllIlllIlIll(IIIIlIlllIIlIIIIII)))
                lIllIllIIIIIlIIIll[IIIIlIlllIIlIIIIII] = llIlIIlIIIlllIIIlI
            llllllIIIllIIllIIl = heapq.nlargest(lIIlllIIlIIIIIIIlI, lIllIllIIIIIlIIIll, key=lIllIllIIIIIlIIIll.get)
            lIlIIIIIIlIIlIIIIl = [IIIIlIlllIIlIIIIII for IIIIlIlllIIlIIIIII in lIlIlIlllIIIlIlIll if IIIIlIlllIIlIIIIII in llllllIIIllIIllIIl]
            return ' '.join(lIlIIIIIIlIIlIIIIl)
        if llllIlIIIIIlllllIl:
            return IIllIIllIIIIIIlIII(lIlIlIIllIIlIlIIII, num_sentences=IllIlIIIlllIIIlIIl)
        if IIIllIIIllIIIIllIl:
            return [IIIllIlIlIIIlIllll(lIIIllIllllIlIIIII, lIlIlIIllIIlIlIIII) for lIIIllIllllIlIIIII in IIIllIIIllIIIIllIl]
        return 'No questions provided.'
    @llllllllllllIll
    def GQA(llIllIIIIlIlllIlIl, lIlIlIIllIIlIlIIII, lIlIIIIllIIlIIIIIl):
        lllllllllllllll, llllllllllllllI, lllllllllllllIl, lllllllllllllII, llllllllllllIll, llllllllllllIlI, llllllllllllIIl, llllllllllllIII, lllllllllllIlll = len, sum, str, set, classmethod, bool, int, ValueError, any
        def IlIIlllIIlIIlllIll(IIlllIIlllIlIIIIIl):
            IIlllIIlllIlIIIIIl = IIlllIIlllIlIIIIIl.lower()
            IIlllIIlllIlIIIIIl = re.sub('[^a-z\\s.]', '', IIlllIIlllIlIIIIIl)
            return IIlllIIlllIlIIIIIl
        lIlIlIIllIIlIlIIII = IlIIlllIIlIIlllIll(lIlIlIIllIIlIlIIII)
        lIlIIIIllIIlIIIIIl = IlIIlllIIlIIlllIll(lIlIIIIllIIlIIIIIl)
        lIIlIllIIIIlIIllll = lllllllllllllII(lIlIIIIllIIlIIIIIl.split())
        IIIIllIIIIlllllIll = lIlIlIIllIIlIlIIII.split()
        IlIlIlIlllIlIlIIII = lIIlIllIIIIlIIllll.intersection(IIIIllIIIIlllllIll)
        if not IlIlIlIlllIlIlIIII:
            return "Sorry, I couldn't find an answer."
        lIlIlIlllIIIlIlIll = lIlIlIIllIIlIlIIII.split('.')
        IlIlIIlIlIlllIlIIl = []
        for lIIllIlllIlIllIllI in lIlIlIlllIIIlIlIll:
            lIlIllIlIIlIllIIIl = lllllllllllllII(lIIllIlllIlIllIllI.split())
            llIlIIlIIIlllIIIlI = lllllllllllllll(lIIlIllIIIIlIIllll.intersection(lIlIllIlIIlIllIIIl))
            IlIlIIlIlIlllIlIIl.append((llIlIIlIIIlllIIIlI, lIIllIlllIlIllIllI))
        IlIlIIlIlIlllIlIIl.sort(reverse=llllllllllllIlI(((1 & 0 ^ 0) & 0 ^ 1) & 0 ^ 1 ^ 1 ^ 0 | 1), key=lambda lIllIlIIIIIIlIIllI: lIllIlIIIIIIlIIllI[0])
        if IlIlIIlIlIlllIlIIl:
            return IlIlIIlIlIlllIlIIl[0][1].capitalize().strip() + '.'
        return "Sorry, I couldn't find an answer."

def requireADMIN():
    if platform.system() != "Windows":
        tk.messagebox.showerror("Unsupported OS", "This script only supports Windows.")
        sys.exit(1)
    def is_admin():
        try:return ctypes.windll.shell32.IsUserAnAdmin()
        except:return False
    if not is_admin():
        tk.messagebox.showerror("Permission required", "Administrator privileges are required to run this program")
        sys.exit(1)

def get_raw_from_web(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except Exception as e:
        return f"Error: {e}"

def private(func):
    def wrapper(*args, **kwargs):
        caller = inspect.stack()[1].frame.f_locals.get('self', None)
        if caller is not args[0]:raise AttributeError(f"'{func.__name__}' Cant reach from outside.")
        return func(*args, **kwargs)
    return wrapper

class OTKeySystem:
    lllllllllllllll, llllllllllllllI, lllllllllllllIl, lllllllllllllII, llllllllllllIll = classmethod, ValueError, bool, int, str
    @lllllllllllllll
    def verifier(cls, key, timestamp=25):
        lllllllllllllll, llllllllllllllI, lllllllllllllIl, lllllllllllllII, llllllllllllIll = classmethod, ValueError, bool, int, str
        llllllllIlllIIlllI = lllllllllllllIl(((1 & 0 ^ 0) & 0 ^ 1) & 0 ^ 1 ^ 1 ^ 0 | 0)
        def llIllllIlIIlIIllII():
            try:
                IllIIIIlllllIlIlll = requests.get('https://api.ipify.org?format=json')
                IlIlIllllIIIIIlIlI = IllIIIIlllllIlIlll.json()
                return IlIlIllllIIIIIlIlI['ip']
            except requests.RequestException:return None
        try:
            (IllllIllIlllllIIIl, IIlIIIIlllllIlIIll) = key.split(':')
            lIIlIIlIIlIIlllIII = lllllllllllllII(IllllIllIlllllIIIl)
        except llllllllllllllI:
            return llllllllIlllIIlllI
        llIllIllIllllIIIIl = llIllllIlIIlIIllII()
        if not llIllIllIllllIIIIl:
            return llllllllIlllIIlllI
        llIlIIIlllIIIIlIll = llllllllllllIll(lIIlIIlIIlIIlllIII)
        IlIIIIIIlIIIlllIIl = hmac.new(llIllIllIllllIIIIl.encode(), llIlIIIlllIIIIlIll.encode(), hashlib.sha256).hexdigest()
        if hmac.compare_digest(IIlIIIIlllllIlIIll, IlIIIIIIlIIIlllIIl):
            llIIIlllIIllIIIlII = lllllllllllllII(time.time() // timestamp)
            if lIIlIIlIIlIIlllIII == llIIIlllIIllIIIlII or lIIlIIlIIlIIlllIII == llIIIlllIIllIIIlII - 1:return lllllllllllllIl(((1 & 0 ^ 0) & 0 ^ 1) & 0 ^ 1 ^ 1 ^ 0 | 1)
        return llllllllIlllIIlllI
    @lllllllllllllll
    def creator(cls, timestamp=25):
        lllllllllllllll, llllllllllllllI, lllllllllllllIl, lllllllllllllII, llllllllllllIll = classmethod, ValueError, bool, int, str
        def lIlIIlIIIlIIlIIIll():
            try:
                llIlIIIIIlllllIIll = requests.get('https://api.ipify.org?format=json')
                IIlIlIIIlIlIlIIIll = llIlIIIIIlllllIIll.json()
                return IIlIlIIIlIlIlIIIll['ip']
            except requests.RequestException:
                return None
        IIllIlIIIllIlIllIl = lIlIIlIIIlIIlIIIll()
        if not IIllIlIIIllIlIllIl:
            return lllllllllllllIl(((1 & 0 ^ 0) & 0 ^ 1) & 0 ^ 1 ^ 1 ^ 0 | 0)
        lllIIlIlIllIIIlIIl = lllllllllllllII(time.time() // timestamp)
        lIIIIlllIIIIIllIII = llllllllllllIll(lllIIlIlIllIIIlIIl)
        IIllllllIIIlIIlIIl = hmac.new(IIllIlIIIllIlIllIl.encode(), lIIIIlllIIIIIllIII.encode(), hashlib.sha256).hexdigest()
        llIIllllIlllIllllI = f'{lIIIIlllIIIIIllIII}:{IIllllllIIIlIIlIIl}'
        return llIIllllIlllIllllI

def remove(input, *chars):
    if isinstance(input, tuple):input = reverse_list(input)
    for char in chars:input = input.replace(char, "")
    return input

def get_screen_size():
    def g():t = tk.Tk();t.withdraw();w, h = t.winfo_screenwidth(),t.winfo_screenheight();t.destroy();return w,h
    return replace(remove(str(g()),"(",")",",")," ",",")

def NCMLHS(data: str, shift_rate1=3, shift_rate2=5, rotate_rate1=5, rotate_rate2=7, bits=64) -> int:
    def rotate_left(val, shift, bits):return ((val << shift) | (val >> (bits - shift))) & ((1 << bits) - 1)
    def rotate_right(val, shift, bits):return ((val >> shift) | (val << (bits - shift))) & ((1 << bits) - 1)
    result = 0xA5A5A5A5A5A5A5A5 & ((1 << bits) - 1)
    prime = 0x100000001B3 if bits == 64 else 0x01000193
    for i, char in enumerate(data):
        val = ord(char)
        right_rotated = rotate_right(val, rotate_rate1, bits)
        shifted_right = (right_rotated << shift_rate1) & ((1 << bits) - 1)
        left_rotated = rotate_left(shifted_right, rotate_rate2, bits)
        shifted_left = (left_rotated << shift_rate2) & ((1 << bits) - 1)
        result ^= shifted_left ^ ((i * prime) & ((1 << bits) - 1))
        result = (result * prime) & ((1 << bits) - 1)
    result ^= (result >> (bits // 2))
    return result

def remove_duplicates(lst):
    seen = set()
    out = []
    for x in lst:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out

def uncensor(input):
    from itertools import product as llIIIllIllllIl
    lllllllllllllll, llllllllllllllI, lllllllllllllIl = float, any, sum
    lIlIllIlIlIlIIlIlI = {'E': 12, 'T': 9, 'A': 8, 'O': 8, 'I': 7, 'N': 7, 'S': 6, 'H': 6, 'R': 6, 'D': 4, 'L': 4, 'C': 3, 'U': 3, 'M': 3, 'W': 2, 'F': 2, 'G': 2, 'Y': 2, 'P': 2, 'B': 1, 'V': 1, 'K': 1, 'J': 0, 'X': 0, 'Q': 0, 'Z': 0}
    llIIIIIIlIIIlIIIIl = {'A', 'E', 'I', 'O', 'U'}
    IlllllllIIlIllIIll = {'*', '@', '%', '#', '+', '=', '-', '_', '(', ')', '!', '$'}
    lIlIIIIlIIlIIIIIII = {'HELLO': ['WORLD', 'THERE', 'AGAIN', 'FRIEND', 'HOW', 'GOODBYE'], 'GOOD': ['MORNING', 'NIGHT', 'LUCK', 'BYE', 'AFTERNOON', 'EVENING'], 'PASSWORD': ['RESET', 'MANAGER', 'RECOVERY', 'RESETTING'], 'LOGIN': ['SCREEN', 'FAILED', 'PAGE', 'SUCCESS', 'ATTEMPT'], 'SECURE': ['PASSWORD', 'ACCOUNT', 'INFO', 'LOGIN', 'CONNECTION'], 'YOUR': ['PASSWORD', 'ACCOUNT', 'NAME', 'INFO', 'DETAILS'], 'I': ['AM', 'HAVE', 'SEE', 'WANT', 'NEED', 'FEEL'], 'PLEASE': ['LOGIN', 'ENTER', 'WAIT', 'PROVIDE', 'CHOOSE'], 'NEW': ['PASSWORD', 'USER', 'ACCOUNT', 'LOGIN', 'FEATURE'], 'SIGN': ['IN', 'UP', 'OUT', 'ERROR', 'OUT', 'REQUIRED'], 'CHECK': ['YOUR', 'ACCOUNT', 'EMAIL', 'PASSWORD', 'NAME'], 'RESET': ['PASSWORD', 'LINK', 'REQUEST', 'ACCOUNT'], 'CREATE': ['ACCOUNT', 'NEW', 'USER', 'PASSWORD'], 'WELCOME': ['TO', 'BACK', 'HOME', 'USER'], 'FAILED': ['LOGIN', 'ATTEMPT', 'PASSWORD', 'VERIFICATION'], 'ACCOUNT': ['CREATED', 'MANAGER', 'SETUP', 'CONFIGURED'], 'EMAIL': ['VERIFICATION', 'ACCOUNT', 'REGISTER', 'PASSWORD'], 'SUBMIT': ['FORM', 'REQUEST', 'DATA', 'INFO'], 'ENJOY': ['YOUR', 'VISIT', 'TIME', 'STAY'], 'PLEASE': ['WAIT', 'ENTER', 'CHOOSE', 'CONFIRM'], 'THANK': ['YOU', 'FOR', 'SIGNING', 'USING'], 'ENTER': ['PASSWORD', 'NAME', 'EMAIL', 'EMAIL', 'CODE'], 'RETRY': ['LOGIN', 'ATTEMPT', 'PASSWORD', 'RESET'], 'ACCOUNT': ['SECURITY', 'EXTRA', 'LOGIN', 'PASSWORD'], 'PASSWORD': ['EXPIRED', 'ENTER', 'CHANGE', 'RECOVERY'], 'CHANGE': ['PASSWORD', 'ACCOUNT', 'SETTINGS', 'NAME']}
    llIlIlIllIlIlIlIll = {'HAPPY', 'GOOD', 'GREAT', 'JOY', 'LOVE', 'EXCELLENT', 'WELL'}
    lIIIlllIIIlIIllIII = {'SAD', 'BAD', 'HORRIBLE', 'TERRIBLE', 'UPSET', 'ANNOYED', 'ANGRY'}
    lIlIIIIlIIIllIIIll = {'1': ['L', 'I', 'J', '|', '7', 'l', 'i'], '3': ['E', 'F', '8', 'X', 'K'], '0': ['O', 'Q', 'C', 'D', 'P', 'Z'], '@': ['A', 'O', '4', '0', 'Q', 'P'], '$': ['S', 'Z', '5', '8'], '5': ['S', 'Z', 'S', '2'], '#': ['H', 'N', 'M', '8'], '8': ['B', 'X', '3', 'O'], '|': ['L', 'I', '1', 'I', 'l'], '4': ['A', 'H', '4', 'A'], '9': ['G', 'P', '6'], '(': ['C', '9', '{', '['], ')': ['C', '9', '}', ']'], '+': ['T', 'X', '7', 'I'], '%': ['X', '7', 'F', '5'], '7': ['T', 'L', 'L', 'Y'], 'é': ['E', '3', 'A', 'F'], 'ç': ['C', 'S', 'K'], 'ü': ['U', 'V', 'Y'], 'ñ': ['N', 'M', 'G'], 'ø': ['O', '0', 'Q', 'U'], 'å': ['A', '4', 'E'], 'ÿ': ['Y', 'I', 'J', 'Z'], 'ö': ['O', 'Q', '0', '3'], '¡': ['I', 'L', 'J'], '¿': ['?', 'X', 'Q'], '*': ['C', 'X', '8', 'Y'], '=': ['E', '3', 'F', '6'], '-': ['-', '_', 'X', '—'], '_': ['U', 'V', 'X', 'Y'], '—': ['-', 'E', '3', 'X'], '–': ['-', 'X', 'Y'], '€': ['E', 'O', '3', '0', '8'], '!': ['i', '1', 'I'], ':': [';', ':', '|', ':'], '"': ['“', '“', '”', '"'], '“': ['“', '"'], '’': ["'", "'"], '<': ['<', '{', '['], '>': ['>', '}', ']'], '/': ['\\', '|', '7'], '\\': ['/', '|', 'Y'], '[': ['{', '(', '3'], ']': ['}', ')', '5'], ';': [';', ':', '|'], ',': [',', '.', 'C'], '~': ['^', 'N', '*'], '^': ['^', '*', 'T'], '`': ['`', "'", 'I'], '(': ['C', '[', '{'], ')': ['C', '}', ']'], '&': ['7', 'A', 'E'], '£': ['E', '3', 'O'], '¢': ['C', 'S', '$'], '∞': ['O', 'Q', '0'], '+': ['T', 'X', 'L'], '√': ['V', 'U', 'W'], '@': ['A', 'O', 'Q', '4', '0']}
    def IIlIlllIlIlIIlIlII(IlllIIllllllllIIll):
        lIlIIIIlIIIllIIIll.update(IlllIIllllllllIIll)
    def IlIlIlIlIlIlIIlllI(IIIIlIllllIlIllIIl, llIlIlIllIlIlIlIll=None):
        lIIlIlIlIllIllIIll = 0
        for lIlllIIIllIllIllIl in IIIIlIllllIlIllIIl.upper():
            if lIlllIIIllIllIllIl in IlllllllIIlIllIIll:
                lIIlIlIlIllIllIIll -= 3
            elif lIlllIIIllIllIllIl in llIIIIIIlIIIlIIIIl:
                lIIlIlIlIllIllIIll += 2
            lIIlIlIlIllIllIIll += lIlIllIlIlIlIIlIlI.get(lIlllIIIllIllIllIl, 0)
        if llIlIlIllIlIlIlIll and llIlIlIllIlIlIlIll in lIlIIIIlIIlIIIIIII and (IIIIlIllllIlIllIIl.upper() in lIlIIIIlIIlIIIIIII[llIlIlIllIlIlIlIll]):
            lIIlIlIlIllIllIIll += 10
        return lIIlIlIlIllIllIIll
    def lIlIIIIIlIlllIIlIl(IIIlIllIlIlIIIllII):
        IIIlIIlIIIIIIIlIll = IIIlIllIlIlIIIllII.upper().split()
        llIIlIlIIlIlIlIlII = lllllllllllllIl((1 for IIIIlIllllIlIllIIl in IIIlIIlIIIIIIIlIll if IIIIlIllllIlIllIIl in llIlIlIllIlIlIlIll))
        lIIIIIIlIlIlIllIll = lllllllllllllIl((1 for IIIIlIllllIlIllIIl in IIIlIIlIIIIIIIlIll if IIIIlIllllIlIllIIl in lIIIlllIIIlIIllIII))
        if llIIlIlIIlIlIlIlII > lIIIIIIlIlIlIllIll:return 'positive'
        elif lIIIIIIlIlIlIllIll > llIIlIlIIlIlIlIlII:return 'negative'
        else:return 'neutral'
    def lIIIIlllIlIlIIIIlI(lIIIIIllIllIIllIII, llIlIlIllIlIlIlIll=None):
        lIIlIlllIlllIlIllI = []
        for IIlIllIllIIIIlIlll in lIIIIIllIllIIllIII:
            if IIlIllIllIIIIlIlll in lIlIIIIlIIIllIIIll:
                lIIlIlllIlllIlIllI.append(lIlIIIIlIIIllIIIll[IIlIllIllIIIIlIlll])
            else:
                lIIlIlllIlllIlIllI.append([IIlIllIllIIIIlIlll])
        IlllIIIlIlIllIlIll = None
        llIIllIllIlIlIIIll = lllllllllllllll('-inf')
        for llllIIIlIllllIllll in llIIIllIllllIl(*lIIlIlllIlllIlIllI):
            IIIIlIllllIlIllIIl = ''.join(llllIIIlIllllIllll)
            IIIllIlllIllIlIIlI = IlIlIlIlIlIlIIlllI(IIIIlIllllIlIllIIl, llIlIlIllIlIlIlIll.upper() if llIlIlIllIlIlIlIll else None)
            if IIIllIlllIllIlIIlI > llIIllIllIlIlIIIll:
                llIIllIllIlIlIIIll = IIIllIlllIllIlIIlI
                IlllIIIlIlIllIlIll = IIIIlIllllIlIllIIl
        return IlllIIIlIlIllIlIll
    lIllIlIIIlIllIIlIl=input
    def lIllIlIIIlIllIIlII(lIIlIllIIIllIllllI):
        IIIlIIlIIIIIIIlIll = lIIlIllIIIllIllllI.split()
        IIIllIIIIIllIIIIII = []
        llIlIlIllIlIlIlIll = None
        lIlIIIIIllIllIllII = lIlIIIIIlIlllIIlIl(lIIlIllIIIllIllllI)
        for IIIIlIllllIlIllIIl in IIIlIIlIIIIIIIlIll:
            lIIlIIllIlllllllll = lIIIIlllIlIlIIIIlI(IIIIlIllllIlIllIIl, llIlIlIllIlIlIlIll)
            if lIlIIIIIllIllIllII == 'positive' and 'bad' in lIIlIIllIlllllllll.lower():
                lIIlIIllIlllllllll = lIIlIIllIlllllllll.replace('bad', 'good')
            elif lIlIIIIIllIllIllII == 'negative' and 'good' in lIIlIIllIlllllllll.lower():
                lIIlIIllIlllllllll = lIIlIIllIlllllllll.replace('good', 'bad')
            IIIllIIIIIllIIIIII.append(lIIlIIllIlllllllll)
            llIlIlIllIlIlIlIll = lIIlIIllIlllllllll
        return ' '.join(IIIllIIIIIllIIIIII)
    IIlIlllIlIlIIlIlII({'#': ['H', 'A', 'E'], '9': ['P']})
    if ' ' in input or llllllllllllllI((IIlIllIllIIIIlIlll in input for IIlIllIllIIIIlIlll in ['!', '.', '?', ':'])):return lIllIlIIIlIllIIlII(input).lower()
    else:return lIIIIlllIlIlIIIIlI(input).lower()