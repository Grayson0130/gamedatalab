"""Build a portable, searchable documentation site; no CDN or runtime backend."""
import html
import json
import os
import re
import shutil
from pathlib import Path
from urllib.parse import urlsplit

try:
    import markdown
except ImportError:
    raise SystemExit('Install documentation dependency: python -m pip install -r requirements-docs.txt')

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'site'
EXCLUDE = {'.git','site','dist','.venv','__pycache__','.github'}
NAV = [('开始','README.md'),('2026 更新','docs/updates-2026.md'),
       ('埋点','docs/telemetry.md'),('指标','docs/metrics.md'),
       ('获客','docs/user-acquisition.md'),('LTV','docs/monetization-ltv.md'),
       ('留存与流失','docs/retention-churn-fraud.md'),('实验','docs/experimentation.md'),
       ('推荐','docs/recommendation.md'),('设计','docs/data-driven-design.md'),
       ('数据栈','docs/modern-stack-2026.md'),('治理','docs/governance.md'),
       ('AI 与 LQA','docs/ai-evaluation.md'),('职业','docs/career.md'),
       ('作品集','portfolio/README.md'),('结果','reports/demo/README.md'),
       ('来源','docs/sources.md'),('开发','docs/development.md')]


def output_path(relative):
    return Path('index.html') if str(relative) == 'README.md' else relative.with_suffix('.html')


def rewrite_link(match, relative):
    href = html.unescape(match.group(1))
    parsed = urlsplit(href)
    if parsed.scheme or parsed.netloc or not parsed.path.endswith('.md'):
        return match.group(0)
    target = Path(os.path.normpath(str(relative.parent/parsed.path)))
    destination = output_path(target)
    rewritten = os.path.relpath(destination, output_path(relative).parent).replace(os.sep,'/')
    if parsed.query:
        rewritten += '?'+parsed.query
    if parsed.fragment:
        rewritten += '#'+parsed.fragment
    return 'href="'+html.escape(rewritten, quote=True)+'"'


def main():
    sources = [p for p in ROOT.rglob('*') if p.is_file()
               and not EXCLUDE.intersection(p.relative_to(ROOT).parts)
               and not p.name.endswith(('.pyc','.zip'))]
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    records = []
    for p in sources:
        rel = p.relative_to(ROOT)
        if p.suffix == '.md':
            text = p.read_text(encoding='utf-8')
            title = next((line[2:] for line in text.splitlines() if line.startswith('# ')), p.stem)
            records.append({'title': title, 'path': str(output_path(rel)),
                            'excerpt': re.sub(r'[#*`|>\[\]]','',text)[:900]})
        elif rel != Path('index.html'):
            target = OUT/rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(p,target)
    for record in records:
        dest = Path(record['path'])
        rel = Path('README.md') if dest == Path('index.html') else dest.with_suffix('.md')
        text = (ROOT/rel).read_text(encoding='utf-8')
        content = markdown.markdown(text, extensions=['tables','fenced_code','toc'])
        content = re.sub(r'href="([^"]*)"', lambda m: rewrite_link(m,rel), content)
        prefix = os.path.relpath('.',dest.parent).replace(os.sep,'/')
        links = []
        for label,path in NAV:
            current = ' aria-current="page"' if Path(path) == rel else ''
            links.append(f'<a href="{prefix}/{output_path(Path(path))}"{current}>{html.escape(label)}</a>')
        navigation = ''.join(links)
        data = json.dumps(records,ensure_ascii=False).replace('<','\\u003c')
        dashboard = ''
        if dest == Path('index.html'):
            s = json.loads((ROOT/'reports/demo/summary.json').read_text())
            dashboard = f'''<section class="hero"><span class="eyebrow">GAME ANALYTICS / FIELD NOTES</span>
            <h1>从玩家行为，走到可靠决策。</h1><p>游戏数据科学 · 可复现分析 · 实验与 AI 评估</p>
            <div class="stats"><div><b>{s['users']:,}</b><span>合成玩家</span></div>
            <div><b>{s['events']:,}</b><span>合成事件</span></div>
            <div><b>3</b><span>可运行案例</span></div><div><b>2026.10</b><span>资料核对</span></div></div>
            <p class="fine">示例数据为合成，不代表真实行业表现。核心分析无需云服务。</p></section>'''
        page = f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">
        <meta name="viewport" content="width=device-width,initial-scale=1">
        <meta name="description" content="游戏数据科学中文实践：指标、留存、LTV、实验、AI 与本地化评估。">
        <title>{html.escape(record['title'])} · Game Data Lab</title>
        <link rel="stylesheet" href="{prefix}/assets/style.css"></head>
        <body><a class="skip" href="#content">跳至正文</a>
        <header><a class="brand" href="{prefix}/index.html">GDL<span>GAME DATA LAB</span></a>
        <span class="edition">2026 EDITION · v0.2</span></header>
        <div class="layout"><aside><label for="search">搜索文档</label>
        <input id="search" type="search" placeholder="留存、实验、LQA…" autocomplete="off">
        <div id="results" aria-live="polite"></div><nav aria-label="文档导航">{navigation}</nav></aside>
        <main id="content">{dashboard}<article>{content}</article>
        <footer>核对截至 2026-10-23 · 文档 CC BY 4.0 · 代码 MIT · 合成数据教学项目</footer></main></div>
        <script>const pages={data};const base={json.dumps(prefix)};
        const input=document.getElementById('search'),results=document.getElementById('results');
        input.addEventListener('input',()=>{{results.replaceChildren();const q=input.value.trim().toLowerCase();
        if(!q)return;const found=pages.filter(p=>(p.title+' '+p.excerpt).toLowerCase().includes(q)).slice(0,8);
        for(const p of found){{const a=document.createElement('a');a.href=base+'/'+p.path;a.textContent=p.title;results.append(a);}}
        if(!found.length)results.textContent='没有匹配文档';}});</script></body></html>'''
        target = OUT/dest
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_text(page,encoding='utf-8')
    (OUT/'.nojekyll').touch()
    print(f'Built {len(records)} HTML documents in {OUT}')


if __name__ == '__main__':
    main()
