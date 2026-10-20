from playwright.sync_api import sync_playwright
import json
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page()
    pg.goto('file:///tmp/claude-0/-home-claude/ec4a174b-80ec-5a39-937b-a8fca1aea0f7/scratchpad/hsk/dist/index.html')
    t=pg.evaluate("window.__enum()")
    print(len(t), pg.evaluate("window.__fnv('你好，欢迎来到汉语考试')"))
    json.dump(t,open('enum.json','w'),ensure_ascii=False)
