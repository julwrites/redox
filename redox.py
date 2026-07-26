"""Redox keyboard generator for klavgen.

Generates the left half of a Redox split keyboard (Reduced Ergodox).
ALL switch positions are taken directly from the official Redox rev1.0 KiCad PCB
files (redox_rev1.kicad_pcb) — this is the single authoritative source.

Usage:
  python redox.py          # MX switches
  python redox.py --choc   # Choc switches (experimental)
  python redox.py --glp    # Gateron Low Profile KS-33 (MX sockets, slimmer case)
"""

import sys

from klavgen import *

# ---------------------------------------------------------------------------
# Switch type
# ---------------------------------------------------------------------------
use_choc = "--choc" in sys.argv
use_glp  = "--glp"  in sys.argv

switch_type = SwitchType.CHOC if use_choc else SwitchType.MX
case_height = 9 if use_glp else 11

config = Config(
    case_config=CaseConfig(
        side_fillet=None,
        palm_rests_top_fillet=None,
        switch_type=switch_type,
        case_base_height=case_height,
    ),
    mx_key_config=MXKeyConfig(case_tile_margin=7.5),
    choc_key_config=ChocKeyConfig(case_tile_margin=7.6),
    controller_config=ControllerConfig(case_tile_margin=5),
    usbc_jack_config=USBCJackConfig(case_tile_margin=5),
)

KEYCAP_1_25U_WIDTH = round(MX_KEYCAP_1U_WIDTH + 0.25 * MX_KEY_X_SPACING, 4)
KEYCAP_1_5U_HEIGHT = round(MX_KEYCAP_1U_DEPTH + 0.5  * MX_KEY_Y_SPACING, 4)

# ---------------------------------------------------------------------------
# Keys — exact positions from KiCad redox_rev1.kicad_pcb
# ---------------------------------------------------------------------------
# KiCad coordinates: origin is somewhere on the PCB, y increases downward.
# klavgen: origin is flexible (centred later), y increases upward.
# We negate the KiCad y values so that row 0 (top) → higher klavgen y,
# and centre the layout around a convenient origin.

_kicad_switches = [
    # Row 0 (top) — K0 … K6
    # ref    x         y         rot   footprint
    ("K0",  91.44,    66.675,   0,    "1.25u"),
    ("K1",  113.03,   66.675,   0,    "1u"),
    ("K2",  132.08,   62.23,    0,    "1u"),
    ("K3",  151.13,   59.69,    0,    "1u"),
    ("K4",  170.18,   62.23,    0,    "1u"),
    ("K5",  189.23,   64.135,   0,    "1u"),
    ("K6",  208.28,   73.66,    0,    "1u"),
    # Row 1 — K10 … K16
    ("K10", 91.44,    85.725,   0,    "1.25u"),
    ("K11", 113.03,   85.725,   0,    "1u"),
    ("K12", 132.08,   81.28,    0,    "1u"),
    ("K13", 151.13,   78.74,    0,    "1u"),
    ("K14", 170.18,   81.28,    0,    "1u"),
    ("K15", 189.23,   83.185,   0,    "1u"),
    ("K16", 208.28,   97.79,    270,   "1.5u"),   # [ key, h=1.5
    # Row 2 — K20 … K26
    ("K20", 91.44,    104.775,  0,    "1.25u"),
    ("K21", 113.03,   104.775,  0,    "1u"),
    ("K22", 132.08,   100.33,   0,    "1u"),
    ("K23", 151.13,   97.79,    0,    "1u"),
    ("K24", 170.18,   100.33,   0,    "1u"),
    ("K25", 189.23,   102.235,  0,    "1u"),
    ("K26", 212.09,   127.635,  330,   "1u"),      # PgUp thumb
    # Row 3 — K30 … K36
    ("K30", 91.44,    123.825,  0,    "1.25u"),
    ("K31", 113.03,   123.825,  0,    "1u"),
    ("K32", 132.08,   119.38,   0,    "1u"),
    ("K33", 151.13,   116.84,   0,    "1u"),
    ("K34", 170.18,   119.38,   0,    "1u"),
    ("K35", 189.23,   121.285,  0,    "1u"),
    ("K36", 228.6,    137.16,   330,   "1u"),      # PgDn thumb
    # Row 4 (bottom) — K40 … K46
    ("K40", 93.98,    142.875,  0,    "1u"),
    ("K41", 113.03,   142.875,  0,    "1u"),
    ("K42", 132.08,   138.43,   0,    "1u"),
    ("K43", 151.13,   135.89,   0,    "1u"),
    ("K44", 176.53,   141.605,  345,   "1.25u"),    # LCtrl thumb
    ("K45", 200.025,  148.59,   240,   "1.5u"),     # Backspace thumb
    ("K46", 216.535,  158.115,  240,   "1.5u"),     # Delete thumb
]

# Convert KiCad → klavgen coordinates.
# KiCad  y increases downward, klavgen y increases upward → negate.
# Shift origin so the layout centres nicely (subtract K3's x, K3's negated y).
ref_x  = 151.13   # K3 x (middle column, top row)
ref_ny = -59.69   # -K3 y (negated for klavgen)

keys = []
for ref, kx, ky, krot, ksize in _kicad_switches:
    # klavgen x,y
    x = kx - ref_x
    y = -ky - ref_ny   # negate KiCad y then shift so K3 is at y=0

    # Keycap width / depth
    w = None
    d = None
    if ksize == "1.25u":
        w = KEYCAP_1_25U_WIDTH
    elif ksize == "1.5u":
        # K16 (rot 270) → wide keycap rotated to be tall → depth is the wider dimension
        # K45, K46 (rot 240) → 1.5u-wide key, depth = standard 1u
        if krot == 270:
            d = KEYCAP_1_5U_HEIGHT
        else:
            w = MX_KEYCAP_1_5U_WIDTH
            d = KEYCAP_1_5U_HEIGHT

    # Rotation in klavgen: KiCad CCW = klavgen CCW (both positive = CCW)
    rot = 0
    if krot not in (0, 360):
        # klavgen Key.rotate is CCW positive (same as KiCad)
        rot = krot

    keys.append(Key(
        x=x, y=y,
        keycap_width=w,
        keycap_depth=d,
        rotate=rot,
    ))

assert len(keys) == 35, f"Expected 35 keys, got {len(keys)}"

# ---------------------------------------------------------------------------
# Case outline
# ---------------------------------------------------------------------------
margin = config.mx_key_config.case_tile_margin
xs = [k.x for k in keys]
ys = [k.y for k in keys]
min_x, max_x = min(xs) - margin, max(xs) + margin + 20  # room for controller
min_y, max_y = min(ys) - margin, max(ys) + margin

h = config.case_config.case_base_height
patches = [
    Patch(
        points=[
            (min_x - 3, max_y + 6),
            (max_x + 3, max_y + 6),
            (max_x + 3, min_y - 6),
            (min_x - 3, min_y - 6),
        ],
        height=h,
    ),
]

# ---------------------------------------------------------------------------
# Controller, jack, screw holes
# ---------------------------------------------------------------------------
controller = Controller(x=max_x - 28, y=min_y + 22)
usbc_jack  = USBCJack(x=max_x - 12, y=min_y + 6, rotate=-90)

screw_holes = [
    ScrewHole(x=min_x + 5,  y=max_y - 5),
    ScrewHole(x=max_x - 40, y=max_y - 5),
    ScrewHole(x=max_x - 5,  y=min_y + 5),
    ScrewHole(x=min_x + 5,  y=min_y + 5),
]

# ---------------------------------------------------------------------------
# Palm rests
# ---------------------------------------------------------------------------
pr_depth = 30
palm_rests = [
    PalmRest(
        points=[
            (min_x - 3, min_y),
            (max_x + 3, min_y),
            (max_x + 3, min_y - pr_depth),
            (min_x - 3, min_y - pr_depth),
        ],
        height=h + 10,
        connector_locations_x=[min_x + 15, min_x + 60, max_x - 15],
    ),
]

# ---------------------------------------------------------------------------
# Generate
# ---------------------------------------------------------------------------
if use_glp:
    label = "Gateron Low Profile"
elif use_choc:
    label = "Choc"
else:
    label = "MX"

print(f"Generating Redox {label} — {len(keys)} keys")
print(f"  Positions from redox_rev1.kicad_pcb")
print(f"  Bounding box: [{min_x:.0f}, {min_y:.0f}] – [{max_x:.0f}, {max_y:.0f}] mm")

keyboard_result = render_and_save_keyboard(
    keys=keys,
    screw_holes=screw_holes,
    controller=controller,
    components=[usbc_jack],
    patches=patches,
    palm_rests=palm_rests,
    debug=False,
    render_standard_components=True,
    config=config,
)

print("Done — STL files written.")
