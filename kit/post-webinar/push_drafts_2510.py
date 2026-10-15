#!/usr/bin/env python3
"""יוצר בסמוב את 5 הטיוטות של הרצף שאחרי וובינר 25.10, בעיצוב המיילים של עדי.
טיוטה בלבד: נמענת אחת (עדי). לא שולח ולא מתזמן כלום.
   python3 push_drafts_2510.py
"""
import os, json, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('pd', os.path.join(HERE, 'push_drafts.py'))
src = open(spec.origin).read().split('MAILS = json.load')[0]
ns = {}
exec(src, ns)

import requests
MAILS = json.load(open(os.path.join(HERE, 'mails2510.json')))
out = []
for m in MAILS:
    body = ns['page'](ns['para'](m['body']))
    r = requests.post('https://rest.smoove.io/v1/Campaigns', headers=ns['H'], timeout=60,
                      json={'subject': m['subject'], 'body': body,
                            'toMembersByEmail': ['adinahirr@gmail.com'], 'trackLinks': True})
    print(m['key'], r.status_code, r.text[:160])
    out.append({'key': m['key'], 'subject': m['subject'],
                'id': (r.json() or {}).get('id') if r.ok else None,
                'resp': r.json() if r.ok else r.text})
json.dump(out, open(os.path.join(HERE, 'created2510.json'), 'w'), ensure_ascii=False, indent=1)
print('→ created2510.json')
