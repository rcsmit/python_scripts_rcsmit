# gmail_delete_playwright.py
# Delete all Gmail messages for a search query using your real Chrome profile
# Example:
#   python gmail_delete_playwright.py
#   python gmail_delete_playwright.py --user-data-root "C:\Users\rcxsm\AppData\Local\Google\Chrome\User Data" --profile-directory "Default" --force

import argparse
import os
import sys
import urllib.parse
from pathlib import Path
from typing import Optional

from playwright.sync_api import Playwright, sync_playwright, TimeoutError as PWTimeout

DEFAULT_QUERY = "category:social label:_teverwijderen"

def detect_user_data_root() -> str:
    home = Path.home()
    if os.name == "nt":
        return str(home / "AppData" / "Local" / "Google" / "Chrome" / "User Data")
    elif sys.platform == "darwin":
        return str(home / "Library" / "Application Support" / "Google" / "Chrome")
    else:
        return str(home / ".config" / "google-chrome")

def build_search_url(query: str, account_index: int = 0) -> str:
    encoded = urllib.parse.quote(query, safe="+:")
    return f"https://mail.google.com/mail/u/{account_index}/#search/{encoded}"

def is_logged_in(page) -> bool:
    # Logged in if the topbar exists or the inbox rows are present
    if page.locator('tr.zA').count() > 0:
        return True
    if page.locator('a[aria-label*="Google Account"], a[aria-label*="Google-account"]').count() > 0:
        return True
    # Not logged in if Google sign-in input is present
    if page.locator('input[type="email"][name="identifier"]').count() > 0:
        return False
    return False

def wait_for_main(page):
    page.wait_for_selector('div[role="main"]', timeout=30000)

def count_rows(page) -> int:
    try:
        return page.locator("tr.zA").count()
    except PWTimeout:
        return 0

def click_select_all_checkbox(page):
    page.locator('div[gh="mtb"] [role="checkbox"]').first.click()

def try_click_select_all_conversations(page) -> bool:
    patt = [
        r"Select all .* conversations",
        r"Select all conversations",
        r"Alle conversaties.*selecteren",
        r"Alle gesprekken.*selecteren",
    ]
    for p in patt:
        loc = page.locator(f'role=link[name=/{p}/i]')
        if loc.count():
            try:
                loc.first.click()
                return True
            except Exception:
                pass
    for p in patt:
        loc = page.locator(f'role=button[name=/{p}/i]')
        if loc.count():
            try:
                loc.first.click()
                return True
            except Exception:
                pass
    return False

def click_delete(page):
    btn = page.locator('div[act="10"]').first
    if btn.count() == 0:
        btn = page.locator(
            'div[aria-label="Delete"], div[aria-label="Verwijderen"], '
            'div[aria-label="Delete forever"], div[aria-label="Voor altijd verwijderen"]'
        ).first
    btn.click()

def wait_for_toast(page):
    try:
        page.wait_for_selector('div[role="alert"]', timeout=8000)
        page.wait_for_timeout(800)
    except PWTimeout:
        pass

def delete_batch(page) -> int:
    rows_before = count_rows(page)
    if rows_before == 0:
        return 0
    click_select_all_checkbox(page)
    try_click_select_all_conversations(page)
    click_delete(page)
    wait_for_toast(page)
    for _ in range(40):
        page.wait_for_timeout(250)
        rows_now = count_rows(page)
        if rows_now != rows_before:
            break
    return rows_before

import psutil

def check_chrome_running(user_data_root: str) -> bool:
    """Check if Chrome is running with the target profile."""
    try:
        for proc in psutil.process_iter(['name', 'cmdline']):
            if proc.info['name'] and 'chrome' in proc.info['name'].lower():
                cmdline = proc.info.get('cmdline', [])
                if cmdline and any(user_data_root in arg for arg in cmdline):
                    return True
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        pass
    return False

import os
from pathlib import Path

def validate_profile(user_data_root: str, profile_directory: str):
    """Validate that the Chrome profile exists and is accessible."""
    print("\n=== Profile Validation ===")
    
    # Check if user data root exists
    if not os.path.exists(user_data_root):
        print(f"❌ User data root does NOT exist: {user_data_root}")
        return False
    print(f"✓ User data root exists: {user_data_root}")
    
    # Check profile directory
    profile_path = Path(user_data_root) / profile_directory
    if not profile_path.exists():
        print(f"❌ Profile directory does NOT exist: {profile_path}")
        print("\nAvailable profiles:")
        for item in Path(user_data_root).iterdir():
            if item.is_dir() and (item.name.startswith("Profile") or item.name == "Default"):
                print(f"  - {item.name}")
        return False
    print(f"✓ Profile directory exists: {profile_path}")
    
    # Check for lock files
    lock_files = [
        profile_path / "SingletonLock",
        profile_path / "lockfile",
        Path(user_data_root) / "SingletonLock",
    ]
    for lock in lock_files:
        if lock.exists():
            print(f"⚠️  Lock file found: {lock}")
            try:
                # Try to read lock file to see if it's stale
                lock.unlink()
                print(f"   Removed stale lock file")
            except Exception as e:
                print(f"   Could not remove lock: {e}")
    
    # Check permissions
    if not os.access(profile_path, os.R_OK | os.W_OK):
        print(f"❌ No read/write permissions on profile directory")
        return False
    print(f"✓ Profile directory has read/write permissions")
    
    print("=== Validation Complete ===\n")
    return True

def run(playwright: Playwright, query: str, user_data_root: str, profile_directory: str, headless: bool, account_index: int):
    print(f"User data root: {user_data_root}")
    print(f"Profile directory: {profile_directory}")
    print("Close Chrome first.")

        # Check if Chrome is running
    if check_chrome_running(user_data_root):
        print("\n⚠️  ERROR: Chrome is already running with this profile!")
        print("Please close all Chrome windows and try again.")
        return
    else:
        print ("\n ✅Chrome is not running. Proceeding...")
    
    # Validate before attempting launch
    if not validate_profile(user_data_root, profile_directory):
        print("\n❌ Profile validation failed. Cannot proceed.")
        return
    else:
        print("\n✅ Profile validation passed. Proceeding...")
    temporary = False
    
    if temporary:
        import tempfile
        temp_dir = tempfile.mkdtemp()
        print(f"Testing with temp profile: {temp_dir}")
        ctx = playwright.chromium.launch_persistent_context(
            user_data_dir=temp_dir,
            channel="chrome",
            headless=headless,
        )
    else:
        ctx = playwright.chromium.launch_persistent_context(
            user_data_dir=user_data_root,
            channel="chrome",
            headless=headless,
            args=[
                "--start-maximized",
                f"--profile-directory={profile_directory}",
            ],
        )
    print ("Launched browser")
    # try:
    if 1==1:
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        print (page)
        # Optional sanity check of active profile
        page.goto("chrome://version/")
        if page.get_by_text("Profile Path").count():
            print("Profile check OK.")
        page.goto(build_search_url(query, account_index), wait_until="domcontentloaded", timeout=120_000)

        wait_for_main(page)
        page.wait_for_timeout(1200)

        if not is_logged_in(page):
            print("Not logged in for this profile or account index.")
            print("Fix path or profile name. Example on Windows:")
            print(r'--user-data-root "C:\Users\rcxsm\AppData\Local\Google\Chrome\User Data" --profile-directory "Default"')
            return

        total = 0
        for i in range(100):
            removed = delete_batch(page)
            if removed == 0:
                break
            total += removed
            print(f"Batch {i+1}. Removed about {removed}. Total about {total}.")
            page.wait_for_timeout(1000)

        print(f"Done. Remaining rows: {count_rows(page)}")
    # finally:
        ctx.close()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--query", default=DEFAULT_QUERY)
    ap.add_argument("--user-data-root", default=detect_user_data_root())
    ap.add_argument("--profile-directory", default="Default")
    ap.add_argument("--headless", action="store_true")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--account-index", type=int, default=0)
    args = ap.parse_args()

    if not args.force:
        print(f"Query: {args.query}")
        print(f"User data root: {args.user_data_root}")
        print(f"Profile directory: {args.profile_directory}")
        # conf = input("Type DELETE to proceed: ").strip().upper()
        # if conf != "DELETE":
        #     print("Aborted.")
        #     return

    with sync_playwright() as p:
        run(p, args.query, args.user_data_root, args.profile_directory, args.headless, args.account_index)

if __name__ == "__main__":
    main()
D