"""Generate natlink architecture layer diagram as PNG."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

OUT_PATH = Path(__file__).resolve().parent.parent / "images" / "natlink_architecture.png"

# --- Config ---
W, H = 1200, 980
BG = "#1e1e2e"
BOX_FILL = "#313244"
BOX_OUTLINE = "#585b70"
ACCENT = "#89b4fa"       # blue accent for key layer
ACCENT2 = "#a6e3a1"      # green for Dragon
ACCENT3 = "#f9e2af"      # yellow for marshal
TEXT_COLOR = "#cdd6f4"
SUBTLE = "#6c7086"
ARROW_COLOR = "#7f849c"
TITLE_COLOR = "#cdd6f4"

FONT_TITLE = ImageFont.truetype("segoeui.ttf", 28)
FONT_BOLD = ImageFont.truetype("segoeuib.ttf", 17)
FONT = ImageFont.truetype("segoeui.ttf", 15)
FONT_SMALL = ImageFont.truetype("segoeui.ttf", 13)
FONT_MONO = ImageFont.truetype("consola.ttf", 13)

img = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(img)

# --- Helpers ---
MARGIN = 140  # left/right margin for side annotations

def rounded_box(y, h, fill=BOX_FILL, outline=BOX_OUTLINE, lw=2):
    x0, x1 = MARGIN, W - MARGIN
    d.rounded_rectangle([x0, y, x1, y + h], radius=12, fill=fill, outline=outline, width=lw)
    return x0, y, x1, y + h

def center_text(text, y, font=FONT_BOLD, fill=TEXT_COLOR):
    bb = d.textbbox((0, 0), text, font=font)
    tw = bb[2] - bb[0]
    d.text(((W - tw) // 2, y), text, font=font, fill=fill)

def left_text(text, x, y, font=FONT, fill=SUBTLE):
    d.text((x, y), text, font=font, fill=fill)

def draw_arrow(x, y1, y2):
    d.line([(x, y1), (x, y2)], fill=ARROW_COLOR, width=2)
    # arrowhead
    d.polygon([(x - 6, y2 - 8), (x + 6, y2 - 8), (x, y2)], fill=ARROW_COLOR)

def draw_dashed_arrow(x, y1, y2):
    step = 8
    for yy in range(y1, y2 - 10, step * 2):
        d.line([(x, yy), (x, min(yy + step, y2 - 10))], fill=ARROW_COLOR, width=2)
    d.polygon([(x - 6, y2 - 8), (x + 6, y2 - 8), (x, y2)], fill=ARROW_COLOR)

# --- Title ---
center_text("Natlink Architecture", 20, font=FONT_TITLE, fill=TITLE_COLOR)
center_text("64-bit Python  \u2194  32-bit Dragon NaturallySpeaking (out-of-process COM)", 56, font=FONT_SMALL, fill=SUBTLE)

# --- Layer 1: User Grammar Code ---
y = 90
rounded_box(y, 62)
center_text("User Grammar Code", y + 8)
center_text("natlinkcore  \u00b7  Dragonfly  \u00b7  Caster  \u00b7  user scripts", y + 32, font=FONT_SMALL, fill=SUBTLE)

draw_arrow(W // 2, y + 62, y + 62 + 22)

# --- Layer 2: natlink shim ---
y = 174
rounded_box(y, 52)
center_text("natlink", y + 6, fill=TEXT_COLOR)
center_text("Module-replacement shim \u2014 intercepts legacy active_loader, re-exports natlink_compat",
            y + 28, font=FONT_SMALL, fill=SUBTLE)

draw_arrow(W // 2, y + 52, y + 52 + 22)

# --- Layer 3: natlink_compat ---
y = 248
rounded_box(y, 72)
center_text("natlink_compat", y + 6, fill=TEXT_COLOR)
left_text("Public API: GramObj, ResObj, DictObj, natConnect/Disconnect", MARGIN + 20, y + 28, font=FONT, fill=SUBTLE)
left_text("Callbacks, state, phase-structured launcher, lifecycle, loader registry", MARGIN + 20, y + 48, font=FONT, fill=SUBTLE)

draw_arrow(W // 2, y + 72, y + 72 + 22)

# --- Layer 4: natlink_com (big box with sub-items) ---
y = 342
x0, y0, x1, y1 = rounded_box(y, 200, outline=ACCENT)
center_text("natlink_com", y + 8, fill=ACCENT)

# Sub-boxes inside natlink_com
sub_items = [
    ("NatlinkCOM", "_com_bridge \u2014 facade over connection, grammars, speech ops"),
    ("DragonConnection", "COM lifecycle, QI chains, raw pointer tracking"),
    ("Sinks", "engine (3 ifaces), grammar, dict, action \u2014 PostMessage deferral"),
    ("Hidden Window + Pump", "Win32 msg dispatch, MsgWait, message stack for sync ops"),
    ("Speech Ops", "mimic, playString, execScript \u2014 block-until-done pattern"),
]
sy = y + 34
for label, desc in sub_items:
    bx0, by0 = MARGIN + 10, sy
    bx1, by1 = W - MARGIN - 10, sy + 28
    d.rounded_rectangle([bx0, by0, bx1, by1], radius=6, fill="#3b3d52", outline="#4a4d68", width=1)
    d.text((MARGIN + 25, sy + 4), label, font=FONT_BOLD, fill=TEXT_COLOR)
    bb = d.textbbox((0, 0), label, font=FONT_BOLD)
    lw = bb[2] - bb[0]
    d.text((MARGIN + 35 + lw, sy + 6), desc, font=FONT_SMALL, fill=SUBTLE)
    sy += 32

draw_arrow(W // 2, y + 200, y + 200 + 22)

# --- Layer 5: Marshal DLL ---
y = 564
rounded_box(y, 52, outline=ACCENT3)
center_text("marshal{32,64}_v{13_14,15_16}.dll", y + 6, fill=ACCENT3)
center_text("Per-process proxy/stub registration \u2014 40+ IIDs \u2014 no HKCU writes \u2014 "
            "32-bit built but Dragon's own DLLs handle stubs at runtime",
            y + 28, font=FONT_SMALL, fill=SUBTLE)

# --- Bitness boundary ---
y_boundary = y + 52 + 8
d.line([(MARGIN, y_boundary + 10), (W - MARGIN, y_boundary + 10)], fill="#f38ba8", width=2)
# dashes
for xx in range(MARGIN, W - MARGIN, 16):
    d.line([(xx, y_boundary + 10), (xx + 8, y_boundary + 10)], fill=BG, width=2)
bb = d.textbbox((0, 0), "32 \u2194 64 bit boundary (ALPC / RPC)", font=FONT_SMALL)
tw = bb[2] - bb[0]
# background behind text
tx = (W - tw) // 2
d.rectangle([tx - 8, y_boundary + 2, tx + tw + 8, y_boundary + 20], fill=BG)
d.text((tx, y_boundary + 2), "32 \u2194 64 bit boundary (ALPC / RPC)", font=FONT_SMALL, fill="#f38ba8")

draw_dashed_arrow(W // 2, y + 52, y_boundary + 22)

# --- Layer 6: Dragon ---
y = y_boundary + 24
rounded_box(y, 62, outline=ACCENT2, fill="#2a3a2a")
center_text("Dragon NaturallySpeaking", y + 8, fill=ACCENT2)
center_text("32-bit COM server  \u00b7  SAPI 4.0  \u00b7  ISRCentralW, IDgnSR* extensions",
            y + 32, font=FONT_SMALL, fill="#7ac992")

# --- Side annotations ---
# Connect sequence (left margin)
ann_x = 10
ann_y = 360
d.text((ann_x, ann_y), "Connect", font=FONT_BOLD, fill=SUBTLE)
steps = [
    "1. CoCreateInstance",
    "   \u2192 IUnknown",
    "2. QI \u2192 ISvcProvider",
    "3. QueryService",
    "   \u2192 ISRCentralW",
    "4. QI fan-out (7 ifaces)",
    "5. Create hidden wnd",
    "6. Register sinks",
    "7. Late QI + GetVersion",
]
for i, s in enumerate(steps):
    d.text((ann_x, ann_y + 20 + i * 15), s, font=FONT_SMALL, fill=SUBTLE)

# Disconnect sequence (right margin)
ann_x2 = W - 10
ann_y2 = 360
bb = d.textbbox((0, 0), "Disconnect", font=FONT_BOLD)
d.text((ann_x2 - (bb[2] - bb[0]), ann_y2), "Disconnect", font=FONT_BOLD, fill=SUBTLE)
steps2 = [
    "1. Stop loaders",
    "2. Unregister sinks",
    "3. Resume if paused",
    "4. Unload grams/dicts",
    "5. Nil + gc.collect \u00d72",
    "6. Release raw ptrs",
    "   (reverse order)",
    "7. Pump\u2192sleep\u2192pump",
    "8. Nil sinks + close",
]
for i, s in enumerate(steps2):
    bb = d.textbbox((0, 0), s, font=FONT_SMALL)
    d.text((ann_x2 - (bb[2] - bb[0]), ann_y2 + 20 + i * 15), s, font=FONT_SMALL, fill=SUBTLE)

# --- Recognition flow (bottom) ---
y_flow = H - 100
d.rounded_rectangle([MARGIN, y_flow, W - MARGIN, y_flow + 82], radius=10, fill="#2a2a3a", outline="#4a4d68", width=1)
center_text("Recognition Flow", y_flow + 4, font=FONT_BOLD, fill=ACCENT)
flow_steps = [
    "Dragon \u2192 GrammarSink.PhraseFinish()  \u2192  parse SRPHRASEW, wrap ComResObj, AddRef, \u2191 pause_recog",
    "\u2192  PostMessage(WM_SENDRESULTS)  \u2192  return 0 immediately (no deadlock)",
    "\u2192  Main pump dispatches  \u2192  user callback  \u2192  \u2193 pause_recog  \u2192  Resume() if deferred",
]
for i, s in enumerate(flow_steps):
    center_text(s, y_flow + 26 + i * 18, font=FONT_SMALL, fill=SUBTLE)

img.save(OUT_PATH, dpi=(144, 144))
print(f"Saved: {OUT_PATH}")
