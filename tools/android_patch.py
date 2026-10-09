"""Small page changes for the Android app (applied to index.html and nyc.html).
The Android shell speaks the iPhone bridge, so the page only needs to know which phone it's on for labels."""
import sys
for path in ['index.html', 'nyc.html']:
    s = open(path, encoding='utf-8').read()
    n0 = s
    s = s.replace("const platform = () => NATIVE ? 'ios' :", "const platform = () => NATIVE ? (window.__ANDROID ? 'android' : 'ios') :", 1)
    s = s.replace("(b.voice==='personal'?'my voice':'iPhone voice')", "(b.voice==='personal'?'my voice':(window.__ANDROID?'phone voice':'iPhone voice'))", 1)
    old = "if(name==='denied'){ setPill('Location blocked','err'); $('nMeta').textContent='Location is off for Ski Nav. Settings > Ski Nav > Location > Always.'; }"
    new = "if(name==='denied'){ setPill('Location blocked','err'); $('nMeta').textContent= window.__ANDROID ? 'Location is off for Ski Nav. Settings > Apps > Ski Nav > Permissions > Location > Allow while using the app.' : 'Location is off for Ski Nav. Settings > Ski Nav > Location > Always.'; }"
    s = s.replace(old, new, 1)
    marker = "/* android: phone voice labels, no Personal Voice */"
    if marker not in s:
        s = s.replace("if(NATIVE){ toNative({cmd:'ready'});", marker + "\nif(window.__ANDROID){ document.querySelectorAll('#bsVoice [data-v=\"default\"], #oVoice [data-v=\"default\"]').forEach(b=>b.textContent='Phone voice'); document.querySelectorAll('#bsVoice [data-v=\"personal\"], #oVoice [data-v=\"personal\"]').forEach(b=>b.hidden=true); }\nif(NATIVE){ toNative({cmd:'ready'});", 1)
    changed = s != n0
    open(path, 'w', encoding='utf-8').write(s)
    print(path, 'patched' if changed else 'unchanged', s.count("window.__ANDROID"))
