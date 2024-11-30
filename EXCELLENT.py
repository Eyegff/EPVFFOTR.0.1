import requests
import json
import time
import uuid
import os
import sys
from colorama import init
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn
from rich import box

# เริ่มต้นการใช้งาน colorama และ rich
init(autoreset=True)
console = Console()

def clear_screen():
    """ฟังก์ชันสำหรับล้างหน้าจอ"""
    if sys.platform.startswith('win'):
        os.system('cls')
    else:
        os.system('clear')

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
                console.print(f"[bold green]✅ เข้าสู่ระบบสำเร็จ: {result.get('msg')}")
                return True
            else:
                console.print(f"[bold red]❌ เข้าสู่ระบบล้มเหลว: {result.get('msg')}")
                return False

    except requests.exceptions.RequestException as e:
        console.print(f"[bold red]เกิดข้อผิดพลาดระหว่างการเข้าสู่ระบบ: {e}")
        return False

def get_validated_input(prompt_text, default, validation_func, error_message):
    """ฟังก์ชันสำหรับรับข้อมูลจากผู้ใช้และตรวจสอบความถูกต้อง"""
    while True:
        user_input = Prompt.ask(prompt_text, default=default)
        if validation_func(user_input):
            return user_input
        else:
            console.print(f"[bold red]{error_message}[/bold red]")

def create_code(session, base_url, username, password):
    """ฟังก์ชันสำหรับสร้างโค้ด VLESS"""
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
        console.print("[bold red]ไม่สามารถเข้าสู่ระบบได้ ไม่สามารถสร้างโค้ดได้")
        console.input("[bold green]กด Enter เพื่อกลับสู่เมนูหลัก...")
        return

    # เพิ่มเมนูเลือกเครือข่ายก่อน
    console.print("\n[bold yellow]กรุณาเลือกเครือข่ายที่ต้องการสร้างโค้ด:\n")
    console.print("  [bold green]1️⃣ ทรูโนโปร[/bold green]")
    console.print("  [bold blue]2️⃣ ทรูโปรเฟส[/bold blue]")
    console.print("  [bold red]3️⃣ AIS[/bold red]")

    carrier_choice = Prompt.ask("\n[bold cyan]🔢 กรุณาพิมพ์หมายเลขที่ต้องการใช้ (1-3)", choices=["1", "2", "3"])

    # กำหนด id ตามเครือข่ายที่เลือก
    carrier_id_mapping = {
        "1": 5,  # ทรูโนโปร
        "2": 3,  # ทรูโปรเฟส
        "3": 7   # AIS
    }

    selected_id = carrier_id_mapping.get(carrier_choice)

    console.print("[bold yellow]\nกรุณากรอกข้อมูลสำหรับสร้างโค้ด\n")

    # รับชื่อโค้ด
    code_name = Prompt.ask("[bold cyan]📝 ตั้งชื่อโค้ดของคุณ")

    # รับจำนวนวันที่ต้องการ (1-30)
    num_days = get_validated_input(
        "[bold cyan]📅 จำนวนวันที่ต้องการ (1-30)",
        default="1",
        validation_func=lambda x: x.isdigit() and 1 <= int(x) <= 30,
        error_message="กรุณากรอกเลขระหว่าง 1-30"
    )
    num_days = int(num_days)

    # รับจำนวน GB ที่ต้องการ (0-1000)
    gb_amount = get_validated_input(
        "[bold cyan]💾 จำนวน GB ที่ต้องการ (0 คือไม่จำกัด, 0-1000)",
        default="0",
        validation_func=lambda x: x.isdigit() and 0 <= int(x) <= 1000,
        error_message="กรุณากรอกเลขระหว่าง 0-1000"
    )
    gb_amount = int(gb_amount)

    # รับจำนวน IP ที่ต้องการให้เชื่อมต่อ (1-20)
    limit_ip = get_validated_input(
        "[bold cyan]👥 จำนวน IP ที่ต้องการให้เชื่อมต่อ (1-20)",
        default="1",
        validation_func=lambda x: x.isdigit() and 1 <= int(x) <= 20,
        error_message="กรุณากรอกเลขระหว่าง 1-20"
    )
    limit_ip = int(limit_ip)

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
        "id": selected_id,  # ใช้ id ตามเครือข่ายที่เลือก
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
            BarColumn(bar_width=None),
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
            console.print("[bold green]✅ สร้างโค้ดสำเร็จ\n")
            # สร้าง VLESS URL
            host_value = base_url.replace('http://', '').replace('https://', '').split(':')[0]
            vless_url = f"vless://{client_id}@{host_value}:2052?path=%2F&security=none&encryption=none&host={host_value}&type=ws#{code_name}"
            console.print(Panel(f"[bold yellow]{vless_url}", title="[bold cyan]🔑 โค้ดของคุณคือ", style="bold green"))
        else:
            console.print(f"[bold red]❌ ไม่สามารถสร้างโค้ดได้: {result.get('msg')}")
    except requests.exceptions.RequestException as e:
        console.print(f"[bold red]เกิดข้อผิดพลาด: {e}")
        if e.response is not None:
            console.print(f"[bold red]รายละเอียด: {e.response.text}")

    console.input("[bold green]กด Enter เพื่อกลับสู่เมนูหลัก...")

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
        console.print("[bold red]ไม่สามารถเข้าสู่ระบบได้ ไม่สามารถดูข้อมูลได้")
        console.input("[bold green]กด Enter เพื่อกลับสู่เมนูหลัก...")
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
                console.print(f"[bold red]❌ ไม่สามารถดึงข้อมูลได้: {result.get('msg')}")
    except requests.exceptions.RequestException as e:
        console.print(f"[bold red]เกิดข้อผิดพลาด: {e}")
        if e.response is not None:
            console.print(f"[bold red]รายละเอียด: {e.response.text}")

    console.input("[bold green]กด Enter เพื่อกลับสู่เมนูหลัก...")

def print_menu():
    """ฟังก์ชันสำหรับแสดงเมนูหลัก"""
    clear_screen()
    console.print(Panel("""
[bold cyan]
╔═════════════════════════════════════════╗
║                                         ║
║      [blink bold yellow]🌟 โปรแกรมจัดการ VLESS 🌟[/blink bold yellow]         ║
║                                         ║
╠═════════════════════════════════════════╣
║   [bold white]กรุณาเลือกหมายเลขที่ต้องการใช้:[/bold white]           ║
║                                         ║
║   [bold green]1️⃣  สร้างโค้ด[/bold green]                           ║
║   [bold blue]2️⃣  ดูจำนวนคนใช้งานออนไลน์[/bold blue]            ║
║   [bold red]3️⃣  ออกจากโปรแกรม[/bold red]                       ║
║                                         ║
╚═════════════════════════════════════════╝
[/bold cyan]
    """, style="bold blue", padding=1))

if __name__ == "__main__":
    # แทนที่ด้วยข้อมูลของคุณ
    base_url = "http://www.opensignal.com.vipbot.vipv2boxth.xyz:2053/0UnAOmjQ1vIaSIr"
    username = "6FocoC0F7a"
    password = "hmSwvyVmAo"

    session = requests.Session()

    while True:
        print_menu()
        choice = Prompt.ask("[bold green]🔢 หมายเลขที่คุณต้องการเลือก", choices=["1", "2", "3"])

        if choice == '1':
            create_code(session, base_url, username, password)
        elif choice == '2':
            view_online_users(session, base_url, username, password)
        elif choice == '3':
            console.print("[bold yellow]\n🙏 ขอบคุณที่ใช้โปรแกรม\n")
            break
