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
    
    for elem in wb_root.iter('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheet'):
        sname = elem.attrib.get('name')
        starget = 'xl/' + rel_map[elem.attrib.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')]
        sroot = ET.fromstring(z.read(starget))
        
        found = []
        for c in sroot.iter('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}c'):
            t = c.attrib.get('t')
            v = c.find('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}v')
            val = v.text if v is not None else ''
            if t == 's' and val:
                try:
                    val = shared_strings[int(val)]
                except:
                    val = ''
            val = str(val or '')
            if any(term.lower() in val.lower() for term in ['event basis', 'workload basis', 'total activity automated', 'reduce %']):
                found.append((c.attrib.get('r'), val))
        if found:
            print(f"Sheet {sname} has matches: {found}")
