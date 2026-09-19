#!/usr/bin/env python3
"""הפעלה חד-פעמית של קמפיין ההרשמות לוובינר 4.10 — 14 יום לפני ההדרכה (20/09/2026 09:00).
מדליק קמפיין + אדסט + 2 המודעות של 4.10, מאמת, מודיע בטלגרם, ומוריד את עצמו מ-launchd.
כיבוי לפני שרץ:  launchctl bootout gui/$(id -u)/local.webinar-0410-activate
בדיקה יבשה:      DRY_RUN=1 python3 activate-0410.py
"""
import json, os, subprocess, sys, time, urllib.request, urllib.parse, datetime
HOME = os.path.expanduser('~'); DRY = os.environ.get('DRY_RUN') == '1'
LABEL = 'local.webinar-0410-activate'; RUN_DAY = '2026-09-20'
CAMPAIGN = '120254624625430558'; ADSET = '120254624626500558'
ADS = {'VID-1 בכל שנתיים · 4.10': '120254896780600558', 'pic_Dreams · 4.10': '120254896781330558'}
V = 'https://graph.facebook.com/v21.0'; LOG = f'{HOME}/webinar-500k-0709/activate-0410.log'

def log(m):
    line = f"{datetime.datetime.now():%Y-%m-%d %H:%M} {m}"; print(line)
    open(LOG, 'a').write(line + '\n')

def token():
    try:
        t = subprocess.run([f'{HOME}/bin/meta-token', 'get'], capture_output=True, text=True, timeout=20).stdout.strip()
        if len(t) > 50: return t
    except Exception as e: log(f'keychain fail: {e}')
    d = json.load(open(f'{HOME}/ad-dashboard-ai/.meta-token.json'))
    return d.get('access_token') or d.get('token') or next(v for v in d.values() if isinstance(v, str) and len(v) > 50)

def api(path, data=None):
    q = dict(data or {}); q['access_token'] = T
    if data is None:
        return json.load(urllib.request.urlopen(f'{V}/{path}{"&" if "?" in path else "?"}{urllib.parse.urlencode(q)}', timeout=30))
    return json.load(urllib.request.urlopen(urllib.request.Request(f'{V}/{path}', data=urllib.parse.urlencode(q).encode()), timeout=30))

def telegram(msg):
    try:
        tok = json.load(open(f'{HOME}/claude-telegram-bot/config.json'))['botToken']
        data = urllib.parse.urlencode({'chat_id': 390198534, 'text': msg}).encode()
        if DRY: log(f'[dry] telegram: {msg}'); return
        urllib.request.urlopen(f'https://api.telegram.org/bot{tok}/sendMessage', data, timeout=30)
    except Exception as e: log(f'telegram fail: {e}')

def bootout():
    if DRY: log('[dry] would bootout launchd job'); return
    subprocess.run(['launchctl', 'bootout', f'gui/{os.getuid()}/{LABEL}'], capture_output=True)
    log('launchd job removed')

today = datetime.date.today().isoformat()
if today != RUN_DAY and not DRY:
    log(f'not the run day ({today} != {RUN_DAY}) — removing job without touching Meta'); bootout(); sys.exit(0)
T = token()
targets = [('campaign', CAMPAIGN), ('adset', ADSET)] + [(n, i) for n, i in ADS.items()]
results = []
for name, oid in targets:
    if DRY: log(f'[dry] would set {name} {oid} ACTIVE'); continue
    for attempt in range(3):
        try: r = api(oid, {'status': 'ACTIVE'}); log(f'{name} {oid} → {r}'); break
        except Exception as e:
            log(f'{name} attempt {attempt+1} failed: {e}'); time.sleep(20)
time.sleep(5 if not DRY else 0)
for name, oid in targets:
    try:
        st = api(f'{oid}?fields=effective_status,status')
        results.append(f"{name}: {st.get('status')} / {st.get('effective_status')}")
    except Exception as e: results.append(f'{name}: check failed {e}')
log('\n'.join(results))
telegram('📣 קמפיין ההרשמות לוובינר 4.10 הודלק (14 יום לפני, ₪100/יום, נשים 25-45).\n' + '\n'.join(results) +
         '\nלכיבוי: להשהות את הקמפיין "וובינר חצי מיליון 4.10 · הרשמות" ב-Ads Manager.')
bootout()
