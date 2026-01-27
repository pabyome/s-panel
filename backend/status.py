import os
import sys
import psutil
import shutil
import subprocess
from sqlmodel import Session, select, func
from app.models.database import engine, User, Website, Plugin, FirewallRule

def get_service_status(service_name="spanel"):
    try:
        # Check if active
        result = subprocess.run(
            ["systemctl", "is-active", service_name], 
            capture_output=True, 
            text=True
        )
        status = result.stdout.strip()
        
        # Get detailed status line if active
        if status == "active":
            return "🟢 Active (Running)"
        elif status == "inactive":
            return "wc Inactive"
        elif status == "failed":
            return "🔴 Failed"
        else:
            return f"⚪ {status}"
    except FileNotFoundError:
        return "wb Not Installed (systemctl not found)"

def get_db_stats():
    try:
        with Session(engine) as session:
            user_count = session.exec(select(func.count(User.id))).one()
            site_count = session.exec(select(func.count(Website.id))).one()
            plugin_count = session.exec(select(func.count(Plugin.id))).one()
            fw_count = session.exec(select(func.count(FirewallRule.id))).one()
            return {
                "users": user_count,
                "websites": site_count,
                "plugins": plugin_count,
                "firewall_rules": fw_count
            }
    except Exception as e:
        return {"error": str(e)}

def format_bytes(size):
    power = 2**10
    n = 0
    power_labels = {0 : '', 1: 'K', 2: 'M', 3: 'G', 4: 'T'}
    while size > power:
        size /= power
        n += 1
    return f"{size:.1f}{power_labels[n]}B"

def print_dashboard():
    # --- System Info ---
    cpu_percent = psutil.cpu_percent(interval=0.1)
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    # --- Service Info ---
    service_status = get_service_status()
    
    # --- App Info ---
    db_stats = get_db_stats()

    # --- Output ---
    width = 50
    print("\n" + "="*width)
    print(f" s-panel Status".center(width))
    print("="*width)
    
    print(f"\n🖥️  SYSTEM")
    print(f"  CPU Usage:    {cpu_percent}%")
    print(f"  Memory:       {format_bytes(mem.used)} / {format_bytes(mem.total)} ({mem.percent}%)")
    print(f"  Disk (/):     {format_bytes(disk.used)} / {format_bytes(disk.total)} ({disk.percent}%)")
    
    print(f"\n⚙️  SERVICE")
    print(f"  Status:       {service_status}")
    
    print(f"\nmd  DATABASE")
    if "error" in db_stats:
        print(f"  Error reading DB: {db_stats['error']}")
    else:
        print(f"  Users:        {db_stats['users']}")
        print(f"  Websites:     {db_stats['websites']}")
        print(f"  Plugins:      {db_stats['plugins']}")
        print(f"  Firewall:     {db_stats['firewall_rules']} rules")
        
    print("\n" + "="*width + "\n")

if __name__ == "__main__":
    print_dashboard()
