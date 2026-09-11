import sys
from pathlib import Path

d = Path(sys.argv[1])
data = (d / "corpus.json").read_text(encoding="utf-8").replace("</", "<\\/")
html = (d / "template.html").read_text(encoding="utf-8").replace("__DATA__", data)
(d / "corpus-map.html").write_text(html, encoding="utf-8")
print(len(html))
