"""Build a resource-only overlay of upstream Showcase, preserving its Java/console code."""
from pathlib import Path
import re
import zipfile

root = Path(__file__).resolve().parents[1]
source = root / 'showcase/src/main/resources'
upstream = root / 'vendor/plugin-showcase-1.7.4.jar'
if not upstream.exists():
    upstream = root / 'halo-data/plugins/plugin-showcase-1.7.4.jar'
output = root / 'dist/plugin-showcase-1.7.4-resource.1.jar'
output.parent.mkdir(exist_ok=True)
overrides = {
    'templates/movie.html': (source / 'templates/resource-shelf.html').read_bytes(),
    'static/resource.css': (source / 'static/resource.css').read_bytes(),
    'static/resource.js': (source / 'static/resource.js').read_bytes(),
}
with zipfile.ZipFile(upstream) as original, zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as package:
    for entry in original.infolist():
        if entry.filename in overrides:
            continue
        if re.match(r'META-INF/[^/]+\.(SF|RSA|DSA)$', entry.filename, re.I):
            raise RuntimeError('Signed upstream JAR requires a full source build.')
        content = original.read(entry.filename)
        if entry.filename == 'plugin.yaml':
            content = content.decode('utf-8').replace('version: "1.7.4"', 'version: "1.7.4-resource.1"').encode('utf-8')
        package.writestr(entry, content)
    for name, content in overrides.items():
        package.writestr(name, content)
    package.writestr('RESOURCE-EDITION.txt', 'Local Resource Shelf frontend. Based on WXY-333/show-shelf 1.7.4 (MIT).\nOriginal Java and Console unchanged. Source: showcase/ and scripts/build-resource-shelf.py.\n')

# The same page is the resource theme homepage; no separate frontend server.
homepage = overrides['templates/movie.html']
(root / 'theme/templates/index.html').write_bytes(homepage)
(root / 'theme/templates/movie.html').write_bytes(homepage)
settings = root / 'theme/settings.yaml'
settings.write_text(settings.read_text(encoding='utf-8').replace('name: theme-starter-setting', 'name: acg-resource-theme-setting'), encoding='utf-8')
with zipfile.ZipFile(root / 'dist/acg-resource-theme-0.2.0.zip', 'w', zipfile.ZIP_DEFLATED) as package:
    for name in ['theme.yaml', 'settings.yaml', 'LICENSE']:
        package.write(root / 'theme' / name, name)
    for path in (root / 'theme/templates').rglob('*'):
        if path.is_file():
            package.write(path, path.relative_to(root / 'theme').as_posix())
print(output)
print(root / 'dist/acg-resource-theme-0.2.0.zip')
