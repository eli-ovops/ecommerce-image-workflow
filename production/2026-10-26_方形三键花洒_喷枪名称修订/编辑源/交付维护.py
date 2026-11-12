"""Maintain the selected delivery only; never delete inputs or redraw a product.

Usage: python3 <this-file> verify
       python3 <this-file> package /absolute/new-output.zip
       python3 <this-file> long /absolute/new-long.jpg
New outputs must not exist. Rebuilding a long image is not pixel-identical to
the existing historical JPEG. Only 'long' requires Pillow.
"""
from pathlib import Path
import hashlib
import json
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    value = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            value.update(chunk)
    return value.hexdigest()


def selected():
    manifest = json.loads((ROOT / 'manifest.json').read_text())
    result = {}
    for item in manifest['items']:
        path = ROOT / item['file']
        assert path.parent == ROOT / 'JPG' and not path.is_symlink()
        assert digest(path) == item['sha256'], path.name
        result[item['id']] = (path, item)
    assert len(result) == 17
    assert len(list((ROOT / 'JPG').glob('*.jpg'))) == 17
    return result


def verify_archive(path, rows):
    expected = {p.name: meta['sha256'] for p, meta in rows.values()}
    with zipfile.ZipFile(path) as archive:
        assert archive.testzip() is None
        assert set(archive.namelist()) == set(expected)
        assert len(archive.namelist()) == 17
        for name, value in expected.items():
            assert hashlib.sha256(archive.read(name)).hexdigest() == value, name


def main():
    command = sys.argv[1] if len(sys.argv) > 1 else 'verify'
    rows = selected()
    if command == 'verify':
        archives = list(ROOT.glob('*.zip'))
        assert len(archives) == 1
        verify_archive(archives[0], rows)
        print('PASS: 17 selected JPGs and ZIP members match the manifest')
        return
    assert command in ('package', 'long'), command
    target = Path(sys.argv[2])
    assert target.is_absolute() and not target.exists()
    assert target.resolve() not in [p.resolve() for p, _ in rows.values()]
    if command == 'package':
        with zipfile.ZipFile(target, 'x', zipfile.ZIP_DEFLATED) as archive:
            for path, _ in sorted(rows.values()):
                archive.write(path, path.name)
        verify_archive(target, rows)
        print('PASS:', target, digest(target))
        return
    from PIL import Image
    chapters = json.loads((Path(__file__).parent / '章节映射.json').read_text())
    pieces = []
    for chapter in chapters:
        im = Image.open(rows[chapter['id']][0]).convert('RGB')
        height = round(im.height * 1000 / im.width)
        pieces.append(im.resize((1000, height), Image.Resampling.LANCZOS))
    canvas = Image.new('RGB', (1000, sum(im.height for im in pieces)))
    y = 0
    for im in pieces:
        canvas.paste(im, (0, y))
        y += im.height
    canvas.save(target, quality=95, subsampling=0)
    print('NEW REBUILD (not byte-identical to existing long JPEG):', target, canvas.size)


if __name__ == '__main__':
    main()
