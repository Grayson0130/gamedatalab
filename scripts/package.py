"""Package verified source plus built site, with deterministic file metadata."""
import hashlib
import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXCLUDE = {'.git','dist','.venv','__pycache__'}


def main():
    if not (ROOT/'site/index.html').exists():
        raise SystemExit('Build site before packaging')
    files = sorted(p for p in ROOT.rglob('*') if p.is_file()
                   and not EXCLUDE.intersection(p.relative_to(ROOT).parts)
                   and not p.name.endswith(('.pyc','.zip'))
                   and 'my-demo' not in p.relative_to(ROOT).parts)
    manifest = {'release':'0.2.0','research_cutoff':'2026-10-23',
                'base_commit':'fc294c1166f216b845bef81e51edb7894b907e3e',
                'files': {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}}
    out = ROOT/'dist/gamedatalab-2026-v0.2.0.zip'
    out.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for p in files:
            info = zipfile.ZipInfo('gamedatalab/'+str(p.relative_to(ROOT)),(2026,10,23,0,0,0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            z.writestr(info,p.read_bytes())
        info = zipfile.ZipInfo('gamedatalab/PACKAGE-MANIFEST.json',(2026,10,23,0,0,0))
        info.compress_type = zipfile.ZIP_DEFLATED
        z.writestr(info,json.dumps(manifest,indent=2,ensure_ascii=False)+'\n')
    print(f'{out} ({out.stat().st_size:,} bytes)')


if __name__ == '__main__':
    main()
