#!/usr/bin/env python3
"""שיפור 2/5, השלמה: מייל התוכן "למה בעצם אני עושה את זה" עבר ב-15/10 מתאריך
קבוע (20.10 08:30) ל-3 שעות מרגע ההרשמה. מי שנרשמה *לפני* השינוי לא תעבור
בטריגר ההצטרפות, ולכן המייל מתוזמן לה בנפרד — לאותו תאריך ושעה שתוכננו
מההתחלה, 20.10 08:30. כך אף אחת לא מקבלת פעמיים ואף אחת לא מפספסת.
"""
import sys, os, json, requests
sys.path.insert(0, os.path.expanduser('~/smoove-watch')); import watch
sys.path.insert(0, os.path.expanduser('~/webinar-500k-0709/kit/smoove')); import mail_tool as mt

LIST = '1176583'                 # נרשמות וובינר 25.10
BUYERS = ('1166676', '1173306')  # רוכשות הליווי — לא מקבלות מיילי וובינר
MAIL = '55617607'
WHEN = '2026-10-20T08:30:00'
KEY = [l.split('=', 1)[1].strip().strip('"') for l in
       open(os.path.expanduser('~/smoove-crm-sync/.env')) if l.startswith('SMOOVE_API_KEY')][0]
H = {'Authorization': KEY, 'User-Agent': 'Mozilla/5.0', 'Content-Type': 'application/json'}


def contacts(lid):
    out, p = [], 1
    while True:
        b = watch.rest_api(f'Lists/{lid}/Contacts?page={p}&itemsPerPage=100&fields=email,firstName')
        rows = b if isinstance(b, list) else (b.get('items') or [])
        out += rows
        if len(rows) < 100:
            return out
        p += 1


regs = {(c.get('email') or '').strip().lower() for c in contacts(LIST)}
regs.discard('')
skip = set()
for b in BUYERS:
    skip |= {(c.get('email') or '').strip().lower() for c in contacts(b)}
to = sorted(regs - skip)
page = mt.page(MAIL)
subject = mt.subject(page)
body = mt.body(MAIL)
print(f'נמענות: {len(to)} (מתוך {len(regs)} ברשימה, {len(regs & skip)} רוכשות הוחרגו)')
print('נושא:', subject)
print('25.10 בגוף:', '25.10' in body, '| [[שם]]:', '[[שם]]' in body, '| אורך', len(body))
print('מתוזמן ל:', WHEN)
print('5 ראשונות:', to[:5])
if '--apply' not in sys.argv:
    print('\nDRY RUN — להרצה אמיתית: --apply')
    raise SystemExit
r = requests.post('https://rest.smoove.io/v1/Campaigns', headers=H, timeout=90,
                  params={'scheduleTo': WHEN},
                  json={'subject': subject, 'body': body, 'trackLinks': True, 'toMembersByEmail': to})
print('POST', r.status_code, r.text[:400])
if r.ok:
    json.dump({'when': WHEN, 'subject': subject, 'to': to, 'resp': r.json()},
              open(os.path.expanduser('~/oneoff/os-webinar-improvements/catchup_content_mail.json'), 'w'),
              ensure_ascii=False, indent=1)
