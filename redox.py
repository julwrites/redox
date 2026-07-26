"""Redox keyboard generator for klavgen.

Generates left half of a Redox split keyboard (Reduced Ergodox).
Main key grid positions from the official VIA/Redox KLE layout, thumb cluster
placed manually to match the physical layout.

Authoritative layout sources:
  VIA  – https://github.com/the-via/keyboards (rotation / size)
  QMK  – keyboards/redox/info.json (matrix mapping)
  KLE  – keyboard-layout-editor.com permalink in the Redox README

Usage:
  python redox.py          # MX switches
  python redox.py --choc   # Choc switches (experimental)
"""

import json
import sys
import math

from klavgen import *

# ---------------------------------------------------------------------------
# Switch type
# ---------------------------------------------------------------------------
use_choc = "--choc" in sys.argv

config = Config(
    case_config=CaseConfig(
        side_fillet=None,              # disable fillets during dev (CadQuery is finicky)
        palm_rests_top_fillet=None,    # enable these once layout is confirmed
        switch_type=SwitchType.CHOC if use_choc else SwitchType.MX,
    ),
    mx_key_config=MXKeyConfig(case_tile_margin=7.5),
    choc_key_config=ChocKeyConfig(case_tile_margin=7.6),
    controller_config=ControllerConfig(case_tile_margin=5),
    usbc_jack_config=USBCJackConfig(case_tile_margin=5),
)

KEYCAP_1_25U_WIDTH = round(MX_KEYCAP_1U_WIDTH + 0.25 * MX_KEY_X_SPACING, 4)
KEYCAP_1_5U_HEIGHT = round(MX_KEYCAP_1U_DEPTH + 0.5  * MX_KEY_Y_SPACING, 4)

# ---------------------------------------------------------------------------
# Main key grid — positions from the official Redox KLE layout
# ---------------------------------------------------------------------------

# KLE JSON for the left-half main grid (VIA-based, right-half keys stripped).
# This produces correct column stagger, key widths, and vertical offsets.
_KLE_MAIN_GRID = [
    {"name": "Redox Left (main grid)"},
    # Physical row 0 (top) — spread across KLE rows for column stagger
    [{"x": 3.5},                       "r0c3"],
    [{"y": -0.875, "x": 2.5},          "r0c2", {"x": 1}, "r0c4"],
    [{"y": -0.875, "x": 5.5},          "r0c5"],
    [{"y": -0.875, "x": 0, "w": 1.5},  "r0c0", "r0c1"],
    [{"y": -0.625, "x": 6.5},          "r0c6"],
    # Physical row 1
    [{"y": -0.75,  "x": 3.5},          "r1c3"],
    [{"y": -0.875, "x": 2.5},          "r1c2", {"x": 1}, "r1c4"],
    [{"y": -0.875, "x": 5.5},          "r1c5"],
    [{"y": -0.875, "x": 0, "w": 1.5},  "r1c0", "r1c1"],
    [{"y": -0.625, "x": 6.5, "h": 1.5},"r1c6"],
    # Physical row 2
    [{"y": -0.75,  "x": 3.5},          "r2c3"],
    [{"y": -0.875, "x": 2.5},          "r2c2", {"x": 1}, "r2c4"],
    [{"y": -0.875, "x": 5.5},          "r2c5"],
    [{"y": -0.875, "x": 0, "w": 1.5},  "r2c0", "r2c1"],
    # Physical row 3
    [{"y": -0.375, "x": 3.5},          "r3c3"],
    [{"y": -0.875, "x": 2.5},          "r3c2", {"x": 1}, "r3c4"],
    [{"y": -0.875, "x": 5.5},          "r3c5"],
    [{"y": -0.875, "x": 0, "w": 1.5},  "r3c0", "r3c1"],
    # Physical row 4 bottom (only cols 0-3 have regular keys here;
    # cols 4-6 are thumb cluster)
    [{"y": -0.375, "x": 3.5},          "r4c3"],
    [{"y": -0.875, "x": 2.5},          "r4c2"],
    [{"y": -0.75,  "x": 0.5},          "r4c0", "r4c1"],
]

# Parse via klavgen's built-in KLE → Key converter
_kg_path = "/tmp/_redox_main.kle.json"
with open(_kg_path, "w") as f:
    json.dump(_KLE_MAIN_GRID, f)

main_keys = generate_keys_from_kle_json(_kg_path)
assert len(main_keys) == 30, f"Expected 30 main-grid keys, got {len(main_keys)}"

# ---------------------------------------------------------------------------
# Thumb cluster — positioned manually relative to the main grid
# ---------------------------------------------------------------------------

# Find reference points from the main grid
main_bottom = min(k.y for k in main_keys)  # most-negative y = closest to user
# Col 5 (index inner) bottom and Col 6 positions
col5_keys = [k for k in main_keys if 100 < k.x < 110]
col6_keys = [k for k in main_keys if 120 < k.x < 130]
thumb_pivot_x = sum(k.x for k in col6_keys) / len(col6_keys)  # ~ 124
thumb_pivot_y = main_bottom + KEYCAP_1_5U_HEIGHT / 2 + 2

# Thumb keys fan out from the pivot point.  Rotation in klavgen is DEGREES
# and the Key.rotate field is applied CCW (contrary to KLE's r which is also
# CCW — so negative values here rotate CW).
#
# Redox thumb cluster, left half (all rotate clockwise so key tops tilt inward):
#   LCtrl     (4,4)  — outer edge, 1.25u wide,      r = -15°
#   Page Up   (2,6)  — upper fan,  1u,              r = -30°
#   Page Down (3,6)  — middle fan, 1u,              r = -30°
#   Backspace (4,5)  — lower fan,  1u wide × 1.5u tall
#   Delete    (4,6)  — lower fan,  1u wide × 1.5u tall

_THUMB_STEP = MX_KEY_X_SPACING + 1   # horizontal stride between fan keys
_THUMB_Y_GAP = MX_KEY_Y_SPACING      # vertical stride

thumb_keys = [
    # LCtrl — outer thumb (rotated -15° around pivot)
    Key(
        x=thumb_pivot_x + 12,
        y=main_bottom - KEYCAP_1_5U_HEIGHT / 2,
        rotate=-15,
        rotate_around=(thumb_pivot_x, thumb_pivot_y),
        keycap_width=KEYCAP_1_25U_WIDTH,
    ),
    # Page Up — thumb fan top
    Key(
        x=thumb_pivot_x + _THUMB_STEP,
        y=thumb_pivot_y - _THUMB_Y_GAP,
        rotate=-30,
        rotate_around=(thumb_pivot_x, thumb_pivot_y),
    ),
    # Page Down — thumb fan middle
    Key(
        x=thumb_pivot_x + _THUMB_STEP + _THUMB_STEP,
        y=thumb_pivot_y - _THUMB_Y_GAP,
        rotate=-30,
        rotate_around=(thumb_pivot_x, thumb_pivot_y),
    ),
    # Backspace — thumb fan bottom (1.5u tall)
    Key(
        x=thumb_pivot_x + _THUMB_STEP,
        y=thumb_pivot_y - _THUMB_Y_GAP - _THUMB_Y_GAP,
        rotate=-30,
        rotate_around=(thumb_pivot_x, thumb_pivot_y),
        keycap_depth=KEYCAP_1_5U_HEIGHT,
    ),
    # Delete — thumb fan bottom right
    Key(
        x=thumb_pivot_x + _THUMB_STEP + _THUMB_STEP,
        y=thumb_pivot_y - _THUMB_Y_GAP - _THUMB_Y_GAP,
        rotate=-30,
        rotate_around=(thumb_pivot_x, thumb_pivot_y),
        keycap_depth=KEYCAP_1_5U_HEIGHT,
    ),
]

# ---------------------------------------------------------------------------
# Combine all keys
# ---------------------------------------------------------------------------
keys = main_keys + thumb_keys
assert len(keys) == 35, f"Expected 35 total keys, got {len(keys)}"

# ---------------------------------------------------------------------------
# Case outline — bounding box of all keys + margin
# ---------------------------------------------------------------------------
margin = config.mx_key_config.case_tile_margin
xs = [k.x for k in keys]
ys = [k.y for k in keys]
min_x, max_x = min(xs) - margin, max(xs) + margin
min_y, max_y = min(ys) - margin, max(ys) + margin

# Expand a bit on the right for the controller area
max_x += 20

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
# Palm rests (optional — comment out if unwanted)
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
print(f"Generating Redox {'Choc' if use_choc else 'MX'} keyboard — {len(keys)} keys")
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
