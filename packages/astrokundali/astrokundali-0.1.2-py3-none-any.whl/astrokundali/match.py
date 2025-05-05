"""
astrokundali/match.py

Enhanced Ashtakoota (Guna Milan) marriage matching with detailed table, faults, remedies, and dynamic interpretation.
"""
import swisseph as swe
from .astro_data import AstroData
from .dispositions import get_dispositions

# 1. Varna mapping (Moon sign -> varna level)
VARNA_MAP = {1:3,2:2,3:1,4:3,5:4,6:2,7:1,8:3,9:4,10:2,11:1,12:4}
VARNA_NAME = {1:'Brahmin',2:'Kshatriya',3:'Vaishya',4:'Shudra'}

# 2. Vashya mapping (Moon sign -> control group)
VASHA_MAP = {
    1:'Chatushpada',2:'Manav',3:'Jalachara',4:'Jalachara',
    5:'Chatushpada',6:'Manav',7:'Manav',8:'Vanachara',
    9:'Manav',10:'Chatushpada',11:'Chatushpada',12:'Jalachara'
}

# 3. Gana groups (nakshatra -> Deva/Manushya/Rakshasa)
GANA_GROUPS = {
    **{n:'Deva' for n in (2,6,10,11,15,19,23,27)},
    **{n:'Manushya' for n in (1,5,7,12,13,17,20,22,24)},
    **{n:'Rakshasa' for n in set(range(1,28)) - {2,6,10,11,15,19,23,27} - {1,5,7,12,13,17,20,22,24}}
}

# 4. Yoni mapping (nakshatra -> animal)
YONI_MAP = {
    1:'Horse',2:'Elephant',3:'Sheep',4:'Snake',5:'Sheep',6:'Dog',
    7:'Cat',8:'Rat',9:'Cow',10:'Rat',11:'Buffalo',12:'Tiger',
    13:'Lion',14:'Mongoose',15:'Deer',16:'Monkey',17:'Tiger',
    18:'Dog',19:'Elephant',20:'Horse',21:'Dog',22:'Horse',
    23:'Sheep',24:'Rat',25:'Deer',26:'Rat',27:'Elephant'
}

# 5. Nadi mapping (nakshatra -> nadi)
NADI_MAP = {i:['Aadi','Madhya','Antya'][(i%3)-1] for i in range(1,28)}

# 6. Koota weights and descriptions
KOOTA_INFO = {
    'Varna':      {'max':1,  'desc':'Spiritual Development'},
    'Vashya':     {'max':2,  'desc':'Mutual Control Compatibility'},
    'Tara':       {'max':3,  'desc':'Health and Longevity'},
    'Yoni':       {'max':4,  'desc':'Physical & Emotional Compatibility'},
    'Graha Maitri':{'max':5,  'desc':'Mental & Emotional Friendship'},
    'Gana':       {'max':6,  'desc':'Temperamental Harmony'},
    'Bhakoot':    {'max':7,  'desc':'Financial & Emotional Stability'},
    'Nadi':       {'max':8,  'desc':'Genetic & Health Harmony'}
}

# 7. Remedies for each dosha
REMINDERS = {
    'Varna': ['Navagraha Shanti Puja', 'Recite Gayatri Mantra'],
    'Vashya': ['Donate sweets/clothes', 'Wear Cat’s Eye gemstone'],
    'Tara': ['Tara Dosha Havan', 'Visit Tara Devi Temple'],
    'Yoni': ['Chant Maha Mrityunjaya Mantra', 'Perform Graha Shanti Pooja'],
    'Gana': ['Gan Dosh Nivaran Puja', 'Chant Jupiter Mantra'],
    'Bhakoot': ['Bhakoot Dosha Puja', 'Charity of white foods'],
    'Graha Maitri': ['Graha Maitri Shanti Havan', 'Wear Pearl & Yellow Sapphire'],
    'Nadi': ['Nadi Dosha Havan', 'Pilgrimage to Saptashrungi'],
    'Manglik': ['Rice Puja at Mangalnath', 'Plant Neem tree for 42 days', 'Donate red items on Tuesday']
}

# 8. Graha friendship for Graha Maitri
FRIENDSHIP = {
    'sun': ['moon','mars','jupiter'],
    'moon': ['sun','mercury'],
    'mars': ['sun','moon','jupiter'],
    'mercury': ['venus','sun'],
    'jupiter': ['sun','moon'],
    'venus': ['mercury','saturn'],
    'saturn': ['mercury','venus'],
    'north_node': [], 'south_node': []
}

# Scoring functions

def varna_koota(m1, m2):
    return 1 if VARNA_MAP[m1['sign_number']] >= VARNA_MAP[m2['sign_number']] else 0


def vashya_koota(m1, m2):
    return 2 if VASHA_MAP[m1['sign_number']] == VASHA_MAP[m2['sign_number']] else 0


def tara_koota(m1, m2):
    n1, n2 = m1['nakshatra'], m2['nakshatra']
    k1 = (n2 - n1) % 9 or 9
    k2 = (n1 - n2) % 9 or 9
    def sc(k):
        if k in (1, 9): return 3
        if k in (3, 5): return 1.5
        return 0
    return sc(k1) + sc(k2)


def yoni_koota(m1, m2):
    return 4 if YONI_MAP[m1['nakshatra']] == YONI_MAP[m2['nakshatra']] else 0


def gana_koota(m1, m2):
    g1 = GANA_GROUPS[m1['nakshatra']]
    g2 = GANA_GROUPS[m2['nakshatra']]
    if g1 == g2:
        return 6
    if set([g1, g2]) == {'Deva', 'Manushya'}:
        return 5
    if set([g1, g2]) == {'Manushya', 'Rakshasa'}:
        return 1
    return 0


def graha_maitri_koota(m1, m2):
    return 5 if m2['sign_lord'] in FRIENDSHIP.get(m1['sign_lord'], []) else 0


def bhakoot_koota(m1, m2):
    diff = abs(m1['sign_number'] - m2['sign_number'])
    return 7 if diff in {1,2,4,6,7,8,10,11} else 0


def nadi_koota(m1, m2):
    return 8 if NADI_MAP[m1['nakshatra']] != NADI_MAP[m2['nakshatra']] else 0


def manglik_dosha(data: AstroData) -> bool:
    raw = data.get_rashi_data()
    asc = raw['ascendant']['lon'] % 360
    mars = raw['mars']['lon'] % 360
    house = int(((mars - asc) % 360) // 30) + 1
    return house in (1,2,4,7,8,12)


def match_kundli(a: AstroData, b: AstroData) -> dict:
    """
    Compute Ashtakoota compatibility, faults, remedies, and dynamic interpretation.
    Returns:
      - table: list of rows with Particular, Boy, Girl, Max, Obtained, Significance
      - faults: list of dosha names
      - remedies: dict of lists of remedies per fault
      - interpretation: narrative recommendation
    """
    # Get dispositions and Moon info
    d1 = get_dispositions(a)
    d2 = get_dispositions(b)
    m1, m2 = d1['moon'], d2['moon']

    # Compute koota scores
    scores = {
        'Varna': varna_koota(m1, m2),
        'Vashya': vashya_koota(m1, m2),
        'Tara': tara_koota(m1, m2),
        'Yoni': yoni_koota(m1, m2),
        'Graha Maitri': graha_maitri_koota(m1, m2),
        'Gana': gana_koota(m1, m2),
        'Bhakoot': bhakoot_koota(m1, m2),
        'Nadi': nadi_koota(m1, m2)
    }
    total = sum(scores.values())
    max_total = sum(info['max'] for info in KOOTA_INFO.values())

    # Identify faults (zero scores)
    faults = [k for k, v in scores.items() if v == 0]
    # Manglik check
    mg_a, mg_b = manglik_dosha(a), manglik_dosha(b)
    if mg_a != mg_b:
        faults.append('Manglik')

    # Build detailed table
    table = []
    for k, pts in scores.items():
        info = KOOTA_INFO[k]
        # Boy/Girl type
        if k == 'Varna':
            # Map sign_number to varna level, then to name
            boy_varna_level = VARNA_MAP[m1['sign_number']]
            girl_varna_level = VARNA_MAP[m2['sign_number']]
            boy_type = VARNA_NAME[boy_varna_level]
            girl_type = VARNA_NAME[girl_varna_level]
        elif k == 'Vashya':
            boy_type = VASHA_MAP[m1['sign_number']]
            girl_type = VASHA_MAP[m2['sign_number']]
        elif k == 'Tara':
            from .dispositions import NAKSHATRA_LORDS
            boy_type = NAKSHATRA_LORDS[m1['nakshatra']-1]
            girl_type = NAKSHATRA_LORDS[m2['nakshatra']-1]
        elif k == 'Yoni':
            boy_type = YONI_MAP[m1['nakshatra']]
            girl_type = YONI_MAP[m2['nakshatra']]
        elif k == 'Gana':
            boy_type = GANA_GROUPS[m1['nakshatra']]
            girl_type = GANA_GROUPS[m2['nakshatra']]
        else:
            boy_type = girl_type = ''
        table.append({
            'Particular': f"{k} Koota",
            'Boy': boy_type,
            'Girl': girl_type,
            'Max': info['max'],
            'Obtained': pts,
            'Significance': info['desc']
        })
    # Add total row
    table.append({
        'Particular': 'Total',
        'Boy': '-', 'Girl': '-',
        'Max': max_total,
        'Obtained': total,
        'Significance': f"Overall Compatibility: {total/max_total*100:.1f}%"
    })

    # Assemble dynamic interpretation
    interp_parts = []
    # Manglik narrative
    if 'Manglik' in faults:
        s = f"Boy is {'Manglik' if mg_a else 'not Manglik'}, "
        s += f"Girl is {'Manglik' if mg_b else 'not Manglik'}."
        s += " However, if Mars is aspected by Jupiter in the boy's chart, this Manglik dosha may be mitigated."
        interp_parts.append(s)
    # Other koota faults
    for f in faults:
        if f == 'Manglik': continue
        desc = KOOTA_INFO[f]['desc']
        rem = '; '.join(REMINDERS.get(f, []))
        interp_parts.append(f"{f} Koota scored zero ({desc}); recommended remedies: {rem}.")
    if not faults:
        interp_parts.append("No doshas detected; the couple shows excellent compatibility across all kootas.")

    interpretation = ' '.join(interp_parts)

    return {
        'table': table,
        'faults': faults,
        'remedies': {f: REMINDERS.get(f, []) for f in faults},
        'interpretation': interpretation
    }

# # Example usage
# if __name__ == '__main__':
#     A = AstroData(1990,1,1,10,0,0,5,30,19.07,72.88)
#     B = AstroData(1992,6,15,16,30,0,5,30,28.61,77.23)
#     from pprint import pprint
#     pprint(match_kundli(A, B))
# Nadi 

# Tara --> 1.5 [Average]
