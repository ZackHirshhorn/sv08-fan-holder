# SV08 minimal 5020 fan holder

A minimal replacement for the Sovol SV08's blue front toolhead cover. It holds only the stock 5020 part-cooling blower and its duct. The hotend, heatsink fan and probe stay fully open.

It replaces the stock blue cover, the stock 5020 duct (JXHSV08-06029) and its cover plate (JXHSV08-06032). The rear 3010 blower and its deflector stay as they are.

![preview](preview.png)

## Design
- **Fan:** the stock 5020 sits in its original position, with its outlet dropping into a socket on the duct.
- **Duct:** feeds three jets aimed just below the nozzle tip, from the front, front-left and front-right. The rear 3010 covers the back. The duct's underside is 3.6 mm above the tip, the same as stock.
- **Mounting:** four magnets in the stock positions. The pads are shaped around the raised rims and screw heads on the extruder plate, so they key on the same way as the stock cover.
- Modeled and collision-checked against Sovol's published hotend STEP (`JXHSV08-06000`, [Sovol3d/SV08](https://github.com/Sovol3d/SV08)).

## Hardware
- Stock 5020 blower
- 2× M3×30 socket head screws, through the fan ears from the front, self-tapping into the bosses
- 4× 4×3 mm disc magnets. Check polarity against the toolhead before gluing.

## Printing
- Print upright, standing on the duct floor. No supports needed.
- ASA or ABS. The part sits right over the heated bed, so PLA will sag.

## Notes
- Modeled with the stock inductive probe. If you use an Eddy probe, check the clearance on the left side.
- With the open front, part cooling is stronger than stock. Re-check your fan percentages.

## Files
| File | What it is |
|---|---|
| `sv08_5020_fan_holder.stl` | Ready to slice |
| `sv08_5020_fan_holder.step` | For editing in Fusion, Onshape, FreeCAD, etc. |
| `sv08_5020_fan_holder.py` | Parametric CadQuery source |
| `preview.png` | Render on the stock toolhead |

## Rebuilding from source
```
pip install cadquery
python sv08_5020_fan_holder.py sv08_5020_fan_holder path/to/hotend.step
```
The STEP argument is optional. It's Sovol's hotend assembly, used to carve clearance around the extruder plate, screw heads and fan ear. All dimensions are parameters at the top of the script. The origin is the nozzle tip, +Y points toward the back of the printer, and +Z points up.
