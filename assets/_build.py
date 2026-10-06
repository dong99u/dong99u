"""Generate README SVG assets for github.com/dong99u.

Fonts (OFL, google/fonts): BricolageGrotesque, GeistMono, IBM Plex Sans KR.
Each SVG embeds only the glyphs it uses (woff2 subset, base64).
"""
import base64, io, os, sys
from fontTools.ttLib import TTFont
from fontTools import subset

FD = os.path.join(os.path.dirname(__file__), "fonts")
OUT = sys.argv[1] if len(sys.argv) > 1 else "assets"
os.makedirs(OUT, exist_ok=True)

FONTS = {
    "disp": "Bricolage-800.ttf",
    "disp6": "Bricolage-600.ttf",
    "mono": "GeistMono-500.ttf",
    "mono4": "GeistMono-400.ttf",
    "kr": "IBMPlexSansKR-Regular.ttf",
    "krm": "IBMPlexSansKR-Medium.ttf",
    "krb": "IBMPlexSansKR-Bold.ttf",
}
_tt = {k: TTFont(os.path.join(FD, v)) for k, v in FONTS.items()}

# ---------- tokens (portfolio v4 「폴더」) ----------
THEME = {
    "light": dict(bg="#F6F6F5", surface="#FFFFFF", line="#DEDEDC", grid="#E6E6E3", gridhi="#D5D5D1",
                  fg="#0C0C0D", fg2="#3E3E42", muted="#6E6E74",
                  blue="#1466B8", green="#08875A", yellow="#9A6B00", pink="#C8155F"),
    "dark": dict(bg="#0A0A0B", surface="#141416", line="#2A2A2F", grid="#17171B", gridhi="#24242B",
                 fg="#F5F5F6", fg2="#B6B6BC", muted="#8A8A92",
                 blue="#1B8CF0", green="#0FC47C", yellow="#F5B60D", pink="#FF2E86"),
}
C = dict(blue="#1B8CF0", green="#0FC47C", yellow="#F5B60D", pink="#FF2E86", ink="#0A0A0B")


HANGUL = lambda s: any("\uac00" <= ch <= "\ud7a3" for ch in s)
FALLBACK = {"disp": "krb", "disp6": "krm", "mono": "krm", "mono4": "kr", "kr": "kr", "krm": "krm", "krb": "krb"}


def pick(text, key):
    """Mono labels with Hangul read better fully in Plex KR than as mixed mono + fallback."""
    if key in ("mono", "mono4") and HANGUL(text):
        return FALLBACK[key]
    return key


def width(text, key, size):
    """Advance width in px; Hangul falls back to Plex KR when the font lacks the glyph."""
    key = pick(text, key)
    total = 0
    for ch in text:
        for k in (key, FALLBACK[key]):
            f = _tt[k]
            g = f.getBestCmap().get(ord(ch))
            if g:
                total += f["hmtx"][g][0] / f["head"].unitsPerEm * size
                break
    return total


class Doc:
    def __init__(self):
        self.used = {k: set() for k in FONTS}
        self.body = []

    def text(self, x, y, s, fam, size, fill, anchor="start", ls=0, extra=""):
        if pick(s, fam) != fam:
            fam, ls = pick(s, fam), 0
        self.used[fam].update(s)
        self.used[FALLBACK[fam]].update(s)  # Hangul fallback
        esc = s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        self.body.append(
            f'<text x="{x:.1f}" y="{y:.1f}" class="{fam}" font-size="{size}" fill="{fill}" '
            f'text-anchor="{anchor}" letter-spacing="{ls}" {extra}>{esc}</text>')

    def raw(self, s):
        self.body.append(s)

    def fontcss(self):
        css = []
        fam_name = {"disp": "D8", "disp6": "D6", "mono": "M5", "mono4": "M4", "kr": "K4", "krm": "K5", "krb": "K7"}
        for k, chars in self.used.items():
            if not chars:
                continue
            opts = subset.Options(); opts.flavor = "woff2"; opts.layout_features = ["*"]
            opts.name_IDs = []; opts.notdef_outline = False; opts.hinting = False
            opts.drop_tables += ["hdmx", "LTSH", "VDMX"]
            f = TTFont(os.path.join(FD, FONTS[k]))
            sub = subset.Subsetter(opts); sub.populate(text="".join(sorted(chars)) + " "); sub.subset(f)
            buf = io.BytesIO(); f.flavor = "woff2"; f.save(buf)
            b64 = base64.b64encode(buf.getvalue()).decode()
            css.append(f"@font-face{{font-family:{fam_name[k]};src:url(data:font/woff2;base64,{b64}) format('woff2')}}")
        stacks = {"disp": "D8,K7", "disp6": "D6,K5", "mono": "M5,K5", "mono4": "M4,K4", "kr": "K4", "krm": "K5", "krb": "K7"}
        # fonts referenced by a stack must be declared even when only used as fallback
        for k, st in stacks.items():
            css.append(f".{k}{{font-family:{st},sans-serif;font-feature-settings:'tnum'}}")
        css.append("text{text-rendering:geometricPrecision}")
        return "".join(css)

    def save(self, name, w, h, title, extra_css=""):
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
               f'role="img" aria-label="{title}"><title>{title}</title>'
               f'<style>{self.fontcss()}{extra_css}</style>' + "".join(self.body) + "</svg>")
        p = os.path.join(OUT, name)
        open(p, "w").write(svg)
        print(f"{p}: {len(svg)/1024:.0f} KB")


def grid(d, x, y, w, h, t, step, major=4, rx=0, clip_id="g"):
    d.raw(f'<defs><pattern id="{clip_id}p" width="{step*major}" height="{step*major}" patternUnits="userSpaceOnUse" x="{x}" y="{y}">'
          + "".join(f'<path d="M{i*step} 0V{step*major}M0 {i*step}H{step*major}" stroke="{t["gridhi"] if i == 0 else t["grid"]}" stroke-width="1"/>'
                    for i in range(major))
          + f'</pattern><clipPath id="{clip_id}c"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}"/></clipPath></defs>')
    d.raw(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{t["bg"]}"/>')
    d.raw(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#{clip_id}p)" clip-path="url(#{clip_id}c)"/>')


MOTION = ("@media (prefers-reduced-motion: reduce){*{animation:none!important}}")

# ======================================================================
# 1) HEADER — drafting sheet with a title block
# ======================================================================
def header(mode):
    t = THEME[mode]; d = Doc(); W, H = 880, 318
    grid(d, 0.5, 0.5, W - 1, H - 1, t, 22, rx=22, clip_id="h")
    d.raw(f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="22" fill="none" stroke="{t["line"]}"/>')

    # registration marks
    for (cx, cy) in ((24, 24), (W - 24, 24), (24, H - 24), (W - 24, H - 24)):
        d.raw(f'<path d="M{cx-6} {cy}H{cx+6}M{cx} {cy-6}V{cy+6}" stroke="{t["muted"]}" stroke-width="1"/>')

    d.text(48, 66, "SHEET 01 — README", "mono", 11, t["muted"], ls=1.6)
    d.text(48, 140, "Park Dongkyu", "disp", 66, t["fg"], ls=-2.6)
    nw = width("Park Dongkyu", "disp", 66) - 2.6 * 11
    # dimension line under the name (drawn once)
    y = 162
    d.raw(f'<g stroke="{t["muted"]}" stroke-width="1">'
          f'<path d="M48 {y-6}V{y+6}M{48+nw:.0f} {y-6}V{y+6}"/>'
          f'<path class="dim" d="M48 {y}H{48+nw:.0f}" pathLength="1"/></g>')
    lab = "Backend Developer"
    lw = width(lab, "mono", 11) + 18
    mx = 48 + nw / 2
    d.raw(f'<rect x="{mx-lw/2:.1f}" y="{y-9}" width="{lw:.1f}" height="18" fill="{t["bg"]}"/>')
    d.text(mx, y + 4, lab, "mono", 11, t["fg2"], anchor="middle", ls=0.6)

    d.text(48, 214, "요구사항을 데이터 구조와", "krb", 23, t["fg"], ls=-0.6)
    d.text(48, 246, "실제 동작하는 시스템으로 구체화합니다.", "krb", 23, t["fg"], ls=-0.6)
    d.text(48, 284, "박동규 · 서울 · github.com/dong99u", "mono4", 12, t["muted"], ls=0.2)

    # title block (right)
    bx, by, bw = 590, 46, 244
    rows = [("ROLE", "백엔드 개발자 (신입)"), ("NOW", "SSAFY 15기 데이터 트랙"), ("STACK", "Spring · Kafka · AWS"), ("STATUS", "구직 중 — 2026")]
    rh = 34
    bh = rh * len(rows) + 58
    d.raw(f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="4" fill="{t["surface"]}" stroke="{t["fg"]}" stroke-width="1.2"/>')
    for i, (k, v) in enumerate(rows):
        yy = by + rh * i
        if i:
            d.raw(f'<path d="M{bx} {yy}H{bx+bw}" stroke="{t["line"]}"/>')
        d.text(bx + 14, yy + 21.5, k, "mono", 9.5, t["muted"], ls=1.4)
        d.text(bx + 78, yy + 22, v, "krm", 13, t["fg"], ls=-0.2)
    d.raw(f'<path d="M{bx+66} {by}V{by+rh*len(rows)}" stroke="{t["line"]}"/>')
    # status pulse
    sy = by + rh * 3 + 17
    sx = bx + 78 + width("구직 중 — 2026", "krm", 13) + 12
    d.raw(f'<circle cx="{sx:.1f}" cy="{sy}" r="4" fill="{C["green"]}"/>'
          f'<circle class="pulse" cx="{sx:.1f}" cy="{sy}" r="4" fill="none" stroke="{C["green"]}" stroke-width="1.5"/>')
    # legend strip: 4 category colours used across the page
    ly = by + rh * len(rows)
    d.raw(f'<path d="M{bx} {ly}H{bx+bw}" stroke="{t["fg"]}" stroke-width="1.2"/>')
    legend = [("blue", "Backend"), ("green", "Data"), ("yellow", "3D·Full"), ("pink", "Mobile·AI")]
    cw = bw / 4
    for i, (c, name) in enumerate(legend):
        x0 = bx + cw * i
        if i:
            d.raw(f'<path d="M{x0:.1f} {ly}V{by+bh}" stroke="{t["line"]}"/>')
        d.raw(f'<rect x="{x0+cw/2-14:.1f}" y="{ly+12}" width="28" height="10" rx="2" fill="{C[c]}"/>')
        d.text(x0 + cw / 2, ly + 41, name, "mono4", 9, t["muted"], anchor="middle")

    css = (".dim{stroke-dasharray:1;stroke-dashoffset:1;animation:draw 1.1s cubic-bezier(.77,0,.175,1) .3s forwards}"
           "@keyframes draw{to{stroke-dashoffset:0}}"
           ".pulse{transform-box:fill-box;transform-origin:center;animation:pulse 2.4s cubic-bezier(.23,1,.32,1) infinite}"
           "@keyframes pulse{0%{transform:scale(1);opacity:.9}70%,100%{transform:scale(3.2);opacity:0}}"
           "@media (prefers-reduced-motion: reduce){.dim{stroke-dashoffset:0;animation:none}.pulse{animation:none;opacity:0}}")
    d.save(f"header-{mode}.svg", W, H, "Park Dongkyu — 요구사항을 데이터 구조와 실제 동작하는 시스템으로 구체화하는 백엔드 개발자", css)


# ======================================================================
# 2) FOLDERS — one per featured project (mode-independent: ink on colour)
# ======================================================================
def folder(slug, color, num, tag, name, period, lines, chip, tilt):
    d = Doc(); W, H = 290, 250
    col = C[color]; ink = C["ink"]
    # back panel + tab sized to its label
    label = f"{num}  {tag}"
    tw = 18 + width(label, "mono", 9.5) + 1.2 * len(label) + 14
    d.raw(f'<path d="M6 34 Q6 26 14 26 H{tw-9:.1f} Q{tw-3:.1f} 26 {tw:.1f} 31 L{tw+6:.1f} 40 H276 Q284 40 284 48 V236 Q284 244 276 244 H14 Q6 244 6 236 Z" '
          f'fill="{col}" opacity=".55"/>')
    # papers peek out to the right of the tab
    px = tw + 14
    d.raw(f'<g transform="rotate({tilt} {px+60} 120)"><rect x="{px:.1f}" y="30" width="{268-px:.1f}" height="150" rx="3" fill="#FFFFFF" stroke="#0A0A0B" stroke-opacity=".12"/>'
          + "".join(f'<path d="M{px+14:.1f} {46+i*9}H{px+30+((i*37)%50):.1f}" stroke="#0A0A0B" stroke-opacity=".16" stroke-width="2" stroke-linecap="round"/>' for i in range(2))
          + "</g>")
    d.raw(f'<rect x="{px+26:.1f}" y="44" width="{250-px-26:.1f}" height="120" rx="3" fill="#FAFAF9" stroke="#0A0A0B" stroke-opacity=".10" transform="rotate({-tilt/2} 200 110)"/>')
    # front panel
    d.raw(f'<path d="M6 72 Q6 64 14 64 H276 Q284 64 284 72 V236 Q284 244 276 244 H14 Q6 244 6 236 Z" fill="{col}"/>')
    d.raw(f'<path d="M6 72 Q6 64 14 64 H276 Q284 64 284 72" fill="none" stroke="#FFFFFF" stroke-opacity=".45"/>')
    d.text(18, 42, label, "mono", 9.5, ink, ls=1.2, extra='fill-opacity=".8"')
    d.text(22, 104, name, "disp", 27, ink, ls=-0.9)
    d.text(22, 124, period, "mono", 10.5, ink, ls=0.3, extra='fill-opacity=".72"')
    for i, ln in enumerate(lines):
        assert width(ln, "krm", 12.5) < 246, (ln, width(ln, "krm", 12.5))
        d.text(22, 150 + i * 19, ln, "krm", 12.5, ink, ls=-0.15)
    cw = width(chip, "mono", 10) + 22
    d.raw(f'<rect x="22" y="{H-38}" width="{cw:.1f}" height="22" rx="11" fill="none" stroke="{ink}" stroke-opacity=".55"/>')
    d.text(33, H - 23, chip, "mono", 10, ink)
    d.text(268, H - 22, "케이스 스터디 →", "krb", 11.5, ink, anchor="end")
    d.save(f"work-{slug}.svg", W, H, f"{name} — {' '.join(lines)}")


# ======================================================================
# 3) TIMELINE — projects above the axis, milestones below
# ======================================================================
def ym(s):
    y, m = s.split("."); return int(y), int(m)


def timeline(mode):
    t = THEME[mode]; d = Doc(); W, H = 880, 372
    grid(d, 0.5, 0.5, W - 1, H - 1, t, 22, rx=22, clip_id="t")
    d.raw(f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="22" fill="none" stroke="{t["line"]}"/>')
    d.text(40, 46, "SHEET 02 — 지나온 순서", "mono", 11, t["muted"], ls=1.6)
    d.text(W - 40, 46, "2023 → 지금", "mono", 11, t["muted"], anchor="end", ls=1.2)

    X0, X1 = 56, W - 56
    start = (2023, 1); months = 4 * 12  # 2023.01 .. 2026.12
    def X(s, end=False):
        y, m = ym(s) if isinstance(s, str) else s
        idx = (y - start[0]) * 12 + (m - 1) + (1 if end else 0)
        return X0 + (X1 - X0) * idx / months
    AX = 214
    # year ticks
    for y in range(2023, 2027):
        x = X(f"{y}.1")
        d.raw(f'<path d="M{x:.1f} {AX-6}V{AX+6}" stroke="{t["fg"]}" stroke-width="1.2"/>')
        d.raw(f'<path d="M{x:.1f} 66V{H-22}" stroke="{t["line"]}" stroke-dasharray="2 4"/>')
        d.text(x + 6, 80, str(y), "mono", 10, t["fg2"], ls=0.5)
    d.raw(f'<path d="M{X0} {AX}H{X1}" stroke="{t["fg"]}" stroke-width="1.4"/>')

    projects = [  # (start, end, name, colour)
        ("2023.09", "2023.10", "GBT Hackathon", "pink"),
        ("2023.09", "2024.04", "Nugget", "pink"),
        ("2024.04", "2024.06", "InnoSheet", "blue"),
        ("2025.02", "2025.05", "LoveKeeper V2", "blue"),
        ("2025.06", "2025.07", "Momento", "blue"),
        ("2025.07", "2025.12", "TradingPT", "blue"),
        ("2026.05", "2026.07", "떠먹는 금융", "green"),
        ("2026.07", "2026.10", "DERO", "yellow"),
    ]
    halo = f'stroke="{t["bg"]}" stroke-width="5" stroke-linejoin="round" paint-order="stroke"'
    labels = []  # drawn last so guide lines never cut through text
    lanes = []  # right edge per lane
    lane_y = [184, 152, 120, 88]
    for s, e, name, c in projects:
        x = X(s); xe = X(e, end=True)
        lw = width(name, "krb", 12) + 4
        right = max(xe, x + lw)
        for li in range(len(lane_y)):
            if li >= len(lanes):
                lanes.append(-1)
            if lanes[li] + 8 < x:
                lanes[li] = right; break
        y = lane_y[li]
        live = name == "DERO"
        d.raw(f'<rect x="{x:.1f}" y="{y}" width="{xe-x:.1f}" height="8" rx="4" fill="{C[c]}"/>')
        if live:
            pass
        d.raw(f'<path d="M{x:.1f} {y+8}V{AX}" stroke="{C[c]}" stroke-width="1" stroke-opacity=".6"/>')
        labels.append((x, y - 6, name, "krb", 12, t["fg"]))

    marks = [  # (date, label, sub, colour or None)
        ("2023.03", "UMC 4~8기", "8기 Spring 파트장", None),
        ("2023.10", "GBT 최우수상 (1위)", "", "pink"),
        ("2024.04", "Solution Challenge", "Global Top 100", "pink"),
        ("2025.07", "UMC Hackathon 우수상", "", "blue"),
        ("2025.12", "SQLD", "", None),
        ("2026.01", "SSAFY 15기", "데이터 트랙", None),
        ("2026.08", "SSAFY 우수상", "DERO", "yellow"),
        ("2026.09", "정보처리기사", "", None),
    ]
    low = [AX + 34, AX + 82, AX + 130]
    lr = [-1] * len(low)
    for s, lab, sub, c in marks:
        x = X(s) + (X(s, True) - X(s)) / 2
        lw = max(width(lab, "krm", 11), width(sub, "mono4", 9.5) if sub else 0) + 10
        for li in range(len(low)):
            if lr[li] + 6 < x - 4:
                lr[li] = x - 4 + lw; break
        y = low[li]
        fill = C[c] if c else t["surface"]
        d.raw(f'<path d="M{x:.1f} {AX+7}V{y-12}" stroke="{t["muted"]}" stroke-width="1" stroke-dasharray="1 3"/>')
        d.raw(f'<rect x="{x-5:.1f}" y="{AX-5}" width="10" height="10" transform="rotate(45 {x:.1f} {AX})" fill="{fill}" stroke="{t["fg"]}" stroke-width="1.2"/>')
        labels.append((x - 4, y, lab, "krm", 11, t["fg"]))
        if sub:
            labels.append((x - 4, y + 15, sub, "mono4", 9.5, t["muted"]))
    for lx, ly, s, fam, size, fill in labels:
        d.text(lx, ly, s, fam, size, fill, extra=halo)
    # now marker
    nx = X("2026.10") + 6
    d.raw(f'<path d="M{nx:.1f} 88V{AX}" stroke="{t["fg"]}" stroke-width="1" stroke-dasharray="3 3"/>')
    d.raw(f'<circle cx="{nx:.1f}" cy="{AX}" r="4" fill="{t["fg"]}"/><circle class="pulse" cx="{nx:.1f}" cy="{AX}" r="4" fill="none" stroke="{t["fg"]}" stroke-width="1.2"/>')
    d.text(nx, 80, "지금", "krb", 11, t["fg"], anchor="middle")
    # key
    ky = H - 26
    d.raw(f'<rect x="40" y="{ky-8}" width="18" height="6" rx="3" fill="{t["fg2"]}"/>')
    d.text(64, ky - 2, "프로젝트 기간", "kr", 10.5, t["muted"])
    kx = 64 + width("프로젝트 기간", "kr", 10.5) + 22
    d.raw(f'<rect x="{kx-4:.1f}" y="{ky-9}" width="8" height="8" transform="rotate(45 {kx:.1f} {ky-5})" fill="{t["surface"]}" stroke="{t["fg"]}"/>')
    d.text(kx + 12, ky - 2, "수상 · 교육 · 자격", "kr", 10.5, t["muted"])

    css = (".pulse{transform-box:fill-box;transform-origin:center;animation:pulse 2.4s cubic-bezier(.23,1,.32,1) infinite}"
           "@keyframes pulse{0%{transform:scale(1);opacity:.9}70%,100%{transform:scale(3.2);opacity:0}}" + MOTION)
    d.save(f"timeline-{mode}.svg", W, H, "2023년부터 지금까지의 프로젝트와 수상·교육·자격 타임라인", css)


if __name__ == "__main__":
    for m in ("light", "dark"):
        header(m); timeline(m)
    folder("tradingpt", "blue", "01", "BACKEND", "TradingPT", "2025.07 — 12 · 운영 중",
           ["트레이딩 교육·매매일지 피드백 플랫폼.", "구독·결제·강의 도메인을 개발하고", "AWS 운영 환경과 배포 파이프라인 구축."],
           "N+1 쿼리 101 → 4", -4)
    folder("fin", "green", "02", "DATA", "떠먹는 금융", "2026.05 — 07 · 데이터 엔지니어",
           ["AI 금융뉴스 큐레이션 데이터 플랫폼.", "멱등 스트리밍 인덱싱 · outbox,", "RRF 하이브리드 검색을 맡았습니다."],
           "Kafka · Flink · ES", 3)
    folder("dero", "yellow", "03", "3D·FULL", "DERO", "2026.07 — 진행 중 · 팀장",
           ["데스크테리어 3D 시뮬레이터.", "3D 에셋 파이프라인, 검색,", "트랜잭션 경계와 문서 체계를 맡았습니다."],
           "2학기 프로젝트 우수상", -3)
