# Construit des tuiles JSON du rôle d'évaluation (données ouvertes MAMH, CC-BY 4.0)
# indexées par préfixe de numéro de lot rénové. Aucun nom ni adresse de propriétaire
# n'existe dans la source ; rien n'est réidentifié.
import sys, os, json, time
from collections import defaultdict
from osgeo import ogr, gdal
gdal.UseExceptions()
GDB = sys.argv[1]; OUT = 'data/role'; os.makedirs(OUT + '/lots', exist_ok=True)
ds = ogr.Open(GDB)
t0 = time.time()
def keep(lng, lat):  # grande région : Outaouais-est → Lanaudière, sans Montréal/Laval
    return (-75.3 <= lng <= -72.7) and ((lng <= -74.0 and lat >= 45.45) or lat >= 45.75) and lat <= 46.85

# 1. Points des unités
pts = ds.GetLayerByName('rol_unite_p'); pts.SetSpatialFilterRect(-75.3, 45.45, -72.7, 46.85)
pos = {}
for f in pts:
    g = f.GetGeometryRef(); x, y = g.GetX(), g.GetY()
    if keep(x, y): pos[f.GetField('id_provinc')] = (round(y, 6), round(x, 6), f.GetField('code_mun'))
print('unités dans la région', len(pos), round(time.time()-t0), 's', flush=True)

# 2. Attributs
U = {}
for f in ds.GetLayerByName('B05EX1_B05V_UNITE_EVALN'):
    k = f.GetField('id_provinc')
    if k not in pos: continue
    gi = lambda n: (lambda v: None if v is None else (int(v) if isinstance(v, (int, float)) else v))(f.GetField(n))
    U[k] = [f.GetField('mat18'), f.GetField('rl0105a'), gi('rl0302a'), gi('rl0402a'), gi('rl0403a'), gi('rl0404a'),
            f.GetField('rl0307a'), f.GetField('rl0303a'), gi('rl0315a')]
print('attributs', len(U), round(time.time()-t0), 's', flush=True)

# 3. Adresse de l'unité (pas du propriétaire)
A = {}
for f in ds.GetLayerByName('B05EX1_B05V_ADR_UNITE_EVALN'):
    k = f.GetField('id_provinc')
    if k not in pos or k in A: continue
    parts = [f.GetField('rl0101a'), f.GetField('rl0101e'), f.GetField('rl0101f'), f.GetField('rl0101g'), f.GetField('rl0101h')]
    A[k] = ' '.join(p.strip() for p in parts if p and str(p).strip())
print('adresses', len(A), round(time.time()-t0), 's', flush=True)

# 4. Propriété : année d'inscription la plus ancienne, nombre d'inscrits, statut (sans nom)
P = defaultdict(lambda: [None, 0, set()])
for f in ds.GetLayerByName('B05EX1_B05V_ADR_PROPRIO'):
    k = f.GetField('id_provinc')
    if k not in pos: continue
    r = P[k]; r[1] += 1
    d = f.GetFieldAsString('rl0201gx')[:4]
    if d.isdigit() and (r[0] is None or d < r[0]): r[0] = d
    s = f.GetField('rl0201hx');  r[2].add(s) if s else None
print('propriétés', len(P), round(time.time()-t0), 's', flush=True)

# 5. Lots rénovés → unité
tiles = defaultdict(dict); nlots = 0
for f in ds.GetLayerByName('B05EX1_B05V_LOT_CADST'):
    k = f.GetField('id_provinc'); lot = (f.GetField('rl0103a') or '').strip()
    if k not in pos or not lot.isdigit(): continue
    u = U.get(k)
    if not u: continue
    p = P.get(k, [None, 0, set()]); la, ln, cm = pos[k]
    rec = u + [A.get(k, ''), p[0], p[1], ''.join(sorted(p[2])), cm, la, ln]
    t = tiles[lot[:4]]
    if lot not in t: t[lot] = rec; nlots += 1
print('lots', nlots, 'tuiles', len(tiles), round(time.time()-t0), 's', flush=True)

for pre, d in tiles.items():
    with open(f'{OUT}/lots/{pre}.json', 'w') as fh: json.dump(d, fh, ensure_ascii=False, separators=(',', ':'))

# 6. Domaines (libellés)
doms = {}
for name in ['CODE_UTILISATION_CUBF_3', 'CODE_GENERIQUE_ADRESSE', 'CODE_ZONAGE_AGRICOLE', 'CODE_STATUT']:
    try: doms[name] = ds.GetFieldDomain(name).GetEnumeration()
    except Exception as e: print('domaine', name, e)
json.dump(doms, open(f'{OUT}/domains.json', 'w'), ensure_ascii=False, separators=(',', ':'))
json.dump({'source': "Rôle d'évaluation foncière du Québec géoréférencé 2026, MAMH, Données Québec, CC-BY 4.0",
           'fields': ['mat18','cubf','sup_m2','v_terrain','v_batiment','v_immeuble','annee_constr','zonage_agri','sup_foret_m2',
                      'adresse_unite','inscrit_depuis','nb_inscrits','statut','code_mun','lat','lng'],
           'lots': nlots, 'tiles': len(tiles), 'built': time.strftime('%Y-%m-%d')},
          open(f'{OUT}/meta.json', 'w'), ensure_ascii=False, indent=1)
print('fini', round(time.time()-t0), 's')
