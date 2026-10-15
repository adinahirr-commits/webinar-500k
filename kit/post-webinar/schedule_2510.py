#!/usr/bin/env python3
"""מתזמן את 5 מיילי אחרי-השידור של 25.10 — רק אחרי אישור עדי על הטקסטים.
נמענות: רשימת 25.10 (1176583) בלי רוכשות הליווי (1166676 אוקטובר, 1173306 נובמבר).
מייל אחד ביום. דדליין אחד בכל המיילים: רביעי 28.10 ב-20:00.
   python3 schedule_2510.py --apply
"""
import os, sys, json, importlib.util, requests

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('pd', os.path.join(HERE, 'push_drafts.py'))
src = open(spec.origin).read().split('MAILS = json.load')[0]
ns = {}
exec(src, ns)

LIST_ID = 1176583
EXCLUDE = [1166676, 1173306]
WHEN = [
    '2026-10-25T22:30:00',   # מיד בתום השידור: הלינק + ההקלטה
    '2026-10-26T08:30:00',   # קייס סטאדי
    '2026-10-27T08:30:00',   # שבירת התנגדות המחיר
    '2026-10-28T08:00:00',   # הוידוי + ההרשמה נסגרת הערב ב-20:00
    '2026-10-28T17:00:00',   # הסגירה
]

MAILS = json.load(open(os.path.join(HERE, 'mails2510.json')))
assert len(MAILS) == len(WHEN), f'{len(MAILS)} מיילים מול {len(WHEN)} מועדים'

if '--apply' not in sys.argv:
    for m, t in zip(MAILS, WHEN):
        print(t, '|', m['subject'])
    print('\nיובש. להרצה אמיתית: --apply')
    raise SystemExit

out = []
for m, t in zip(MAILS, WHEN):
    req = {'subject': m['subject'], 'body': ns['page'](ns['para'](m['body'])), 'trackLinks': True,
           'toListsById': [LIST_ID], 'excludeFromLists': EXCLUDE}
    r = requests.post('https://rest.smoove.io/v1/Campaigns', headers=ns['H'],
                      params={'scheduleTo': t}, json=req, timeout=60)
    print(t, r.status_code, r.text[:160])
    out.append({'when': t, 'subject': m['subject'], 'resp': r.json() if r.ok else r.text})
json.dump(out, open(os.path.join(HERE, 'scheduled2510.json'), 'w'), ensure_ascii=False, indent=1)
print('→ scheduled2510.json')
