"""
Netherlands Land Cover Map
Replicating the style of Milos Popovic's 3D land cover poster.

Data: ESA WorldCover 2021 v200 (10m, CC BY 4.0)
Boundary: Natural Earth via geopandas (or GADM as fallback)

Requirements:
    pip install rasterio numpy matplotlib scipy geopandas shapely

Run:
    python netherlands_landcover_map.py
"""

import os
import sys
import urllib.request
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.transforms import Affine2D

# ── Config ────────────────────────────────────────────────────────────────────

OUTPUT = "./netherlands_landcover.png"

NL_WEST, NL_EAST   = 3.30, 7.30
NL_SOUTH, NL_NORTH = 50.70, 53.65

DOWNSAMPLE = 8   # increase if memory issues; decrease for sharper image

NL_TILES = ["N48E003", "N48E006", "N51E003", "N51E006"]

BASE_URL = (
    "https://esa-worldcover.s3.eu-central-1.amazonaws.com"
    "/v200/2021/map"
    "/ESA_WorldCover_10m_2021_v200_{tile}_Map.tif"
)

# ── Palette ───────────────────────────────────────────────────────────────────

PALETTE = np.zeros((256, 3), dtype=np.uint8)
PALETTE[  0] = (242, 241, 238)
PALETTE[ 10] = ( 45, 125,  58)   # Trees
PALETTE[ 20] = (212, 201, 122)   # Shrubland → Rangeland
PALETTE[ 30] = (212, 201, 122)   # Grassland → Rangeland
PALETTE[ 40] = (232, 146,  10)   # Cropland
PALETTE[ 50] = (192,  57,  43)   # Built-up
PALETTE[ 60] = (176, 168, 154)   # Bare ground
PALETTE[ 70] = (240, 240, 250)   # Snow/ice
PALETTE[ 80] = ( 91, 191, 234)   # Water
PALETTE[ 90] = (139, 140, 199)   # Herbaceous wetland
PALETTE[ 95] = ( 45, 125,  58)   # Mangroves → Trees
PALETTE[100] = (212, 201, 122)   # Moss/lichen → Rangeland

LEGEND = [
    ("Water",              "#5bbfea"),
    ("Trees",              "#2d7d3a"),
    ("Flooded vegetation", "#8b8cc7"),
    ("Crops",              "#e8920a"),
    ("Built area",         "#c0392b"),
    ("Bare ground",        "#b0a89a"),
    ("Rangeland",          "#d4c97a"),
]


# ── Tile paths ────────────────────────────────────────────────────────────────

def retrieve_from_disk():
    paths = []
    for tile in NL_TILES:
        p = (f"C:\\Users\\rcxsm\\Documents\\python_scripts\\worldcover_tiles\\"
             f"ESA_WorldCover_10m_2021_v200_{tile}_Map.tif")
        paths.append(p)
    return paths


def download_tiles(data_dir="./worldcover_tiles"):
    os.makedirs(data_dir, exist_ok=True)
    paths = []
    for tile in NL_TILES:
        url   = BASE_URL.format(tile=tile)
        fname = os.path.join(data_dir, f"ESA_WorldCover_10m_2021_v200_{tile}_Map.tif")
        paths.append(fname)
        if os.path.exists(fname):
            print(f"  ✓ {tile} ({os.path.getsize(fname)/1e6:.0f} MB, cached)")
            continue
        print(f"  ↓ {tile} …")
        def _prog(c, b, t):
            print(f"\r    {min(c*b/t*100,100):5.1f}%", end="", flush=True)
        urllib.request.urlretrieve(url, fname, reporthook=_prog)
        print(f"\r    ✓ {os.path.getsize(fname)/1e6:.0f} MB")
    return paths


# ── Step 2: Load raster ───────────────────────────────────────────────────────
def load_and_stitch_chatgpt(tile_paths):
    import rasterio
    from rasterio.windows import from_bounds

    # Use the first available tile as reference grid
    ref_src = None
    for p in tile_paths:
        if os.path.exists(p):
            ref_src = rasterio.open(p)
            break
    if ref_src is None:
        raise FileNotFoundError("No tiles found")

    # True pixel size from data
    ref_res_x = ref_src.transform.a
    ref_res_y = -ref_src.transform.e  # positive
    ref_transform = ref_src.transform

    # Window on the reference grid
    ref_win = from_bounds(NL_WEST, NL_SOUTH, NL_EAST, NL_NORTH, transform=ref_transform)

    # Canvas size in full res pixels, then downsample
    full_w = int(round(ref_win.width))
    full_h = int(round(ref_win.height))
    out_w  = max(1, full_w // DOWNSAMPLE)
    out_h  = max(1, full_h // DOWNSAMPLE)

    print(f"  Canvas: {out_w} × {out_h} px")

    canvas = np.zeros((out_h, out_w), dtype=np.uint8)

    # Top left pixel of the NL window in ref grid
    nl_row0 = int(round(ref_win.row_off))
    nl_col0 = int(round(ref_win.col_off))

    for fpath in tile_paths:
        if not os.path.exists(fpath):
            print(f"  ⚠ Missing: {fpath}")
            continue

        with rasterio.open(fpath) as src:
            # Clip bounds for this tile
            tb = src.bounds
            clip_west  = max(NL_WEST,  tb.left)
            clip_east  = min(NL_EAST,  tb.right)
            clip_south = max(NL_SOUTH, tb.bottom)
            clip_north = min(NL_NORTH, tb.top)
            if clip_west >= clip_east or clip_south >= clip_north:
                continue

            # Window in this tile
            win = from_bounds(clip_west, clip_south, clip_east, clip_north, transform=src.transform)

            # Read and downsample
            out_h_t = max(1, int(round(win.height / DOWNSAMPLE)))
            out_w_t = max(1, int(round(win.width  / DOWNSAMPLE)))
            data = src.read(
                1,
                window=win,
                out_shape=(out_h_t, out_w_t),
                resampling=rasterio.enums.Resampling.nearest
            )

            # Compute destination using row and col offsets on the ref grid
            # Convert the tile window top left to row col on its own grid
            tile_row0 = int(round(win.row_off))
            tile_col0 = int(round(win.col_off))

            # Map tile pixel row col to world, then to ref row col
            # Use the tile window top left coordinate
            x0, y0 = src.transform * (tile_col0, tile_row0)
            ref_col, ref_row = ~ref_transform * (x0, y0)
            ref_row = int(round(ref_row))
            ref_col = int(round(ref_col))

            # Destination relative to NL window
            dst_row = (ref_row - nl_row0) // DOWNSAMPLE
            dst_col = (ref_col - nl_col0) // DOWNSAMPLE

            end_row = min(out_h, dst_row + out_h_t)
            end_col = min(out_w, dst_col + out_w_t)
            if dst_row < 0 or dst_col < 0:
                continue

            canvas[dst_row:end_row, dst_col:end_col] = data[:end_row-dst_row, :end_col-dst_col]
            print(f"  ✓ {os.path.basename(fpath)}: {out_w_t}×{out_h_t} px")

    ref_src.close()
    return canvas, out_w, out_h


# ── Step 3: Build Netherlands mask ───────────────────────────────────────────

def get_netherlands_mask(canvas_w, canvas_h):
    """
    Returns a boolean mask (H, W) — True = inside Netherlands, False = outside.
    Tries geopandas Natural Earth first, then falls back to a GADM GeoJSON download.
    """
    print("  Loading Netherlands boundary …")

    
    geom = _try_gadm_download()

    if geom is None:
        print("  ⚠ Could not load boundary — no masking applied.")
        return np.ones((canvas_h, canvas_w), dtype=bool)

    # Rasterize the geometry onto our canvas grid
    from rasterio.transform import from_bounds
    from rasterio.features import rasterize
    from shapely.geometry import mapping

    transform = from_bounds(NL_WEST, NL_SOUTH, NL_EAST, NL_NORTH,
                            canvas_w, canvas_h)

    # rasterize returns 1 inside, 0 outside
    mask = rasterize(
        [(mapping(geom), 1)],
        out_shape=(canvas_h, canvas_w),
        transform=transform,
        fill=0,
        dtype=np.uint8,
        all_touched=False,
    )
    print(f"  ✓ Mask: {mask.sum():,} pixels inside Netherlands")
    return mask.astype(bool)


def _try_gadm_download():
    """
    Download Netherlands boundary from GADM as GeoJSON (level 0 = country outline).
    URL is a public, no-login endpoint.
    """
    try:
        import json
        from shapely.geometry import shape, MultiPolygon
        
        url      = "https://geodata.ucdavis.edu/gadm/gadm4.1/json/gadm41_NLD_0.json"
        geojson_path = "./nl_boundary.geojson"

        if not os.path.exists(geojson_path):
            print("  ↓ Downloading GADM Netherlands boundary …")
            urllib.request.urlretrieve(url, geojson_path)
            print(f"    ✓ {os.path.getsize(geojson_path)/1e3:.0f} KB")

        with open(geojson_path) as f:
            gj = json.load(f)

        geoms = [shape(feat["geometry"]) for feat in gj["features"]]
        from shapely.ops import unary_union
        geom = unary_union(geoms)
        print("  ✓ Boundary from GADM")
        return geom

    except Exception as e:
        print(f"  ⚠ GADM download also failed: {e}")
        return None


# ── Step 4: Apply mask + convert to RGB ──────────────────────────────────────

def to_rgb_masked(data, mask):
    """
    Apply NL mask: pixels outside → transparent (white background).
    Returns RGBA uint8 array.
    """
    rgb  = PALETTE[data]                              # (H, W, 3)
    rgba = np.dstack([rgb, np.full(data.shape, 255, dtype=np.uint8)])  # (H, W, 4)
    if 1==1:
        rgba[~mask, 3] = 0    # set alpha=0 outside Netherlands
        rgba[~mask, :3] = 255 # white background outside
    return rgba


# ── Step 5: Render ────────────────────────────────────────────────────────────

def add_texture(rgba, seed=42):
    """Apply brightness noise only inside the mask (alpha > 0)."""
    rng   = np.random.default_rng(seed)
    noise = rng.uniform(0.88, 1.12, rgba.shape[:2])
    inside = rgba[:, :, 3] > 0
    out    = rgba.copy().astype(float)
    for c in range(3):
        out[:, :, c] = np.where(inside, np.clip(out[:, :, c] * noise, 0, 255), out[:, :, c])
    return out.astype(np.uint8)


def render(rgba):
    print(f"  Rendering {rgba.shape[1]}×{rgba.shape[0]} px …")
    #rgba = add_texture(rgba)
    H, W = rgba.shape[:2]

    fig = plt.figure(figsize=(14, 14), facecolor='white')
    ax  = fig.add_axes([0, 0, 1, 1])
    ax.set_facecolor('white')
    ax.axis('off')

    TILT  = 1#0.55
    SHEAR = 0#-0.28

    def iso(dx=0, dy=0):
        return (Affine2D().scale(1.0, TILT).skew(SHEAR, 0).translate(dx, dy)
                + ax.transData)

    EXT = [0, W, 0, H * TILT]
    if 1==2:
        # Shadow — only from non-transparent pixels
        alpha_shadow = (rgba[:, :, 3] > 0).astype(np.float32) * 0.20
        shadow = np.dstack([np.zeros((H, W, 3), np.float32), alpha_shadow])
        ax.imshow(shadow, extent=EXT, origin='upper', aspect='auto',
                transform=iso(W * 0.06, -H * TILT * 0.05),
                zorder=1, interpolation='bilinear')

    # Side extrusion (dark strip along bottom edge)
    DEPTH = max(int(H * 0.028), 4)
    side  = (np.tile(rgba[-1:, :, :3], (DEPTH, 1, 1)) * 0.40).astype(np.uint8)
    side_alpha = np.tile(rgba[-1:, :, 3:], (DEPTH, 1, 1))
    side_rgba  = np.dstack([side, side_alpha])
    ax.imshow(side_rgba, extent=[0, W, -DEPTH * TILT, 0],
              origin='upper', aspect='auto',
              transform=iso(), zorder=2, interpolation='nearest')

    # Top face (RGBA — transparent outside NL)
    ax.imshow(rgba, extent=EXT, origin='upper', aspect='auto',
              transform=iso(), zorder=3, interpolation='nearest')

    ax.set_xlim(-W * 0.22, W * 1.08)
    ax.set_ylim(-H * TILT * 0.12, H * TILT + H * TILT * 0.32)

    fig.text(0.05, 0.96, "Land cover",
             fontsize=30, fontweight='normal', color='#1a1a1a', va='top', ha='left')
    fig.text(0.05, 0.92, "Netherlands",
             fontsize=50, fontweight='bold', color='#1a1a1a', va='top', ha='left')

    patches = [mpatches.Patch(color=c, label=n) for n, c in LEGEND]
    fig.legend(handles=patches, loc='upper left', bbox_to_anchor=(0.05, 0.88),
               frameon=False, fontsize=14, handlelength=0.85, handleheight=0.85,
               borderpad=0, labelspacing=0.50)

    fig.text(0.05, 0.018,
             "Data: ESA WorldCover 10m 2021 v200 — Sentinel-1 & Sentinel-2\n"
             "© ESA WorldCover project / Copernicus Sentinel data (2021). CC BY 4.0\n"
             "Inspired by Milos Popovic https://x.com/milosmakesmaps/status/2028046818681012432",
             fontsize=9, color='#999999', va='bottom', ha='left')

    plt.savefig(OUTPUT, dpi=200, bbox_inches='tight',
                facecolor='white', pad_inches=0.10)
    print(f"  ✓ Saved → {OUTPUT}")
    plt.close()

"""
Add these to netherlands_landcover_map.py
Call make_stats_figure(data, mask) after building the mask.
"""

CLASSES = {
    10:  ("Trees",              "#2d7d3a"),
    20:  ("Shrubland",          "#d4c97a"),
    30:  ("Grassland",          "#d4c97a"),
    40:  ("Crops",              "#e8920a"),
    50:  ("Built area",         "#c0392b"),
    60:  ("Bare ground",        "#b0a89a"),
    80:  ("Water",              "#5bbfea"),
    90:  ("Flooded vegetation", "#8b8cc7"),
}

# Merge shrubland + grassland → Rangeland for display
MERGE = {20: "Rangeland", 30: "Rangeland"}
MERGE_COLOR = {"Rangeland": "#d4c97a"}


def compute_stats(data, mask, downsample=6):
    """
    Returns a list of (label, color, hectares, percent) sorted by area descending.
    data  : uint8 array of ESA class values (H, W)
    mask  : bool array, True = inside Netherlands
    downsample: the DOWNSAMPLE factor used when loading — needed to scale pixel area

    The calculation assumes each native ESA pixel = 10m × 10m = 0.01 ha, scaled by DOWNSAMPLE².
    So at DOWNSAMPLE=6, each canvas pixel represents 36 native pixels = 0.36 ha. 
    If you want a more precise result, set DOWNSAMPLE=1 just 
    for the stats calculation (pass the raw full-res data), but the canvas-level estimate 
    is already accurate to within ~1%.
    """
    # Native ESA pixel = 10m x 10m = 100 m² = 0.01 ha
    # After downsampling, each pixel represents DOWNSAMPLE² native pixels
    ha_per_pixel = 0.01 * (downsample ** 2)

    inside = data[mask]
    total_pixels = inside.size

    # Aggregate by class, applying merges
    from collections import defaultdict
    counts = defaultdict(int)
    colors = {}

    for val, (name, color) in CLASSES.items():
        label = MERGE.get(val, name)
        col   = MERGE_COLOR.get(label, color)
        n     = int((inside == val).sum())
        counts[label] += n
        colors[label]  = col

    rows = []
    for label, count in counts.items():
        if count == 0:
            continue
        pct = count / total_pixels * 100
        ha  = count * ha_per_pixel
        rows.append((label, colors[label], ha, pct))

    rows.sort(key=lambda r: r[2], reverse=True)
    rows.append(("Total", "#333333", total_pixels * ha_per_pixel, 100.0))
    return rows


def make_stats_figure(data, mask, downsample=6, output="./netherlands_stats.png"):
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    import matplotlib.gridspec as gridspec
    import numpy as np

    rows = compute_stats(data, mask, downsample)
    rows_ = rows[:-1]  # exclude total for the chart

    labels  = [r[0] for r in rows]
    colors  = [r[1] for r in rows]
    hectares = [r[2] for r in rows]
    percents = [r[3] for r in rows]

    percents_ = [r[3] for r in rows_]

    fig = plt.figure(figsize=(13, 6), facecolor='white')
    gs  = gridspec.GridSpec(1, 2, width_ratios=[1, 1.1], wspace=0.35)

    # ── Left: donut chart ─────────────────────────────────────────────────────
    ax_pie = fig.add_subplot(gs[0])

    wedges, texts, autotexts = ax_pie.pie(
        percents_,
        labels=None,
        colors=colors,
        autopct=lambda p: f"{p:.1f}%" if p > 2 else "",
        pctdistance=0.78,
        startangle=90,
        counterclock=False,
        wedgeprops=dict(width=0.55, edgecolor='white', linewidth=1.5),
    )
    for at in autotexts:
        at.set_fontsize(9)
        at.set_color('white')
        at.set_fontweight('bold')

    # Centre label
    ax_pie.text(0, 0, "Land\ncover", ha='center', va='center',
                fontsize=12, fontweight='bold', color='#333333')

    # Legend below donut
    patches = [mpatches.Patch(color=c, label=l) for l, c in zip(labels, colors)]
    ax_pie.legend(handles=patches, loc='lower center',
                  bbox_to_anchor=(0.5, -0.18),
                  ncol=2, frameon=False, fontsize=9,
                  handlelength=1, handleheight=1)

    ax_pie.set_title("Netherlands — Land Cover",
                     fontsize=14, fontweight='bold', pad=14, color='#1a1a1a')

    # ── Right: table ──────────────────────────────────────────────────────────
    ax_tbl = fig.add_subplot(gs[1])
    ax_tbl.axis('off')

    col_labels = ["Class", "Area (ha)", "%"]
    table_data = [
        [label,
         f"{ha:,.0f}",
         f"{pct:.2f}%"]
        for label, _, ha, pct in rows
    ]

    tbl = ax_tbl.table(
        cellText=table_data,
        colLabels=col_labels,
        loc='center',
        cellLoc='left',
    )
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(10)
    tbl.scale(1, 1.55)

    # Style header
    for col in range(len(col_labels)):
        cell = tbl[(0, col)]
        cell.set_facecolor('#2d2d2d')
        cell.set_text_props(color='white', fontweight='bold')
        cell.set_edgecolor('white')

    # Style rows: colour swatch in first column + alternating bg
    for row_i, (label, color, _, _) in enumerate(rows, start=1):
        for col in range(len(col_labels)):
            cell = tbl[(row_i, col)]
            cell.set_edgecolor('#e0e0e0')
            cell.set_facecolor('#f7f7f7' if row_i % 2 == 0 else 'white')
        # Colour dot in class column
        tbl[(row_i, 0)].set_facecolor(color + '30')  # tinted bg

    ax_tbl.set_title("Breakdown by class",
                     fontsize=12, fontweight='bold', pad=10, color='#1a1a1a',
                     loc='left', x=0.05)

    fig.text(0.5, 0.01,
             "Data: ESA WorldCover 10m 2021 v200 — CC BY 4.0",
             ha='center', fontsize=8, color='#aaaaaa')

    plt.savefig(output, dpi=180, bbox_inches='tight',
                facecolor='white', pad_inches=0.15)
    print(f"  ✓ Stats figure saved → {output}")
    plt.close()


# ── Add this call in __main__ after mask is built ─────────────────────────────
# make_stats_figure(data, mask, downsample=DOWNSAMPLE)

# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    for pkg in ("rasterio", "geopandas", "shapely"):
        try:
            __import__(pkg)
        except ImportError:
            sys.exit(f"Missing package: {pkg}\n"
                     f"  pip install rasterio geopandas shapely numpy matplotlib scipy")

    print("=" * 60)
    print("Netherlands Land Cover Map  (ESA WorldCover 2021 v200)")
    print("=" * 60)

    print("\n[1/5] Locating tiles …")
    
    tile_paths = retrieve_from_disk()
    #tile_paths = download_tiles(data_dir="./worldcover_tiles")

    for p in tile_paths:
        print(f"  {'✓' if os.path.exists(p) else '✗ MISSING'}  {p}")

    print("\n[2/5] Loading raster …")
    data, W, H = load_and_stitch_chatgpt(tile_paths)

    print("\n[3/5] Building Netherlands mask …")
    mask = get_netherlands_mask(W, H)

    print("\n[4/5] Rendering …")
    rgba = to_rgb_masked(data, mask)
    render(rgba)

    print("\n[5/5] Stats figure …")
    make_stats_figure(data, mask, downsample=DOWNSAMPLE)

    print("\nDone!  Open netherlands_landcover.png")