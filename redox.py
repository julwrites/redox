"""Redox keyboard generator for klavgen.

Generates the left half of a Redox keyboard (Reduced Ergodox) with exact key
positions from the QMK firmware layout definition.

Redox is an ergonomic split keyboard with:
  - 7 columns, 5 rows per half
  - 1.5u pinky column, 1.25u inner column
  - 1.5u + 2x 1.25u thumb cluster per half
  - 70 keys total (35 per half)

Usage:
  python redox.py          # Generate MX switch STLs
  python redox.py --choc   # Generate Choc switch STLs (experimental)

Requires CadQuery: https://cadquery.readthedocs.io/en/latest/installation.html
"""

import sys

from klavgen import *

# ---------------------------------------------------------------------------
# Keycap width helper
# Standard keycap widths as positioned by klavgen:
#   1u   = 18 mm  (MX_KEYCAP_1U_WIDTH)
#   1.5u = 23 mm  (MX_KEYCAP_1_5U_WIDTH)
# For in-between sizes we interpolate based on centre-to-centre spacing.
# ---------------------------------------------------------------------------
KEYCAP_1_25U_WIDTH = round(
    MX_KEYCAP_1U_WIDTH + 0.25 * MX_KEY_X_SPACING, 4
)  # ~ 22.7625

KEYCAP_1_5U_HEIGHT = round(
    MX_KEYCAP_1U_DEPTH + 0.5 * MX_KEY_Y_SPACING, 4
)  # ~ 27.525

# ---------------------------------------------------------------------------
# Switch type  (set --choc for experimental Choc support)
# ---------------------------------------------------------------------------
use_choc = "--choc" in sys.argv

config = Config(
    case_config=CaseConfig(
        side_fillet=4,
        palm_rests_top_fillet=5,
        switch_type=SwitchType.CHOC if use_choc else SwitchType.MX,
    ),
    mx_key_config=MXKeyConfig(case_tile_margin=7.5),
    choc_key_config=ChocKeyConfig(case_tile_margin=7.6),
    controller_config=ControllerConfig(case_tile_margin=5),
    trrs_jack_config=TrrsJackConfig(case_tile_margin=5),
    usbc_jack_config=USBCJackConfig(case_tile_margin=5),
)

S = MX_KEY_X_SPACING  # 19.05 mm  — centre-to-centre horizontal
SY = MX_KEY_Y_SPACING  # 19.05 mm — centre-to-centre vertical

# ---------------------------------------------------------------------------
# Key positions — exact QMK Redox layout (one half)
#
# Source: QMK Firmware  keyboards/redox/info.json
# Units converted to mm:  klavgen_x = (qmk_x + w/2) * 19.05
#                          klavgen_y = -(qmk_y + h/2) * 19.05
#
# Y increases upward in klavgen (contrary to QMK / KLE).
# ---------------------------------------------------------------------------

keys = [
    # === Row 0 (top row — 6 keys) ======================================
    Key(x=11.906250, y=-16.668750, keycap_width=MX_KEYCAP_1_5U_WIDTH),
    Key(x=33.337500, y=-16.668750),
    Key(x=52.387500, y=-11.906250),
    Key(x=71.437500, y=-9.525000),
    Key(x=90.487500, y=-11.906250),
    Key(x=109.537500, y=-14.287500),
    # === Row 1 (7 keys) ================================================
    Key(x=11.906250, y=-35.718750, keycap_width=MX_KEYCAP_1_5U_WIDTH),
    Key(x=33.337500, y=-35.718750),
    Key(x=52.387500, y=-30.956250),
    Key(x=71.437500, y=-28.575000),
    Key(x=90.487500, y=-30.956250),
    Key(x=109.537500, y=-33.337500),
    Key(x=128.587500, y=-23.812500),  # MO(_SYMB) / layer
    # === Row 2 (7 keys) ================================================
    Key(x=11.906250, y=-54.768750, keycap_width=MX_KEYCAP_1_5U_WIDTH),
    Key(x=33.337500, y=-54.768750),
    Key(x=52.387500, y=-50.006250),
    Key(x=71.437500, y=-47.625000),
    Key(x=90.487500, y=-50.006250),
    Key(x=109.537500, y=-52.387500),
    Key(x=128.587500, y=-47.625000, keycap_depth=KEYCAP_1_5U_HEIGHT),  # [
    # === Row 3 (8 keys) ================================================
    Key(x=11.906250, y=-73.818750, keycap_width=MX_KEYCAP_1_5U_WIDTH),
    Key(x=33.337500, y=-73.818750),
    Key(x=52.387500, y=-69.056250),
    Key(x=71.437500, y=-66.675000),
    Key(x=90.487500, y=-69.056250),
    Key(x=109.537500, y=-71.437500),
    Key(x=138.112500, y=-80.962500),  # Page Up
    Key(x=157.162500, y=-80.962500),  # Page Down
    # === Row 4 — bottom (7 keys) =======================================
    Key(x=14.287500, y=-92.868750),
    Key(x=33.337500, y=-92.868750),
    Key(x=52.387500, y=-88.106250),
    Key(x=71.437500, y=-85.725000),
    Key(x=116.681250, y=-109.537500, keycap_width=KEYCAP_1_25U_WIDTH),
    Key(x=138.112500, y=-104.775000, keycap_depth=KEYCAP_1_5U_HEIGHT),  # Back
    Key(x=157.162500, y=-104.775000, keycap_depth=KEYCAP_1_5U_HEIGHT),  # Del
]

# ---------------------------------------------------------------------------
# Case outline  —  bounding box of all keys + standard margin
# ---------------------------------------------------------------------------
mx, my = config.mx_key_config.case_tile_margin, config.mx_key_config.case_tile_margin
xs = [k.x for k in keys]
ys = [k.y for k in keys]
min_x = min(xs) - MX_KEYCAP_1_5U_WIDTH / 2 - mx
max_x = max(xs) + MX_KEYCAP_1U_WIDTH / 2 + mx
min_y = min(ys) - MX_KEYCAP_1U_WIDTH / 2 - my
max_y = max(ys) + MX_KEYCAP_1U_WIDTH / 2 + my

# ---------------------------------------------------------------------------
# Controller and jack holders  (approximate positions — tune for your build)
# ---------------------------------------------------------------------------
controller = Controller(
    x=(max_x - 25), y=(min_y + 20)
)

usbc_jack = USBCJack(
    x=(max_x - 10), y=(min_y + 5), rotate=-90
)

# ---------------------------------------------------------------------------
# Screw holes  (approximate — tune for your build)
# ---------------------------------------------------------------------------
screw_holes = [
    ScrewHole(x=min_x + 5, y=max_y - 5),
    ScrewHole(x=max_x - 5, y=max_y - 5),
    ScrewHole(x=max_x - 5, y=min_y + 5),
    ScrewHole(x=min_x + 5, y=min_y + 5),
]

# ---------------------------------------------------------------------------
# Case patches  — a simple polygon around the key outline
# ---------------------------------------------------------------------------
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
    )
]

# ---------------------------------------------------------------------------
# Palm rests  (optional — comment out if not wanted)
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
# Texts
# ---------------------------------------------------------------------------
texts = [
    Text(x=min_x + 16, y=max_y - 10, z=0, text="Redox", font_size=10, extrude=0.4),
]

# ---------------------------------------------------------------------------
# Render & save
# ---------------------------------------------------------------------------
print(f"Generating Redox {'Choc' if use_choc else 'MX'} keyboard STLs …")
print(f"  {len(keys)} keys")
print(f"  Bounding box: [{min_x:.1f}, {min_y:.1f}] – [{max_x:.1f}, {max_y:.1f}] mm")

keyboard_result = render_and_save_keyboard(
    keys=keys,
    screw_holes=screw_holes,
    controller=controller,
    components=[usbc_jack],
    patches=patches,
    palm_rests=palm_rests,
    texts=texts,
    debug=False,
    render_standard_components=True,
    config=config,
)

print("Done — STL files written to current directory.")
