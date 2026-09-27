#!/usr/bin/env python3
"""
תיוג UTM לשתי מודעות הוובינר 4.10 — להריץ ב-05/10 בבוקר, אחרי שהקמפיין נסגר (end_time 4.10 20:00).
משימה strategy:measure:utm-webinar. לא נוגעים בהן לפני כן: pic_Dreams מביאה לידים ב-8₪ ותיוג שולח לביקורת ומאפס למידה.

    python3 tag-ads-0410.py            # יבש: מראה מה ישתנה
    APPLY=1 python3 tag-ads-0410.py    # מבצע

מה קורה: לכל מודעה נוצר קריאייטיב חדש מאותו פוסט (object_story_id, כדי לשמור לייקים ותגובות)
עם url_tags, והמודעה מוצבעת אליו. הסטטוס לא משתנה (המודעות ממילא נגמרו). המודעות של המחזור
הבא נוצרות כבר מתויגות — ר' kit/WEBINAR-IN-A-BOX.md סעיף 1 שורה 7.
"""
import json, os, subprocess, urllib.parse, urllib.request, sys, datetime

HOME = os.path.expanduser('~'); APPLY = os.environ.get('APPLY') == '1'
V = 'https://graph.facebook.com/v21.0'
CYCLE = json.load(open(f'{HOME}/webinar-500k-0709/kit/cycle.json', encoding='utf-8'))
ADS = CYCLE['meta']['ads']; UTM_CAMPAIGN = CYCLE['meta']['utm_campaign']
TAGS = f'ref=facebookad&utm_source=facebook&utm_medium=paid&utm_campaign={UTM_CAMPAIGN}&utm_content={{{{ad.name}}}}'
ACCOUNT = None

def token():
    try:
        t = subprocess.run([f'{HOME}/bin/meta-token', 'get'], capture_output=True, text=True, timeout=20).stdout.strip()
        if t: return t
    except Exception: pass
    d = json.load(open(f'{HOME}/ad-dashboard-ai/.meta-token.json')); return d.get('access_token') or d.get('token')
T = token()

def get(path, **q):
    q['access_token'] = T
    return json.load(urllib.request.urlopen(f'{V}/{path}?{urllib.parse.urlencode(q)}', timeout=30))
def post(path, **q):
    q['access_token'] = T
    return json.load(urllib.request.urlopen(urllib.request.Request(f'{V}/{path}', data=urllib.parse.urlencode(q).encode()), timeout=30))

end = datetime.datetime.fromisoformat(CYCLE['date'] + 'T' + CYCLE['time'])
if APPLY and datetime.datetime.now() < end:
    print(f'⛔ הקמפיין עדיין רץ (נסגר {end:%d.%m %H:%M}). לא מתייגים מודעה שמוציאה כסף.'); sys.exit(1)

for name, aid in ADS.items():
    ad = get(aid, fields='name,status,effective_status,account_id,creative{id,url_tags,effective_object_story_id,name}')
    cr = ad['creative']; ACCOUNT = ad['account_id']
    print(f'▸ {ad["name"]} ({aid}) · {ad["effective_status"]} · creative {cr["id"]} · url_tags={cr.get("url_tags") or "—"}')
    if cr.get('url_tags') == TAGS:
        print('   ✓ כבר מתויגת'); continue
    print(f'   → יווצר קריאייטיב חדש מפוסט {cr.get("effective_object_story_id")} עם:\n     {TAGS}')
    if not APPLY: continue
    new = post(f'act_{ACCOUNT}/adcreatives', name=f'{cr.get("name") or ad["name"]} · utm', object_story_id=cr['effective_object_story_id'], url_tags=TAGS)
    upd = post(aid, creative=json.dumps({'creative_id': new['id']}))
    chk = get(aid, fields='creative{id,url_tags}')
    print(f'   ✅ creative {new["id"]} · ad updated={upd.get("success")} · now url_tags={chk["creative"].get("url_tags")}')

if not APPLY: print('\n(יבש. להריץ עם APPLY=1 ב-05/10 בבוקר.)')
