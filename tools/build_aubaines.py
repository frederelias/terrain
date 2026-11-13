# Ventes pour défaut de paiement de taxes (avis publics des MRC, documents publics en vertu du Code municipal).
# Ne conserve AUCUN nom de propriétaire : seulement lot, montant, type d'immeuble, date et lieu de la vente, lien vers l'avis officiel.
import json, re, subprocess, time, urllib.request, urllib.parse, os, sys, html
UA={'User-Agent':'LOTS-aubaines/1.0 (+https://lots.quebec; robot hebdomadaire, avis publics seulement)'}
CAD='https://geo.environnement.gouv.qc.ca/donnees/rest/services/Reference/Cadastre_allege/MapServer/0/query'
SDA='https://servicescarto.mrnf.gouv.qc.ca/pes/rest/services/Territoire/SDA_WMS/MapServer/2/query'
MOIS={'janvier':1,'février':2,'fevrier':2,'mars':3,'avril':4,'mai':5,'juin':6,'juillet':7,'août':8,'aout':8,'septembre':9,'octobre':10,'novembre':11,'décembre':12,'decembre':12}
ORD={'premier':1,'deuxième':2,'troisième':3,'quatrième':4,'cinquième':5,'sixième':6,'septième':7,'huitième':8,'neuvième':9,'dixième':10,'onzième':11,'douzième':12,'treizième':13,'quatorzième':14,'quinzième':15,'seizième':16,'dix-septième':17,'dix-huitième':18,'dix-neuvième':19,'vingtième':20}
def get(url,binary=True,timeout=40):
    req=urllib.request.Request(url,headers=UA)
    with urllib.request.urlopen(req,timeout=timeout) as r: d=r.read(); return d if binary else d.decode('utf-8','replace')
def pdf_text(data):
    open('/tmp/a.pdf','wb').write(data); subprocess.run(['pdftotext','-layout','/tmp/a.pdf','/tmp/a.txt'],check=True,timeout=120); return open('/tmp/a.txt',encoding='utf-8',errors='replace').read()
def sale_date(t):
    low=t.lower()
    m=re.search(r'(\d{1,2})(?:er|e)?\s*(?:jour du mois de\s+)?(janvier|f[ée]vrier|mars|avril|mai|juin|juillet|ao[uû]t|septembre|octobre|novembre|d[ée]cembre)\s+(?:de l.an\s+[^\(]{0,60}\()?\s*(?:\d{1,2}\s+\w+\s+)?(20\d\d)',low)
    cands=[]
    for m in re.finditer(r'(\d{1,2})(?:er|e)?\s+(janvier|f[ée]vrier|mars|avril|mai|juin|juillet|ao[uû]t|septembre|octobre|novembre|d[ée]cembre)\s+(20\d\d)',low):
        cands.append((m.start(),int(m.group(1)),MOIS[m.group(2).replace('é','é')] if m.group(2) in MOIS else MOIS.get(m.group(2).replace('e','é',1),6),int(m.group(3))))
    # la vente est la date la plus proche après « enchère » / « seront vendus » / « vente »
    anchor=min([i for i in (low.find('enchère'),low.find('seront vendus'),low.find('vendus à'),low.find('vente')) if i>=0] or [0])
    after=[c for c in cands if c[0]>=anchor and c[2] in (5,6,7)] or [c for c in cands if c[2] in (5,6,7)] or cands
    if not after: return None
    c=after[0]; return f'{c[3]:04d}-{c[2]:02d}-{c[1]:02d}'
def sale_place(t):
    one=' '.join(t.split()); m=re.search(r'(?:enchère publique|seront vendus[^,]{0,80}),?\s*(?:au|à la|à l.|en la)\s+(.{10,140}?),\s*(?:le\s|province|\()',one,re.I)
    return m.group(1).strip() if m else ''
LOT=re.compile(r'(?<!\d)(\d{1,2} \d{3} \d{3})(?![\d,])')
AMT=re.compile(r'(\d{1,3}(?:[ \u00a0\u202f]\d{3})*,\d{2})\s?\$')
TYPES=[('terrain vacant','Terrain vacant'),('vacant','Terrain vacant'),('chalet','Chalet'),('résidence','Résidence'),('maison','Résidence'),('bâtiment','Bâtiment'),('commercial','Commercial'),('agricole','Agricole'),('boisé','Boisé'),('terre','Terre')]
def parse_lots(t):
    out=[]; lines=t.splitlines()
    for i,ln in enumerate(lines):
        for m in LOT.finditer(ln):
            lot=m.group(1)
            ctx=ln.lower()
            if not any(k in ctx for k,_ in TYPES):
                nb=[x for x in lines[max(0,i-1):i+2] if not LOT.search(x)]; ctx=' '.join(nb).lower()
            am=AMT.search(ln[m.end():]) or AMT.search(' '.join(lines[i:i+3]))
            typ=next((lab for k,lab in TYPES if k in ctx),None)
            out.append({'lot':lot,'montant':am.group(1).replace('\u00a0',' ').replace('\u202f',' ') if am else None,'type':typ})
    seen={}; [seen.setdefault(o['lot'],o) for o in out]; return list(seen.values())
def discover(page):
    try: h=get(page,binary=False)
    except Exception as e: print('  page injoignable',page,e); return []
    links=re.findall(r'href=["\']([^"\']+\.pdf)["\']',h,re.I); res=[]
    for l in links:
        u=urllib.parse.urljoin(page,html.unescape(l))
        if re.search(r'vente|taxe|vpt|d[ée]faut|impay|non.?paiement|ench',u,re.I): res.append(u)
    return res
WP_TERMS=['vente pour taxes','vente taxes','VPT','défaut de paiement','non-paiement','non paiement des taxes']
def wp_discover(base,min_year):
    found={}
    for term in WP_TERMS:
        u=base.rstrip('/')+'/wp-json/wp/v2/media?'+urllib.parse.urlencode({'search':term,'per_page':50,'_fields':'source_url,date,mime_type,title'})
        try: items=json.loads(get(u,binary=False))
        except Exception as e: print('  wp injoignable',base,str(e)[:60]); return []
        for it in items if isinstance(items,list) else []:
            url=it.get('source_url',''); d=it.get('date','')[:10]
            if url.lower().endswith('.pdf') and d[:4].isdigit() and int(d[:4])>=min_year and not re.search(r'guide|faq|reglement|règlement|procedurier',url,re.I): found[url]=d
        time.sleep(0.4)
    return [u for u,_ in sorted(found.items(),key=lambda x:x[1],reverse=True)]
def cadastre(lots):
    geo={}
    for k in range(0,len(lots),40):
        chunk=lots[k:k+40]; where="NO_LOT IN ("+','.join("'"+l+"'" for l in chunk)+")"
        q=urllib.parse.urlencode({'where':where,'outFields':'NO_LOT','returnGeometry':'true','outSR':'4326','f':'geojson'})
        try: j=json.loads(get(CAD+'?'+q))
        except Exception as e: print('  cadastre erreur',e); continue
        for f in j.get('features',[]):
            g=f['geometry']; ring=g['coordinates'][0] if g['type']=='Polygon' else g['coordinates'][0][0]
            xs=[c[0] for c in ring]; ys=[c[1] for c in ring]
            geo[f['properties']['NO_LOT']]={'lat':round(sum(ys)/len(ys),6),'lng':round(sum(xs)/len(xs),6),'bbox':[round(min(xs),6),round(min(ys),6),round(max(xs),6),round(max(ys),6)]}
        time.sleep(0.5)
    return geo
def muni(lat,lng,cache={}):
    k=(round(lat,2),round(lng,2))
    if k in cache: return cache[k]
    q=urllib.parse.urlencode({'geometry':f'{lng},{lat}','geometryType':'esriGeometryPoint','inSR':'4326','spatialRel':'esriSpatialRelIntersects','outFields':'MUS_NM_MUN','returnGeometry':'false','f':'json'})
    try: j=json.loads(get(SDA+'?'+q)); v=j['features'][0]['attributes']['MUS_NM_MUN'] if j.get('features') else None
    except Exception: v=None
    cache[k]=v; time.sleep(0.2); return v
src=json.load(open('tools/aubaines_sources.json',encoding='utf-8'))['sources']
events=[]; lots_out=[]; report=[]
for s in src:
    wp=[u for b in s.get('wp',[]) for u in wp_discover(b,int(time.strftime('%Y'))-1)]
    urls=list(dict.fromkeys(wp+s.get('pdfs',[])+(discover(s['page']) if s.get('page') else [])))
    for u in urls:
        print('—',s['mrc'],u)
        try: t=pdf_text(get(u))
        except Exception as e: report.append({'mrc':s['mrc'],'url':u,'statut':'injoignable','detail':str(e)[:80]}); print('  injoignable',e); continue
        lots=parse_lots(t); d=sale_date(t); place=sale_place(t)
        if not lots: report.append({'mrc':s['mrc'],'url':u,'statut':'aucun lot trouvé (liste absente ou format non lu)','date':d}); print('  aucun lot'); continue
        if any(e['mrc']==s['mrc'] and e['date']==d for e in events): report.append({'mrc':s['mrc'],'url':u,'statut':'version antérieure ignorée','date':d}); print('  version antérieure, ignorée'); continue
        geo=cadastre([l['lot'] for l in lots]); ev=len(events)
        found=0
        for l in lots:
            g=geo.get(l['lot']);
            if not g: continue
            found+=1; lots_out.append({**l,'e':ev,**g,'muni':muni(g['lat'],g['lng'])})
        events.append({'mrc':s['mrc'],'date':d,'lieu':place,'url':u,'lots':found,'lus':len(lots)})
        report.append({'mrc':s['mrc'],'url':u,'statut':'ok','date':d,'lots_lus':len(lots),'lots_places':found}); print(f'  {len(lots)} lots lus, {found} placés, vente {d}')
os.makedirs('out',exist_ok=True)
json.dump({'built':time.strftime('%Y-%m-%d'),'note':"Avis publics de vente pour défaut de paiement de taxes (Code municipal, art. 1022 et suiv.). Aucun nom de propriétaire n'est conservé. La liste change jusqu'au jour de la vente : vérifier auprès de la MRC.",'events':events,'lots':lots_out},open('out/aubaines.json','w',encoding='utf-8'),ensure_ascii=False,separators=(',',':'))
json.dump(report,open('out/rapport.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
print('TOTAL',len(events),'ventes',len(lots_out),'lots placés')
