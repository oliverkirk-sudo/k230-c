"""Preserve schematic population intent in native footprints; no geometry edits."""
import pcbnew as k

def properties(component):
 return {p.get('name'):p.get('value') for p in component.findall('property')}

def expected_attributes(component, existing_attributes):
 p=properties(component);dnp='dnp' in p
 exclude_bom='exclude_from_bom' in p
 # J1 is fabricated edge copper, not an assembled connector. DNP components
 # remain physical but must not enter the default placement export.
 exclude_pos=('exclude_from_pos_files' in p) or dnp or component.get('ref')=='J1'
 mask=k.FP_DNP|k.FP_EXCLUDE_FROM_BOM|k.FP_EXCLUDE_FROM_POS_FILES
 return (existing_attributes & ~mask)|(k.FP_DNP if dnp else 0)|(k.FP_EXCLUDE_FROM_BOM if exclude_bom else 0)|(k.FP_EXCLUDE_FROM_POS_FILES if exclude_pos else 0)

def apply_population(component, footprint):
 before=[(p.GetNumber(),p.GetNetname(),p.GetPosition().x,p.GetPosition().y,p.GetSize().x,p.GetSize().y)for p in footprint.Pads()]
 footprint.SetAttributes(expected_attributes(component,footprint.GetAttributes()))
 after=[(p.GetNumber(),p.GetNetname(),p.GetPosition().x,p.GetPosition().y,p.GetSize().x,p.GetSize().y)for p in footprint.Pads()]
 assert before==after,'Population edit changed pad geometry or connectivity'
 return footprint.GetAttributes()

def validate_population(component, footprint):
 assert footprint.GetAttributes()==expected_attributes(component,footprint.GetAttributes()),'DNP/BOM/placement attributes differ from master intent'
 return True
