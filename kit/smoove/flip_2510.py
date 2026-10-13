#!/usr/bin/env python3
"""המעבר למחזור 25.10 (רץ ב-13/10 11:00): דחיפת הדפים, הפעלת האוטומציות החדשות, עצירת אישור 13.10, עדכון מרכז הלינקים."""
import sys, os, subprocess, json, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import bpmn_tool as T
log = lambda m: print(f'{datetime.datetime.now():%H:%M:%S} {m}', flush=True)
step = sys.argv[1] if len(sys.argv) > 1 else 'all'

if step in ('all', 'pages'):
    r = subprocess.run(['git', 'push', 'origin', 'HEAD'], cwd=os.path.expanduser('~/webinar-500k-0709'), capture_output=True, text=True)
    log(f'git push: rc={r.returncode} {r.stderr.strip()[-200:]}')

if step in ('all', 'smoove'):
    for iid, label in (('275983', 'הפעלה'), ('275984', 'הפעלה'), ('275442', 'עצירה')):
        try:
            st = T.postback(iid, label); log(f'{iid} {label} → {st}')
        except SystemExit as e: log(f'{iid} {label} FAILED: {e}')

if step in ('all', 'links'):
    import psycopg2
    env = {l.split('=', 1)[0]: l.split('=', 1)[1].strip() for l in open(os.path.expanduser('~/course-portal/.env')) if '=' in l and not l.startswith('#')}
    c = psycopg2.connect(env['DATABASE_URL']); cur = c.cursor()
    cur.execute("update links set url=%s where code='webinar-cal'", ('https://calendar.google.com/calendar/event?action=TEMPLATE&tmeid=ZmJqM29icjg1bm9scnU3ZmprMGR2Y2twYmcg&tmsrc=adinahirr%40gmail.com',))
    cur.execute("update links set url=%s where code='webinar-zoom'", ('https://us06web.zoom.us/j/5110698373?pwd=Si81b0pUSlV5ZkRrZkEvcCtCL0xWZz09',))
    c.commit()
    cur.execute("select code,url from links where code in ('webinar-cal','webinar-zoom')"); log(f'links: {cur.fetchall()}')

if step in ('all', 'watch'):
    p = os.path.expanduser('~/link-watch/sites.json'); s = open(p, encoding='utf-8').read()
    s = s.replace('"10:00",\n        "13.10"', '"20:00",\n        "25.10"').replace('"tmeid=ZGR2Z2tmYWgwMG9qODZmOHBndGM3bzIydjgg"', '"tmeid=ZmJqM29icjg1bm9scnU3ZmprMGR2Y2twYmcg"').replace('"webinar.ics",\n        "13.10"', '"webinar.ics",\n        "25.10"')
    open(p, 'w', encoding='utf-8').write(s); json.load(open(p)); log('link-watch sites.json → 25.10')
