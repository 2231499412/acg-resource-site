from pathlib import Path
p=Path(r'F:\acg-resource-site\halo-data\themes\theme-earth\templates\post.html')
backup=p.with_name('post.html.before-resource-cover.bak')
backup.write_bytes(p.read_bytes())
lines=p.read_text(encoding='utf-8').splitlines(keepends=True)
start=next(i for i,l in enumerate(lines) if '    <section th:unless="${#strings.isEmpty(post.spec.cover)}">' in l)
section2=next(i for i,l in enumerate(lines[start+1:],start+1) if l.startswith('  <section') and 'grid max-w-7xl' in ''.join(lines[i:i+3]))
# Replace from cover section through opening second section, retaining rest of second section body.
replacement='''    <section th:unless="${#strings.isEmpty(post.spec.cover)}" class="mx-auto max-w-7xl px-4 pt-6 lg:px-6">\n      <div class="flex justify-center rounded-xl bg-gray-50 p-2 dark:bg-slate-800">\n        <img\n          class="max-h-96 w-auto max-w-full rounded-lg object-contain"\n          th:src="${post.spec.cover}"\n          th:alt="${post.spec.title}"\n        />\n      </div>\n    </section>\n\n\n  <section\n    class="mx-auto mt-6 grid max-w-7xl grid-cols-1 gap-6 px-4 md:grid-cols-[1fr_18rem] lg:px-6"\n  >\n'''.splitlines(keepends=True)
lines=lines[:start]+replacement+lines[section2+3:]
# remove conditional title display so title appears in content card after the normal cover
lines=[l for l in lines if 'th:if="${#strings.isEmpty(post.spec.cover)} or ${theme.config.post.title_position == \'content\'}"' not in l]
p.write_text(''.join(lines),encoding='utf-8')
print(f'patched {p}; backup {backup}; replaced lines {start+1}-{section2+3}')
for i,l in enumerate(lines,1):
    if 'max-h-96' in l or 'section th:unless' in l or 'th:if="${#strings.isEmpty(post.spec.cover)}' in l:
        print(i,l.rstrip())
