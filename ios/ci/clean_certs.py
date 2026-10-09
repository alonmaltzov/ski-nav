"""Revoke the throwaway "Created via API" development certificates that CI builds make.

Every cloud build signs the archive with a fresh Apple Development certificate (the runner is wiped after),
and Apple caps how many an account can have. This removes only certificates named "Created via API" of a
development type; Alon's own certificates and the cloud-managed distribution certificate are never touched.
Usage: python3 clean_certs.py <key.p8> <key id> <issuer id>"""
import sys, time, json, urllib.request
import jwt  # PyJWT

p8, kid, iss = sys.argv[1], sys.argv[2], sys.argv[3]
token = jwt.encode({'iss': iss, 'iat': int(time.time()), 'exp': int(time.time()) + 600, 'aud': 'appstoreconnect-v1'},
                   open(p8).read(), algorithm='ES256', headers={'kid': kid, 'typ': 'JWT'})
def call(method, path):
    req = urllib.request.Request('https://api.appstoreconnect.apple.com' + path, method=method,
                                 headers={'Authorization': 'Bearer ' + token})
    with urllib.request.urlopen(req, timeout=30) as r:
        body = r.read()
        return json.loads(body) if body else {}

certs = call('GET', '/v1/certificates?limit=200&fields[certificates]=name,certificateType,displayName')['data']
n = 0
for c in certs:
    a = c['attributes']
    if a.get('name') == 'Created via API' and 'DEVELOPMENT' in (a.get('certificateType') or ''):
        call('DELETE', '/v1/certificates/' + c['id']); n += 1
print(f'revoked {n} throwaway CI development certificate(s); {len(certs) - n} left untouched')
