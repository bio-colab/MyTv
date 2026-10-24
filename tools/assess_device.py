#!/usr/bin/env python3
"""
MyTv Device Hardware & Capability Assessor
أداة فحص وتقدير مواصفات عتاد التلفاز - مخصصة للشاشات العربية والأجهزة الاقتصادية.

Usage:
  python tools/assess_device.py [tv_ip] [--port 5555] [--json] [--arabic]

This tool inspects:
  - RAM (Total, Available, Low-Memory threshold)
  - Storage (Total, Free space on /data)
  - CPU Architecture (32-bit vs 64-bit, core count)
  - Android OS version & SDK level
  - TV Board / Manufacturer (CVTE, Realtek, Amlogic, MediaTek, etc.)
  - Installed Arab regional apps (Shahid, TOD, Watch IT, IPTV, etc.)
  - Detection of third-party app stores on non-Google Play AOSP TVs

Outputs a Hardware Tier (Tier 1: Ultra-Budget, Tier 2: Mid-Range, Tier 3: High-End)
and generates tailored configuration recommendations for the MyTv launcher.
"""

import sys
import os
import re
import json
import subprocess
import argparse

REGIONAL_APPS = {
    "com.mbc.shahid": "Shahid (شاهد VIP)",
    "com.tod": "TOD (تود - beIN)",
    "tv.beinsports.connect": "beIN CONNECT",
    "com.watchit": "WATCH IT",
    "com.starzplay.android": "STARZPLAY",
    "com.osn.go": "OSN+ / OSN Streaming",
    "net.aloula.app": "Aloula (الأولى)",
    "com.spacetoon.online": "Spacetoon Go (سبيستون غو)",
    "com.jawwy.tv": "Jawwy TV / stc tv",
    "com.liskovsoft.smarttubetv.beta": "SmartTube (بديل يوتيوب بدون إعلانات)",
    "com.liskovsoft.videomanager": "SmartTube Stable",
    "com.google.android.youtube.tv": "YouTube TV",
    "org.videolan.vlc": "VLC Media Player",
    "com.mxtech.videoplayer.ad": "MX Player",
    "com.mxtech.videoplayer.pro": "MX Player Pro",
    "com.nst.iptvsmarterstvbox": "IPTV Smarters Pro",
    "ru.iptvremote.android.iptv": "IPTV (Alexander Sofronov)",
    "com.quran.labs.androidquran": "Quran Android (القرآن الكريم)",
    "com.majnioui.tv.prayer": "Prayer Times (مواقيت الصلاة)",
}

THIRD_PARTY_STORES = {
    "cm.aptoidetv.pt": "Aptoide TV",
    "com.apkpure.aerie": "APKPure",
    "com.aurora.store": "Aurora Store",
    "com.uptodown": "Uptodown App Store",
    "com.zeasn.tvstore": "Zeasn Whale Store",
    "com.tcl.appmarket": "TCL Channel / App Market",
}

CRITICAL_SYSTEM_PACKAGES = [
    "com.android.vending",
    "com.google.android.gms",
    "com.google.android.gsf",
    "com.android.systemui",
    "com.android.settings",
    "com.android.tv.settings",
    "com.android.packageinstaller",
    "com.google.android.packageinstaller",
    "com.android.permissioncontroller",
]

def run_adb(cmd, host=None, port=5555):
    """Run an adb shell command."""
    prefix = ["adb"]
    if host:
        prefix.extend(["-s", f"{host}:{port}"])
    prefix.append("shell")
    if isinstance(cmd, list):
        full_cmd = prefix + cmd
    else:
        full_cmd = prefix + [cmd]
    try:
        res = subprocess.run(full_cmd, capture_output=True, text=True, timeout=12)
        return res.stdout.strip()
    except Exception as e:
        return ""

def parse_meminfo(output):
    total_kb = 0
    avail_kb = 0
    for line in output.splitlines():
        if line.startswith("MemTotal:"):
            parts = line.split()
            if len(parts) >= 2 and parts[1].isdigit():
                total_kb = int(parts[1])
        elif line.startswith("MemAvailable:"):
            parts = line.split()
            if len(parts) >= 2 and parts[1].isdigit():
                avail_kb = int(parts[1])
        elif line.startswith("MemFree:") and avail_kb == 0:
            parts = line.split()
            if len(parts) >= 2 and parts[1].isdigit():
                avail_kb = int(parts[1])
    return total_kb, avail_kb

def parse_df(output):
    """Parse df output for /data in KB."""
    total_kb = 0
    avail_kb = 0
    for line in output.splitlines():
        if "/data" in line:
            parts = line.split()
            # typically: Filesystem 1K-blocks Used Available Use% Mounted on
            if len(parts) >= 4:
                try:
                    total_kb = int(parts[1])
                    avail_kb = int(parts[3])
                except ValueError:
                    pass
    return total_kb, avail_kb

def assess(host=None, port=5555):
    report = {
        "device": {},
        "hardware": {},
        "installed_apps": {},
        "regional_apps": [],
        "third_party_stores": [],
        "tier": 1,
        "tier_name": "Tier 1: Ultra-Budget (الفئة الاقتصادية المتواضعة)",
        "recommendations": {},
        "warnings": []
    }

    # 1. Device identity
    manufacturer = run_adb("getprop ro.product.manufacturer", host, port) or "Unknown"
    brand = run_adb("getprop ro.product.brand", host, port) or manufacturer
    model = run_adb("getprop ro.product.model", host, port) or "Unknown"
    board = run_adb("getprop ro.board.platform", host, port) or "Unknown"
    hardware = run_adb("getprop ro.hardware", host, port) or "Unknown"
    sdk_str = run_adb("getprop ro.build.version.sdk", host, port) or "0"
    android_ver = run_adb("getprop ro.build.version.release", host, port) or "Unknown"
    abi = run_adb("getprop ro.product.cpu.abi", host, port) or "Unknown"

    sdk = int(sdk_str) if sdk_str.isdigit() else 0

    report["device"] = {
        "manufacturer": manufacturer,
        "brand": brand,
        "model": model,
        "board": board,
        "hardware": hardware,
        "android_version": android_ver,
        "sdk": sdk,
        "cpu_abi": abi
    }

    # 2. Memory
    mem_out = run_adb("cat /proc/meminfo", host, port)
    tot_mem_kb, avail_mem_kb = parse_meminfo(mem_out)
    tot_mem_mb = tot_mem_kb // 1024
    avail_mem_mb = avail_mem_kb // 1024

    # 3. Storage
    df_out = run_adb("df -k /data", host, port)
    tot_data_kb, avail_data_kb = parse_df(df_out)
    avail_data_mb = avail_data_kb // 1024

    # 4. Display
    wm_size = run_adb("wm size", host, port) or "Unknown"
    wm_density = run_adb("wm density", host, port) or "Unknown"

    report["hardware"] = {
        "ram_total_mb": tot_mem_mb,
        "ram_available_mb": avail_mem_mb,
        "storage_available_mb": avail_data_mb,
        "display_size": wm_size,
        "display_density": wm_density
    }

    # 5. Packages
    pkg_out = run_adb("pm list packages", host, port)
    installed_pkgs = set()
    for line in pkg_out.splitlines():
        if line.startswith("package:"):
            p = line.split(":", 1)[1].strip()
            installed_pkgs.add(p)

    # Detect Arab regional apps
    for p, name in REGIONAL_APPS.items():
        if p in installed_pkgs:
            report["regional_apps"].append({"package": p, "name": name})

    # Detect 3rd party stores
    has_play_store = "com.android.vending" in installed_pkgs
    for p, name in THIRD_PARTY_STORES.items():
        if p in installed_pkgs:
            report["third_party_stores"].append({"package": p, "name": name})

    # 6. Assess Tier
    # Tier 1 (Ultra-Budget): RAM <= 1024 MB or free RAM < 200MB or free storage < 800MB or SDK < 26
    # Tier 2 (Mid-Range): RAM 1025-2048 MB, free storage >= 1000MB, SDK >= 26
    # Tier 3 (High-End): RAM > 2048 MB, free storage >= 2500MB, SDK >= 28
    if tot_mem_mb <= 1024 or avail_data_mb < 800 or sdk < 26:
        tier = 1
        tier_name = "Tier 1: الفئة الاقتصادية الضعيفة (Ultra-Budget / Legacy)"
    elif tot_mem_mb <= 2048:
        tier = 2
        tier_name = "Tier 2: الفئة المتوسطة المتوازنة (Mid-Range)"
    else:
        tier = 3
        tier_name = "Tier 3: الفئة العالية المتقدمة (High-End)"

    report["tier"] = tier
    report["tier_name"] = tier_name

    # 7. Warnings & Caveats
    if sdk < 26:
        report["warnings"].append(
            f"إصدار أندرويد قديم جداً (Android {android_ver}, SDK {sdk}). المشغل الافتراضي يتطلب SDK 26 (Android 8.0). "
            "يُنصح فقط بإجراء عملية التنظيف (Debloat) دون استبدال اللانشر، أو استخدام نسخة مخصصة للأجهزة القديمة."
        )

    # CVTE / MStar board detection
    is_cvte = any("com.cvte" in p for p in installed_pkgs) or "cvte" in board.lower() or "cvte" in hardware.lower()
    if is_cvte:
        report["warnings"].append(
            "تم اكتشاف لوحة CVTE (شائعة في تلفزيونات Haier, Tornado, Skyworth, Changhong, Condor, Star-X). "
            "تحذير صارم: إياك وتعطيل مشغل المصنع الأصلي أو فتح قوائم المصنع (Factory Menu)، واحرص على بقاء خدمات إدخال HDMI نشطة."
        )

    if not has_play_store:
        report["warnings"].append(
            "التلفاز لا يحتوي على متجر Google Play (شاشة أندرويد مفتوحة المصدر AOSP). "
            "تأكد تماماً من عدم تعطيل أي متجر تطبيقات بديل (مثل Aptoide أو APKPure) حتى لا يفقد المستخدم القدرة على تثبيت التطبيقات."
        )

    if avail_data_mb < 500:
        report["warnings"].append(
            f"مساحة التخزين المتاحة منخفضة جداً ({avail_data_mb} ميغابايت). "
            "تجنب تحميل أو حفظ خلفيات عالية الدقة لتفادي نفاد ذاكرة النظام."
        )

    # 8. Tailored recommendations for config.xml / theme
    if tier == 1:
        recs = {
            "profile": "ultra-lite",
            "reduced_motion": True,
            "focus_overshoot": False,
            "ambient_glow": False,
            "advanced_effects": False,
            "show_stats": False,
            "module_cards": False,  # save background memory
            "wallpaper": "solid_black_or_lightweight",
            "dock_apps_count": 4,
            "notes": "تم اختيار إعدادات فائقة الخفة لتحرير الرام والمعالج لتطبيقات البث مثل شاهد وتود واليوتيوب."
        }
    elif tier == 2:
        recs = {
            "profile": "balanced",
            "reduced_motion": False,
            "focus_overshoot": True,
            "ambient_glow": True,
            "advanced_effects": False,
            "show_stats": False,
            "module_cards": True,
            "wallpaper": "minimal_gradient",
            "dock_apps_count": 4,
            "notes": "إعدادات متوازنة تجمع بين الجمالية وسلاسة الحركة والاستقرار."
        }
    else:
        recs = {
            "profile": "high-end",
            "reduced_motion": False,
            "focus_overshoot": True,
            "ambient_glow": True,
            "advanced_effects": True,
            "show_stats": True,
            "module_cards": True,
            "wallpaper": "cinematic_scenes",
            "dock_apps_count": 5,
            "notes": "إعدادات كاملة مع تأثيرات الإضاءة الزجاجية الديناميكية وشريط التطبيقات الواسع."
        }

    report["recommendations"] = recs
    return report

def print_arabic_report(rep):
    print("=" * 65)
    print("        تقرير تقييم عتاد الشاشة - مشروع MyTv (تلفازي)")
    print("=" * 65)
    dev = rep["device"]
    hw = rep["hardware"]

    print(f"الجهاز: {dev['brand']} {dev['model']} (المصنّع: {dev['manufacturer']})")
    print(f"اللوحة / المعالج: {dev['board']} | المعمارية: {dev['cpu_abi']}")
    print(f"نظام أندرويد: {dev['android_version']} (مستوى SDK: {dev['sdk']})")
    print("-" * 65)
    print(f"الذاكرة العشوائية (RAM): {hw['ram_total_mb']} ميغابايت (المتاح حالياً: ~{hw['ram_available_mb']} ميغابايت)")
    print(f"المساحة التخزينية المتاحة: {hw['storage_available_mb']} ميغابايت")
    print(f"دقة الشاشة: {hw['display_size']} ({hw['display_density']})")
    print("-" * 65)
    print(f"تصنيف الجهاز: {rep['tier_name']}")
    print("-" * 65)

    if rep["regional_apps"]:
        print("التطبيقات العربية الإقليمية المكتشفة (ستتم حمايتها تلقائياً):")
        for app in rep["regional_apps"]:
            print(f"  ✓ {app['name']} ({app['package']})")
    else:
        print("لم يتم العثور على تطبيقات عربية شائعة مسبقة التثبيت.")

    if rep["third_party_stores"]:
        print("\nمتاجر التطبيقات المكتشفة (حظر تعطيلها للحفاظ على استقلالية التلفاز):")
        for store in rep["third_party_stores"]:
            print(f"  ★ {store['name']} ({store['package']})")

    if rep["warnings"]:
        print("\n⚠️ تنبيهات وتحذيرات أمان هامة:")
        for w in rep["warnings"]:
            print(f"  ! {w}")

    print("-" * 65)
    print("التوصيات والإعدادات المقترحة لـ MyTv:")
    rec = rep["recommendations"]
    print(f"  * البروفايل: {rec['profile']}")
    print(f"  * تقليل الحركة الثقيلة (reduced_motion): {rec['reduced_motion']}")
    print(f"  * التوهج المحيطي (ambient_glow): {rec['ambient_glow']}")
    print(f"  * ارتداد التركيز (focus_overshoot): {rec['focus_overshoot']}")
    print(f"  * تشغيل بطاقات الوحدات في الخلفية (module_cards): {rec['module_cards']}")
    print(f"  * ملاحظة: {rec['notes']}")
    print("=" * 65)

def main():
    parser = argparse.ArgumentParser(description="MyTv Device Hardware & Capability Assessor")
    parser.add_argument("host", nargs="?", default=os.environ.get("TV_HOST"), help="TV IP or hostname")
    parser.add_argument("--port", type=int, default=int(os.environ.get("TV_PORT", 5555)), help="ADB port (default 5555)")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    args = parser.parse_args()

    rep = assess(args.host, args.port)

    if args.json:
        print(json.dumps(rep, indent=2, ensure_ascii=False))
    else:
        print_arabic_report(rep)

if __name__ == "__main__":
    main()
