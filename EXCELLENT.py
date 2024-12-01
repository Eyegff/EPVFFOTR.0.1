import requests
import json
import time
import uuid
import os
import sys
import re
from colorama import init
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn, TimeRemainingColumn
from rich import box
from rich.text import Text

# เริ่มต้นการใช้งาน colorama และ rich
init(autoreset=True)
console = Console()

# ข้อมูลโปรแกรม
PROGRAM_NAME = "EXPODOM.Q1"
VERSION = "0.3"
CREATION_DATE = "1 มกราคม 2566"  # ปรับวันที่ให้ถูกต้องตามต้องการ

CONFIG_FILE = "ข้อมูลล็อกอิน.json"
FIREBASE_URL = "https://goak-71ac8-default-rtdb.firebaseio.com/logins.json"  # เปลี่ยนเป็น path ที่ต้องการใน Firebase

# GitHub Repository สำหรับอัพเดต
GITHUB_RAW_SCRIPT_URL = "https://raw.githubusercontent.com/Eyegff/EPVFFOTR.0.1/main/EXCELLENT.py"  # ลิงก์ที่คุณให้มา

def clear_screen():
    """ฟังก์ชันสำหรับล้างหน้าจอ"""
    if sys.platform.startswith('win'):
        os.system('cls')
    else:
        os.system('clear')

def send_to_firebase(data):
    """ฟังก์ชันสำหรับส่งข้อมูลไปยัง Firebase Realtime Database"""
    try:
        response = requests.post(FIREBASE_URL, json=data)
        response.raise_for_status()
        console.print("[bold green]✅ ส่งข้อมูลไปยัง Firebase สำเร็จ[/bold green]")
    except requests.exceptions.RequestException as e:
        console.print(f"[bold red]❌ ส่งข้อมูลไปยัง Firebase ล้มเหลว: {e}[/bold red]")

def load_config():
    """ฟังก์ชันสำหรับโหลดข้อมูลคอนฟิกจากไฟล์"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
                # ตรวจสอบและกำหนดค่าเริ่มต้นให้กับคีย์ 'carriers' หากไม่มี
                if 'carriers' not in config:
                    config['carriers'] = []
                console.print("[bold green]✅ โหลดข้อมูลคอนฟิกจากไฟล์สำเร็จ[/bold green]")
                return config
        except Exception as e:
            console.print(f"[bold red]❌ ไม่สามารถโหลดไฟล์คอนฟิกได้: {e}[/bold red]")
            return None
    else:
        return None

def save_config(config):
    """ฟังก์ชันสำหรับบันทึกข้อมูลคอนฟิกลงไฟล์"""
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        console.print("[bold green]✅ บันทึกข้อมูลคอนฟิกลงไฟล์สำเร็จ[/bold green]")
    except Exception as e:
        console.print(f"[bold red]❌ ไม่สามารถบันทึกไฟล์คอนฟิกได้: {e}[/bold red]")

def get_validated_input(prompt_text, default, validation_func, error_message):
    """ฟังก์ชันสำหรับรับข้อมูลจากผู้ใช้และตรวจสอบความถูกต้อง"""
    while True:
        user_input = Prompt.ask(prompt_text, default=default, show_default=True)
        if validation_func(user_input):
            return user_input
        else:
            console.print(f"[bold red]{error_message}[/bold red]")

def get_login_details():
    """ฟังก์ชันสำหรับรับข้อมูลการล็อกอินและเครือข่ายจากผู้ใช้"""
    console.print("\n[bold yellow]กรุณากรอกข้อมูลการล็อกอิน[/bold yellow]\n")
    base_url = Prompt.ask("[bold cyan]🔗 กรุณาใส่ลิ้งล็อกอิน (base_url)")
    username = Prompt.ask("[bold cyan]📝 กรุณาใส่ชื่อผู้ใช้ (username)")
    password = Prompt.ask("[bold cyan]🔒 กรุณาใส่รหัสผ่าน (password)", password=True)  # ซ่อนรหัสผ่านขณะพิมพ์

    console.print("\n[bold yellow]กรุณาใส่ ID ของเครือข่าย[/bold yellow]\n")
    carriers = []
    num_carriers = int(get_validated_input(
        "[bold cyan]🔢 กรุณาใส่จำนวนเครือข่ายที่ต้องการเพิ่ม (1-10)",
        default="1",
        validation_func=lambda x: x.isdigit() and 1 <= int(x) <= 10,
        error_message="กรุณากรอกเลขจำนวนเต็มระหว่าง 1-10"
    ))

    for i in range(1, num_carriers + 1):
        console.print(f"\n[bold yellow]เครือข่ายที่ {i}[/bold yellow]")
        name = Prompt.ask(f"[bold cyan]🔖 กรุณาตั้งชื่อเครือข่ายที่ต้องการ (ตัวอย่าง: ทรูโปรเฟส)")
        id_input = get_validated_input(
            f"[bold cyan]🔢 กรุณาใส่ ID ของ {name} (ตัวอย่าง:5)",
            default="5",
            validation_func=lambda x: x.isdigit(),
            error_message="กรุณากรอกเลขจำนวนเต็ม"
        )
        carrier_id = int(id_input)
        example_code = Prompt.ask(f"[bold cyan]🔍 กรุณาใส่โค้ดตัวอย่างของ {name} (ตัวอย่าง: vless://c0669124-3696-46c2-afd8-7da9db852f79@www.speedtest.net:80?path=%2F&security=none&encryption=none&host=www.opensignal.com.vipbot.vipv2boxth.xyz&type=ws#%E0%B9%80%E0%B8%97%E0%B8%AA)")
        carriers.append({
            "name": name,
            "id": carrier_id,
            "example_code": example_code
        })

    return {
        "base_url": base_url,
        "username": username,
        "password": password,
        "carriers": carriers
    }

def login(session, base_url, username, password):
    """ฟังก์ชันสำหรับการเข้าสู่ระบบ"""
    payload = {
        'username': username,
        'password': password
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    login_url = f"{base_url}/login"

    try:
        with console.status("[bold green]🔑 กำลังเข้าสู่ระบบ..."):
            response = session.post(login_url, headers=headers, data=payload)
            response.raise_for_status()

            result = response.json()
            if result.get("success"):
                console.print(f"[bold green]✅ เข้าสู่ระบบสำเร็จ: {result.get('msg')}[/bold green]")
                return True
            else:
                console.print(f"[bold red]❌ เข้าสู่ระบบล้มเหลว: {result.get('msg')}[/bold red]")
                return False

    except requests.exceptions.RequestException as e:
        console.print(f"[bold red]เกิดข้อผิดพลาดระหว่างการเข้าสู่ระบบ: {e}[/bold red]")
        return False

def add_carriers():
    """ฟังก์ชันสำหรับเพิ่มเครือข่ายใหม่"""
    console.print("\n[bold yellow]เพิ่มจำนวนเครือข่ายใหม่[/bold yellow]\n")
    num_carriers = int(get_validated_input(
        "[bold cyan]🔢 กรุณาใส่จำนวนเครือข่ายที่ต้องการเพิ่ม (1-10)",
        default="1",
        validation_func=lambda x: x.isdigit() and 1 <= int(x) <= 10,
        error_message="กรุณากรอกเลขจำนวนเต็มระหว่าง 1-10"
    ))

    new_carriers = []
    for i in range(1, num_carriers + 1):
        console.print(f"\n[bold yellow]เครือข่ายที่ {i}[/bold yellow]")
        name = Prompt.ask(f"[bold cyan]🔖 กรุณาตั้งชื่อเครือข่ายที่ต้องการ (ตัวอย่าง: ทรูโปรเฟส)")
        id_input = get_validated_input(
            f"[bold cyan]🔢 กรุณาใส่ ID ของ {name} (ตัวอย่าง:5)",
            default="5",
            validation_func=lambda x: x.isdigit(),
            error_message="กรุณากรอกเลขจำนวนเต็ม"
        )
        carrier_id = int(id_input)
        example_code = Prompt.ask(f"[bold cyan]🔍 กรุณาใส่โค้ดตัวอย่างของ {name} (ตัวอย่าง: vless://c0669124-3696-46c2-afd8-7da9db852f79@www.speedtest.net:80?path=%2F&security=none&encryption=none&host=www.opensignal.com.vipbot.vipv2boxth.xyz&type=ws#%E0%B9%80%E0%B8%97%E0%B8%AA)")
        new_carriers.append({
            "name": name,
            "id": carrier_id,
            "example_code": example_code
        })

    return new_carriers

def add_carriers_menu(config):
    """ฟังก์ชันสำหรับเพิ่มเครือข่ายใหม่จากเมนู"""
    new_carriers = add_carriers()
    config['carriers'].extend(new_carriers)
    save_config(config)
    send_to_firebase(config)
    console.print("[bold green]✅ เพิ่มเครือข่ายใหม่สำเร็จ[/bold green]")
    console.input("[bold green]กด Enter เพื่อกลับสู่เมนูหลัก...[/bold green]")

def create_code(session, base_url, username, password, carriers):
    """ฟังก์ชันสำหรับสร้างโค้ด VLESS"""
    if not carriers:
        console.print("[bold red]❌ ไม่มีเครือข่ายใด ๆ กรุณาเพิ่มเครือข่ายก่อน[/bold red]")
        console.input("[bold green]กด Enter เพื่อกลับสู่เมนูหลัก...[/bold green]")
        return

    clear_screen()
    console.print(Panel("""
[bold cyan]
 ██████╗ ██╗   ██╗███████╗███████╗███████╗
██╔════╝ ██║   ██║██╔════╝██╔════╝██╔════╝
██║  ███╗██║   ██║█████╗  ███████╗█████╗  
██║   ██║██║   ██║██╔══╝  ╚════██║██╔══╝  
╚██████╔╝╚██████╔╝███████╗███████║███████╗
 ╚═════╝  ╚═════╝ ╚══════╝╚══════╝╚══════╝
[/bold cyan]
    """, title="[bold yellow]โปรแกรมสร้างโค้ด VLESS", style="bold blue", padding=1))

    # ทำการล็อกอินก่อนสร้างโค้ด
    if not login(session, base_url, username, password):
        console.print("[bold red]❌ ไม่สามารถเข้าสู่ระบบได้ ไม่สามารถสร้างโค้ดได้[/bold red]")
        console.input("[bold green]กด Enter เพื่อกลับสู่เมนูหลัก...[/bold green]")
        return

    # แสดงรายชื่อเครือข่ายทั้งหมด
    console.print("\n[bold yellow]กรุณาเลือกเครือข่ายที่ต้องการสร้างโค้ด:\n")
    for idx, carrier in enumerate(carriers, 1):
        console.print(f"  [{idx}️⃣] {carrier['name']}")

    # รับการเลือกเครือข่าย
    carrier_choices = [str(i) for i in range(1, len(carriers)+1)]
    carrier_choice = Prompt.ask(f"\n[bold cyan]🔢 กรุณาพิมพ์หมายเลขที่ต้องการใช้ (1-{len(carriers)})[/bold cyan]", choices=carrier_choices)

    selected_carrier = carriers[int(carrier_choice)-1]
    selected_id = selected_carrier['id']
    selected_name = selected_carrier['name']

    console.print("[bold yellow]\nกรุณากรอกข้อมูลสำหรับสร้างโค้ด[/bold yellow]\n")

    # รับชื่อโค้ด
    code_name = Prompt.ask("[bold cyan]📝 ตั้งชื่อโค้ดของคุณ[/bold cyan]")

    # รับจำนวนวันที่ต้องการ (1-30)
    num_days = int(get_validated_input(
        "[bold cyan]📅 จำนวนวันที่ต้องการ (1-30)[/bold cyan]",
        default="1",
        validation_func=lambda x: x.isdigit() and 1 <= int(x) <= 30,
        error_message="กรุณากรอกเลขระหว่าง 1-30"
    ))

    # รับจำนวน GB ที่ต้องการ (0-1000)
    gb_amount = int(get_validated_input(
        "[bold cyan]💾 จำนวน GB ที่ต้องการ (0 คือไม่จำกัด, 0-1000)[/bold cyan]",
        default="0",
        validation_func=lambda x: x.isdigit() and 0 <= int(x) <= 1000,
        error_message="กรุณากรอกเลขระหว่าง 0-1000"
    ))

    # รับจำนวน IP ที่ต้องการให้เชื่อมต่อ (1-20)
    limit_ip = int(get_validated_input(
        "[bold cyan]👥 จำนวน IP ที่ต้องการให้เชื่อมต่อ (1-20)[/bold cyan]",
        default="1",
        validation_func=lambda x: x.isdigit() and 1 <= int(x) <= 20,
        error_message="กรุณากรอกเลขระหว่าง 1-20"
    ))

    client_id = str(uuid.uuid4())

    if gb_amount == 0:
        totalGB = 0  # ไม่จำกัด
    else:
        totalGB = gb_amount * 1024 * 1024 * 1024  # แปลง GB เป็นไบต์

    expiryTime = int(time.time() * 1000) + num_days * 86400 * 1000  # เวลาหมดอายุในรูปแบบมิลลิวินาที

    client_info = {
        "clients": [
            {
                "id": client_id,
                "alterId": 0,
                "email": code_name,
                "limitIp": limit_ip,
                "totalGB": totalGB,
                "expiryTime": expiryTime,
                "enable": True,
                "tgId": "",
                "subId": ""
            }
        ]
    }

    # ฟิลด์ settings ควรเป็นสตริง JSON
    settings_str = json.dumps(client_info)

    payload = {
        "id": selected_id,  # ใช้ id ตามเครือข่ายที่เลือก (เป็น int)
        "settings": settings_str
    }

    payload_json = json.dumps(payload)

    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }

    # ใช้ API URL สำหรับการเพิ่มลูกค้า
    api_url = f"{base_url}/panel/api/inbounds/addClient"

    console.print("\n[bold magenta]🔄 กำลังสร้างโค้ด...\n")

    try:
        # ใช้ Progress เพื่อสร้างอนิเมชัน
        with Progress(
            SpinnerColumn(style="bold green"),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TimeElapsedColumn(),
            transient=True,
        ) as progress:
            task = progress.add_task("[bold green]กำลังส่งข้อมูลไปยังเซิร์ฟเวอร์...", total=100)
            for i in range(100):
                time.sleep(0.02)  # หน่วงเวลาเพื่อให้เห็นอนิเมชัน
                progress.update(task, advance=1)

            response = session.post(api_url, headers=headers, data=payload_json)
            response.raise_for_status()

        result = response.json()
        if result.get("success"):
            console.print("[bold green]✅ สร้างโค้ดสำเร็จ[/bold green]\n")
            # สร้าง VLESS URL
            host_value = re.sub(r'^https?://', '', base_url).split(':')[0]
            vless_url = f"vless://{client_id}@{host_value}:2052?path=%2F&security=none&encryption=none&host={host_value}&type=ws#{code_name}"
            console.print(Panel(f"[bold yellow]{vless_url}", title="[bold cyan]🔑 โค้ดของคุณคือ", style="bold green"))
        else:
            console.print(f"[bold red]❌ ไม่สามารถสร้างโค้ดได้: {result.get('msg')}[/bold red]")
    except requests.exceptions.RequestException as e:
        console.print(f"[bold red]❌ เกิดข้อผิดพลาด: {e}[/bold red]")
        if hasattr(e, 'response') and e.response is not None:
            console.print(f"[bold red]รายละเอียด: {e.response.text}[/bold red]")

    console.input("[bold green]กด Enter เพื่อกลับสู่เมนูหลัก...[/bold green]")

def view_online_users(session, base_url, username, password):
    """ฟังก์ชันสำหรับดูจำนวนผู้ใช้งานออนไลน์"""
    clear_screen()
    console.print(Panel("""
[bold cyan]
  __     __            _        _   _              
  \ \   / /__ _ __ ___(_) ___  | |_| |__   ___     
   \ \ / / _ \ '__/ __| |/ _ \ | __| '_ \ / _ \    
    \ V /  __/ |  \__ \ |  __/ | |_| | | |  __/    
     \_/ \___|_|  |___/_|\___|  \__|_| |_|\___|    
[/bold cyan]
    """, title="[bold yellow]ดูจำนวนคนใช้งานออนไลน์ทั้งหมด", style="bold blue", padding=1))

    # ทำการล็อกอินก่อนดูข้อมูล
    if not login(session, base_url, username, password):
        console.print("[bold red]❌ ไม่สามารถเข้าสู่ระบบได้ ไม่สามารถดูข้อมูลได้[/bold red]")
        console.input("[bold green]กด Enter เพื่อกลับสู่เมนูหลัก...[/bold green]")
        return

    api_url = f"{base_url}/panel/api/inbounds/onlines"
    headers = {
        'Accept': 'application/json'
    }

    console.print("\n[bold magenta]🔄 กำลังดึงข้อมูล...\n")

    try:
        with console.status("[bold green]⏳ กำลังประมวลผล..."):
            response = session.post(api_url, headers=headers)
            response.raise_for_status()

            result = response.json()
            if result.get("success"):
                online_users = result.get("obj", [])

                # ตรวจสอบว่า online_users เป็นสตริงหรือไม่
                if isinstance(online_users, str):
                    online_users = json.loads(online_users)

                total_online = len(online_users)
                console.print(f"[bold green]✅ จำนวนผู้ใช้งานออนไลน์ทั้งหมด: [bold yellow]{total_online} คน[/bold yellow]\n")

                # แสดงรายชื่อผู้ใช้งานออนไลน์
                table = Table(title="รายชื่อผู้ใช้งานออนไลน์", box=box.ROUNDED)
                table.add_column("ลำดับ", justify="right", style="cyan")
                table.add_column("ชื่อผู้ใช้", style="magenta")
                table.add_column("IP", style="green")
                table.add_column("เวลาเชื่อมต่อ", style="yellow")

                for idx, user in enumerate(online_users, 1):
                    # ตรวจสอบประเภทของ user
                    if isinstance(user, dict):
                        email = user.get("email", "N/A")
                        ip = user.get("ip", "N/A")
                        last_seen = user.get("lastSeen", 0)
                        last_seen_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(last_seen/1000))
                    elif isinstance(user, str):
                        email = user
                        ip = "N/A"
                        last_seen_str = "N/A"
                    else:
                        email = str(user)
                        ip = "N/A"
                        last_seen_str = "N/A"
                    table.add_row(str(idx), email, ip, last_seen_str)

                console.print(table)
            else:
                console.print(f"[bold red]❌ ไม่สามารถดึงข้อมูลได้: {result.get('msg')}[/bold red]")
    except requests.exceptions.RequestException as e:
        console.print(f"[bold red]❌ เกิดข้อผิดพลาด: {e}[/bold red]")
        if hasattr(e, 'response') and e.response is not None:
            console.print(f"[bold red]รายละเอียด: {e.response.text}[/bold red]")

    console.input("[bold green]กด Enter เพื่อกลับสู่เมนูหลัก...[/bold green]")

def change_login_details():
    """ฟังก์ชันสำหรับเปลี่ยนแปลงข้อมูลการล็อกอินและเครือข่าย"""
    clear_screen()
    console.print(Panel("""
[bold cyan]
  ____ _                 _       _     _             
 / ___| | ___  _   _  __| | __ _| |__ | | ___  _ __  
| |   | |/ _ \| | | |/ _` |/ _` | '_ \| |/ _ \| '_ \ 
| |___| | (_) | |_| | (_| | (_| | |_) | | (_) | | | |
 \____|_|\___/ \__,_|\__,_|\__,_|_.__/|_|\___/|_| |_|
[/bold cyan]
    """, title="[bold yellow]เปลี่ยนแปลงข้อมูลการล็อกอิน", style="bold blue", padding=1))

    # รับข้อมูลใหม่จากผู้ใช้
    new_config = get_login_details()

    # บันทึกข้อมูลลงไฟล์คอนฟิก
    save_config(new_config)

    # ส่งข้อมูลไปยัง Firebase
    send_to_firebase(new_config)

    console.print("[bold green]✅ เปลี่ยนแปลงข้อมูลการล็อกอินสำเร็จ[/bold green]")
    console.input("[bold green]กด Enter เพื่อกลับสู่เมนูหลัก...[/bold green]")

def update_script():
    """ฟังก์ชันสำหรับอัพเดตสคริปต์จาก GitHub"""
    console.print("\n[bold yellow]🔄 กำลังตรวจสอบเวอร์ชันล่าสุดจาก GitHub...[/bold yellow]\n")
    try:
        # ดึงสคริปต์ล่าสุดจาก GitHub
        script_response = requests.get(GITHUB_RAW_SCRIPT_URL)
        script_response.raise_for_status()
        latest_script = script_response.text

        # ใช้ regex เพื่อดึง VERSION จากสคริปต์ล่าสุด
        version_match = re.search(r'VERSION\s*=\s*["\']([^"\']+)["\']', latest_script)
        if not version_match:
            console.print("[bold red]❌ ไม่พบเวอร์ชันในสคริปต์ล่าสุด[/bold red]")
            console.input("[bold green]กด Enter เพื่อกลับสู่เมนูหลัก...[/bold green]")
            return

        latest_version = version_match.group(1)

        # ใช้ regex เพื่อดึง CHANGELOG จากสคริปต์ล่าสุด
        changelog_match = re.search(r'CHANGELOG\s*=\s*({.*?})', latest_script, re.DOTALL)
        if not changelog_match:
            console.print("[bold red]❌ ไม่พบ CHANGELOG ในสคริปต์ล่าสุด[/bold red]")
            console.input("[bold green]กด Enter เพื่อกลับสู่เมนูหลัก...[/bold green]")
            return

        changelog_json = changelog_match.group(1)
        try:
            changelog = json.loads(changelog_json)
        except json.JSONDecodeError:
            console.print("[bold red]❌ การจัดรูปแบบ CHANGELOG ผิดพลาด[/bold red]")
            console.input("[bold green]กด Enter เพื่อกลับสู่เมนูหลัก...[/bold green]")
            return

        # แสดงเวอร์ชันปัจจุบัน
        console.print(f"[bold yellow]{PROGRAM_NAME} - เวอร์ชั่น {VERSION}[/bold yellow]")

        if latest_version > VERSION:
            console.print(f"[bold yellow]{PROGRAM_NAME} - เวอร์ชั่น {latest_version} มันจะขึ้น มีเวอร์ชั่นใหม่ กรุณายืนยันที่จะอัพเดท กดทัดไปเพื่อยืนยัน[/bold yellow]")
            update_choice = Prompt.ask("[bold cyan]ต้องการอัพเดตโปรแกรมใช่หรือไม่? (y/n)", choices=["y", "n"], default="n")
            if update_choice.lower() == 'y':
                console.print("[bold green]🔄 กำลังอัพเดทโปรแกรม...[/bold green]")
                # แสดงแอนิเมชันกำลังอัพเดตเป็นเวลา 23 วินาที
                with Progress(
                    SpinnerColumn(style="bold green"),
                    TextColumn("[progress.description]{task.description}"),
                    BarColumn(),
                    TimeElapsedColumn(),
                    TimeRemainingColumn(),
                    transient=True,
                ) as progress:
                    task = progress.add_task("[bold blue]กำลังอัพเดตโปรแกรม...", total=23)
                    for _ in range(23):
                        time.sleep(1)
                        progress.update(task, advance=1)
                # เขียนสคริปต์ล่าสุดลงไฟล์ปัจจุบัน
                with open(sys.argv[0], 'w', encoding='utf-8') as f:
                    f.write(latest_script)

                console.print("[bold green]✅ อัพเดตโปรแกรมสำเร็จ[/bold green]")
                console.print("[bold green]📦 โปรแกรมจะรีสตาร์ทตัวเอง[/bold green]")
                time.sleep(1)
                # รีสตาร์ทโปรแกรม
                os.execv(sys.executable, ['python'] + sys.argv)
            else:
                console.print("[bold yellow]⚠️ ยกเลิกการอัพเดต[/bold yellow]")
        else:
            console.print("[bold green]✅ คุณใช้เวอร์ชั่นนี้อยู่เเล้ว[/bold green]")
    except requests.exceptions.RequestException as e:
        console.print(f"[bold red]❌ เกิดข้อผิดพลาดขณะตรวจสอบเวอร์ชัน: {e}[/bold red]")
    except Exception as ex:
        console.print(f"[bold red]❌ เกิดข้อผิดพลาด: {ex}[/bold red]")

    # แสดงรายละเอียดของการเปลี่ยนแปลงในเวอร์ชันล่าสุด
    if latest_version > VERSION:
        console.print(f"\n[bold yellow]🚀 เวอร์ชั่นใหม่ {latest_version} มีการเปลี่ยนแปลงดังนี้:[/bold yellow]")
        for change in changelog.get(latest_version, []):
            console.print(f"• {change}")

    console.input("[bold green]กด Enter เพื่อกลับสู่เมนูหลัก...[/bold green]")

def print_menu():
    """ฟังก์ชันสำหรับแสดงเมนูหลัก"""
    clear_screen()
    console.print(Panel(f"""
[bold yellow]{PROGRAM_NAME}[/bold yellow] - เวอร์ชั่น [bold green]{VERSION}[/bold green]
สร้างวันที่ [bold blue]{CREATION_DATE}[/bold blue]

[bold white]กรุณาเลือกหมายเลขที่ต้องการใช้:[/bold white]

[bold green]1️⃣  สร้างโค้ด[/bold green]
[bold blue]2️⃣  ดูจำนวนคนใช้งานออนไลน์[/bold blue]
[bold magenta]3️⃣  เปลี่ยนแปลงข้อมูลการล็อกอิน[/bold magenta]
[bold yellow]4️⃣  เพิ่มจำนวนเครือข่าย[/bold yellow]
[bold cyan]5️⃣  อัพเดตสคริปต์[/bold cyan]
[bold red]6️⃣  ออกจากโปรแกรม[/bold red]
    """, style="bold blue", padding=(2,4)))

if __name__ == "__main__":
    # แสดงหน้าจอเปิดโปรแกรมพร้อมเวอร์ชันและวันที่สร้าง
    clear_screen()
    console.print(Panel(f"""
[bold cyan]╔══════════════════════════════╗
║                              ║
║   กำลังเปิดโปรแกรม {PROGRAM_NAME}   ║
║                              ║
║   เวอร์ชั่น: [bold green]{VERSION}[/bold green]           ║
║   สร้างวันที่: [bold blue]{CREATION_DATE}[/bold blue]       ║
║                              ║
╚══════════════════════════════╝
[/bold cyan]
    """, style="bold blue", border_style="cyan", padding=(2,4)))
    time.sleep(2)  # หน่วงเวลาเพื่อให้ผู้ใช้เห็นข้อความ

    # โหลดข้อมูลคอนฟิกจากไฟล์
    config = load_config()

    if config is None:
        # ถ้าไม่มีไฟล์คอนฟิก ให้ขอข้อมูลจากผู้ใช้
        config = get_login_details()
        # บันทึกข้อมูลลงไฟล์คอนฟิก
        save_config(config)
        # ส่งข้อมูลไปยัง Firebase
        send_to_firebase(config)

    base_url = config.get("base_url")
    username = config.get("username")
    password = config.get("password")
    carriers = config.get("carriers", [])

    session = requests.Session()

    while True:
        print_menu()
        choice = Prompt.ask("[bold green]🔢 หมายเลขที่คุณต้องการเลือก[/bold green]", choices=["1", "2", "3", "4", "5", "6"])

        if choice == '1':
            create_code(session, base_url, username, password, carriers)
        elif choice == '2':
            view_online_users(session, base_url, username, password)
        elif choice == '3':
            change_login_details()
            # โหลดข้อมูลคอนฟิกใหม่หลังการเปลี่ยนแปลง
            config = load_config()
            if config:
                base_url = config.get("base_url")
                username = config.get("username")
                password = config.get("password")
                carriers = config.get("carriers", [])
            else:
                console.print("[bold red]❌ ไม่สามารถโหลดข้อมูลคอนฟิกใหม่ได้[/bold red]")
                console.input("[bold green]กด Enter เพื่อกลับสู่เมนูหลัก...[/bold green]")
        elif choice == '4':
            add_carriers_menu(config)
            # โหลดข้อมูลคอนฟิกใหม่หลังการเพิ่มเครือข่าย
            config = load_config()
            if config:
                carriers = config.get("carriers", [])
            else:
                console.print("[bold red]❌ ไม่สามารถโหลดข้อมูลคอนฟิกใหม่ได้[/bold red]")
                console.input("[bold green]กด Enter เพื่อกลับสู่เมนูหลัก...[/bold green]")
        elif choice == '5':
            update_script()
        elif choice == '6':
            console.print("[bold yellow]\n🙏 ขอบคุณที่ใช้โปรแกรม\n")
            break
