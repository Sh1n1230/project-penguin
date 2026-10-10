"""Dependency-free SVG sources, white tintable icons on a 24px viewBox."""
import json
import math
from pathlib import Path
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'Assets/UI/DesignSystem/Icons'
SHAPES = {
    'electricity': '<path d="M13 2 5 13h6l-1 9 9-13h-6z"/>',
    'water': '<path d="M12 2C10 6 5 11 5 15a7 7 0 0 0 14 0c0-4-5-9-7-13Z"/><path d="M8 15a4 4 0 0 0 4 4"/>',
    'gas': '<path d="M13 2c1 7-5 7-3 12 2 0 4-3 4-5 4 3 5 6 4 9a7 7 0 0 1-13-2c0-5 4-7 8-14Z"/>',
    'pearl': '<path d="M3 12 6 6l6-3 6 3 3 6-3 8H6Z"/><circle cx="12" cy="13" r="4"/><path d="M6 7 8 10m4-6v4m6-1-2 3"/>',
    'fish': '<path d="M4 12c4-8 11-8 15 0-4 8-11 8-15 0Zm0 0-2-4v8Zm7-7 3-2 1 3m-4 13 3 2 1-3"/><circle cx="16" cy="11" r=".7" fill="white"/>',
    'surimi': '<path d="M3 13h18c-1 5-4 8-9 8s-8-3-9-8Z"/><path d="M5 13c0-3 2-6 5-6 1-4 7-3 7 0 3 0 4 3 3 6"/>',
    'salt': '<path d="m8 3 4 2 4-2-1 5c3 3 6 7 4 11-2 3-12 3-14 0-2-4 1-8 4-11Z"/><path d="M9 8h6m-6 6h6m-5 3h4"/>',
    'kelp': '<path d="M5 21c4-4-3-5 0-9s0-6 2-9m5 18c-3-4 3-5 0-9s0-5 1-10m6 19c-4-4 3-5 0-9s0-6-2-9"/>',
    'kamaboko': '<path d="M3 19v-4a9 9 0 0 1 18 0v4Zm4-1v-3a5 5 0 0 1 10 0v3M2 21h20"/>',
    'chikuwa': '<path d="M7 7 17 3c5 0 6 6 3 9L10 21c-4 3-9-4-7-9Z"/><ellipse cx="7" cy="15" rx="3" ry="4" transform="rotate(-25 7 15)"/><path d="m10 8 5 7m-2-9 5 6"/>',
    'dried-fish': '<path d="M4 12c4-8 11-8 15 0-4 8-11 8-15 0Zm0 0-2-4v8ZM7 12h11m-8-4v8m4-8v8"/><circle cx="17" cy="11" r=".6" fill="white"/>',
    'oden': '<path d="M12 2v20m-5-5h10v3H7Z"/><circle cx="12" cy="12" r="3"/><path d="m12 3 4 5H8Z"/>',
    'build': '<path d="m3 11 9-8 9 8M5 10v11h14V10m-9 11v-6h4v6"/><path d="M18 2v6m-3-3h6"/>',
    'move': '<path d="M12 2v20M2 12h20M8 6l4-4 4 4m-8 12 4 4 4-4M6 8l-4 4 4 4m12-8 4 4-4 4"/>',
    'undo': '<path d="M8 4 3 9l5 5M3 9h10a7 7 0 0 1 0 14"/>',
    'demolish': '<path d="M4 6h16M9 6V3h6v3M6 6l1 15h10l1-15m-8 4v7m4-7v7"/>',
    'connect': '<circle cx="5" cy="6" r="3"/><circle cx="19" cy="18" r="3"/><path d="M8 6h4v12h4m-3-3 3 3-3 3"/>',
    'disconnect': '<path d="m8 8-3 3a4 4 0 0 0 6 6l2-2m3-5 3-3a4 4 0 0 0-6-6l-2 2M3 3l18 18m-10-9 2-2"/>',
    'expand-island': '<path d="M3 15 7 11h10l4 4-3 6H6ZM12 2v7M9 5l3-3 3 3m3 3 3-3m-3 0h3v3M6 8 3 5m0 3V5h3"/>',
    'deliver': '<path d="M3 12v9h18v-9M2 12h20M12 2v13M8 11l4 4 4-4"/>',
    'research': '<path d="M9 2h6m-5 0v7l-6 10c-1 2 1 3 3 3h10c2 0 4-1 3-3L14 9V2M7 15h10"/><circle cx="12" cy="18" r=".7" fill="white"/>',
    'recipe-high': '<path d="M3 16h18l-2 5H5ZM7 3c3 4-4 4 0 9m5-11c3 5-4 6 0 11m5-9c3 4-4 4 0 9"/>',
    'recipe-low': '<path d="M3 16h18l-2 5H5ZM9 8c2 2-2 3 0 5m6-5c2 2-2 3 0 5"/>',
    'time-forward': '<circle cx="10" cy="12" r="8"/><path d="M10 6v6l3 2m5-5 4 3-4 3"/>',
    'production': '<path d="M3 21V10l6 3V8l6 4V3h4l2 18ZM7 17h1m3 0h1m3 0h1"/>',
    'worker-shortage': '<circle cx="9" cy="6" r="3"/><path d="M3 20v-4a6 6 0 0 1 12 0v4M18 9v6m0 4v.1"/>',
    'gas-empty': '<path d="M10 2c1 6-4 7-3 11 2 0 3-2 3-4 3 3 4 5 3 8a6 6 0 0 1-11-2c0-4 4-8 8-13Zm6 12 6 6m0-6-6 6"/>',
    'storage-full': '<path d="m3 7 9-4 9 4v14H3Zm0 0 9 4 9-4m-9 4v10M6 14h3m6 0h3M6 18h3m6 0h3"/>',
    'material-wait': '<path d="M4 3h16M4 21h16M6 3v4l6 5-6 5v4m12-18v4l-6 5 6 5v4M9 19h6"/>',
    'no-coast': '<path d="M2 15q3-3 6 0t6 0 6 0M2 20q3-3 6 0t6 0 6 0M7 2l10 9m0-9L7 11"/>',
    'increase': '<path d="M12 21V3M5 10l7-7 7 7"/>',
    'decrease': '<path d="M12 3v18M5 14l7 7 7-7"/>',
    'warning': '<path d="m12 2 10 19H2ZM12 8v6m0 3v.1"/>',
    'priority-one': '<circle cx="12" cy="12" r="10"/><path d="m9 9 3-2v10m-3 0h6"/>',
}
OUT.mkdir(parents=True, exist_ok=True)
for name, body in SHAPES.items():
    svg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">\n'
    svg += '<g fill="none" stroke="#FFFFFF" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">'+body+'</g>\n</svg>\n'
    ElementTree.fromstring(svg)
    (OUT/('icon-'+name+'.svg')).write_text(svg, encoding='utf-8')

# Browser-reviewable sheet uses the same white SVGs over a token-blue background.
rows = ''.join(f'<figure><img src="../../Assets/UI/DesignSystem/Icons/icon-{n}.svg"><figcaption>{n}</figcaption></figure>' for n in SHAPES)
html = '<!doctype html><meta charset="utf-8"><title>Production Island Icons</title><style>body{font:15px system-ui;background:#EEF7FF;color:#17385F;margin:32px}main{display:grid;grid-template-columns:repeat(7,1fr);gap:16px}figure{margin:0;text-align:center}img{width:64px;height:64px;padding:20px;background:#1F8BEA;border-radius:16px}figcaption{margin:8px}</style><h1>Production Island · Icons</h1><main>'+rows+'</main>'
(ROOT/'ArtSource/ProductionIsland_v001/Icon_ContactSheet.html').write_text(html,encoding='utf-8')

# Functional soft particles: alpha carries shape; material tint supplies item color.
try:
    from PIL import Image
    folder=ROOT/'Assets/VFX/ProductionIsland/Textures'
    folder.mkdir(parents=True,exist_ok=True)
    for shape in ('Particle','IceShard'):
        image=Image.new('RGBA',(64,64))
        for y in range(64):
            for x in range(64):
                dx,dy=(x-31.5)/31.5,(y-31.5)/31.5
                radius=math.sqrt(dx*dx+dy*dy) if shape=='Particle' else abs(dx)+abs(dy)
                alpha=int(255*max(0,min(1,(1-radius)*4)))
                image.putpixel((x,y),(255,255,255,alpha))
        image.save(folder/(shape+'_v001.png'))
except ImportError:
    raise RuntimeError('Pillow is required for the VFX particle textures')
print(f'{len(SHAPES)} SVG icons and 2 particle textures created')
