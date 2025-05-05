# astrokundali/yogas_detector.py

from .astro_data import AstroData
from typing import Dict, List, Any
from .dispositions import get_dispositions, DRISHTI, _anticlockwise_house


def _in_kendra(h1: int, h2: int) -> bool:
    """True if houses h1→h2 are Kendra apart (1,4,7,10 anticlockwise)."""
    diff = (h2 - h1) % 12
    return diff in (0, 3, 6, 9)

def detect_yogas(
    astrodata: AstroData,
    dispositions: Dict[str, Any],
    houses: Dict[int, List[str]]
) -> List[str]:
    """
    Return list of yoga‑keys that apply in this chart.
    Expand this function with all your yogas.
    """
    found = []

    # Example: GajaKesari: Moon & Jupiter mutual Kendra
    m_h = dispositions['moon']['house_number']
    j_h = dispositions['jupiter']['house_number']
    if m_h and j_h and _in_kendra(m_h, j_h) and _in_kendra(j_h, m_h):
        found.append('gajakesari_yoga')

    # Example: Budha‑Aditya: Sun+Mercury in same house
    for hn, pls in houses.items():
        if 'sun' in pls and 'mercury' in pls:
            found.append('budha_aditya_yoga')
            break

    # (add more detection rules here)

    # remove duplicates, preserve order
    return list(dict.fromkeys(found))
