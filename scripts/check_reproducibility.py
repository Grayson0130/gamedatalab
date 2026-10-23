"""Compare two independent default runs and the committed sample byte-for-byte."""
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory() as tmp:
    dirs = [Path(tmp)/'one', Path(tmp)/'two']
    for directory in dirs:
        subprocess.run([sys.executable,'-m','gamedatalab','--output',str(directory)], cwd=ROOT, check=True)
    names = sorted(p.name for p in dirs[0].iterdir())
    for name in names:
        expected = (ROOT/'reports/demo'/name).read_bytes()
        assert (dirs[0]/name).read_bytes() == (dirs[1]/name).read_bytes() == expected, name
print('Reproducibility verified: independent runs match committed demo files.')
