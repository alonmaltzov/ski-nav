"""Builds the Liquid Glass web demo: index.html + demo/glass.css + demo/glass.js -> one file. Usage: build_glass_demo.py OUT.html"""
import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
s = open(os.path.join(ROOT, 'index.html'), encoding='utf-8').read()
css = open(os.path.join(ROOT, 'demo', 'glass.css'), encoding='utf-8').read()
js = open(os.path.join(ROOT, 'demo', 'glass.js'), encoding='utf-8').read()
skip_tour = "<script>try{localStorage.setItem('skinav-onb','1')}catch(e){}</script>"
s = s.replace('<head>', '<head>' + skip_tour, 1)
i = s.find('</head>'); s = s[:i] + '<style id="lg-css">' + css + '</style>' + s[i:]
i = s.rfind('</body>')
s = (s[:i] if i > 0 else s) + '<script id="lg-js">' + js + '</script>' + (s[i:] if i > 0 else '')
open(sys.argv[1], 'w', encoding='utf-8').write(s)
print('wrote', sys.argv[1], len(s))
