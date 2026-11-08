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
    
    starget = None
    for elem in wb_root.iter('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheet'):
        if elem.attrib.get('name') == 'New Report':
            starget = 'xl/' + rel_map[elem.attrib.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')]
            
    sroot = ET.fromstring(z.read(starget))
    
    row_data = {}
    for row in sroot.iter('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}row'):
        r_num = int(row.attrib.get('r'))
        if r_num > 20: continue
        row_data[r_num] = {}
        for c in row.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}c'):
            ref = c.attrib.get('r')
            t = c.attrib.get('t')
            v = c.find('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}v')
            f = c.find('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}f')
            val = v.text if v is not None else ''
            if t == 's' and val:
                try: val = shared_strings[int(val)]
                except: val = ''
            formula = f.text if f is not None else ''
            # only print columns from BK to BV
            col_letters = ''.join([ch for ch in ref if ch.isalpha()])
            if col_letters >= 'BK' and col_letters <= 'BX':
                row_data[r_num][ref] = (val, formula)
                
    for r_num in sorted(row_data.keys()):
        cols = row_data[r_num]
        if cols:
            line_str = " | ".join([f"{k}: {repr(v[0])}" + (f" (f={v[1]})" if v[1] else "") for k, v in sorted(cols.items())])
            print(f"Row {r_num:2d}: {line_str}")

