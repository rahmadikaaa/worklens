import zipfile
import xml.etree.ElementTree as ET

fn = r'C:\Users\rahma\Downloads\AGIT L1 EOD Daily Report (4).xlsx'

with zipfile.ZipFile(fn, 'r') as z:
    # get shared strings
    shared_strings = []
    if 'xl/sharedStrings.xml' in z.namelist():
        sst_xml = z.read('xl/sharedStrings.xml')
        sst_root = ET.fromstring(sst_xml)
        for si in sst_root.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}si'):
            t = ''.join([e.text or '' for e in si.iter('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t')])
            shared_strings.append(t)
            
    # get sheet map
    wb_xml = z.read('xl/workbook.xml')
    wb_root = ET.fromstring(wb_xml)
    sheets = {}
    for elem in wb_root.iter('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheet'):
        sheets[elem.attrib.get('name')] = elem.attrib.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')
        
    # get rels
    rels_xml = z.read('xl/_rels/workbook.xml.rels')
    rels_root = ET.fromstring(rels_xml)
    rel_map = {}
    for elem in rels_root.iter('{http://schemas.openxmlformats.org/package/2006/relationships}Relationship'):
        rel_map[elem.attrib.get('Id')] = elem.attrib.get('Target')
        
    for target_sheet in ['Pivot', 'EOD Dashboard']:
        r_id = sheets.get(target_sheet)
        if not r_id: continue
        target_path = 'xl/' + rel_map[r_id]
        sheet_xml = z.read(target_path)
        sheet_root = ET.fromstring(sheet_xml)
        print(f"\n================ SHEET: {target_sheet} ================")
        row_data = {}
        for row in sheet_root.iter('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}row'):
            r_num = int(row.attrib.get('r'))
            if r_num > 40: continue
            row_data[r_num] = {}
            for c in row.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}c'):
                c_ref = c.attrib.get('r')
                t = c.attrib.get('t')
                v_elem = c.find('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}v')
                f_elem = c.find('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}f')
                val = v_elem.text if v_elem is not None else ''
                formula = f_elem.text if f_elem is not None else ''
                if t == 's' and val:
                    val = shared_strings[int(val)]
                row_data[r_num][c_ref] = (val, formula)
                
        for r_num in sorted(row_data.keys()):
            cols = row_data[r_num]
            row_str = " | ".join([f"{k}: {v[0]}" + (f" (f={v[1]})" if v[1] else "") for k, v in sorted(cols.items())])
            print(f"Row {r_num:2d}: {row_str}")

