import zipfile
import xml.etree.ElementTree as ET

fn = r'C:\Users\rahma\Downloads\AGIT L1 EOD Daily Report (4).xlsx'

with zipfile.ZipFile(fn, 'r') as z:
    sst_root = ET.fromstring(z.read('xl/sharedStrings.xml'))
    shared_strings = [''.join([e.text or '' for e in si.iter('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t')])
                      for si in sst_root.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}si')]
    
    wb_root = ET.fromstring(z.read('xl/workbook.xml'))
    rels_root = ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))
    rel_map = {elem.attrib.get('Id'): elem.attrib.get('Target') for elem in rels_root.iter('{http://schemas.openxmlformats.org/package/2006/relationships}Relationship')}
    
    sheet_target = None
    for elem in wb_root.iter('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheet'):
        if elem.attrib.get('name') == 'Pivot':
            sheet_target = 'xl/' + rel_map[elem.attrib.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')]
            
    sheet_root = ET.fromstring(z.read(sheet_target))
    for row in sheet_root.iter('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}row'):
        r_num = int(row.attrib.get('r'))
        cells = {}
        for c in row.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}c'):
            ref = c.attrib.get('r')
            t = c.attrib.get('t')
            v = c.find('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}v')
            f = c.find('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}f')
            val = v.text if v is not None else ''
            if t == 's' and val: val = shared_strings[int(val)]
            formula = f.text if f is not None else ''
            cells[ref] = (val, formula)
        
        # print if contains any pivot header keywords
        line_text = " ".join([v[0] for v in cells.values()])
        if any(w in line_text for w in ['Mission Critical', 'Business Critical', 'Total Activity', 'Triggered', 'Event Basis', 'Workload Basis', 'Reduce', 'Automated']):
            print(f"Row {r_num:2d}: " + " | ".join([f"{k}: {v[0]}" + (f" [f={v[1]}]" if v[1] else "") for k, v in sorted(cells.items())]))

