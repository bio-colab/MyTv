# موجه تشغيل وكيل الذكاء الاصطناعي (MyTv Prompt for Antigravity)

انسخ هذا النص وضعه في محادثتك مع وكيل **Google Antigravity** (أو أي وكيل برمجي يمتلك صلاحية الوصول لسطر الأوامر) على جهاز كمبيوتر متصل بنفس شبكة الـ Wi-Fi الخاصة بالتلفاز.
المشروع مخصص لشاشات وأجهزة **Android TV / Google TV** (مثل Xiaomi, TCL, Hisense, Skyworth, Tornado, Haier, Nikai, Realme, Sony, وغيرها).

---

```markdown
أريد تنظيف شاشة التلفاز الخاصة بي وتسريعها واستبدال المشغل الافتراضي بلانشر MyTv الخفيف والسريع.
طراز جهازي أو شاشتي هو: <اكتب موديل الشاشة أو دعني اكتشفه تلقائياً>.

اتبع الخطوات الآتية بدقة واعمل على الشاشة الحقيقية عبر شبكة Wi-Fi وأدوات هذا المستودع (https://github.com/bio-colab/MyTv):

1. الاتصال بالشاشة (Connect):
   - ابحث عن التلفاز على شبكتي المحلية أو اسألني عن عنوان الـ IP الخاص به، ثم اتصل عبر المنفذ 5555.
   - نبهني عند ظهور رسالة «السماح بتصحيح أخطاء USB» على الشاشة لأوافق عليها.

2. فحص العتاد وتحديد الإمكانيات أولاً (Hardware Assessment):
   - قم بتشغيل أداة `python tools/assess_device.py <TV_IP>` فور الاتصال.
   - استخرج حجم الذاكرة العشوائية (RAM)، المساحة التخزينية، إصدار أندرويد، ونوع اللوحة/المعالج.
   - إذا كان الجهاز من الفئة الاقتصادية (Tier 1: Ultra-Budget - رام 1 جيجابايت أو أقل أو أندرويد قديم):
     * التزم بتطبيق بروفايل `ultra-lite` (تعطيل الحركات الثقيلة والتوهج الديناميكي لتوفير الرام والمعالج).
     * إذا كان إصدار أندرويد أقل من SDK 26 (Android 7 أو أقدم)، وضح لي أن المشغل يتطلب أندرويد 8+ واعرض علي الاكتفاء بالتنظيف الآمن فقط دون تثبيت اللانشر.

3. النسخ الاحتياطي الصارم (Backup):
   - احفظ قائمة الحزم الكاملة وإعدادات النظام في مجلد `backup/` قبل إجراء أي تعديل.
   - تأكد من جاهزية نص الاسترجاع `tools/restore.sh` أو `restore.ps1` للرجوع لأي حالة سابقة بضغطة زر.

4. التنظيف الآمن مع مراعاة البيئة العربية (Safe Debloat):
   - عطل الحزم الإعلانية وتتبع المصنع عبر `pm disable-user --user 0` فقط، ولا تحذف أي حزمة نظام نهائياً.
   - احذر من المساس بتطبيقات البث العربية الشائعة المثبتة لدي (مثل شاهد Shahid، تود TOD، beIN، WATCH IT، STARZPLAY، القرآن الكريم، تطبيقات IPTV).
   - إذا كان التلفاز لا يحتوي على متجر Google Play (شاشة صينية اقتصادية بنظام AOSP)، إياك وتعطيل المتاجر البديلة (مثل Aptoide أو APKPure) حتى لا أفقد القدرة على تثبيت التطبيقات.
   - إذا كانت الشاشة تحتوي على حزم `com.cvte.*` أو لوحات مدمجة، احرص على بقاء خدمات التبديل بين منافذ HDMI وأزرار جهاز التحكم (الريموت) سليمة.

5. بناء وتثبيت لانشر MyTv:
   - اضبط إعدادات `launcher/app/src/main/res/values/config.xml` بناءً على فئة جهازي وتطبيقاتي المفضلة.
   - ابنِ وثبت اللانشر وتأكد من أنه أصبح الشاشة الرئيسية الافتراضية.
   - التقط لقطات شاشة (`tools/tv.py --screenshot`) وتأكد من سلامة الواجهة.

6. تأمين الجهاز بعد الانتهاء:
   - ذكرني بإيقاف خيار تصحيح أخطاء USB من التلفاز، وافحص إغلاق المنفذ 5555 لحماية شبكتي المنزلية.
```

## Technical Safety Rules & Edge Cases

- Factory menus and test packages: Never start or enable factory packages like `com.cvte.tv.hkcfac` or `mediatek.factorymenu.ui`. Check with `dumpsys package` before touching unfamiliar system components; see `docs/TROUBLESHOOTING.md` for recovery.
- If the stock launcher also answers the remote's app buttons, dead keys may report `KEY_UNKNOWN` or `KEY_PROGRAM`. Use `settings_key_scancodes` in only `config.xml` with the accessibility helper.
- Key repeat helper: on a TCL G09 build (Google TV 12) ask me to hold volume up before enabling any key helper; it is all or nothing. If enabled, say which one I am giving up. See `docs/devices/tcl-55p71b-g09-key-repeat.md`. On other sets this was not measured.
- Firmware limits: If `pm disable-user` is refused for every package, check `pm list packages -d` to confirm, and refer to `docs/TROUBLESHOOTING.md`.
- Home guard: Query current activities with `query-activities` and confirm default home with `cmd package set-home-activity`. Check `mFocusedApp` before claiming success.
- Screen grid and density: Check `wm density` and `display_density_forced` before configuring the grid. A skewed display is not a launcher bug; consult `docs/TROUBLESHOOTING.md`.
- Android version check: Check `getprop ro.build.version.sdk` first. The launcher requires `minSdk 26` (Android 8.0+). On older versions, offer debloat only.
