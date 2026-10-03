# New sealed-enclosure temperature requirement

User stated that the sealed environment may reach75–85°C. Whether this is enclosure air or device surface is still being clarified. Do not silently convert one into the other.

## Present candidate is not temperature-qualified

- Samsung K4F8E304HB-MGCJ is explicitly Tc−25…85°C. If enclosure air can be85°C, there is no positive case-rise allowance. At75°C air only10°C remains before its stated case maximum, including heating from neighboring devices
- KLMAG1JETD-B041 lists an85°C operating maximum; the exact sensor/location and higher-temperature alternative need confirmation
- AUP logic is an85°C ambient grade. Operation at the endpoint is not extra ambient margin, and a hot local pocket may exceed it
- X5R ends at85°C component temperature. It is not an acceptable fit shortcut for an assumed85°C enclosure-air design. X7R/125°C alternatives still need bias, tolerance, aging, ripple and placement checks
- Regulator junction maximum, PCB temperature, package case temperature and enclosure air are different quantities. A125°C junction rating does not mean125°C ambient capability

## Thermal architecture required before release

Define worst enclosure air and wall temperatures, duty cycle, heat-source distribution, allowed power throttling (not currently authorized as a performance change), and mechanical contact/height for a heat spreader. Maintain the38×38mm interface target; do not assume a fan or larger board. Actual power at the intended workload and rail efficiencies must be measured or reliably bounded.

For illustration only, with85°C air and a125°C junction ceiling, the entire allowed junction-to-air rise is40°C: a3W hotspot would require effective thermal resistance below13.3°C/W, a5W hotspot below8°C/W, and10W below4°C/W. These are arithmetic upper bounds with zero design margin, not an achieved thermal solution or a use of JEDEC theta-JA as a real enclosure model. Board and neighboring-device coupling make independent component calculations insufficient.

The existing rail-current table is a guide allocation, not measured module dissipation. It excludes memory, conversion losses and some external loads. It cannot be presented as a validated enclosure thermal budget.

Higher-temperature1GB LPDDR4 and16GB eMMC candidates may preserve functionality, but package/ball mapping, voltage, startup, firmware training and lifecycle must be reviewed before replacement. Current symbols/footprints must not be relabeled as another memory part.

## Required evidence

1. Confirm air versus surface temperature and realistic enclosure wall/heat-path boundary
2. Select temperature-qualified memory/logic/passives or demonstrate acceptable local temperatures with margin
3. Review power losses and thermal paths at each operating corner
4. Instrument real prototype with suitable thermocouples/IR emissivity treatment and junction telemetry; test full workload, cold/hot startup and sustained sealed operation

No thermal pass, performance reduction, added cooling hardware, procurement or fabrication is authorized by this note.
