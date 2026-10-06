"""Generate profile README SVGs (dark + light). Run: python3 assets/gen.py"""
from pathlib import Path

OUT = Path(__file__).parent
MONO = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, 'Liberation Mono', monospace"
SANS = "-apple-system, BlinkMacSystemFont, 'Segoe UI', 'Apple SD Gothic Neo', 'Noto Sans KR', 'Malgun Gothic', Helvetica, Arial, sans-serif"

THEMES = {
    "dark": dict(bg="#0d1117", panel="#11161d", border="#262c36", text="#e6edf3", muted="#8b949e",
                 faint="#30363d", ok="#3fb950", blue="#58a6ff", amber="#d29922", violet="#bc8cff"),
    "light": dict(bg="#ffffff", panel="#f6f8fa", border="#d0d7de", text="#1f2328", muted="#59636e",
                  faint="#d8dee4", ok="#1a7f37", blue="#0969da", amber="#9a6700", violet="#8250df"),
}

STYLE = """
<style>
  .mono {{ font-family: {mono}; }}
  .sans {{ font-family: {sans}; }}
  .bar {{ transform-box: fill-box; transform-origin: left center; animation: grow .9s cubic-bezier(.2,.8,.2,1) both; }}
  .fade {{ animation: fade .6s ease-out both; }}
  .blink {{ animation: blink 1.1s steps(1) infinite; }}
  @keyframes grow {{ from {{ transform: scaleX(0); }} to {{ transform: scaleX(1); }} }}
  @keyframes fade {{ from {{ opacity: 0; }} to {{ opacity: 1; }} }}
  @keyframes blink {{ 50% {{ opacity: 0; }} }}
  @media (prefers-reduced-motion: reduce) {{ .bar, .fade, .blink {{ animation: none; }} }}
</style>
""".format(mono=MONO, sans=SANS)


def header(t):
    W, H = 880, 330
    # trace spans: (label, start, width, color, duration)
    spans = [
        ("GET /dongkyu", 0.00, 1.00, t["ok"], "200 OK"),
        ("reproduce()", 0.02, 0.16, t["muted"], "the symptom"),
        ("trace.rootCause()", 0.18, 0.30, t["amber"], "why, not what"),
        ("measure(k6, p95)", 0.48, 0.18, t["blue"], "numbers first"),
        ("fix(query · tx · infra)", 0.66, 0.20, t["ok"], "smallest change"),
        ("write(ADR)", 0.86, 0.14, t["violet"], "decision log"),
    ]
    x0, x1 = 300, 820  # waterfall track
    tw = x1 - x0
    y0, row = 168, 24

    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Park Dongkyu — Backend Engineer">',
         "<title>Park Dongkyu — Backend Engineer</title>", STYLE,
         f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="14" fill="{t["bg"]}" stroke="{t["border"]}"/>']
    # window chrome
    s.append(f'<g class="mono" font-size="11" fill="{t["muted"]}">'
             f'<circle cx="26" cy="24" r="5" fill="{t["faint"]}"/><circle cx="44" cy="24" r="5" fill="{t["faint"]}"/><circle cx="62" cy="24" r="5" fill="{t["faint"]}"/>'
             f'<text x="84" y="28">trace · service=backend · span=dong99u</text>'
             f'<text x="{W-26}" y="28" text-anchor="end">seoul, kr</text></g>')
    s.append(f'<line x1="0" y1="44" x2="{W}" y2="44" stroke="{t["border"]}"/>')
    # identity
    s.append(f'<g class="fade">'
             f'<text x="32" y="98" class="sans" font-size="38" font-weight="700" fill="{t["text"]}" letter-spacing="-0.5">Park Dongkyu'
             f'<tspan dx="12" font-size="20" font-weight="500" letter-spacing="0" fill="{t["muted"]}">박동규</tspan></text>'
             f'<text x="34" y="128" class="mono" font-size="14" fill="{t["muted"]}">'
             f'<tspan fill="{t["ok"]}">❯</tspan> backend engineer — chasing root causes, shipping measured fixes'
             f'<tspan class="blink" dx="4" fill="{t["ok"]}">▍</tspan></text></g>')
    # axis
    s.append(f'<g class="mono" font-size="10" fill="{t["muted"]}">')
    for i in range(6):
        x = x0 + tw * i / 5
        s.append(f'<line x1="{x:.1f}" y1="{y0-14}" x2="{x:.1f}" y2="{y0 + row*len(spans) - 6}" stroke="{t["faint"]}" stroke-dasharray="2 4"/>')
    s.append(f'<text x="32" y="{y0-18}" font-weight="700">SPAN</text><text x="{x1}" y="{y0-18}" text-anchor="end">how I work →</text></g>')
    # spans
    for i, (label, st, w, color, note) in enumerate(spans):
        y = y0 + i * row
        indent = 0 if i == 0 else 14
        prefix = "" if i == 0 else ("└ " if i == len(spans) - 1 else "├ ")
        weight = "700" if i == 0 else "400"
        s.append(f'<text x="{32+indent}" y="{y+5}" class="mono" font-size="12.5" font-weight="{weight}" fill="{t["text"]}">'
                 f'<tspan fill="{t["muted"]}">{prefix}</tspan>{label}</text>')
        bx, bw = x0 + tw * st, tw * w
        s.append(f'<rect class="bar" style="animation-delay:{0.15 + i*0.18:.2f}s" x="{bx:.1f}" y="{y-6}" width="{bw:.1f}" height="12" rx="3" fill="{color}" fill-opacity="{0.9 if i == 0 else 0.85}"/>')
        tx = bx + bw - 8
        if i == 0:
            s.append(f'<text class="fade mono" style="animation-delay:1.3s" x="{tx:.1f}" y="{y+4}" text-anchor="end" font-size="10" font-weight="700" fill="{t["bg"]}">{note}</text>')
        elif st + w > 0.75:
            s.append(f'<text class="fade mono" style="animation-delay:1.3s" x="{bx-8:.1f}" y="{y+4}" text-anchor="end" font-size="10" fill="{t["muted"]}">{note}</text>')
        else:
            s.append(f'<text class="fade mono" style="animation-delay:{0.6 + i*0.18:.2f}s" x="{bx+bw+8:.1f}" y="{y+4}" font-size="10" fill="{t["muted"]}">{note}</text>')
    s.append("</svg>")
    return "\n".join(s)


def impact(t):
    W, H = 880, 150
    cells = [
        ("SQL / REQUEST", "101", "4", "−96%", "N+1 · HikariCP"),
        ("P95 LATENCY", "40.7s", "0.8s", "−97%", "k6 · 1,000 VU"),
        ("PAYMENT SUCCESS", "0%", "100%", "fixed", "TX isolation"),
        ("IN PRODUCTION", "642+", "users", "live", "5,300+ feedback reqs"),
    ]
    cw = (W - 2) / len(cells)
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Impact metrics">',
         "<title>Impact: SQL 101→4, p95 40.7s→0.8s, payment success 0%→100%, 642+ users</title>", STYLE,
         f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="14" fill="{t["bg"]}" stroke="{t["border"]}"/>']
    for i, (label, a, b, delta, sub) in enumerate(cells):
        x = 1 + i * cw
        if i:
            s.append(f'<line x1="{x:.1f}" y1="22" x2="{x:.1f}" y2="{H-22}" stroke="{t["border"]}"/>')
        cx = x + 24
        live = i == 3
        s.append(f'<g class="fade" style="animation-delay:{i*0.15:.2f}s">')
        s.append(f'<text x="{cx:.1f}" y="40" class="mono" font-size="10.5" font-weight="700" letter-spacing="1" fill="{t["muted"]}">{label}</text>')
        if live:
            s.append(f'<text x="{cx:.1f}" y="86" class="sans" font-size="32" font-weight="700" fill="{t["text"]}">{a}'
                     f'<tspan dx="6" font-size="15" font-weight="500" fill="{t["muted"]}">{b}</tspan></text>')
        else:
            s.append(f'<text x="{cx:.1f}" y="86" class="sans" font-weight="700" fill="{t["text"]}">'
                     f'<tspan font-size="15" font-weight="500" fill="{t["muted"]}" text-decoration="line-through">{a}</tspan>'
                     f'<tspan dx="6" font-size="15" fill="{t["muted"]}">→</tspan><tspan dx="6" font-size="32">{b}</tspan></text>')
        pill_w = 8 + len(delta) * 7.2
        s.append(f'<rect x="{cx:.1f}" y="104" width="{pill_w:.1f}" height="20" rx="10" fill="{t["ok"]}" fill-opacity="0.15"/>'
                 f'<text x="{cx + pill_w/2:.1f}" y="118" text-anchor="middle" class="mono" font-size="11" font-weight="700" fill="{t["ok"]}">{delta}</text>'
                 f'<text x="{cx + pill_w + 8:.1f}" y="118" class="mono" font-size="10.5" fill="{t["muted"]}">{sub}</text>')
        s.append("</g>")
    s.append("</svg>")
    return "\n".join(s)


for name, t in THEMES.items():
    (OUT / f"header-{name}.svg").write_text(header(t), encoding="utf-8")
    (OUT / f"impact-{name}.svg").write_text(impact(t), encoding="utf-8")
print("ok")
