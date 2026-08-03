"""Dispatch architecture: closure queue + signal primitives.

Depicts the current implementation of ``natlink_com._hidden_wnd``:
``dispatch()`` queues closures on per-channel deques and ``signal()``
posts sync-op completions with real Win32 wparam/lparam. The refactor
this diagram originally previewed has landed; kept alongside
``generate_postmsg_diagram.py`` which stays for the broader
PostMessage-deferral narrative.
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

OUT_PATH = Path(__file__).resolve().parent.parent / "images" / "natlink_proposed_dispatch.png"

# --- Config ---
SCALE = 2
_W, _H = 1500, 2130
W, H = _W * SCALE, _H * SCALE
BG = "#1e1e2e"
BOX_FILL = "#313244"
BOX_OUTLINE = "#585b70"
ACCENT = "#89b4fa"       # blue (dispatch / main thread)
ACCENT2 = "#a6e3a1"      # green (Dragon / success)
ACCENT3 = "#f9e2af"      # yellow (sinks)
RED = "#f38ba8"          # red (errors / pause_recog)
MAUVE = "#cba6f7"        # purple (user callback / sync op)
PEACH = "#fab387"        # peach (signal / special case)
TEXT = "#cdd6f4"
SUBTLE = "#6c7086"
ARROW = "#7f849c"
DARK_FILL = "#2a2a3a"

# New palette dimension: "removed" vs "new" callouts
CRIMSON = "#eba0ac"      # strike-through old
MINT = "#94e2d5"         # new / added

FONT_TITLE = ImageFont.truetype("segoeui.ttf", 28 * SCALE)
FONT_SECTION = ImageFont.truetype("segoeuib.ttf", 20 * SCALE)
FONT_BOLD = ImageFont.truetype("segoeuib.ttf", 15 * SCALE)
FONT = ImageFont.truetype("segoeui.ttf", 14 * SCALE)
FONT_SMALL = ImageFont.truetype("segoeui.ttf", 12 * SCALE)
FONT_MONO = ImageFont.truetype("consola.ttf", 12 * SCALE)
FONT_MONO_B = ImageFont.truetype("consolab.ttf", 13 * SCALE)

img = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(img)


# --- Helpers (logical units, scaled by SCALE) ---
def s(*vals):
    if len(vals) == 1:
        return int(vals[0] * SCALE)
    return tuple(int(v * SCALE) for v in vals)


def rbox(x, y, w, h, fill=BOX_FILL, outline=BOX_OUTLINE, r=10, lw=2):
    x, y, w, h, r, lw = s(x), s(y), s(w), s(h), s(r), max(1, s(lw))
    d.rounded_rectangle([x, y, x + w, y + h], radius=r, fill=fill,
                        outline=outline, width=lw)


def ctext(text, x, y, w, font=FONT_BOLD, fill=TEXT):
    x, y, w = s(x), s(y), s(w)
    bb = d.textbbox((0, 0), text, font=font)
    tw = bb[2] - bb[0]
    d.text((x + (w - tw) // 2, y), text, font=font, fill=fill)


def txt(text, x, y, font=FONT, fill=TEXT):
    d.text((s(x), s(y)), text, font=font, fill=fill)


def arrow_down(x, y1, y2, color=ARROW, w=2):
    x, y1, y2 = s(x), s(y1), s(y2)
    d.line([(x, y1), (x, y2)], fill=color, width=max(1, s(w)))
    a = s(5)
    d.polygon([(x - a, y2 - s(7)), (x + a, y2 - s(7)), (x, y2)], fill=color)


def arrow_right(x1, x2, y, color=ARROW, w=2):
    x1, x2, y = s(x1), s(x2), s(y)
    d.line([(x1, y), (x2, y)], fill=color, width=max(1, s(w)))
    a = s(5)
    d.polygon([(x2 - s(7), y - a), (x2 - s(7), y + a), (x2, y)], fill=color)


def arrow_left(x1, x2, y, color=ARROW, w=2):
    x1, x2, y = s(x1), s(x2), s(y)
    d.line([(x1, y), (x2, y)], fill=color, width=max(1, s(w)))
    a = s(5)
    d.polygon([(x2 + s(7), y - a), (x2 + s(7), y + a), (x2, y)], fill=color)


# ============================================================
# TITLE
# ============================================================
ctext("Dispatch Architecture  —  dispatch() + signal()",
      0, 20, _W, font=FONT_TITLE, fill=MINT)
ctext("Closure queue + signal primitives. Single entry per concern. "
      "Observability built in.",
      0, 56, _W, font=FONT, fill=SUBTLE)

# Implementation banner
rbox(80, 82, 1340, 26, fill="#2a3a2a", outline=MINT, r=4, lw=1)
ctext("Current implementation (src/natlink_com/_hidden_wnd.py). "
      "Compare against natlink_postmsg_deferral.png for background.",
      0, 87, _W, font=FONT_SMALL, fill=MINT)

# ============================================================
# SECTION 1: Two primitives, side by side
# ============================================================
SEC1_Y = 130
ctext("Two Primitives (the entire public surface)",
      0, SEC1_Y, _W, font=FONT_SECTION, fill=ACCENT)

p_y = SEC1_Y + 34
pw = 660
gap = 20
px1 = 80
px2 = px1 + pw + gap

# Left: dispatch
rbox(px1, p_y, pw, 250, outline=ACCENT)
txt("dispatch(fn, *args, channel=WM_DEFERRED_CALL) -> bool",
    px1 + 20, p_y + 10, font=FONT_MONO_B, fill=ACCENT)
txt("Queue a Python callable for STA execution.",
    px1 + 20, p_y + 34, font=FONT_SMALL, fill=SUBTLE)
d.line([s(px1 + 20), s(p_y + 56), s(px1 + pw - 20), s(p_y + 56)],
       fill="#3b3d52", width=s(1))
txt("q = _queues[channel]", px1 + 30, p_y + 68, font=FONT_MONO, fill=TEXT)
txt("q.append((fn, args, t_enq))",
    px1 + 30, p_y + 86, font=FONT_MONO, fill=TEXT)
txt("PostMessageW(hwnd, channel, 0, 0)",
    px1 + 30, p_y + 104, font=FONT_MONO, fill=TEXT)
txt("# wparam/lparam unused — payload lives in Python",
    px1 + 30, p_y + 122, font=FONT_MONO, fill=SUBTLE)
txt("wndproc on drain:",
    px1 + 20, p_y + 148, font=FONT_BOLD, fill=ACCENT)
txt("fn, args, t_enq = q.popleft()",
    px1 + 30, p_y + 168, font=FONT_MONO, fill=TEXT)
txt("fn(*args)",
    px1 + 30, p_y + 186, font=FONT_MONO, fill=MAUVE)
txt("10 call sites:  2 direct + 4 via conn router + 4 UI actions",
    px1 + 20, p_y + 216, font=FONT_SMALL, fill=ACCENT)

# Right: signal
rbox(px2, p_y, pw, 250, outline=PEACH)
txt("signal(msg, wparam, lparam=0, *, data=None) -> bool",
    px2 + 20, p_y + 10, font=FONT_MONO_B, fill=PEACH)
txt("Post a sync-op completion. Real Win32 wp/lp travel with the message.",
    px2 + 20, p_y + 34, font=FONT_SMALL, fill=SUBTLE)
d.line([s(px2 + 20), s(p_y + 56), s(px2 + pw - 20), s(p_y + 56)],
       fill="#3b3d52", width=s(1))
txt("if data is not None:",
    px2 + 30, p_y + 68, font=FONT_MONO, fill=TEXT)
txt("    _signal_data[(msg, wparam)] = data",
    px2 + 30, p_y + 86, font=FONT_MONO, fill=TEXT)
txt("PostMessageW(hwnd, msg, wparam, lparam)",
    px2 + 30, p_y + 104, font=FONT_MONO, fill=TEXT)
txt("# pump.message_loop() matches entry.wparam",
    px2 + 30, p_y + 122, font=FONT_MONO, fill=SUBTLE)
txt("wndproc on arrival:",
    px2 + 20, p_y + 148, font=FONT_BOLD, fill=PEACH)
txt("trigger_message(msg, wparam, lparam)",
    px2 + 30, p_y + 168, font=FONT_MONO, fill=TEXT)
txt("# consumer later: take_signal_data(msg, wp)",
    px2 + 30, p_y + 186, font=FONT_MONO, fill=SUBTLE)
txt("6 call sites:  4 action sink + 2 engine sink",
    px2 + 20, p_y + 216, font=FONT_SMALL, fill=PEACH)

# ============================================================
# SECTION 2: Message Flow (swim lanes)
# ============================================================
SEC2_Y = SEC1_Y + 310
ctext("Message Flow", 0, SEC2_Y, _W, font=FONT_SECTION, fill=ACCENT)

LANE_W = 360
GAP = 40
LANE1_X = 80
LANE2_X = LANE1_X + LANE_W + GAP
LANE3_X = LANE2_X + LANE_W + GAP

LANE_TOP = SEC2_Y + 30
LANE_H = 640

# Lane headers
for lx, label, color in [
    (LANE1_X, "Dragon (COM RPC)", ACCENT2),
    (LANE2_X, "Sink Callbacks", ACCENT3),
    (LANE3_X, "Main Thread (Pump)", ACCENT),
]:
    rbox(lx, LANE_TOP, LANE_W, 30, fill="#3b3d52", outline=color)
    ctext(label, lx, LANE_TOP + 6, LANE_W, font=FONT_BOLD, fill=color)

# Vertical lane dividers (dotted)
for lx in [LANE1_X + LANE_W // 2, LANE2_X + LANE_W // 2,
           LANE3_X + LANE_W // 2]:
    for yy in range(LANE_TOP + 35, LANE_TOP + LANE_H, 8):
        d.line([(s(lx), s(yy)),
                (s(lx), s(min(yy + 4, LANE_TOP + LANE_H)))],
               fill="#3b3d52", width=s(1))

# Step 1: Dragon fires PhraseFinish
s1y = LANE_TOP + 60
rbox(LANE1_X + 20, s1y, LANE_W - 40, 50, fill="#2a3a2a", outline=ACCENT2)
ctext("PhraseFinish()", LANE1_X + 20, s1y + 6, LANE_W - 40,
      font=FONT_MONO_B, fill=ACCENT2)
txt("RPC call to sink", LANE1_X + 20, s1y + 28,
    font=FONT_SMALL, fill=SUBTLE)
arrow_right(LANE1_X + LANE_W - 20, LANE2_X + 20, s1y + 25, color=ACCENT2)

# Step 2: Sink — the new decision path
s2y = s1y
rbox(LANE2_X + 10, s2y, LANE_W - 20, 160, fill="#3a3520", outline=ACCENT3)
txt("1. Parse SRPHRASEW", LANE2_X + 20, s2y + 8,
    font=FONT_MONO, fill=ACCENT3)
txt("2. Wrap in ComResObj", LANE2_X + 20, s2y + 26,
    font=FONT_MONO, fill=ACCENT3)
txt("3. AddRef(pUnknown)", LANE2_X + 20, s2y + 44,
    font=FONT_MONO, fill=ACCENT3)
txt("4. pause_recog++", LANE2_X + 20, s2y + 62,
    font=FONT_MONO, fill=RED)
txt("5. conn.defer_send_results(", LANE2_X + 20, s2y + 84,
    font=FONT_MONO, fill=MINT)
txt("     gram_handle, dwFlags, res_obj)", LANE2_X + 20, s2y + 102,
    font=FONT_MONO, fill=MINT)
txt("   # NEW: handle-keyed route via conn.", LANE2_X + 20, s2y + 120,
    font=FONT_MONO, fill=SUBTLE)
txt("   # preserves unload-race fallback.", LANE2_X + 20, s2y + 136,
    font=FONT_MONO, fill=SUBTLE)

# Arrow from sink to pump's hwnd
s3y = s2y + 95
arrow_right(LANE2_X + LANE_W - 10, LANE3_X + 20, s3y + 2, color=ACCENT)
txt("dispatch", (LANE2_X + LANE_W + LANE3_X) // 2 - 30, s3y - 12,
    font=FONT_SMALL, fill=ACCENT)

# Step 3: return 0
s4y = s2y + 172
rbox(LANE2_X + 30, s4y, LANE_W - 60, 32, fill="#2a3a2a", outline=ACCENT2)
ctext("return 0", LANE2_X + 30, s4y + 4, LANE_W - 60,
      font=FONT_MONO_B, fill=ACCENT2)
arrow_left(LANE2_X + 30, LANE1_X + LANE_W - 20, s4y + 16, color=ACCENT2)

# Dragon unblocks
s5y = s4y + 4
rbox(LANE1_X + 30, s5y, LANE_W - 60, 28, fill="#2a3a2a", outline="#585b70")
ctext("COM call returns", LANE1_X + 30, s5y + 4, LANE_W - 60,
      font=FONT_SMALL, fill=SUBTLE)

# Step 4: Main thread receives
s6y = s3y + 30
rbox(LANE3_X + 10, s6y, LANE_W - 20, 170, fill=DARK_FILL, outline=ACCENT)
txt("MsgWait unblocks", LANE3_X + 20, s6y + 8, font=FONT_MONO, fill=ACCENT)
txt("DispatchMessage", LANE3_X + 20, s6y + 28, font=FONT_MONO, fill=TEXT)
txt("  → wndproc(WM_SENDRESULTS)", LANE3_X + 20, s6y + 46,
    font=FONT_MONO, fill=SUBTLE)
txt("  q = _queues[WM_SENDRESULTS]", LANE3_X + 20, s6y + 68,
    font=FONT_MONO, fill=MINT)
txt("  fn, args, t_enq = q.popleft()", LANE3_X + 20, s6y + 86,
    font=FONT_MONO, fill=MINT)
txt("  t_start = perf_counter()", LANE3_X + 20, s6y + 104,
    font=FONT_MONO, fill=MINT)
txt("  fn(*args)  # conn._do_send_results",
    LANE3_X + 20, s6y + 122, font=FONT_MONO, fill=MAUVE)
txt("  log drain: wait=X dur=Y ms", LANE3_X + 20, s6y + 144,
    font=FONT_MONO, fill=SUBTLE)

# Step 5: Router runs on connection
s7y = s6y + 186
rbox(LANE3_X + 10, s7y, LANE_W - 20, 130, fill="#2a2a40", outline=MAUVE)
txt("conn._do_send_results(...)", LANE3_X + 20, s7y + 8,
    font=FONT_MONO_B, fill=MAUVE)
txt("gram = _grammar_sinks.get(handle)",
    LANE3_X + 20, s7y + 30, font=FONT_MONO, fill=TEXT)
txt("if gram:",
    LANE3_X + 20, s7y + 48, font=FONT_MONO, fill=TEXT)
txt("    gram._do_phrase_finish(...)",
    LANE3_X + 20, s7y + 66, font=FONT_MONO, fill=ACCENT2)
txt("else:  # unloaded during race",
    LANE3_X + 20, s7y + 86, font=FONT_MONO, fill=RED)
txt("    self.reset_pause_recog()",
    LANE3_X + 20, s7y + 104, font=FONT_MONO, fill=RED)

# Step 6: Resume (after user callback)
s8y = s7y + 146
rbox(LANE3_X + 20, s8y, LANE_W - 40, 32, fill="#2a3a2a", outline=ACCENT2)
ctext("Resume(cookie)", LANE3_X + 20, s8y + 6, LANE_W - 40,
      font=FONT_MONO_B, fill=ACCENT2)
arrow_left(LANE3_X + 20, LANE1_X + LANE_W - 20, s8y + 16, color=ACCENT2)

rbox(LANE1_X + 20, s8y, LANE_W - 40, 32, fill="#2a3a2a", outline=ACCENT2)
ctext("Recognition resumes", LANE1_X + 20, s8y + 6, LANE_W - 40,
      font=FONT_SMALL, fill=ACCENT2)

# ============================================================
# SECTION 3: Connection-owned routing (handle-keyed channels)
# ============================================================
SEC3_Y = LANE_TOP + LANE_H + 30
ctext("Connection-Owned Routing  (grammar/dict lifecycle)",
      0, SEC3_Y, _W, font=FONT_SECTION, fill=MAUVE)

sy = SEC3_Y + 34
rbox(80, sy, 1340, 140, outline=MAUVE)

txt("Why?  Grammar/dict sinks can be unloaded mid-connection "
    "(loader toggle, grammar reload).",
    100, sy + 10, font=FONT, fill=TEXT)
txt("Closure-captured self would keep the sink alive past unload — "
    "COM object may already be released.",
    100, sy + 32, font=FONT, fill=SUBTLE)
txt("Solution:  connection owns the router.  Closure captures the "
    "connection (long-lived), looks up",
    100, sy + 50, font=FONT, fill=SUBTLE)
txt("the sink in its authoritative dict at drain time.  Missing sink → "
    "unwind pause_recog.",
    100, sy + 68, font=FONT, fill=SUBTLE)

txt("Routes:", 100, sy + 96, font=FONT_BOLD, fill=MAUVE)
txt("conn.defer_send_results",
    200, sy + 96, font=FONT_MONO, fill=TEXT)
txt("→ _grammar_sinks[h]._do_phrase_finish",
    430, sy + 96, font=FONT_MONO, fill=SUBTLE)
txt("conn.defer_phrase_hypo",
    200, sy + 114, font=FONT_MONO, fill=TEXT)
txt("→ _grammar_sinks[h]._do_phrase_hypothesis",
    430, sy + 114, font=FONT_MONO, fill=SUBTLE)
txt("conn.defer_dict_text_changed",
    800, sy + 96, font=FONT_MONO, fill=TEXT)
txt("→ _dict_sinks[h]._do_dict_text_changed",
    1080, sy + 96, font=FONT_MONO, fill=SUBTLE)
txt("(engine/action use dispatch directly — singleton lifetime)",
    800, sy + 114, font=FONT_MONO, fill=SUBTLE)

# ============================================================
# SECTION 3b: Shutdown & Drain Guards
# ============================================================
SEC3B_Y = SEC3_Y + 200
ctext("Shutdown & Drain Guards  (close pre-existing races at the same time)",
      0, SEC3B_Y, _W, font=FONT_SECTION, fill=RED)

sy = SEC3B_Y + 34
# Three guards, one box each
gw = 440
gh = 120
gap = 10
gx1 = 80
gx2 = gx1 + gw + gap
gx3 = gx2 + gw + gap

# Guard 1: connection-level flag
rbox(gx1, sy, gw, gh, outline=RED)
txt("① conn._shutting_down", gx1 + 14, sy + 8,
    font=FONT_MONO_B, fill=RED)
txt("Set True as first line of unregister_sinks().",
    gx1 + 14, sy + 32, font=FONT_SMALL, fill=SUBTLE)
txt("conn.defer_*  checks it:", gx1 + 14, sy + 54,
    font=FONT_MONO, fill=TEXT)
txt("  if self._shutting_down:", gx1 + 14, sy + 72,
    font=FONT_MONO, fill=TEXT)
txt("      self.reset_pause_recog()", gx1 + 14, sy + 88,
    font=FONT_MONO, fill=MAUVE)
txt("      return False", gx1 + 14, sy + 104,
    font=FONT_MONO, fill=MAUVE)

# Guard 2: module-level accepting flag
rbox(gx2, sy, gw, gh, outline=RED)
txt("② _hidden_wnd._accepting", gx2 + 14, sy + 8,
    font=FONT_MONO_B, fill=RED)
txt("Set False at destroy() before _queues.clear().",
    gx2 + 14, sy + 32, font=FONT_SMALL, fill=SUBTLE)
txt("dispatch()  checks it:", gx2 + 14, sy + 54,
    font=FONT_MONO, fill=TEXT)
txt("  if not _accepting:", gx2 + 14, sy + 72,
    font=FONT_MONO, fill=TEXT)
txt("      return False  # UI drops", gx2 + 14, sy + 88,
    font=FONT_MONO, fill=MAUVE)
txt("  # no queue entry, no leak", gx2 + 14, sy + 104,
    font=FONT_MONO, fill=SUBTLE)

# Guard 3: drain-time callback slot guard
rbox(gx3, sy, gw, gh, outline=RED)
txt("③ drain-time slot guard", gx3 + 14, sy + 8,
    font=FONT_MONO_B, fill=RED)
txt("Each _do_* re-reads the callback slot.",
    gx3 + 14, sy + 32, font=FONT_SMALL, fill=SUBTLE)
txt("def _do_dict_text_changed(...):",
    gx3 + 14, sy + 54, font=FONT_MONO, fill=TEXT)
txt("  cb = conn.on_dict_text_changed",
    gx3 + 14, sy + 72, font=FONT_MONO, fill=TEXT)
txt("  if cb is None: return",
    gx3 + 14, sy + 88, font=FONT_MONO, fill=MAUVE)
txt("  cb(...)", gx3 + 14, sy + 104, font=FONT_MONO, fill=ACCENT2)

# Timeline strip below the guards
ty = sy + gh + 8
rbox(80, ty, 1340, 40, fill=DARK_FILL, outline="#3b3d52", r=6, lw=1)
txt("Disconnect timeline:",
    100, ty + 4, font=FONT_BOLD, fill=RED)
txt("① shutting_down=True  →  drain sync ops  →  Resume  →  UnRegister  "
    "→  pump  →  ② _accepting=False  →  _queues.clear()  →  release COM",
    100, ty + 22, font=FONT_MONO, fill=SUBTLE)

# ============================================================
# SECTION 4: Channel map
# ============================================================
SEC4_Y = SEC3B_Y + 220
ctext("Channel Map  (every post site after the refactor)",
      0, SEC4_Y, _W, font=FONT_SECTION, fill=TEXT)

sy = SEC4_Y + 30
# Header
rbox(80, sy, 1340, 24, fill="#3b3d52", outline="#4a4d68")
txt("Channel", 95, sy + 4, font=FONT_BOLD, fill=TEXT)
txt("ID", 310, sy + 4, font=FONT_BOLD, fill=TEXT)
txt("Primitive", 370, sy + 4, font=FONT_BOLD, fill=TEXT)
txt("Posted from", 520, sy + 4, font=FONT_BOLD, fill=TEXT)
txt("Drained by", 830, sy + 4, font=FONT_BOLD, fill=TEXT)
txt("Notes", 1160, sy + 4, font=FONT_BOLD, fill=TEXT)

sy += 28
rows = [
    ("WM_PLAYBACK", "345", "signal", "_action_sink (x2)",
     "pump.message_loop", "wp=code lp=0/1",                  ACCENT2),
    ("WM_EXECUTION", "346", "signal", "_action_sink (x2)",
     "pump.message_loop",  "data=errmsg on abort",           PEACH),
    ("WM_ATTRIBCHANGED", "347", "signal", "_engine_sink",
     "pump.message_loop",  "wp=dwCode (signal only now)",    ACCENT2),
    ("WM_PAUSED", "348", "dispatch", "_engine_sink",
     "engine_sink._do_paused",
     "closure-safe singleton",                                ACCENT),
    ("WM_SENDRESULTS", "349", "dispatch", "_grammar_sink",
     "conn._do_send_results", "handle-routed, race-safe",    ACCENT),
    ("WM_MIMICDONE", "350", "signal", "_engine_sink",
     "pump.message_loop",  "wp=code lp=failed",              ACCENT2),
    ("WM_PHRASE_HYPO", "351", "dispatch", "_grammar_sink",
     "conn._do_phrase_hypo",  "handle-routed",               ACCENT),
    ("WM_DICT_TEXTCHANGED", "352", "dispatch", "_dict_sink (x2)",
     "conn._do_dict_text_changed", "handle-routed",          ACCENT),
    ("WM_DEFERRED_CALL", "353", "dispatch", "natlink_compat (x4)",
     "closure target",  "UI default channel",                MINT),
    ("WM_ATTRIBCHANGED_WORK", "354 NEW", "dispatch", "_engine_sink",
     "engine_sink._dispatch_attrib_changed",
     "split from 347 to kill hybrid",                         MINT),
    ("WM_TIMER", "OS", "os_handler", "Windows SetTimer",
     "pump heartbeat",      "register_os_handler",           SUBTLE),
]
for name, wm_id, prim, src, dst, note, color in rows:
    rbox(80, sy, 1340, 22, fill=DARK_FILL, outline="#3b3d52", r=4, lw=1)
    txt(name, 95, sy + 3, font=FONT_MONO_B, fill=color)
    txt(wm_id, 310, sy + 3, font=FONT_MONO, fill=SUBTLE)
    txt(prim, 370, sy + 3, font=FONT_MONO, fill=color)
    txt(src, 520, sy + 3, font=FONT_MONO, fill=TEXT)
    txt(dst, 830, sy + 3, font=FONT_MONO, fill=TEXT)
    txt(note, 1160, sy + 3, font=FONT_SMALL, fill=SUBTLE)
    sy += 24

# ============================================================
# SECTION 5: Observability
# ============================================================
SEC5_Y = sy + 20
ctext("Observability  (new logger family)",
      0, SEC5_Y, _W, font=FONT_SECTION, fill=MINT)

sy = SEC5_Y + 30
rbox(80, sy, 1340, 160, outline=MINT)
rows_obs = [
    ("natlink.com.sta",          "INFO",    "lifecycle: window create/destroy, queue drain shutdown",     ACCENT),
    ("natlink.com.sta.dispatch", "DEBUG",   "enqueue: channel · fn.__qualname__ · tid · depth",           ACCENT),
    ("natlink.com.sta.drain",    "DEBUG",   "drain:   channel · fn.__qualname__ · wait_ms · dur_ms",       ACCENT),
    ("natlink.com.sta.health",   "WARNING", "backlog >= 16 on any channel · drop when hwnd absent",        RED),
    ("natlink.com.sta.error",    "ERROR",   "handler raised inside wndproc (closure exception)",           RED),
]
sy2 = sy + 14
txt("Logger", 100, sy2, font=FONT_BOLD, fill=TEXT)
txt("Default", 440, sy2, font=FONT_BOLD, fill=TEXT)
txt("Fires on", 580, sy2, font=FONT_BOLD, fill=TEXT)
sy2 += 22
for name, lvl, desc, color in rows_obs:
    txt(name, 100, sy2, font=FONT_MONO_B, fill=color)
    txt(lvl, 440, sy2, font=FONT_MONO, fill=SUBTLE)
    txt(desc, 580, sy2, font=FONT_MONO, fill=TEXT)
    sy2 += 22

# ============================================================
# SECTION 6: What's gone vs. what replaces it
# ============================================================
SEC6_Y = SEC5_Y + 210
ctext("What Went Away  (vs. the earlier stash-based pump)",
      0, SEC6_Y, _W, font=FONT_SECTION, fill=CRIMSON)

sy = SEC6_Y + 30
# Header
rbox(80, sy, 1340, 24, fill="#3b3d52", outline="#4a4d68")
txt("Removed", 95, sy + 4, font=FONT_BOLD, fill=CRIMSON)
txt("Replacement (current)", 700, sy + 4, font=FONT_BOLD, fill=MINT)
sy += 28
pairs = [
    ("stash_put / stash_pop / stash_and_post",
     "signal(data=...)  +  take_signal_data(msg, wp)"),
    ("post(msg, wp, lp)",
     "signal(msg, wp, lp)  OR  dispatch(fn, ...)"),
    ("push_to_com(fn, *args)",
     "dispatch(fn, *args)   # default channel = WM_DEFERRED_CALL"),
    ("register_handler(msg, fn)  +  unregister_all_handlers()",
     "dispatch channels auto-route · register_os_handler for WM_TIMER"),
    ("_handlers dict  +  _handle_deferred_call  +  _register_builtin_handlers",
     "deleted — wndproc drains deques directly"),
    ("_stash dict  +  _stash_seq  +  stash-cleanup-on-post-failure",
     "deleted — closures hold payload; no rollback race"),
    ("Handler lambdas in _connection.py:361-432 (~70 lines)",
     "conn.defer_* + conn._do_* methods  (handle-routed channels only)"),
    ("WM_ATTRIBCHANGED does signal+dispatch in one handler",
     "WM_ATTRIBCHANGED = signal  ·  WM_ATTRIBCHANGED_WORK = dispatch"),
]
for old, new in pairs:
    rbox(80, sy, 1340, 30, fill=DARK_FILL, outline="#3b3d52", r=4, lw=1)
    txt(old, 95, sy + 7, font=FONT_MONO, fill=CRIMSON)
    txt(new, 700, sy + 7, font=FONT_MONO, fill=MINT)
    sy += 34

# ============================================================
# SECTION 7: Bug-fix callouts (from review)
# ============================================================
SEC7_Y = sy + 16
ctext("Review Findings Addressed",
      0, SEC7_Y, _W, font=FONT_SECTION, fill=RED)

sy = SEC7_Y + 30
findings = [
    ("Bug A: Sync-op completion needs real wp/lp",
     "Kept signal() separate from dispatch() so wp/lp travel in the MSG struct.",
     PEACH),
    ("Bug B: Grammar/dict unload-race fallback",
     "Connection owns the router; dict lookup stays authoritative; "
     "closure captures conn not sink.",
     MAUVE),
    ("Rollback race on PostMessage failure",
     "Closure stays in deque on failure — drains on next successful post. "
     "No cross-thread q.pop() race.",
     ACCENT2),
    ("WM_EXECUTION error payload needed stash",
     "signal(data=error_msg) attaches payload via sidecar dict keyed by "
     "(msg, wparam). Consumer: take_signal_data.",
     PEACH),
    ("Shutdown race (pre-existing — closed as part of refactor)",
     "conn._shutting_down + _hidden_wnd._accepting + drain-time callback-slot "
     "guards.  New dispatches rejected at source once disconnect starts; "
     "closures that do drain re-read slots.",
     RED),
]
for head, body, color in findings:
    rbox(80, sy, 1340, 42, fill=DARK_FILL, outline=color, r=6, lw=1)
    txt(head, 100, sy + 6, font=FONT_BOLD, fill=color)
    txt(body, 100, sy + 24, font=FONT_SMALL, fill=SUBTLE)
    sy += 46

# ============================================================
img.save(OUT_PATH, dpi=(144, 144))
print(f"Saved: {OUT_PATH}")
