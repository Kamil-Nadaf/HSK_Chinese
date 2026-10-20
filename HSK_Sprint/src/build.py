import json, re, os, base64, subprocess, sys
H = os.path.dirname(os.path.abspath(__file__))
OUT = next((a for a in sys.argv[1:] if not a.startswith('--')), os.path.join(H, 'dist'))
os.makedirs(OUT, exist_ok=True)
FONT = '/mnt/user-data/uploads/Chinese Practice Sheets/fonts/LXGWNeoZhiSongPlus.ttf'

# ---------- vocab ----------
lessons, vocab, seen_ids = [], [], set()
cur = None
for line in open(f'{H}/vocab.txt', encoding='utf8'):
    line = line.rstrip('\n')
    if not line.strip():
        continue
    if line.startswith('#'):
        k, t = line[1:].strip().split('|')
        k = k.strip()
        k = k[1:] if k.startswith('L') else k
        cur = k
        lessons.append({'k': k, 't': t})
        continue
    f = line.split('|')
    h, p, e = f[0], f[1], f[2]
    em = f[3] if len(f) > 3 else ''
    fl = f[4] if len(f) > 4 else ''
    # allow flags in the emoji slot when no emoji given (e.g. "x")
    if len(f) == 4 and f[3] in ('x', 'w'):
        em, fl = '', f[3]
    vid = h + '|' + p
    assert vid not in seen_ids, vid
    seen_ids.add(vid)
    vocab.append({'id': vid, 'h': h, 'p': p, 'e': e, 'em': em, 'l': cur,
                  **({'x': 1} if 'x' in fl else {}), **({'w': 1} if 'w' in fl else {})})

# ---------- sentences ----------
PUNCT = '，。？！、'
sentences = []
for line in open(f'{H}/sentences.txt', encoding='utf8'):
    line = line.strip()
    if not line or line.startswith('#'):
        continue
    lv, toks, py, en = line.split('|')
    lv = 'S' if lv == '13' else lv
    t, pu = [], []
    for tok in toks.split():
        if tok in PUNCT:
            if t:
                pu[-1] = pu[-1] + tok
        else:
            t.append(tok)
            pu.append('')
    end = pu[-1]
    sentences.append({'l': lv, 't': t, 'pu': pu, 'end': end, 'p': py, 'e': en})

# ---------- Q&A ----------
qa = []
for line in open(f'{H}/qa.txt', encoding='utf8'):
    line = line.strip()
    if not line or line.startswith('#'):
        continue
    l, qz, qp, az, ap, ae = line.split('|')
    qa.append({'l': l, 'qz': qz, 'qp': qp, 'az': az, 'ap': ap, 'ae': ae})

sample = json.load(open(f'{H}/sample.json', encoding='utf8'))

# ---------- grammar ----------
grammar = [
 {'t': 'Say yes/no and who: 是, 不, 吗', 'p': 'S + 是 + noun   |   S + 不是 + noun   |   … 吗？',
  'e': [['我是学生。', 'Wǒ shì xuésheng.', 'I am a student.'], ['我不是老师。', 'Wǒ bú shì lǎoshī.', 'I am not a teacher.'], ['你是学生吗？', 'Nǐ shì xuésheng ma?', 'Are you a student?']],
  'n': '不 becomes bú before a 4th-tone syllable: 不是 bú shì, 不会 bú huì, 不客气 bú kèqi.'},
 {'t': 'Numbers: 二 or 两, and 一 as yāo', 'p': '两 + measure word + noun',
  'e': [['两个人', 'liǎng ge rén', 'two people'], ['两本书', 'liǎng běn shū', 'two books'], ['两块二毛', 'liǎng kuài èr máo', '2.2 yuan']],
  'n': 'Use 二 when counting or in a number (二十, 第二). In phone and room numbers, 1 is read yāo.'},
 {'t': 'Measure words', 'p': '一 + 个/口/只/本/杯 + noun',
  'e': [['你家有几口人？', 'Nǐ jiā yǒu jǐ kǒu rén?', 'How many people in your family?'], ['一只小猫', 'yì zhī xiǎo māo', 'one little cat'], ['一本书、一杯茶', 'yì běn shū, yì bēi chá', 'a book, a cup of tea']],
  'n': '个 is the default. 口 is only for family members, 只 for cats and dogs, 本 for books, 杯 for cups of drink.'},
 {'t': 'Asking age', 'p': '几岁 (under ten)  |  多大 (anyone)  |  多少岁 (anyone)  |  您今年多大了 (elders)',
  'e': [['你今年多大了？', 'Nǐ jīnnián duō dà le?', 'How old are you?'], ['我今年二十岁。', 'Wǒ jīnnián èrshí suì.', 'I am 20.']], 'n': ''},
 {'t': 'Having: 有 and 没有', 'p': 'S + 有 + noun   |   S + 没有 + noun   |   Place + 有 + thing',
  'e': [['我有两个姐姐。', 'Wǒ yǒu liǎng ge jiějie.', 'I have two older sisters.'], ['我没有姐姐。', 'Wǒ méiyǒu jiějie.', 'I have no older sister.'], ['桌子上有一本书。', 'Zhuōzi shàng yǒu yì běn shū.', 'There is a book on the table.']],
  'n': 'Negative is always 没有, never 不有. After 没有 drop the number and measure word.'},
 {'t': 'Ability: 会 and 能', 'p': 'S + 会 + verb (learned skill, will)   |   S + 能 + verb (able, allowed, conditions)',
  'e': [['我会说汉语。', 'Wǒ huì shuō Hànyǔ.', 'I can speak Chinese (learned).'], ['我能坐这儿吗？', 'Wǒ néng zuò zhèr ma?', 'May I sit here?'], ['我生病了，不能去学校。', 'Wǒ shēngbìng le, bù néng qù xuéxiào.', 'I am sick, I cannot go to school.']],
  'n': 'Answer a 能 question with 可以 or 不能. 会 also means "will": 今天会下雨吗？'},
 {'t': 'How: 怎么 and 怎么样', 'p': '怎么 + verb (how to do it)   |   noun + 怎么样？ (how is it)',
  'e': [['这个字怎么写？', 'Zhège zì zěnme xiě?', 'How do you write this character?'], ['今天天气怎么样？', 'Jīntiān tiānqì zěnmeyàng?', 'How is the weather today?']], 'n': ''},
 {'t': 'Dates and ages without 是', 'p': 'S + noun (date, weekday, age, nationality)',
  'e': [['今天星期三。', 'Jīntiān xīngqīsān.', 'Today is Wednesday.'], ['我二十岁。', 'Wǒ èrshí suì.', 'I am twenty.']],
  'n': 'Order is year, month, day, weekday: 2026年9月20号，星期日. 号 is spoken, 日 is written.'},
 {'t': 'Going somewhere to do something', 'p': 'S + 去 + place + verb phrase',
  'e': [['我去学校看书。', 'Wǒ qù xuéxiào kàn shū.', 'I go to school to read.'], ['下午我想去商店。', 'Xiàwǔ wǒ xiǎng qù shāngdiàn.', 'I want to go to the shop this afternoon.']], 'n': ''},
 {'t': 'Wanting: 想', 'p': 'S + 想 + verb (+ object)',
  'e': [['我想喝茶。', 'Wǒ xiǎng hē chá.', 'I want to drink tea.'], ['你想买什么？', 'Nǐ xiǎng mǎi shénme?', 'What do you want to buy?']], 'n': ''},
 {'t': 'Location: 在', 'p': 'A + 在 + B + 上面/下面/里面/前面/后面/左面/右面',
  'e': [['小狗在椅子下面。', 'Xiǎo gǒu zài yǐzi xiàmian.', 'The puppy is under the chair.'], ['商店在学校左面。', 'Shāngdiàn zài xuéxiào zuǒmian.', 'The shop is left of the school.'], ['你在哪儿？', 'Nǐ zài nǎr?', 'Where are you?']], 'n': ''},
 {'t': 'Doing something somewhere', 'p': 'S + 在 + place + verb',
  'e': [['我在学校学习汉语。', 'Wǒ zài xuéxiào xuéxí Hànyǔ.', 'I study Chinese at school.'], ['我在商店买杯子。', 'Wǒ zài shāngdiàn mǎi bēizi.', 'I buy cups at the shop.']], 'n': 'Place goes before the verb.'},
 {'t': 'Doing right now: 在 … 呢', 'p': 'S + 在 + verb + (object) + 呢   |   S + 没 + 在 + verb',
  'e': [['我在看书呢。', 'Wǒ zài kàn shū ne.', 'I am reading.'], ['他没在看书。', 'Tā méi zài kàn shū.', 'He is not reading.']], 'n': ''},
 {'t': 'Time words go before the verb', 'p': 'S + time + verb   (or time at the start)',
  'e': [['我七点去学校。', 'Wǒ qī diǎn qù xuéxiào.', 'I go to school at seven.'], ['我中午在家吃饭。', 'Wǒ zhōngwǔ zài jiā chī fàn.', 'I eat at home at noon.']],
  'n': 'Order: who, when, where, what. Clock: 十点十分, 十点一刻 (:15), 十点半 (:30), 八点差一分 (7:59). 前 = before: 五点前.'},
 {'t': 'Degree: 很, 太…了, 有点儿, 不太', 'p': '很 + adj   |   太 + adj + 了   |   有点儿 + adj   |   不太 + adj',
  'e': [['很热、不太热、有点儿热、太热了', 'hěn rè, bú tài rè, yǒudiǎnr rè, tài rè le', 'very / not very / a little / too hot']], 'n': '不冷不热 means neither cold nor hot.'},
 {'t': 'Do more or less: 多 / 少 + verb', 'p': '多 + verb + (些) + noun   |   少 + verb',
  'e': [['多吃些水果，多喝水。', 'Duō chī xiē shuǐguǒ, duō hē shuǐ.', 'Eat more fruit, drink more water.'], ['少吃蛋糕。', 'Shǎo chī dàngāo.', 'Eat less cake.']], 'n': ''},
 {'t': 'Money', 'p': '多少钱？  …块…毛',
  'e': [['这个杯子多少钱？', 'Zhège bēizi duōshao qián?', 'How much is this cup?'], ['五块二毛', 'wǔ kuài èr máo', '5.2 yuan'], ['一百块零五毛', 'yìbǎi kuài líng wǔ máo', '100.5 yuan']], 'n': '2 yuan is 两块. A gap inside a number is read 零.'},
 {'t': 'Phone calls: 喂, 给, 吧', 'p': '喂？ | 给 + person + 打电话 | suggestion + 吧',
  'e': [['我现在给她打电话。', 'Wǒ xiànzài gěi tā dǎ diànhuà.', 'I will call her now.'], ['你下午打吧。', 'Nǐ xiàwǔ dǎ ba.', 'Call this afternoon.']], 'n': 'Phone numbers are read digit by digit, with 1 as yāo.'},
]

# ---------- strokes ----------
chars = sorted({c for v in vocab for c in v['h'] if '一' <= c <= '鿿'})
strokes, missing = {}, []
for c in chars:
    fp = f'{H}/node_modules/hanzi-writer-data/{c}.json'
    if os.path.exists(fp):
        d = json.load(open(fp, encoding='utf8'))
        strokes[c] = {'strokes': d['strokes'], 'medians': d['medians']}
    else:
        missing.append(c)
print('chars', len(chars), 'missing', missing)

AUDIO = json.load(open(f'{H}/audio_manifest.json')) if os.path.exists(f'{H}/audio_manifest.json') and '--audio' in sys.argv else []
data = {'audio': AUDIO, 'vocab': vocab, 'lessons': lessons, 'sentences': sentences, 'qa': qa, 'sample': sample,
        'grammar': grammar, 'strokes': strokes}
data_js = json.dumps(data, ensure_ascii=False, separators=(',', ':'))

# ---------- template ----------
tpl = open(f'{H}/template.html', encoding='utf8').read()
hw = open(f'{H}/node_modules/hanzi-writer/dist/hanzi-writer.min.js', encoding='utf8').read().replace('</script', '<\\/script')
html = tpl.replace('/*DATA*/', data_js).replace('/*HANZIWRITER*/', hw)

# ---------- fonts: Noto Serif SC from Google Fonts, with system Song fonts as fallback ----------
LINK = ('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
        '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@500;700&display=swap">')
def _ff(fam, wt, sub, rng):
    d = open(f'{H}/fonts/ibm-plex-sans-{sub}-{wt}-normal.woff2', 'rb').read()
    return ("@font-face{font-family:'IBM Plex Sans';font-style:normal;font-weight:%s;font-display:swap;src:url(data:font/woff2;base64,%s) format('woff2');unicode-range:%s}"
            % (wt, base64.b64encode(d).decode(), rng))
LAT = 'U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+0304,U+0308,U+0329,U+2000-206F,U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD'
EXT = 'U+0100-02BA,U+02BD-02C5,U+02C7-02CC,U+02CE-02D7,U+02DD-02FF,U+0304,U+0308,U+0329,U+1D00-1DBF,U+1E00-1E9F,U+1EF2-1EFF,U+2020,U+20A0-20AB,U+20AD-20C0,U+2113,U+2C60-2C7F,U+A720-A7FF'
FONTCSS = ''.join(_ff('IBM Plex Sans', w, 'latin', LAT) + _ff('IBM Plex Sans', w, 'latin-ext', EXT) for w in (400, 600))
html = html.replace('/*FONTFACE*/', FONTCSS)
html = html.replace('<title>HSK 1 Sprint</title>', '<title>HSK 1 Sprint</title>\n' + LINK, 1)

PWA = '\n<meta name="theme-color" content="#0F6E7A">\n<link rel="manifest" href="manifest.webmanifest">\n<link rel="icon" href="icon-192.png">'
# fragment for the Artifact tool
open(f'{OUT}/fragment.html', 'w', encoding='utf8').write(html)
# standalone page for local use
full = ('<!doctype html>\n<html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">'
        '<meta name="color-scheme" content="light dark">'
        '<style>:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}</style></head><body>\n'
        + html.replace('<title>HSK 1 Sprint</title>', '').replace(LINK, '').replace(PWA, '') + '\n</body></html>')
full = full.replace('<head>', '<head><title>HSK 1 Sprint</title>' + PWA + LINK, 1)
open(f'{OUT}/index.html', 'w', encoding='utf8').write(full)
print('vocab', len(vocab), 'sentences', len(sentences), 'qa', len(qa), 'size kb', len(full) // 1024)
import shutil, glob
for f in glob.glob(f'{H}/pwa/*'):
    shutil.copy(f, OUT)
