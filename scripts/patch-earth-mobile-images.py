from pathlib import Path
import re


ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "halo-data" / "themes" / "theme-earth" / "templates" / "post.html"
STYLE = '''    <style id="mobile-article-images">
      @media (max-width: 639px) {
        #content figure[data-content-type="image"] {
          width: calc(100% + 4rem - 8px);
          margin-top: 0;
          margin-bottom: 4px;
          margin-right: calc(-2rem + 4px);
          margin-left: calc(-2rem + 4px);
        }

        #content figure[data-content-type="image"] + p:empty {
          display: none;
        }

        #content figure[data-content-type="image"] > img {
          width: 100% !important;
          max-width: none !important;
          height: auto !important;
        }
      }
    </style>'''


def main():
    if not TEMPLATE.exists():
        raise SystemExit(f"Halo Earth post template not found: {TEMPLATE}")

    content = TEMPLATE.read_text(encoding="utf-8")
    style_pattern = re.compile(r'    <style id="mobile-article-images">.*?    </style>', re.DOTALL)
    if style_pattern.search(content):
        updated, count = style_pattern.subn(STYLE, content, count=1)
    else:
        anchor = '    <link rel="stylesheet" crossorigin href="/themes/theme-earth/assets/markdown-body-BoBcq-aF.css">'
        if anchor not in content:
            raise SystemExit("Could not find the Earth theme stylesheet insertion point")
        updated = content.replace(anchor, f"{anchor}\n{STYLE}", 1)

    if updated != content:
        TEMPLATE.write_text(updated, encoding="utf-8", newline="")
    print(f"Applied mobile article image spacing to {TEMPLATE}")


if __name__ == "__main__":
    main()
