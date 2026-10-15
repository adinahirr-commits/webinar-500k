#!/usr/bin/env python3
"""שיפור 2/5: מייל התוכן "למה בעצם אני עושה את זה" (55617607) עובר מתאריך קבוע
(20.10 08:30) ל-3 שעות מרגע ההרשמה, באוטומציה 275984 של וובינר 25.10.

הפער: ב-13.10 מייל התוכן המקביל הגיע ל-200 מתוך 383 נרשמות (48%), ומייל
"3 דברים" ל-45 בלבד (12%) — כי התאריך הקבוע קדם לגל ההרשמה. שתיים מהרוכשות
נרשמו פחות מחצי שעה לפני השידור וקיבלו רק מייל אישור.

מה הסקריפט עושה: מוסיף שרשרת [הצטרפות לרשימה → השהיה 3 שעות] שמתחברת לאותו
node של המייל, ומוחק את טריגר התאריך הקבוע — כך אף אחת לא מקבלת את המייל פעמיים.
מיילי הלוגיסטיקה (24.10, 25.10 ×2) ומייל התוכן השני (22.10) לא נוגעים.
"""
import json, sys, os
sys.path.insert(0, os.path.expanduser('~/webinar-500k-0709/kit/smoove'))
import bpmn_tool as T

IID = '275984'
MAIL_NODE = 'vip_275984_339157829260_1406'      # email,a-send → 55617607
OLD_TRIG = 'vip_275984_339157829260_1548'       # time,t-schedule-send 2026-10-20T08:30
LIST_KEY = 'oqa4ggmbxkqf1i8d'                   # רשימת 25.10 (1176583) בהקשר האוטומציה הזאת
NEW = 'vip_275984_339600000001_'
DRY = '--apply' not in sys.argv

p, bd, st, nm, al = T.get(IID)
print('state', st, '| nodes', len(bd['nodes']), '| conns', len(bd['connections']))
ids = {n['nodeId'] for n in bd['nodes']}
assert MAIL_NODE in ids and OLD_TRIG in ids, 'מבנה האוטומציה השתנה — עוצר'
trig = [n for n in bd['nodes'] if n['nodeId'] == OLD_TRIG][0]
assert trig['nodeData'].get('scheduledDate') == '2026-10-20T08:30:00', trig['nodeData']
assert any(n['nodeId'] == NEW + '1' for n in bd['nodes']) is False, 'כבר רץ פעם אחת'

nodes = [n for n in bd['nodes'] if n['nodeId'] != OLD_TRIG]
nodes.append({"nodeData": {"listKey": LIST_KEY, "applyOn": "new", "toolTip": ""},
              "positionX": 2340, "positionY": 650, "nodeId": NEW + '1', "nodeKey": "list,t-added"})
nodes.append({"nodeData": {"delayType": "hours", "delayAmount": 3, "skipOn": [],
                           "specifyTime": False, "scheduleTime": "08:00", "toolTip": ""},
              "positionX": 2150, "positionY": 650, "nodeId": NEW + '2', "nodeKey": "time,a-delay"})

conns = [c for c in bd['connections'] if c['nodeSourceId'] != OLD_TRIG and c['nodeTargetId'] != OLD_TRIG]
assert len(conns) == len(bd['connections']) - 1, 'יותר מחיבור אחד לטריגר הישן'
conns.append({"connectionId": f"vip_con_{NEW}1_{NEW}2_list-added", "nodeSourceId": NEW + '1',
              "nodeTargetId": NEW + '2', "connectionContext": "list-added", "allowOnlyOnce": False})
conns.append({"connectionId": f"vip_con_{NEW}2_{MAIL_NODE}_time-delay", "nodeSourceId": NEW + '2',
              "nodeTargetId": MAIL_NODE, "connectionContext": "time-delay", "allowOnlyOnce": False})

new_bd = {"nodes": nodes, "connections": conns}
print('after: nodes', len(nodes), 'conns', len(conns))
if DRY:
    print(json.dumps(new_bd, ensure_ascii=False, indent=1)[:1200])
    print('\nDRY RUN — להרצה אמיתית: --apply')
    raise SystemExit
ok, st2, nm2, bd2 = T.save(IID, new_bd)
print('saved ok =', ok, '| state', st2)
for n in bd2['nodes']:
    print('  ', n['nodeId'], n['nodeKey'], json.dumps(n['nodeData'], ensure_ascii=False)[:120])
