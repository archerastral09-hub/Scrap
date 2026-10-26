import sys, os, re, csv, email
from email import policy
from bs4 import BeautifulSoup

def html_of(path):
    raw = open(path, 'rb').read()
    try:
        m = email.message_from_bytes(raw, policy=policy.default)
        for p in m.walk():
            if p.get_content_type() == 'text/html':
                return p.get_payload(decode=True).decode('utf-8', 'replace')
    except Exception:
        pass
    return raw.decode('utf-8', 'replace')

def parse(path):
    s = BeautifulSoup(html_of(path), 'html.parser')
    lines = [l for l in s.get_text('\n', strip=True).split('\n') if l]
    t = '\n'.join(lines)
    siren = (re.search(r'SIREN\s*:?\s*([\d ]{9,11})', t) or [None, ''])[1].replace(' ', '')
    h1 = s.find('h1')
    nom = h1.get_text(strip=True) if h1 else ''
    if not nom:
        title = s.title.get_text() if s.title else ''
        nom = re.split(r' - ', title)[0].strip()
    adresse = ''
    if 'Adresse' in lines:
        i = lines.index('Adresse')
        adresse = ' '.join(lines[i+1:i+4])
    return [siren, nom, adresse, os.path.basename(path)]

if __name__ == '__main__':
    root, out = sys.argv[1], sys.argv[2]
    rows = []
    for d, _, fs in os.walk(root):
        for f in fs:
            try: rows.append(parse(os.path.join(d, f)))
            except Exception as e: rows.append(['', '', 'ERREUR ' + str(e), f])
    with open(out, 'w', newline='', encoding='utf-8-sig') as fh:
        w = csv.writer(fh); w.writerow(['siren', 'nom', 'adresse', 'fichier']); w.writerows(rows)
    print(len(rows), 'fiches')
