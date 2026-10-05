"""Turn QA logs (qa-out/*/log.txt) into qa-out/REPORT.md and qa-out/summary.json."""
import json, os, glob, re, sys

OUT = os.environ.get('QA_OUT', os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'qa-out'))
runs = {}
for log in sorted(glob.glob(os.path.join(OUT, '*', 'log.txt'))):
    name = os.path.basename(os.path.dirname(log))
    r = runs[name] = dict(audits=[], results=[], errors=[], done=False, shots=sorted(os.path.basename(p) for p in glob.glob(os.path.join(os.path.dirname(log), '*.png'))))
    for line in open(log, errors='replace'):
        m = re.search(r'QA (AUDIT|RESULT) (\{.*\})\s*$', line)
        if m:
            try: obj = json.loads(m.group(2))
            except Exception: continue
            (r['audits'] if m.group(1) == 'AUDIT' else r['results']).append(obj)
        elif 'QA DONE' in line: r['done'] = True
        elif re.search(r'\[web\] (ERROR|REJECT)|\[app\] .*(ERROR|failed|crashed)', line): r['errors'].append(line.strip()[:300])

md = ['# Ski Nav QA report', '']
total_fail = 0
for name, r in runs.items():
    fails = [x for x in r['results'] if not x.get('ok')]
    a_issues = sum(len(a['small']) + len(a['covered']) + len(a['offscreen']) + len(a['overflowX']) for a in r['audits'])
    total_fail += len(fails) + a_issues + len(r['errors']) + (0 if r['done'] else 1)
    md += [f'## {name}', '',
           f"Tour finished: {'yes' if r['done'] else '**NO**'} · checks {len(r['results']) - len(fails)}/{len(r['results'])} passed · "
           f"layout issues {a_issues} · JS/app errors {len(r['errors'])} · screenshots {len(r['shots'])}", '']
    md += ['### Behaviour checks', ''] + [f"- {'PASS' if x.get('ok') else '**FAIL**'} {x.get('check')}{(': ' + str(x.get('detail'))) if x.get('detail') else ''}" for x in r['results']] + ['']
    md += ['### Layout per screen', '', '| screen | page | targets | too small (<44) | glove (<52) | covered | offscreen | sideways scroll | tiny text (<12px) | crowded |', '|---|---|---|---|---|---|---|---|---|---|']
    for a in r['audits']:
        md.append(f"| {a['screen']} | {a['page']} | {a['targets']} | {len(a['small'])} | {len(a['gloveSmall'])} | {len(a['covered'])} | {len(a['offscreen'])} | {len(a['overflowX'])} | {len(a['tinyText'])} | {len(a['crowded'])} |")
    md.append('')
    for a in r['audits']:
        det = []
        for k, title in [('small', 'Too small'), ('gloveSmall', 'Small for gloves'), ('covered', 'Covered (tap goes elsewhere)'), ('offscreen', 'Off screen'), ('overflowX', 'Sideways scroll'), ('tinyText', 'Tiny text'), ('crowded', 'Crowded')]:
            if a[k]: det.append(f"- {title}: " + '; '.join(json.dumps(x, ensure_ascii=False) if not isinstance(x, str) else x for x in a[k][:12]))
        if det: md += [f"#### {a['screen']}"] + det + ['']
    if r['errors']: md += ['### Errors', ''] + ['- `' + e.replace('`', "'") + '`' for e in r['errors'][:30]] + ['']
md.insert(2, f"**Overall: {'ALL CLEAR' if total_fail == 0 else str(total_fail) + ' issue(s)'}**\n")
open(os.path.join(OUT, 'REPORT.md'), 'w').write('\n'.join(md))
json.dump(runs, open(os.path.join(OUT, 'summary.json'), 'w'), indent=1)
print('\n'.join(md[:12]))
print('issues', total_fail)
