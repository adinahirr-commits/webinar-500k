#!/usr/bin/env python3
"""ההעברה למצב מכירה אחרי וובינר 25.10 — דדליין אחד בכל הנכסים: רביעי 28.10 20:00.
רץ רק באישור עדי, מיד בתום השידור.

  python3 post_2510.py                      # יובש: מראה מה ישתנה
  python3 post_2510.py --yt <YT_ID> --apply # מריץ

מה הוא עושה:
 1. דף ההקלטה (course-portal/static/recording): YT_ID חדש, CLOSES=26.10 22:00, SLUG=recording-2510
 2. דפי הליווי (livui): דוחף את ההעלאה ששעון הבונוס בה מקובע ל-28.10 20:00
 3. בדיקה: הדפים עולים, והדדליין שמופיע בהם זהה לדדליין במיילים
לא נוגע בסמוב. התזמון של המיילים הוא post-webinar/schedule_2510.py.
"""
import os, re, sys, subprocess, urllib.request

OFFER_CLOSE = "2026-10-28T20:00:00+02:00"   # רביעי 28.10 20:00 — שעון חורף, +02:00
REC_CLOSE   = "2026-10-26T22:00:00+02:00"   # 24 שעות מתום השידור
REC = os.path.expanduser('~/course-portal/static/recording/index.html')
LIVUI = os.path.expanduser('~/livui')
APPLY = '--apply' in sys.argv
YT = None
if '--yt' in sys.argv:
    YT = sys.argv[sys.argv.index('--yt') + 1]


def patch_recording():
    s = open(REC, encoding='utf-8').read()
    new = s
    new = re.sub(r'var CLOSES  = "[^"]*"', f'var CLOSES  = "{REC_CLOSE}"', new)
    new = re.sub(r'var SLUG    = "[^"]*"', 'var SLUG    = "recording-2510"', new)
    if YT:
        new = re.sub(r'var YT_ID   = "[^"]*"', f'var YT_ID   = "{YT}"', new)
    else:
        print('  ⚠️  בלי --yt: מזהה היוטיוב של 25.10 לא הוחלף, הדף יציג את ההקלטה של 13.10')
    for line in new.split('\n'):
        if 'var CLOSES' in line or 'var SLUG' in line or 'var YT_ID' in line:
            print('  ' + line.strip())
    if APPLY:
        open(REC, encoding='utf-8', mode='w').write(new)
        print('  ✓ נכתב. הפריסה של הפורטל היא ידנית (זהירות: import journey ב-app.py)')


def check_livui():
    out = subprocess.run(['git', 'log', '--oneline', '-1'], cwd=LIVUI,
                         capture_output=True, text=True).stdout.strip()
    s = open(os.path.join(LIVUI, 'index.html'), encoding='utf-8').read()
    ok = OFFER_CLOSE in s
    print(f'  livui HEAD: {out}')
    print(f'  שעון הבונוס מקובע ל-{OFFER_CLOSE}: ' + ('✓' if ok else '✗'))
    if APPLY and ok:
        r = subprocess.run(['git', 'push', 'origin', 'HEAD:main'], cwd=LIVUI,
                           capture_output=True, text=True)
        print('  push:', (r.stdout + r.stderr).strip()[-200:])


def verify():
    for url, must in [('https://livui.mominvest.co.il/', 'רביעי 28.10'),
                      ('https://academy.mominvest.co.il/recording', 'ההקלטה')]:
        try:
            with urllib.request.urlopen(url, timeout=30) as f:
                body = f.read().decode('utf-8', 'ignore')
            print(f'  {url} → {f.status}, "{must}" ' + ('✓' if must in body else '✗ (לא נמצא)'))
        except Exception as e:
            print(f'  {url} → {e}')


print('1) דף ההקלטה');  patch_recording()
print('2) דפי הליווי');  check_livui()
print('3) בדיקה');       verify()
if not APPLY:
    print('\nיובש. להרצה אמיתית: --yt <YT_ID> --apply')
