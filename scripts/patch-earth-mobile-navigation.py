"""Install the shared mobile header/drawer in an installed Halo Earth theme.

Usage: sudo python3 scripts/patch-earth-mobile-navigation.py --halo-data-dir /opt/halo-data
Restart Halo after applying so its template cache is cleared.
"""

import argparse
from pathlib import Path
import re
import shutil


ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "deploy" / "theme-earth"
MARKER = '<!-- resource-mobile-navigation -->'
HEADER = re.compile(r'<header\s+id="header-menu"')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--halo-data-dir", type=Path, default=ROOT / "halo-data")
    args = parser.parse_args()
    templates = args.halo_data_dir / "themes" / "theme-earth" / "templates"
    if not templates.is_dir():
        raise SystemExit(f"Halo Earth templates not found: {templates}")

    # Validate all templates before writing; existing desktop markup stays intact.
    updates = {}
    for template in templates.glob("*.html"):
        content = template.read_text(encoding="utf-8")
        if not HEADER.search(content) or MARKER in content:
            continue
        if "</head>" not in content:
            raise SystemExit(f"Missing </head>: {template}")
        head = '''<!-- resource-mobile-navigation-assets -->
    <link rel="stylesheet" href="/themes/theme-earth/assets/resource-mobile-navigation.css?v=1" />
    <script defer src="/themes/theme-earth/assets/resource-mobile-navigation.js?v=1"></script>
  </head>'''
        content = content.replace("</head>", head, 1)
        content = HEADER.sub(MARKER + '\n    <th:block th:replace="~{modules/resource-mobile-navigation :: navigation}" />\n    <header\n  id="header-menu"', content, count=1)
        updates[template] = content

    modules = templates / "modules"
    assets = templates / "assets"
    modules.mkdir(exist_ok=True)
    assets.mkdir(exist_ok=True)
    for source, target in (
        ("mobile-navigation.html", modules / "resource-mobile-navigation.html"),
        ("mobile-categories.html", modules / "resource-mobile-categories.html"),
        ("mobile-navigation.css", assets / "resource-mobile-navigation.css"),
        ("mobile-navigation.js", assets / "resource-mobile-navigation.js"),
    ):
        shutil.copyfile(ASSETS / source, target)
    for template, content in updates.items():
        backup = template.with_suffix(".html.before-mobile-navigation.bak")
        if not backup.exists():
            shutil.copyfile(template, backup)
        template.write_text(content, encoding="utf-8")
    print(f"Updated {len(updates)} page templates; mobile navigation assets installed in {templates}")
    print("Restart Halo to load the updated templates.")


if __name__ == "__main__":
    main()
