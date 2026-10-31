import argparse
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parent.parent
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
    parser = argparse.ArgumentParser(description="Apply mobile image spacing to the Halo Earth theme")
    parser.add_argument(
        "--halo-data-dir",
        type=Path,
        default=ROOT / "halo-data",
        help="Halo data directory (defaults to halo-data under the repository)",
    )
    args = parser.parse_args()
    template = args.halo_data_dir / "themes" / "theme-earth" / "templates" / "post.html"

    if not template.exists():
        raise SystemExit(f"Halo Earth post template not found: {template}")

    content = template.read_text(encoding="utf-8")
    style_pattern = re.compile(r'    <style id="mobile-article-images">.*?    </style>', re.DOTALL)
    if style_pattern.search(content):
        updated, count = style_pattern.subn(STYLE, content, count=1)
    else:
        anchor = '    <link rel="stylesheet" crossorigin href="/themes/theme-earth/assets/markdown-body-BoBcq-aF.css">'
        if anchor not in content:
            raise SystemExit("Could not find the Earth theme stylesheet insertion point")
        updated = content.replace(anchor, f"{anchor}\n{STYLE}", 1)

    if updated != content:
        template.write_text(updated, encoding="utf-8", newline="")
    print(f"Applied mobile article image spacing to {template}")


if __name__ == "__main__":
    main()
