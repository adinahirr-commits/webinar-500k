# -*- coding: utf-8 -*-
"""בונה את preview-faces.html: דף ההרשמה + סקשן הפרצופים (עמית ורות)."""
import os, io, json, re, sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
ROOT = os.path.abspath(ROOT)
SRC  = os.path.join(ROOT, 'index.html')
COPY = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'copy.json')

C = json.load(open(COPY, encoding='utf-8'))

CSS = """
  /* ---------- הצוות: פרצופים אמיתיים (מור, 23.9) ---------- */
  .team-say{max-width:520px;margin:0 auto 20px;text-align:center;font-size:1.06rem;
            line-height:1.6;color:#35364B;font-weight:600}
  .team-row{display:grid;grid-template-columns:1fr 1fr;gap:14px;max-width:440px;margin:0 auto 20px}
  .team-row figure{background:#fff;border:1px solid var(--line);border-radius:16px;
                   padding:14px 10px 16px;text-align:center;
                   box-shadow:0 12px 30px -22px rgba(26,27,46,.55)}
  .team-row img{width:116px;height:116px;border-radius:50%;object-fit:cover;margin:0 auto 10px}
  .team-row b{display:block;font-weight:900;font-size:1.08rem;line-height:1.25}
  .team-row span{display:block;font-size:.92rem;color:var(--soft);font-weight:600;margin-top:4px;line-height:1.35}
  .team-proof{max-width:360px;margin:0 auto;background:#fff;border:1px solid var(--line);
              border-radius:14px;padding:9px;box-shadow:0 10px 26px -20px rgba(26,27,46,.5)}
  .team-proof img{border-radius:9px;width:100%}
  .team-proof figcaption{font-size:.9rem;color:var(--soft);font-weight:700;padding:11px 6px 4px;text-align:center}
  .team-note{max-width:540px;margin:20px auto 0;text-align:center;font-size:.9rem;
             color:var(--soft);line-height:1.6}
  @media(max-width:420px){ .team-row{gap:10px} .team-row img{width:96px;height:96px} }
"""

SEC = """
<section class="bordered" id="team">
  <div class="wrap narrow">
    <h3>{h}</h3>
    <p class="team-say">{say}</p>
    <div class="team-row">
      <figure>
        <img src="assets/team-amit.jpg" alt="עמית, מהצוות של אמא משקיעה" width="480" height="480" loading="lazy">
        <b>עמית</b><span>מהצוות של אמא משקיעה</span>
      </figure>
      <figure>
        <img src="assets/team-ruth.jpg" alt="רות, מהצוות של אמא משקיעה" width="480" height="480" loading="lazy">
        <b>רות</b><span>מהצוות של אמא משקיעה</span>
      </figure>
    </div>
    <figure class="team-proof">
      <img src="assets/team-amit-proof.jpg" width="895" height="1000" loading="lazy"
           alt="הודעה שקיבלתי אחרי פגישה עם עמית: דיברתי עכשיו עם עמית, איזה אלוף הוא וחמוד, עשה לי ממש סדר בסבלנות, הסביר לי הכל, וגיליתי דווקא שאני במסלולים טובים יחסית">
      <figcaption>{cap}</figcaption>
    </figure>
    <p class="team-note">{note}</p>
  </div>
</section>
"""

def build(out_name, preview=True):
    html = open(SRC, encoding='utf-8').read()
    # CSS נכנס לפני סוף ה-style
    assert '</style>' in html
    html = html.replace('</style>', CSS + '</style>', 1)
    # הסקשן נכנס מיד לפני הטופס הסוגר
    anchor = '<section class="closing" id="form-bottom">'
    assert anchor in html, 'anchor not found'
    sec = SEC.format(h=C['h'], say=C['say'], cap=C['cap'], note=C['note'])
    html = html.replace(anchor, sec + '\n' + anchor, 1)
    if preview:
        html = html.replace('<head>', '<head>\n<meta name="robots" content="noindex,nofollow">', 1)
    open(os.path.join(ROOT, out_name), 'w', encoding='utf-8').write(html)
    print('wrote', out_name, len(html))

if __name__ == '__main__':
    build(sys.argv[1] if len(sys.argv) > 1 else 'preview-faces.html',
          preview=(len(sys.argv) < 3 or sys.argv[2] != '--live'))
