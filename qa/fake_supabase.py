"""A tiny stand-in for Supabase's REST API (just /rest/v1/rpc/<function>) on top of a local Postgres,
so the group features can be tested end to end without the real project.
Usage: python3 qa/fake_supabase.py <port> <postgres dsn>"""
import json, sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import psycopg2
from psycopg2.extras import Json

PORT = int(sys.argv[1]); DSN = sys.argv[2]
ALLOWED = {'create_trip', 'trip_preview', 'join_trip', 'trip_state', 'post_position', 'set_sharing', 'update_me', 'set_meet', 'set_plan', 'remove_member'}

class H(BaseHTTPRequestHandler):
    def _cors(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Headers', 'apikey, authorization, content-type, prefer')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
    def do_OPTIONS(self):
        self.send_response(204); self._cors(); self.end_headers()
    def do_POST(self):
        fn = self.path.split('?')[0].rsplit('/', 1)[-1]
        if not self.path.startswith('/rest/v1/rpc/') or fn not in ALLOWED or not self.headers.get('apikey'):
            self.send_response(404); self._cors(); self.end_headers(); return
        args = json.loads(self.rfile.read(int(self.headers.get('Content-Length') or 0)) or b'{}')
        args = {k: Json(v) if isinstance(v, (dict, list)) else v for k, v in args.items()}
        names = sorted(args)
        sql = 'select %s(%s)' % (fn, ', '.join('%s => %%(%s)s' % (k, k) for k in names))
        try:
            with psycopg2.connect(DSN) as c, c.cursor() as cur:
                cur.execute('set role anon')
                cur.execute(sql, args)
                out = cur.fetchone()[0]
            body = json.dumps(out).encode(); self.send_response(200)
        except psycopg2.Error as e:
            body = json.dumps({'message': (e.pgerror or str(e)).split('\n')[0].replace('ERROR:  ', ''), 'code': e.pgcode}).encode(); self.send_response(400)
        self._cors(); self.send_header('Content-Type', 'application/json'); self.end_headers(); self.wfile.write(body)
    def log_message(self, *a): pass

ThreadingHTTPServer(('127.0.0.1', PORT), H).serve_forever()
