"""
SV08 minimal 5020 fan holder + part-cooling duct
Replaces the stock blue front cover, the stock 5020 duct and its cover plate.
The rear 3010 blower and its deflector stay as they are.

Coordinates: origin = nozzle tip, +X right (seen from the front), +Y toward the
back of the printer, +Z up. All dimensions in mm, measured from Sovol's
published SV08 hotend STEP (JXHSV08-06000).

Hardware:
  - stock 5020 blower
  - 2x M3x30 socket head screws (through the fan ears from the front,
    self-tapping into the bosses)
  - 4x 4x3 mm disc magnets (same size as stock; check polarity against the
    toolhead before gluing)
"""
import math
import cadquery as cq

# ---------------- parameters ----------------
FLOOR_Z    = 3.6      # duct underside above nozzle tip (stock: 3.3-3.6)
WALL       = 1.2
TARGET     = (0.0, 0.0, -0.8)   # where the jets aim (just under the tip)

# 5020 blower (stock position)
FAN_X      = (-28.8, 20.5)   # outlet outer footprint
FAN_Y      = (-30.41, -10.25)
FAN_BOT_Z  = 15.4
FAN_OUT_X  = (-27.5, 15.7)   # outlet inner opening
FAN_OUT_Y  = (-29.5, -11.7)
EARS       = [(18.58, 19.10), (-25.26, 57.26)]   # (x, z) of the two ear holes
SOCKET_CLR = 0.25
SOCKET_H   = 4.0
SOCKET_T   = 1.6

# screws / bosses
BOSS_D     = 10.0     # 3.7 mm wall around the pilot
BOSS_LEN   = 10.0     # behind the fan back face
PILOT_D    = 2.6      # M3 self-tapping

# magnets (stock pocket positions on the extruder plate)
MATE_Y     = 17.25
MAGNETS    = [(-28.57, 29.65), (26.93, 29.65), (-29.07, 83.40), (27.42, 83.40)]
MAG_D      = 4.25
MAG_DEPTH  = 3.1
PAD_W, PAD_H, PAD_T = 8.0, 9.0, 6.0
X_LIMITS   = (-32.0, 30.5)   # stay inside the stock extruder plate's width

# side cheeks: deep YZ plates from the duct floor up to the magnet pads.
# The space between the fan's back face and the extruder plate is empty on
# both sides, so the cheeks use all of it; depth in Y is what resists
# pulling the part off the magnets.
CHEEK_X_L  = (-32.0, -26.0)
CHEEK_X_R  = (25.3, 30.5)    # 2515 fan screw heads end at x=24.5
CHEEK_FRONT = -9.6           # 0.8 behind the 5020, 1.5 behind the extruder adapter plate
CHEEK_BACK = 11.0            # ahead of the plate's screw heads (y>11.6)
FLANGE     = 5.0             # front / back edge width around the lightening holes
RIB        = 4.0             # diagonal ribs between the flanges

# ---------------- helpers ----------------
def box(x0, x1, y0, y1, z0, z1):
    return (cq.Workplane("XY")
            .box(x1 - x0, y1 - y0, z1 - z0, centered=False)
            .translate((x0, y0, z0)))

def cyl_y(x, z, y0, y1, d):
    return (cq.Workplane("XZ").center(x, z).circle(d / 2)
            .extrude(-(y1 - y0)).translate((0, y0, 0)))

def slot(p, w, h, length, along):
    """Slot cutter centred on point p, aimed from p at TARGET.
    w = width (horizontal, across the jet), h = height, `along` = horizontal
    axis of the slot face ('x' or 'y')."""
    d = [TARGET[i] - p[i] for i in range(3)]
    n = math.sqrt(sum(c * c for c in d)); d = [c / n for c in d]
    # local frame: x' = d, y' = horizontal width axis, z' = d x y'
    wv = (1, 0, 0) if along == "x" else (0, 1, 0)
    plane = cq.Plane(origin=p, xDir=d, normal=(
        d[1] * wv[2] - d[2] * wv[1],
        d[2] * wv[0] - d[0] * wv[2],
        d[0] * wv[1] - d[1] * wv[0]))
    return cq.Workplane(plane).rect(length, w).extrude(h / 2, both=True)

# ---------------- duct body ----------------
sx0, sx1 = FAN_X[0] - SOCKET_CLR, FAN_X[1] + SOCKET_CLR
sy0, sy1 = FAN_Y[0] - SOCKET_CLR, FAN_Y[1] + SOCKET_CLR
ox0, ox1 = sx0 - SOCKET_T, sx1 + SOCKET_T
oy0, oy1 = sy0 - SOCKET_T, sy1 + SOCKET_T          # oy1 ~ -8.4

ARM_TOP = 14.0
L_ARM = (ox0, -17.5, -12.0, 2.6)     # x0, x1, y0, y1  (probe sits at y>4.2)
R_ARM = (12.5, 26.0, -12.0, 8.5)     # 3010 deflector sits at y>12.5

outer = (box(ox0, ox1, oy0, oy1, FLOOR_Z, FAN_BOT_Z + SOCKET_H)
         .union(box(L_ARM[0], L_ARM[1], L_ARM[2], L_ARM[3], FLOOR_Z, ARM_TOP))
         .union(box(R_ARM[0], R_ARM[1], R_ARM[2], R_ARM[3], FLOOR_Z, ARM_TOP)))

zi0 = FLOOR_Z + WALL
void = (box(ox0 + WALL, ox1 - WALL, oy0 + WALL, oy1 - WALL, zi0, FAN_BOT_Z - WALL)
        # left channel stops at the cheek so the cheek stays solid down to the floor
        .union(box(CHEEK_X_L[1], L_ARM[1] - WALL, L_ARM[2], L_ARM[3] - WALL, zi0, ARM_TOP - WALL))
        .union(box(R_ARM[0] + WALL, R_ARM[1] - WALL, R_ARM[2], R_ARM[3] - WALL, zi0, ARM_TOP - WALL))
        # opening under the fan outlet (fan rests on the ledge around it)
        .union(box(FAN_OUT_X[0] + 0.2, FAN_OUT_X[1] - 0.2, FAN_OUT_Y[0] + 0.2, FAN_OUT_Y[1] - 0.2,
                   FAN_BOT_Z - WALL - 0.1, FAN_BOT_Z + 0.1))
        # socket the fan outlet drops into
        .union(box(sx0, sx1, sy0, sy1, FAN_BOT_Z, FAN_BOT_Z + SOCKET_H + 0.1)))

# ---------------- frame ----------------
frame = cq.Workplane("XY")
# fan ear bosses
for (ex, ez) in EARS:
    frame = frame.union(cyl_y(ex, ez, FAN_Y[1], FAN_Y[1] + BOSS_LEN, BOSS_D))
# lower-right boss sits on the right arm, tied sideways into the right cheek
frame = frame.union(box(EARS[0][0] - BOSS_D / 2, CHEEK_X_R[0] + 1, FAN_Y[1], FAN_Y[1] + BOSS_LEN,
                        ARM_TOP - 1, EARS[0][1]))
# (the upper-left boss merges straight into the left cheek)

def yz_prism(pts, x0, x1):
    return (cq.Workplane("YZ").polyline(pts).close()
            .extrude(x1 - x0).translate((x0, 0, 0)))

def cheek(x0, x1, arm_y1, lo_z, hi_z):
    """Side plate in the YZ plane: solid foot beside the duct arm, a 56 deg
    ramp back to the lower pad, front/back flanges up to the upper pad, and
    triangular lightening holes between diagonal ribs. Every downward-facing
    edge is 45 deg or steeper, so it prints upright without support."""
    lo_top, hi_bot = lo_z + PAD_H / 2, hi_z - PAD_H / 2
    ch = MATE_Y - CHEEK_BACK                     # 45 deg chamfers into the pads
    outline = [(CHEEK_FRONT, FLOOR_Z), (arm_y1, FLOOR_Z),
               (MATE_Y, lo_z - PAD_H / 2), (MATE_Y, lo_top),
               (CHEEK_BACK, lo_top + ch), (CHEEK_BACK, hi_bot - ch),
               (MATE_Y, hi_bot), (MATE_Y, hi_z + PAD_H / 2),
               (CHEEK_FRONT, hi_z + PAD_H / 2)]
    wy0, wy1 = CHEEK_FRONT + FLANGE, CHEEK_BACK - FLANGE
    wz0 = ARM_TOP + 6
    roof = (wy1 - wy0) / 2
    wz1 = hi_bot - ch - FLANGE                   # top of the gable roof
    window = yz_prism([(wy0, wz0), (wy1, wz0), (wy1, wz1 - roof),
                       ((wy0 + wy1) / 2, wz1), (wy0, wz1 - roof)], x0 - 1, x1 + 1)
    # zig-zag ribs, flange to flange
    n = 3
    step = (wz1 - roof - wz0) / n
    ribs = cq.Workplane("XY")
    for i in range(n):
        ya, yb = (wy1, wy0) if i % 2 == 0 else (wy0, wy1)
        za, zb = wz0 + i * step, wz0 + (i + 1) * step
        L = math.hypot(yb - ya, zb - za)
        uy, uz = (yb - ya) / L, (zb - za) / L     # along the rib
        py, pz = -uz * RIB / 2, uy * RIB / 2      # half-width across it
        ya, za, yb, zb = ya - uy * 3, za - uz * 3, yb + uy * 3, zb + uz * 3
        ribs = ribs.union(yz_prism([(ya + py, za + pz), (yb + py, zb + pz),
                                    (yb - py, zb - pz), (ya - py, za - pz)], x0 - 1, x1 + 1))
    return yz_prism(outline, x0, x1).cut(window.cut(ribs))

frame = frame.union(cheek(*CHEEK_X_L, L_ARM[3], MAGNETS[0][1], MAGNETS[2][1]))
frame = frame.union(cheek(*CHEEK_X_R, R_ARM[3], MAGNETS[1][1], MAGNETS[3][1]))

# magnet pads (wider than the cheeks so the pockets keep a full wall)
for (mx, mz) in MAGNETS:
    frame = frame.union(box(max(mx - PAD_W / 2, X_LIMITS[0]), min(mx + PAD_W / 2, X_LIMITS[1]), MATE_Y - PAD_T, MATE_Y,
                            mz - PAD_H / 2, mz + PAD_H / 2))

body = outer.union(frame).cut(void)

# ---------------- cooling jets ----------------
JET_H = 3.4
jets = [
    slot((L_ARM[1], -4.5, 7.6), 10.0, JET_H, 6.0, "y"),   # left
    slot((R_ARM[0],  0.5, 7.6), 11.0, JET_H, 6.0, "y"),   # right
    slot((-1.0, oy1, 7.6),      13.0, JET_H, 6.0, "x"),   # front
]
for j in jets:
    body = body.cut(j)

# ---------------- holes & pockets ----------------
for (ex, ez) in EARS:
    body = body.cut(cyl_y(ex, ez, FAN_Y[1] - 1, FAN_Y[1] + BOSS_LEN + 1, PILOT_D))
for (mx, mz) in MAGNETS:
    body = body.cut(cyl_y(mx, mz, MATE_Y - MAG_DEPTH, MATE_Y + 1, MAG_D))

# ---------------- keep-outs from the stock CAD ----------------
# Subtracts the real toolhead parts (with clearance) so the pads key onto the
# plate's magnet rims and every screw head / edge gets relief.
NOZZLE_TIP_RAW = (-335.6996, 225.0547, -224.0749)   # tip position in Sovol's STEP
CLR = 0.35

def stock_parts(step_path):
    from OCP.STEPCAFControl import STEPCAFControl_Reader
    from OCP.TDocStd import TDocStd_Document
    from OCP.XCAFDoc import XCAFDoc_DocumentTool
    from OCP.TDF import TDF_LabelSequence, TDF_Label
    from OCP.TCollection import TCollection_ExtendedString
    from OCP.TDataStd import TDataStd_Name
    from OCP.TopLoc import TopLoc_Location
    doc = TDocStd_Document(TCollection_ExtendedString("doc"))
    r = STEPCAFControl_Reader(); r.SetNameMode(True); r.ReadFile(step_path); r.Transfer(doc)
    st = XCAFDoc_DocumentTool.ShapeTool_s(doc.Main())
    out = []
    def name(l):
        a = TDataStd_Name()
        return a.Get().ToExtString() if l.FindAttribute(TDataStd_Name.GetID_s(), a) else ""
    def walk(lbl, loc):
        if st.IsAssembly_s(lbl):
            comps = TDF_LabelSequence(); st.GetComponents_s(lbl, comps)
            for i in range(1, comps.Length() + 1):
                c = comps.Value(i); ref = TDF_Label(); st.GetReferredShape_s(c, ref)
                walk(ref, loc.Multiplied(st.GetLocation_s(c)))
        else:
            s = cq.Shape.cast(st.GetShape_s(lbl).Moved(loc))
            out.append((name(lbl), s.translate(cq.Vector(*NOZZLE_TIP_RAW) * -1)))
    roots = TDF_LabelSequence(); st.GetFreeShapes(roots)
    for i in range(1, roots.Length() + 1):
        walk(roots.Value(i), TopLoc_Location())
    return out

# Only these zones of my part can touch the stock parts; cropping the stock
# solids to them keeps the booleans light.
KEEPOUT_ZONES = {
    "plate":  [(-34.5, -20.0, 3.0, 18.5, 18.0, 93.0), (20.0, 32.5, 3.0, 18.5, 18.0, 93.0)],
    "fanear": [(13.0, 24.0, -31.5, -9.5, 14.0, 26.0)],
}
KEEPOUT_KEYS = {"06008": "plate", "06009": "plate", "M3x12": "plate", "M2.5X18": "plate",
                "06037": "fanear"}

def apply_keepouts(body, step_path):
    shifts = [(0, 0, 0), (CLR, 0, 0), (-CLR, 0, 0), (0, 0, CLR), (0, 0, -CLR), (0, -CLR, 0)]
    cutters = []
    for n, s in stock_parts(step_path):
        zone = next((z for k, z in KEEPOUT_KEYS.items() if k in n), None)
        if zone is None:
            continue
        for zb in KEEPOUT_ZONES[zone]:
            sb = s.BoundingBox()
            if (sb.xmax < zb[0] or sb.xmin > zb[1] or sb.ymax < zb[2] or sb.ymin > zb[3]
                    or sb.zmax < zb[4] or sb.zmin > zb[5]):
                continue
            crop = s.intersect(box(*zb).val())
            if crop.Volume() < 1e-3:
                continue
            for v in shifts:
                if zone == "fanear" and v[1] != 0:
                    continue          # never push the fan into its bosses
                cutters.append(crop.translate(cq.Vector(*v)))
    print("keep-out cutters:", len(cutters))
    for c in cutters:
        body = body.cut(cq.Workplane().add(c))
    return body

if __name__ == "__main__":
    import sys
    out = sys.argv[1] if len(sys.argv) > 1 else "sv08_fan_holder"
    if len(sys.argv) > 2:
        body = apply_keepouts(body, sys.argv[2])
        sols = body.val().Solids(); print("solids after keepouts:", [round(s.Volume(),1) for s in sols])
        body = cq.Workplane().add(max(sols, key=lambda s: s.Volume()))
    cq.exporters.export(body, out + ".step")
    cq.exporters.export(body, out + ".stl", tolerance=0.02, angularTolerance=0.1)
    bb = body.val().BoundingBox()
    print("bbox", [round(v, 2) for v in (bb.xmin, bb.xmax, bb.ymin, bb.ymax, bb.zmin, bb.zmax)],
          "volume cm3", round(body.val().Volume() / 1000, 2))
