import json,re,sys,collections
D='../dict/'
hsk={}
for w in json.load(open(D+'hsk.json',encoding='utf8')):
    hsk[w['simplified']]=w.get('frequency',99999)
rows=collections.defaultdict(list)
rx=re.compile(r'^(\S+) (\S+) \[([^\]]*)\] /(.*)/$')
for l in open(D+'cedict_ts.u8',encoding='utf8'):
    if l.startswith('#'):continue
    m=rx.match(l.strip())
    if not m:continue
    t,s,p,e=m.groups()
    if len(s)>5 and s not in hsk:continue
    gl=[g.strip() for g in e.split('/') if g.strip() and not g.startswith('CL:') and not g.startswith('old variant of') and not g.startswith('variant of')]
    if not gl: continue
    def cl(g):
        g=re.sub(r'(?:\S+?\|)?(\S+?)\[[^\]]*\]',r'\1',g)
        return re.sub(r'\s+',' ',g).strip()
    gl=[cl(g) for g in gl]
    nosee=[g for g in gl if not g.startswith('see ') and not g.startswith('also written') and not g.startswith('abbr. for')]
    gl=nosee or gl
    sur=gl[0].startswith('surname ')
    gl=gl[:4]
    eng='; '.join(gl)[:110]
    p=p.replace('u:','ü').replace('\t',' ')
    r=hsk.get(s,60000)+(40000 if sur else 0)
    rows[s].append((r,p,eng))
out=[]
for s in sorted(rows):
    seen=set()
    for r,p,e in sorted(rows[s])[:6]:
        if (p,e) in seen: continue
        seen.add((p,e)); out.append('\t'.join([s,p,e,str(r//1000 if r<60000 else (9 if r<100000 else 99))]))
txt='\n'.join(out)
open(sys.argv[1],'w',encoding='utf8').write('window.DICT='+json.dumps(txt,ensure_ascii=False)+';')
print(len(out),len(txt)//1024,'KB')
