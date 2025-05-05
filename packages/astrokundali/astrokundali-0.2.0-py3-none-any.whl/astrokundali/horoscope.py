# astrokundali/horoscope.py

import json, codecs
from pathlib import Path
from itertools import combinations
from typing import List, Dict, Any, Tuple

from .astro_data   import AstroData
from .astro_chart  import AstroChart
from .dispositions import get_dispositions, DRISHTI, _anticlockwise_house
from .yogas_detector import detect_yogas
try:
    from ftfy import fix_text
except ImportError:
    print("ftfy not found. Install it with 'pip install ftfy' to fix mojibake.")

# ─── Load Interpretation Data ──────────────────────────────────────────────────
DATA_DIR = Path(__file__).parent / 'data'

# Ascendant‐focused interpretations (sign, lord, friends, neutrals, enemies)
ASC_INT   = json.load(open(DATA_DIR / 'ascendant_interpretations.json'))

# Conjunction texts by combination + house
CONJ_INT  = json.load(open(DATA_DIR / 'conj_interpretations.json'))

# General planet interpretations (if needed)
GEN_INT   = json.load(open(DATA_DIR / 'general_interpretations.json'))

# Yoga definitions
YOGAS     = json.load(open(DATA_DIR / 'yogas.json'))

# ARUDHA definitions
ARUDHA_DATA     = json.load(open(DATA_DIR / 'arudha_lagna.json'))

# 1) Static map of Rāśi → Element
_SIGN_TO_ELEMENT = {
    "Aries":       "Fire",
    "Leo":         "Fire",
    "Sagittarius": "Fire",
    "Taurus":      "Earth",
    "Virgo":       "Earth",
    "Capricorn":   "Earth",
    "Gemini":      "Air",
    "Libra":       "Air",
    "Aquarius":    "Air",
    "Cancer":      "Water",
    "Scorpio":     "Water",
    "Pisces":      "Water",
}

# ─── Helpers ──────────────────────────────────────────────────────────────────

def _house_conjunctions(pls: List[str]) -> List[Tuple[str,...]]:
    """Return all 2‑n planet combinations in the same house."""
    combos = []
    for r in range(2, len(pls)+1):
        combos += list(combinations(pls, r))
    return combos

def _is_canceled(key: str, dispositions: Dict[str,Any]) -> bool:
    """
    A conjunction is 'canceled' if any planet in its
    'cancel_if_aspected_by' casts drishti onto the Ascendant.
    """
    info     = CONJ_INT.get(key, {})
    triggers = info.get('cancel_if_aspected_by', [])
    asc_house= dispositions['ascendant']['house_number']
    for t in triggers:
        for step in DRISHTI.get(t, []):
            if _anticlockwise_house(asc_house, step) == asc_house:
                return True
    return False


def json_sanitize(obj):
    r"""
    Recursively walk through obj (dict/list/str) and apply ftfy.fix_text()
    to every string, which will repair mojibake and unescape any \uXXXX.
    """
    if isinstance(obj, str):
        # fix_text will:
        #  • detect and undo Windows‑1252→UTF‑8 mojibake
        #  • decode backslashed escapes (\uXXXX)
        #  • uncurl quotes, fix weird punctuation, etc.
        return fix_text(obj)
    elif isinstance(obj, list):
        return [json_sanitize(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: json_sanitize(val) for key, val in obj.items()}
    else:
        return obj


def get_ascendant_element(
    disp: Dict[str, Any],
    elements_path: Path = Path(__file__).parent / "data" / "elements.json"
) -> Dict[str, Any]:
    """
    Given your dispositions dict `disp`, return a dict with:
      - asc_sign:       the Ascendant Rāśi name
      - element:        one of "Fire", "Earth", "Air", "Water"
      - interpretation: full text pulled from elements.json
    """
    # 2) Extract sign name
    asc_sign = disp["ascendant"]["sign_name"]
    # 3) Map to Element
    element = _SIGN_TO_ELEMENT.get(asc_sign)
    # 4) Load your elements.json
    with open(elements_path, encoding="utf-8") as f:
        elements_data = json.load(f)
    # 5) Pull interpretation (or empty string if missing)
    interp = elements_data.get(element, "")
    return {
        "asc_sign":        asc_sign,
        "element":         element,
        "interpretation":  interp
    }


# ─── Main Report Function ─────────────────────────────────────────────────────

def generate_report(
    astrodata: AstroData,
    house_system: str = 'whole_sign'
) -> Dict[str, Any]:
    """
    Returns a JSON‑ready dict with:
      - ascendant: sign/lord/friends/neutrals/enemies + their texts
      - interpretation: a list of sentences summarizing all of the above
      - houses: planet lists per house
      - conjunctions: combo texts + cancel flags
      - yogas: all defined yogas
      - arudha_lagna: house, planets, interpretation
    """
    # 1) dispositions: includes Ascendant and every planet’s house, status, etc.
    disp = get_dispositions(astrodata, house_system)

    # 2) Ascendant data
    asc        = disp['ascendant']
    asc_sign   = str(asc['sign_number'])
    asc_lord   = asc['sign_lord']
    friends    = [p for p,d in disp.items() if p!='ascendant' and 'Friendly Sign' in d['status']]
    neutrals   = [p for p,d in disp.items() if p!='ascendant' and 'Neutral Sign'  in d['status']]
    enemies    = [p for p,d in disp.items() if p!='ascendant' and 'Enemy Sign'    in d['status']]

    # 3) Build 'ascendant' section by pulling from ASC_INT
    asc_section = {
        'sign_number': asc['sign_number'],
        'sign_name':   asc['sign_name'],
        'sign_text':   ASC_INT['sign'].get(asc_sign, []),
        'lord':        asc_lord,
        'lord_text':   ASC_INT['lord'].get(asc_lord, []),
        'friends':     friends,
        'friends_text':   sum((ASC_INT['friends'].get(p, []) for p in friends), []),
        'neutrals':    neutrals,
        'neutrals_text':  sum((ASC_INT['neutrals'].get(p, []) for p in neutrals), []),
        'enemies':     enemies,
        'enemies_text':   sum((ASC_INT['enemies'].get(p, []) for p in enemies), [])
    }

    # 4) Dynamic 'interpretation' list
    interp: List[str] = []

    # 4a) summary
    f_str = ", ".join(friends)  if friends  else "none"
    n_str = ", ".join(neutrals) if neutrals else "none"
    e_str = ", ".join(enemies)  if enemies else "none"
    interp.append(
        f"Ascendant ({asc_section['sign_name']}): Lord is {asc_lord}. "
        f"Friends: {f_str}. Neutrals: {n_str}. Enemies: {e_str}."
    )

    # 4b) sign + lord details
    interp += asc_section['sign_text']
    interp += asc_section['lord_text']

    # 4c) friends / neutrals / enemies details
    interp += asc_section['friends_text']
    interp += asc_section['neutrals_text']
    interp += asc_section['enemies_text']

    # 4d) drishti modifiers on Ascendant
    drishti_planets = []
    asc_house       = asc['house_number']
    for p, d in disp.items():
        if p=='ascendant': continue
        for step in DRISHTI.get(p, []):
            if _anticlockwise_house(d['sign_number'], step) == asc_house:
                drishti_planets.append(p)
                break
    if drishti_planets:
        dp = ", ".join(drishti_planets)
        interp.append(
            f"However, the drishti of {dp} modifies these relationships with the Ascendant."
        )

    # 5) Houses & Conjunctions
    # build house → planet list
    houses = {i: [] for i in range(1,13)}
    for p,d in disp.items():
        if p=='ascendant': continue
        hn = d.get('house_number')
        if hn:
            houses[hn].append(p)

    conj_out = {}
    for hn, pls in houses.items():
        for combo in _house_conjunctions(pls):
            key = "_".join(sorted(combo) + [str(hn)])
            if key in CONJ_INT:
                conj_out[key] = {
                    'planets': combo,
                    'house':   hn,
                    'text':    CONJ_INT[key]['text'],
                    'canceled': _is_canceled(key, disp)
                }

    # 6) Yogas – detect & interpret
    # — existing data structures —
    # houses: Dict[int,List[str]]
    # disp: dispositions
 # 6) Yogas
    # detect which yogas apply
    yoga_keys = detect_yogas(astrodata, disp, houses)

    # build a list of interpretation strings
    yoga_section: List[str] = []
    if yoga_keys:
        # summary line
        names = [YOGAS[k]['name'] for k in yoga_keys]
        yoga_section.append(
            f"In your Kundali, the following Yogas are present: {', '.join(names)}."
        )
        # detailed descriptions
        for key in yoga_keys:
            info = YOGAS.get(key, {})
            # add all lines of the yoga's description
            yoga_section += info.get('description', [])
            # if malefic, check cancellation
            if info.get('type') == 'bad':
                canceled = _is_canceled(key, disp)
                note = "cancelled" if canceled else "not cancelled"
                yoga_section.append(
                    f"{info.get('name')} is {note} by Ascendant‑aspect Drishti."
                )
    else:
        yoga_section.append("No significant Yogas found in your Kundali.")



    # 7) Arudha Lagna
        # — calculate arudha_house exactly as before —
    lord_house = disp[asc_lord]['house_number'] or asc['sign_number']
    ar = (lord_house - 1 + lord_house - 1) % 12 + 1
    if ar == 1: ar = 10
    if ar == 7: ar = 4

    # 7a) pull generic intro
    interpretation = ARUDHA_DATA.get('generic', [])

    # 7b) pull house‑specific text
    house_texts = ARUDHA_DATA.get('houses', {}).get(str(ar), [])
    interpretation += house_texts

    # 7c) pull each planet’s Arudha entry
    ar_pl = houses.get(ar, []).copy()
    for p,d in disp.items():
        if p=='ascendant': continue
        for step in DRISHTI.get(p, []):
            if _anticlockwise_house(d['sign_number'], step) == ar:
                ar_pl.append(p)
                break

    # 7d) pull each planet’s Arudha entry
    planet_texts = []
    for pl in sorted(set(ar_pl)):  # your arudha planets list
        planet_texts += ARUDHA_DATA.get('planets', {}).get(pl, [])
    interpretation += planet_texts
    # interpretation += f'{" ".join(planet_texts)  if planet_texts else "none"}'

    arudha_section = {
        'house':         ar,
        'planets':       sorted(set(ar_pl)),
        'interpretation': interpretation
    }

    # 8) Compile final report
    # report['yogas_found'] = yoga_keys
    # report['yogas'] = yoga_section
    element_section = get_ascendant_element(disp)
    interp.append(
        f"Your Ascendant is in the {element_section['element']} element."
    )
    element_interp = element_section['interpretation']
    interp.append(
        f'You are {" ".join(element_interp)  if element_interp else "none"}'
    )
    report = {
        'ascendant':       asc_section,
        'ascendant_element': element_section,
        'interpretation':  interp,
        'houses':          houses,
        'conjunctions':    conj_out,
        'yogas_found':     yoga_keys,
        'yogas':           yoga_section,
        'arudha_lagna':    arudha_section
    }

    # clean up any “Â… codes” in all returned strings
    # return json_sanitize(report)
    return report


# # ─── Script Mode ─────────────────────────────────────────────────────────────
# if __name__ == '__main__':
#     from astrokundali import AstroData
#     import json
#     from astrokundali import generate_report, json_sanitize
#     data = AstroData(2009,3,30,9,36,0,5,30,19.0760,72.8777,ayanamsa='lahiri')
#     report  = json_sanitize(generate_report(data))
#     print(json.dumps(report, ensure_ascii=False, indent=2))
