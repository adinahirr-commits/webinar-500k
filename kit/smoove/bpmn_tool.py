#!/usr/bin/env python3
"""עריכת אוטומציה בסמוב בלי דפדפן (עוגיות כרום): get / save / activate / stop. גיבוי לפני ואחרי ב-~/smoove-backups."""
import sys, os, re, json, html, urllib.request, urllib.parse, datetime
from html.parser import HTMLParser
sys.path.insert(0, os.path.expanduser('~/smoove-watch')); import watch
BK = os.path.expanduser('~/smoove-backups')
class Form(HTMLParser):
    def __init__(s): super().__init__(convert_charrefs=True); s.f = []
    def handle_starttag(s, t, a):
        a = dict(a)
        if t == 'input' and a.get('name'):
            ty = (a.get('type') or 'text').lower()
            if ty in ('submit', 'button', 'image', 'file', 'reset'): return
            if ty in ('checkbox', 'radio') and 'checked' not in a: return
            s.f.append([a['name'], a.get('value') or ''])
def req(url, data=None):
    h = {'Cookie': watch.admin_cookies(), 'User-Agent': 'Mozilla/5.0'}
    if data: h['Content-Type'] = 'application/x-www-form-urlencoded'
    return urllib.request.urlopen(urllib.request.Request(url, data=data, headers=h), timeout=120).read().decode('utf-8', 'replace')
def url(iid): return f'https://admin.smoove.io/modules/Bpmn/BpmnEdit.aspx?iid={iid}'
def parse(page):
    bd = json.loads(html.unescape(re.search(r'id="bpmnData"[^>]*value="([^"]*)"', page).group(1)))
    st = re.search(r'id="bpmnState"[^>]*value="([^"]*)"', page).group(1)
    nm = re.search(r'id="bpmnName"[^>]*value="([^"]*)"', page); nm = html.unescape(nm.group(1)) if nm else ''
    al = re.search(r'id="bpmnAll"[^>]*value="([^"]*)"', page).group(1)
    return bd, st, nm, al
def get(iid):
    p = req(url(iid)); bd, st, nm, al = parse(p); return p, bd, st, nm, al
def backup(iid, tag, bd):
    f = f'{BK}/bpmn_{iid}_{tag}_{datetime.datetime.now():%Y-%m-%d_%H%M%S}.json'
    json.dump(bd, open(f, 'w'), ensure_ascii=False); return f
def save(iid, new_bd, new_name=None):
    page, bd, st, nm, al = get(iid)
    backup(iid, 'before', bd)
    form = Form(); form.feed(page)
    P = 'ctl00$BodyContentPlaceHolder$'
    fields = []
    for n, v in form.f:
        if n in (P + 'bpmnData', P + 'bpmnIsUnsaved'): continue   # השמות המלאים — בלי הקידומת הערך הישן נשלח במקביל והשרת שומר אותו
        if new_name and n == P + 'bpmnName': v = new_name
        fields.append((n, v))
    fields += [(P + 'bpmnData', json.dumps(new_bd, ensure_ascii=False, separators=(',', ':'))), (P + 'bpmnIsUnsaved', 'true'),
               (P + 'bpmnSave', 'שמור')]
    req(url(iid), urllib.parse.urlencode(fields).encode())
    page2, bd2, st2, nm2, al2 = get(iid)
    backup(iid, 'after', bd2)
    want = sorted(json.dumps(n['nodeData'], sort_keys=True) for n in new_bd['nodes'])
    got = sorted(json.dumps(n['nodeData'], sort_keys=True) for n in bd2['nodes'])
    ok = want == got and len(bd2['connections']) == len(new_bd['connections'])
    return ok, st2, nm2, bd2
def postback(iid, label):
    """לחיצה על 'הפעלה' / 'עצירה' — ה-target נשלף מה-href של הקישור."""
    page, bd, st, nm, al = get(iid)
    m = re.search(r'WebForm_PostBackOptions\("([^"]+)"[^)]*\)\)">\s*' + label, html.unescape(page))
    if not m:
        # fallback: look for the anchor id patterns
        ids = re.findall(r"href=\"javascript:__doPostBack\(&#39;([^&]+)&#39;", page)
        raise SystemExit(f'no button "{label}"; targets={ids[:8]}')
    target = m.group(1)
    form = Form(); form.feed(page)
    P = 'ctl00$BodyContentPlaceHolder$'
    fields = [(n, v) for n, v in form.f if n not in ('__EVENTTARGET', '__EVENTARGUMENT', P + 'bpmnIsUnsaved')]
    fields += [('__EVENTTARGET', target), ('__EVENTARGUMENT', ''), (P + 'bpmnIsUnsaved', 'false')]
    req(url(iid), urllib.parse.urlencode(fields).encode())
    return get(iid)[2]
if __name__ == '__main__':
    iid = sys.argv[1]; cmd = sys.argv[2] if len(sys.argv) > 2 else 'get'
    page, bd, st, nm, al = get(iid)
    if cmd == 'get':
        print(iid, st, nm, al)
        for n in bd['nodes']: print('  ', n['nodeKey'], n['nodeId'], {k: v for k, v in n['nodeData'].items() if k != 'toolTip'})
        print('  connections:', len(bd['connections']))
    elif cmd == 'buttons':
        print(re.findall(r"__doPostBack\(&#39;([^&]+)&#39;,&#39;&#39;\)[^>]*>\s*([^<\s]+)", page)[:10])
