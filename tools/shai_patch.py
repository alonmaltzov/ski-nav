"""The guide is Shai: his face everywhere the old guide face was (Brief button, brief, ask, tour), and his name."""
import os, re, json
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIN, SKIN2, HAIR, BEARD = '#D6A27A', '#C08A62', '#2B201B', '#33261F'
BODY = (
 '<circle cx="60" cy="60" r="58" fill="#FFF4EA"/>'
 '<path d="M18 120 Q22 96 46 92 L74 92 Q98 96 102 120 Z" fill="#D81F26"/>'
 f'<path d="M50 86 L70 86 L72 98 Q60 104 48 98 Z" fill="{SKIN2}"/>'
 '<path d="M46 93 Q60 104 74 93 L78 99 Q60 112 42 99 Z" fill="#F2F2F2"/>'
 f'<ellipse cx="31" cy="64" rx="6" ry="9" fill="{SKIN2}"/><ellipse cx="89" cy="64" rx="6" ry="9" fill="{SKIN2}"/>'
 f'<path d="M32 58 Q32 28 60 28 Q88 28 88 58 L88 70 Q88 94 60 96 Q32 94 32 70 Z" fill="{SKIN}"/>'
 f'<path d="M31 56 Q28 26 58 22 Q86 20 90 50 Q86 40 76 37 Q66 33 52 36 Q38 38 34 52 Z" fill="{HAIR}"/>'
 f'<path d="M33 66 Q34 84 46 92 Q60 100 74 92 Q86 84 87 66 Q84 76 78 80 Q70 74 60 74 Q50 74 42 80 Q36 76 33 66 Z" fill="{BEARD}"/>'
 f'<path d="M47 76 Q53 71 60 73 Q67 71 73 76 Q67 75 60 77 Q53 75 47 76 Z" fill="{BEARD}"/>'
 f'<path d="M58 58 Q55 68 58 69 Q60 70 63 68" stroke="{SKIN2}" stroke-width="2.4" fill="none" stroke-linecap="round"/>'
 '<ellipse cx="48" cy="58" rx="3.6" ry="4" fill="#2B2420"/><ellipse cx="72" cy="58" rx="3.6" ry="4" fill="#2B2420"/><circle cx="49.2" cy="56.6" r="1.2" fill="#fff"/><circle cx="73.2" cy="56.6" r="1.2" fill="#fff"/>'
 f'<path d="M41 50 Q48 46 54 49" stroke="{HAIR}" stroke-width="3.4" fill="none" stroke-linecap="round"/><path d="M66 49 Q72 46 79 50" stroke="{HAIR}" stroke-width="3.4" fill="none" stroke-linecap="round"/>')
MOUTHS = ('<path class="gm-smile" d="M52 79 Q60 86 68 79 Q60 82 52 79 Z" fill="#7A1F2B"/>'
          '<ellipse class="gm-talk" cx="60" cy="81" rx="6.5" ry="5" fill="#7A1F2B"/>'
          '<ellipse class="gm-o" cx="60" cy="81" rx="3.5" ry="3.2" fill="#2B2420"/>')
def svg(cls='gface', talk_only=False):
    m = '<ellipse cx="60" cy="81" rx="6.5" ry="5" fill="#7A1F2B"/>' if talk_only else MOUTHS
    return f'<svg class="{cls}" viewBox="0 0 120 120" aria-hidden="true">{BODY}{m}</svg>'
def run(path):
    s = open(path, encoding='utf-8').read()
    s, n1 = re.subn(r'<svg class="gface" viewBox="14 14 92 100" aria-hidden="true">.*?</svg>', lambda m: svg(), s, flags=re.S)
    # the tour's face (open mouth)
    s, n2 = re.subn(r'<svg viewBox="0 0 120 120" aria-hidden="true"><circle cx="60" cy="64" r="44".*?</svg>', lambda m: svg('', True).replace('class="" ', ''), s, flags=re.S)
    s = s.replace('"name": "Snowy"', '"name": "Shai"')
    s = s.replace('<b>Brief</b><small><i class="ldot" id="wxLiftDot" hidden></i>', '<b>Shai</b><small><i class="ldot" id="wxLiftDot" hidden></i>')
    s = s.replace("say:(o)=>(o.name ? 'Hey '+o.name+'! ' : 'Hey! ')+'I’m your guide. Allow location, pick Always.',",
                  "say:(o)=>(o.name ? 'Hey '+o.name+'! ' : 'Hey! ')+'Shai here. Couldn’t make the trip, so I’m in your phone. Allow location, pick Always.',")
    s = s.replace("html:(o)=>'<b>'+(o.name ? 'Hey '+esc(o.name)+'!' : 'Hey!')+' I’m your guide.</b><br>Allow location, pick <b>Always</b>.',",
                  "html:(o)=>'<b>'+(o.name ? 'Hey '+esc(o.name)+'!' : 'Hey!')+' Shai here.</b> Couldn’t make the trip, so I’m in your phone.<br>Allow location, pick <b>Always</b>.',")
    s = s.replace("'Today’s brief: the day, weather, what to wear and lifts'", "'Shai: today’s brief, the day, weather, what to wear and lifts'")
    open(path, 'w', encoding='utf-8').write(s)
    return n1, n2
if __name__ == '__main__':
    print('index', run(os.path.join(ROOT, 'index.html')))
    b = json.load(open(os.path.join(ROOT, 'brief.json'))); b['name'] = 'Shai'; json.dump(b, open(os.path.join(ROOT, 'brief.json'), 'w'), indent=2, ensure_ascii=False)
