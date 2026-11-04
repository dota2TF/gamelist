"""生成可双击打开的本地预览；修改页面或配置后重新运行本脚本。"""

import base64
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import unquote, urlparse


ROOT = Path(__file__).resolve().parent.parent
html = (ROOT / "index.html").read_text(encoding="utf-8")
styles = (ROOT / "styles.css").read_text(encoding="utf-8")
script = (ROOT / "app.js").read_text(encoding="utf-8")
config = json.loads((ROOT / "game_list.json").read_text(encoding="utf-8"))

for game in config["data"]["items"]:
    image = urlparse(game["imageUrl"])
    if image.netloc == "dota2tf.github.io" and image.path.startswith("/gamelist/"):
        game["imageUrl"] = unquote(image.path.removeprefix("/gamelist/"))

# 只在生成的预览中替换网络读取，正式页面仍使用 JSON 配置入口。
start = script.index("    const response = await fetch(CONFIG_URL,")
end = script.index("    allGames =", start)
embedded_config = json.dumps(config, ensure_ascii=False).replace("<", "\\u003c")
script = script[:start] + f"    const config = validateConfig({embedded_config});\n" + script[end:]


def csp_hash(content):
    digest = hashlib.sha256(content.encode("utf-8")).digest()
    return "'sha256-" + base64.b64encode(digest).decode("ascii") + "'"


policy = (
    "default-src 'none'; img-src 'self' https://dota2tf.github.io data:; "
    f"script-src {csp_hash(script)}; style-src {csp_hash(styles)}; "
    "base-uri 'none'; form-action 'none'"
)
html = re.sub(
    r'(<meta\s+http-equiv="Content-Security-Policy"\s+content=")[^"]*("\s*>)',
    lambda match: match[1] + policy + match[2],
    html,
)
html = re.sub(r'<link rel="stylesheet" href="styles\.css[^\"]*">', lambda _: f"<style>{styles}</style>", html)
html = re.sub(r'<script src="app\.js[^\"]*" defer></script>\n', "", html)
html = html.replace("  </body>", f"    <script>{script}</script>\n  </body>")
output = ROOT / "local-preview.html"
output.write_text(html, encoding="utf-8", newline="\n")
print(output)
