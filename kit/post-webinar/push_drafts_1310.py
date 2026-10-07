"""יוצר בסמוב 5 טיוטות לרצף שאחרי וובינר 4.10, בעיצוב של המיילים של 8-9.9.
טיוטה בלבד: נמענת אחת (עדי). לא שולח כלום (שליחה היא קריאה נפרדת /Send)."""
import os, json, requests, html
KEY = [l.split('=', 1)[1].strip().strip('"') for l in open(os.path.expanduser('~/smoove-crm-sync/.env')) if l.startswith('SMOOVE_API_KEY')][0]
H = {'Authorization': KEY, 'User-Agent': 'Mozilla/5.0', 'Content-Type': 'application/json'}
IMG = 'https://content.viplus.com/adinahirr_gmail_com/Content/2_500x500-r(1).png'
LOGO = 'https://content.viplus.com/adinahirr_gmail_com/Content/%d7%90%d7%9e%d7%90%20%d7%9e%d7%a9%d7%a7%d7%99%d7%a2%d7%94%20%d7%9c%d7%95%d7%92%d7%95%20%d7%a9%d7%97%d7%95%d7%a8.png'
IG, WA = 'https://www.instagram.com/adi_somech_', 'https://wa.me/972509563781'
WA_GROUP = 'https://chat.whatsapp.com/I59tLUyA1CoGnJ4wFFMPqE'

def btn(text, url):
    return (f'<div><a href="{url}" style="color:#0000EE;text-decoration:underline;">'
            f'<strong><span style="font-size:22px;">{text}</span></strong></a></div>')

def para(lines):
    """שורות → בלוק; שורה ריקה = רווח. [[btn|טקסט|url]] = כפתור-קישור."""
    out = []
    for l in lines.strip('\n').split('\n'):
        if l.startswith('[[btn|'):
            t, u = l[6:-2].split('|'); out.append(btn(t, u))
        elif not l.strip(): out.append('<div><br></div>')
        else: out.append(f'<div>{l}</div>')
    return '\n'.join(out)

def page(body):
    return f'''<div dir="rtl" style="background:#ffffff;">
<table border="0" cellspacing="0" cellpadding="0" width="600" align="center" style="max-width:600px;width:100%;background:#ffffff;font-family:Arial;">
<tr><td dir="rtl" align="right" style="padding:29px;font-size:16px;line-height:32px;color:#000000;font-family:Arial;">
{body}
</td></tr>
<tr><td align="center" style="padding:15px 0;"><img src="{IMG}" width="225" height="225" alt="עדי סומך" style="display:block;border:0;"></td></tr>
<tr><td style="padding:10px 0;"><div style="border-bottom:1px solid #cccccc;height:0;"></div></td></tr>
<tr><td align="center" style="padding:5px 10px;">
<a href="{IG}" style="text-decoration:none;display:inline-block;margin:0 6px;"><img width="32" height="32" src="https://content.viplus.com/viplus/AtpTemplates/M/scl_instagram_fullColor.png" alt="Instagram" border="0"></a>
<a href="{WA}" style="text-decoration:none;display:inline-block;margin:0 6px;"><img width="32" height="32" src="https://content.viplus.com/viplus/AtpTemplates/M/scl_whatsapp_fullColor.png" alt="WhatsApp" border="0"></a>
</td></tr>
<tr><td align="center" style="padding:15px 0 30px;"><img src="{LOGO}" width="150" height="60" alt="אמא משקיעה" style="display:block;border:0;"></td></tr>
</table></div>'''

MAILS = json.load(open(os.path.join(os.path.dirname(__file__), 'mails1310.json')))
res = []
for m in MAILS:
    body = page(para(m['body']))
    r = requests.post('https://rest.smoove.io/v1/Campaigns', headers=H, timeout=60,
                      json={'subject': m['subject'], 'body': body, 'toMembersByEmail': ['adinahirr@gmail.com'], 'trackLinks': True})
    print(m['key'], r.status_code, r.text[:200]); res.append({'key': m['key'], 'subject': m['subject'], 'resp': r.json() if r.ok else r.text})
json.dump(res, open(os.path.join(os.path.dirname(__file__), 'created1310.json'), 'w'), ensure_ascii=False, indent=1)
