import json, os, sys, time
from concurrent.futures import ThreadPoolExecutor
from gtts import gTTS
H=os.path.dirname(os.path.abspath(__file__))
OUT=sys.argv[1]
os.makedirs(OUT,exist_ok=True)
def fnv(t):
    b=t.encode('utf8'); h=0x811c9dc5
    for x in b: h^=x; h=(h*16777619)&0xffffffff
    return f"{h:08x}-{len(b):x}"
texts=set()
# gather from sources
for line in open(f'{H}/vocab.txt',encoding='utf8'):
    if line.startswith('#') or not line.strip(): continue
    texts.add(line.split('|')[0])
PUN='，。？！、'
for line in open(f'{H}/sentences.txt',encoding='utf8'):
    if line.startswith('#') or not line.strip(): continue
    toks=[t for t in line.split('|')[1].split() if t not in PUN]
    texts.add(''.join(toks))
for sec in json.load(open(f'{H}/sample.json',encoding='utf8')):
    for q in sec['qs']:
        if q.get('audio'): texts.add(q['audio'])
texts.add('你好，欢迎来到汉语考试')
texts|=set(json.load(open(f'{H}/enum.json',encoding='utf8')))
texts={t for t in texts if t.strip()}
names={}
for t in texts:
    k=fnv(t); assert k not in names,(t,names[k]); names[k]=t
print('texts',len(texts))
def one(item):
    k,t=item; fp=f'{OUT}/{k}.mp3'
    if os.path.exists(fp) and os.path.getsize(fp)>500: return k,True
    for a in range(6):
        try:
            gTTS(t,lang='zh-CN').save(fp)
            if os.path.getsize(fp)>500: return k,True
        except Exception as e:
            time.sleep(1.5*(a+1))
    return k,False
ok=[];bad=[]
with ThreadPoolExecutor(8) as ex:
    for i,(k,r) in enumerate(ex.map(one,names.items())):
        (ok if r else bad).append(k)
        if i%200==0: print(i,flush=True)
print('ok',len(ok),'bad',[names[k] for k in bad])
json.dump(sorted(ok),open(f'{H}/audio_manifest.json','w'))
