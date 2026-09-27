#!/usr/bin/env python3
"""
וובינר בקופסה — מחזור חדש של "חצי מיליון לכל ילד" בפקודה אחת.

    python3 kit/new-cycle.py --date 2026-11-08 --time 20:00            # תוכנית בלבד (מה ישתנה, מתי יישלח כל מייל)
    python3 kit/new-cycle.py --date 2026-11-08 --time 20:00 --apply    # מעדכן את דפי ההרשמה והתודה + כותב את המיילים המלאים ל-kit/out/
    python3 kit/new-cycle.py ... --apply --smoove                      # + פותח רשימה בסמוב ויוצר את 5 המיילים כטיוטות (נמענת: עדי בלבד)
    python3 kit/new-cycle.py ... --apply --portal                      # + מוסיף את המחזור ל-course-portal (app.py + webinar_kpi.py), בלי commit

אופציונלי: --zoom URL  --cal URL  --wa URL  (בלי — נשארים של המחזור הקודם, והצ'קליסט מזכיר להחליף)

מה הוא לא עושה (ובכוונה): לא שולח שום דבר, לא מפעיל אוטומציה, לא נוגע במודעות במטא.
הכל נשאר טיוטה עד שעדי מאשרת. הצ'קליסט המלא: WEBINAR-IN-A-BOX.md
"""
import argparse, datetime, json, os, re, sys, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
PORTAL = os.path.expanduser('~/course-portal')
DAYS = ['שני', 'שלישי', 'רביעי', 'חמישי', 'שישי', 'שבת', 'ראשון']   # weekday(): Monday=0

def load_cycle():
    return json.load(open(os.path.join(HERE, 'cycle.json'), encoding='utf-8'))

def shabbat_shift(dt):
    """אין הודעות בשבת: שישי מ-16:00 עד מוצ"ש 20:30 → מוצ"ש 20:30. מחזיר (dt חדש, האם הוזז)."""
    wd = dt.weekday()
    if (wd == 4 and dt.hour >= 16) or (wd == 5 and (dt.hour, dt.minute) < (20, 30)):
        base = dt if wd == 5 else dt + datetime.timedelta(days=1)
        return base.replace(hour=20, minute=30), True
    return dt, False

def date_str(d):
    return f'{d.day}.{d.month}'

def render(template, vals):
    body = re.sub(r'^---\n.*?\n---\n', '', template, flags=re.S)
    for k, v in vals.items():
        body = body.replace('{{%s}}' % k, v)
    return body

def replace_page(path, old, new, plan):
    s = open(path, encoding='utf-8').read(); orig = s
    date_re = re.compile(r'(?<![\d.])' + re.escape(old['date_str']) + r'(?![\d])')
    s = s.replace('יום ' + old['day'], 'יום ' + new['day'])
    s = date_re.sub(new['date_str'], s)
    if old['time'] != new['time']:
        s = s.replace(old['time'], new['time'])
    for k in ('code', 'page_id', 'thanks_id', 'recording_id'):
        s = s.replace(old[k], new[k])
    for k in ('zoom', 'calendar_template', 'whatsapp_group'):
        if old[k] != new[k]:
            s = s.replace(old[k], new[k])
    n = sum(1 for a, b in zip(orig.splitlines(), s.splitlines()) if a != b)
    plan.append(f'{os.path.relpath(path, REPO)}: {n} שורות משתנות')
    return s

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--date', required=True, help='YYYY-MM-DD של השידור')
    ap.add_argument('--time', default='20:00')
    ap.add_argument('--zoom'); ap.add_argument('--cal'); ap.add_argument('--wa')
    ap.add_argument('--apply', action='store_true'); ap.add_argument('--smoove', action='store_true'); ap.add_argument('--portal', action='store_true')
    a = ap.parse_args()

    old = load_cycle()
    d = datetime.date.fromisoformat(a.date)
    hh, mm = map(int, a.time.split(':'))
    ddmm = f'{d.day:02d}{d.month:02d}'
    new = dict(old)
    new.update({
        'code': 'w' + ddmm, 'date': a.date, 'date_str': date_str(d), 'day': DAYS[d.weekday()], 'time': a.time,
        'page_id': 'webinar-' + ddmm, 'thanks_id': 'thanks-' + ddmm, 'recording_id': 'recording-' + ddmm,
        'zoom': a.zoom or old['zoom'], 'calendar_template': a.cal or old['calendar_template'], 'whatsapp_group': a.wa or old['whatsapp_group'],
        'smoove_list_name': f'וובינר חצי מליון לכל ילד {d.day}/{d.month}/{d.strftime("%y")}',
        'deck_name': f'חצי מליון לכל ילד {d.day}/{d.month}',
        'sales_close': (datetime.datetime.combine(d, datetime.time(22, 0)) + datetime.timedelta(days=2)).strftime('%Y-%m-%d %H:%M'),
        'smoove_list_id': '', 'smoove_list_key': '', 'calendar_event_id': '',
        'smoove': {'automation_scheduled': '', 'automation_confirmation': '', 'confirmation_email': '', 'sequence_emails': [],
                   'whatsapp_5min_template': old['smoove']['whatsapp_5min_template'], 'previous_cycle': old['code']},
        'meta': {'campaign': old['meta']['campaign'], 'adset': '', 'ads': {}, 'utm_campaign': 'webinar' + ddmm},
        'canva_deck': '',
    })
    if d.weekday() in (4, 5):
        print('⛔ השידור נופל על שישי/שבת. תבחרי תאריך אחר.'); sys.exit(1)

    print(f'📦 מחזור חדש: יום {new["day"]} {new["date_str"]} בשעה {new["time"]}  (קוד {new["code"]}, במקום {old["code"]})\n')

    # ── המיילים ──
    vals = {'DAY': new['day'], 'TIME': new['time'], 'ZOOM': new['zoom'], 'CAL': new['calendar_template'], 'WA_GROUP': new['whatsapp_group']}
    emails = []
    for f in sorted(os.listdir(os.path.join(HERE, 'emails'))):
        if not f.endswith('.md'): continue
        t = open(os.path.join(HERE, 'emails', f), encoding='utf-8').read()
        off = int(re.search(r'send_day_offset: (-?\d+)', t).group(1))
        at = re.search(r'send_time: (\d\d:\d\d)', t).group(1)
        send = datetime.datetime.combine(d + datetime.timedelta(days=off), datetime.time(*map(int, at.split(':'))))
        if off == 0 and at == '19:30':   # "עוד חצי שעה" — תמיד חצי שעה לפני השידור
            send = datetime.datetime.combine(d, datetime.time(hh, mm)) - datetime.timedelta(minutes=30)
        send, moved = shabbat_shift(send)
        body = render(t, vals)
        subject = re.search(r'^נושא: (.+)$', body, re.M).group(1).replace('20:00', new['time'])
        body = body.replace('נושא: ' + re.search(r'^נושא: (.+)$', body, re.M).group(1) + '\n\n', '', 1)
        emails.append({'file': f, 'subject': subject, 'send': send, 'moved': moved, 'body': body})
    print('✉️  לוח השליחה של 5 מיילי הציפייה (כולם טיוטות עד שעדי מאשרת):')
    for e in emails:
        print(f'   {e["send"]:%a %d.%m %H:%M}  {e["subject"]}' + ('   ⚠️ הוזז בגלל שבת' if e['moved'] else ''))
    leftovers = sorted({m for e in emails for m in re.findall(r'\{\{[A-Z_]+\}\}', e['body'])})
    if leftovers: print('   ⚠️ placeholders שלא מולאו:', leftovers)

    # ── הדפים ──
    plan = []
    pages = {}
    for rel in ('index.html', 'thanks/index.html'):
        p = os.path.join(REPO, rel)
        pages[p] = replace_page(p, old, new, plan)
    print('\n🌐 דפי ההרשמה והתודה:'); [print('   ' + x) for x in plan]
    if not a.zoom: print('   ⚠️ לינק הזום נשאר של המחזור הקודם — ליצור פגישה חדשה בזום ולהריץ שוב עם --zoom')
    if not a.cal: print('   ⚠️ אירוע היומן נשאר של המחזור הקודם — עדי יוצרת אירוע חדש ביומן, ואז --cal עם לינק ה-TEMPLATE')
    if not a.wa: print('   ℹ️ קבוצת הווטסאפ נשארת אותה קבוצה (ככה היה גם בין 7.9 ל-4.10)')

    if not a.apply:
        print('\n(תוכנית בלבד. להריץ שוב עם --apply כדי לכתוב.)'); return

    # ── כתיבה ──
    for p, s in pages.items():
        open(p, 'w', encoding='utf-8').write(s)
    outdir = os.path.join(HERE, 'out', new['code']); os.makedirs(outdir, exist_ok=True)
    for e in emails:
        open(os.path.join(outdir, e['file']), 'w', encoding='utf-8').write(f'נושא: {e["subject"]}\nשליחה: {e["send"]:%Y-%m-%d %H:%M}\n\n{e["body"]}')
    print(f'\n✅ הדפים עודכנו, המיילים המלאים ב-kit/out/{new["code"]}/')

    if a.smoove:
        key = [l.split('=', 1)[1].strip() for l in open(os.path.expanduser('~/mama-sales/.env')) if l.startswith('SMOOVE_API_KEY=')][0]
        H = {'Authorization': key, 'User-Agent': 'curl/8.7.1', 'Content-Type': 'application/json'}
        def post(path, data):
            r = urllib.request.urlopen(urllib.request.Request('https://rest.smoove.io/v1' + path, data=json.dumps(data).encode(), headers=H), timeout=30)
            return json.load(r)
        lst = post('/Lists', {'name': new['smoove_list_name'], 'description': f'נרשמות לשידור {new["date_str"]} (נוצר מ-kit/new-cycle.py)'})
        new['smoove_list_id'] = str(lst.get('id') or lst.get('listId') or '')
        print(f'📋 רשימת סמוב נפתחה: {new["smoove_list_id"]} "{new["smoove_list_name"]}"')
        ids = []
        for e in emails:
            html_body = '<div dir="rtl" style="font-family:Arial;font-size:17px;line-height:1.7">' + e['body'].strip().replace('\n', '<br>') + '</div>'
            c = post('/Campaigns', {'subject': e['subject'], 'body': html_body, 'toMembersByEmail': ['adinahirr@gmail.com']})
            ids.append(c.get('id')); print(f'   טיוטה {c.get("id")}: {e["subject"]}')
        new['smoove']['sequence_emails'] = ids

    if a.portal:
        ap_path = os.path.join(PORTAL, 'app.py'); s = open(ap_path, encoding='utf-8').read()
        line = f'    "{new["code"]}": os.environ.get("WEBINAR_{ddmm}_LIST_ID", "{new["smoove_list_id"] or "TODO"}"),\n'
        if new['code'] not in s:
            s = s.replace(f'    "{old["code"]}": os.environ.get(', line + f'    "{old["code"]}": os.environ.get(', 1)
            open(ap_path, 'w', encoding='utf-8').write(s)
        kp = os.path.join(PORTAL, 'webinar_kpi.py'); k = open(kp, encoding='utf-8').read()
        if new['code'] not in k:
            block = ('    {\n' f'        "slug": "{new["code"]}",\n' f'        "name": "חצי מיליון לכל ילד · {new["date_str"]}",\n'
                     f'        "meta_match": "{new["date_str"]}",\n' f'        "live_at": "{new["date"]} {new["time"]}",\n'
                     f'        "closes_at": "{new["sales_close"]}",\n' f'        "page": "{new["page_id"]}",\n' f'        "thanks": "{new["thanks_id"]}",\n'
                     '        "wa": "wa-group",\n        "cal": ["cal-google", "cal-ics"],\n' f'        "recording": "{new["recording_id"]}",\n'
                     '        "sales": ["livui", "livui-price", "livui-bonus", "livui-pay"],\n        "product": ["הליווי של אמא משקיעה"],\n'
                     '        "price": 2800,\n        "offer_min": 88,\n        "seats": 30,\n    },\n')
            k = k.replace('WEBINARS = [\n', 'WEBINARS = [\n' + block, 1)
            open(kp, 'w', encoding='utf-8').write(k)
        print('🧩 course-portal: המחזור נוסף ל-app.py (WEBINARS) ול-webinar_kpi.py — לבדוק diff, להוסיף לוח mama_hub אם צריך, ולפרוס')

    json.dump(new, open(os.path.join(HERE, 'cycle.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    prev = os.path.join(HERE, f'cycle-{old["code"]}.json'); json.dump(old, open(prev, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'\n💾 cycle.json עודכן (הקודם נשמר ב-{os.path.basename(prev)}). עכשיו: WEBINAR-IN-A-BOX.md, שלב "אחרי הסקריפט".')

if __name__ == '__main__':
    main()
