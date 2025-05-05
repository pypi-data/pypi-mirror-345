import math
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import swisseph as swe

from .astro_chart import House
from .astro_data import AstroData
from .houses import equal_houses, get_house_cusps
from .dispositions import DEBILITATIONS

# House drawing definitions (assumed imported or defined above)
HOUSE_VERTICES = [
    [(100,225),(200,300),(300,225),(200,150)],
    [(100,225),(  0,300),(200,300)],
    [(  0,150),(  0,300),(100,225)],
    [(  0,150),(100,225),(200,150),(100, 75)],
    [(  0,  0),(  0,150),(100, 75)],
    [(  0,  0),(100, 75),(200,  0)],
    [(100, 75),(200,150),(300, 75),(200,  0)],
    [(200,  0),(300, 75),(400,  0)],
    [(300, 75),(400,150),(400,  0)],
    [(300, 75),(200,150),(300,225),(400,150)],
    [(300,225),(400,300),(400,150)],
    [(300,225),(200,300),(400,300)]
]
# Layout definitions
# HOUSE_VERTICES = [
#     [(100,225),(200,300),(300,225),(200,150)],
#     [(100,225),(  0,300),(200,300)],
#     [(  0,150),(  0,300),(100,225)],
#     [(  0,150),(100,225),(200,150),(100, 75)],
#     [(  0,  0),(  0,150),(100, 75)],
#     [(  0,  0),(100, 75),(200,  0)],
#     [(100, 75),(200,150),(300, 75),(200,  0)],
#     [(200,  0),(300, 75),(400,  0)],
#     [(300, 75),(400,150),(400,  0)],
#     [(300, 75),(200,150),(300,225),(400,150)],
#     [(300,225),(400,300),(400,150)],
#     [(300,225),(200,300),(400,300)]
# ]
# CENTERS = [
#     (190,75),(100,30),(30,75),(90,150),
#     (30,225),(90,278),(190,225),(290,278),
#     (360,225),(290,150),(360,75),(290,30)
# ]
PLANET_ABBR = {
    'sun':'Su','moon':'Mo','mercury':'Me','venus':'Ve',
    'mars':'Ma','jupiter':'Ju','saturn':'Sa','uranus':'Ur',
    'neptune':'Ne','pluto':'Pl','north_node':'Ra','south_node':'Ke'
}

def _build_houses(raw: dict, house_system: str, astrodata) -> list[House]:
    """
    Build House objects from raw rashi/divisional data,
    tagging both retrograde and debilitation status.
    """
    asc_lon = raw['ascendant']['lon']
    sign0   = raw['ascendant']['sign_num']

    # 1) Compute cusps
    if house_system == 'equal':
        cusps = equal_houses(asc_lon)
    else:
        flags = swe.FLG_SWIEPH | swe.FLG_SPEED | swe.FLG_SIDEREAL
        _, ascmc = swe.houses_ex(
            astrodata.julian_day, astrodata.lat, astrodata.lon,
            b'B', flags
        )
        mc = ascmc[1]
        cusps = get_house_cusps(
            house_system, asc_lon,
            JD = astrodata.julian_day,
            lat = astrodata.lat,
            lon = astrodata.lon,
            mc = mc
        )

    # 2) Initialize House objects
    houses = []
    s = sign0
    for _ in range(12):
        h = House(s)
        houses.append(h)
        s = 1 if s == 12 else s + 1
    houses[0].is_asc = True

    # 3) Assign planets + flags
    for name, info in raw.items():
        if name == 'ascendant':
            continue
        lon    = info['lon']
        retro  = info.get('retro', False)
        sign_n = info.get('sign_num')
        # Debilitated if sign_num matches the 'fall' sign :contentReference[oaicite:2]{index=2}
        deb = (name in DEBILITATIONS and DEBILITATIONS[name] == sign_n)

        for i in range(12):
            start, end = cusps[i], cusps[(i+1) % 12]
            in_house = (start <= lon < end) if end > start else (lon >= start or lon < end)
            if in_house:
                houses[i].planets[name] = {
                    'lon': lon,
                    'retro': retro,
                    'debilitated': deb
                }
                break

    return houses


# (1) Define how far to shift sign‑numbers toward the chart center
SIGN_SHIFT = {
    'top':        ( 0, +5),
    'bottom':     ( 0, -5),
    'left':       (+5,  0),
    'right':      (-5,  0),
    'center':     ( 0,  0),
    'top-left':   (+3, +3),
    'top-right':  (-3, +3),
    'bot-left':   (+3, -3),
    'bot-right':  (-3, -3),
}

# (2) Planets move opposite to sign‑numbers
PLANET_SHIFT = { region: (-dx, -dy)
                 for region, (dx, dy) in SIGN_SHIFT.items() }

def _region(cx: float, cy: float, width=400, height=300) -> str:
    """
    Bucket (cx,cy) into one of:
       'top', 'bottom', 'left', 'right', 'center', plus 4 corners.
    """
    x3 = width  / 3
    y3 = height / 3

    vert = 'center'
    if cy < y3:
        vert = 'top'
    elif cy > 2*y3:
        vert = 'bottom'

    horiz = 'center'
    if cx < x3:
        horiz = 'left'
    elif cx > 2*x3:
        horiz = 'right'

    # corners
    if vert in ('top','bottom') and horiz in ('left','right'):
        key = f"{vert[:-1]}-{horiz}" if vert.endswith('t') else f"{vert}-{horiz}"
        # normalize naming: 'top-left','bottom-right', etc.
        return key.replace('bottom','bot')
    return vert if vert != 'center' else horiz

def _plot_chart(
    houses: list[House],
    title: str,
    description: str,
    show_retro: bool = False
):
    """
    Draw North‑Indian Kundali with:
      • sign‑numbers & planet labels shifted per SIGN_SHIFT/PLANET_SHIFT
      • planet labels clamped within chart bounds
      • bottom description moved up
    """
    fig, ax = plt.subplots(figsize=(6,6))

    # Title up near the top
    fig.suptitle(title, fontsize=16, y=0.87, weight='bold')
    fig.subplots_adjust(top=0.85, bottom=0.07, left=0.03, right=0.97)

    ax.set_xlim(0,400)
    ax.set_ylim(0,300)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.invert_yaxis()

    # draw house outlines
    for verts in HOUSE_VERTICES:
        ax.add_patch(Polygon(verts, closed=True, fill=False, edgecolor='black', linewidth=1))

    # annotate each house
    for i, h in enumerate(houses):
        xs, ys = zip(*HOUSE_VERTICES[i])
        cx, cy = sum(xs)/len(xs), sum(ys)/len(ys)

        region    = _region(cx, cy)
        sdx, sdy  = SIGN_SHIFT.get(region, (0,0))
        pdx, pdy  = PLANET_SHIFT.get(region, (0,0))

        # draw sign number
        ax.text(cx + sdx, cy + sdy, str(h.sign_num),
                ha='center', va='center',
                fontsize=10, weight='bold', color='blue')

        # draw planets
        for j, (pl, dat) in enumerate(h.planets.items()):
            angle = 2 * math.pi * j / max(len(h.planets),1)
            # raw coords
            x = cx + pdx + 20 * math.cos(angle)
            y = cy + pdy + 20 * math.sin(angle)
            # clamp to [5,395] × [5,295]
            x = min(max(x, 5), 395)
            y = min(max(y, 5), 295)

            label = f"{PLANET_ABBR.get(pl,pl[:2])} {int(dat['lon']%30)}°"
            if show_retro and dat.get('retro', False):
                label = f"{label}$^{{Re}}$"
            if show_retro and dat.get('debilitated', False):
                label = f"{label}$_{{De}}$"

            ax.text(x, y, label,
                    ha='center', va='center',
                    fontsize=8, weight='bold', color='orange')

    # move bottom description up slightly
    fig.text(0.5, 0.06, description, ha='center', fontsize=12)
    plt.show()


    
# def _build_houses(raw: dict, house_system: str, astrodata: AstroData) -> list[House]:
#     """
#     Build House objects from raw positions, including retrograde flag.
#     """
#     asc_lon = raw['ascendant']['lon']
#     sign0   = raw['ascendant']['sign_num']

#     # Determine house cusps
#     if house_system == 'equal':
#         cusps = equal_houses(asc_lon)
#     else:
#         flags = swe.FLG_SWIEPH | swe.FLG_SPEED | swe.FLG_SIDEREAL
#         _, ascmc = swe.houses_ex(
#             astrodata.julian_day,
#             astrodata.lat,
#             astrodata.lon,
#             b'B', flags
#         )
#         mc = ascmc[1]
#         cusps = get_house_cusps(
#             house_system, asc_lon,
#             JD=astrodata.julian_day,
#             lat=astrodata.lat,
#             lon=astrodata.lon,
#             mc=mc
#         )

#     # Initialize houses
#     houses = []
#     s = sign0
#     for _ in range(12):
#         h = House(s)
#         houses.append(h)
#         s = 1 if s == 12 else s + 1
#     houses[0].is_asc = True

#     # Assign planets
#     for name, info in raw.items():
#         if name == 'ascendant':
#             continue
#         lon = info['lon']
#         retro = info.get('retro', False)
#         for i in range(12):
#             start, end = cusps[i], cusps[(i+1) % 12]
#             in_house = (start <= lon < end) if end > start else (lon >= start or lon < end)
#             if in_house:
#                 houses[i].planets[name] = {'lon': lon, 'retro': retro}
#                 break
#     return houses


# def _plot_chart(houses: list[House], title: str, description: str, show_retro: bool = False):
#     """
#     Draw the chart with optional retrograde superscript.
#     """
#     fig, ax = plt.subplots(figsize=(6,6))
#     fig.suptitle(title, fontsize=18)
#     ax.set_xlim(0,400); ax.set_ylim(0,300)
#     ax.set_aspect('equal'); ax.axis('off'); ax.invert_yaxis()

#     # draw houses
#     for verts in HOUSE_VERTICES:
#         ax.add_patch(Polygon(verts, closed=True, fill=False, edgecolor='black'))

#     # annotate
#     for i, h in enumerate(houses):
#         cx, cy = CENTERS[i]
#         ax.text(cx, cy, str(h.sign_num), ha='center', va='center', fontsize=16)
#         for j, (pl, dat) in enumerate(h.planets.items()):
#             angle = 2 * math.pi * j / max(len(h.planets),1)
#             x = cx + 15 * math.cos(angle)
#             y = cy + 15 * math.sin(angle)
#             deg = int(dat['lon'] % 30)
#             label = f"{PLANET_ABBR.get(pl,pl[:2])} {deg}°"
#             if show_retro and dat.get('retro', False):
#                 label = f"{label}$^{{Re}}$"
#             ax.text(x, y, label, ha='center', va='center', fontsize=10, weight='bold')

#     fig.text(0.5, 0.02, description, ha='center', fontsize=12)
#     plt.show()


def plot_lagna_chart(
    first_arg,
    house_system: str = 'whole_sign',
    show_retro: bool = False
) -> list[House]:
    """
    Plot D1 chart. Accepts AstroData or precomputed houses.
    """
    if isinstance(first_arg, list) and all(isinstance(h, House) for h in first_arg):
        houses = first_arg
    else:
        astrodata = first_arg
        raw       = astrodata.get_rashi_data()
        houses    = _build_houses(raw, house_system, astrodata)
    _plot_chart(houses, 'Lagna Chart', 'Main Kundali (D1)', show_retro=show_retro)
    return houses


def plot_moon_chart(
    astrodata: AstroData,
    house_system: str = 'whole_sign',
    show_retro: bool = False
) -> list[House]:
    """
    Plot Moon Chart: rotate so Moon is ascendant.
    """
    raw = astrodata.get_rashi_data()
    moon = raw['moon']
    raw_moon = raw.copy()
    raw_moon['ascendant'] = {'lon': moon['lon'], 'sign_num': moon['sign_num'], 'retro': False}
    houses = _build_houses(raw_moon, house_system, astrodata)
    _plot_chart(houses, 'Moon Chart (Chandra Lagna)', 'Mental & emotional insights', show_retro=show_retro)
    return houses


def plot_navamsa_chart(astrodata: AstroData, house_system: str = 'whole_sign', show_retro: bool = False) -> list[House]:
    """Plot D9 (Navamsa): Marriage & Partnerships."""
    raw = astrodata.get_rashi_data()
    raw9 = {k: {'sign_num': int((v['lon']*9)%360/30)+1, 'lon': (v['lon']*9)%360, 'retro': v.get('retro',False)} for k,v in raw.items()}
    houses = _build_houses(raw9, house_system, astrodata)
    _plot_chart(houses, 'Navamsa Chart (D9)', 'Marriage & Partnerships', show_retro=show_retro)
    return houses


def plot_hora_chart(astrodata: AstroData, house_system: str = 'whole_sign', show_retro: bool = False) -> list[House]:
    """Plot D2 (Hora): Prosperity & Wealth."""
    raw = astrodata.get_rashi_data()
    raw2 = {k: {'sign_num': int((v['lon']*2)%360/30)+1, 'lon': (v['lon']*2)%360, 'retro': v.get('retro',False)} for k,v in raw.items()}
    houses = _build_houses(raw2, house_system, astrodata)
    _plot_chart(houses, 'Hora Chart (D2)', 'Prosperity & Wealth', show_retro=show_retro)
    return houses


def plot_drekkana_chart(astrodata: AstroData, house_system: str = 'whole_sign', show_retro: bool = False) -> list[House]:
    """Plot D3 (Drekkana): Siblings & Courage."""
    raw = astrodata.get_rashi_data()
    raw3 = {k: {'sign_num': int((v['lon']*3)%360/30)+1, 'lon': (v['lon']*3)%360, 'retro': v.get('retro',False)} for k,v in raw.items()}
    houses = _build_houses(raw3, house_system, astrodata)
    _plot_chart(houses, 'Drekkana Chart (D3)', 'Siblings & well-being', show_retro=show_retro)
    return houses


def plot_chaturthamsha_chart(astrodata: AstroData, house_system: str = 'whole_sign', show_retro: bool = False) -> list[House]:
    """Plot D4 (Chaturthamsha): Luck & Residence."""
    raw = astrodata.get_rashi_data()
    raw4 = {k: {'sign_num': int((v['lon']*4)%360/30)+1, 'lon': (v['lon']*4)%360, 'retro': v.get('retro',False)} for k,v in raw.items()}
    houses = _build_houses(raw4, house_system, astrodata)
    _plot_chart(houses, 'Chaturthamsha Chart (D4)', 'Luck & Residence', show_retro=show_retro)
    return houses


def plot_saptamamsha_chart(astrodata: AstroData, house_system: str = 'whole_sign', show_retro: bool = False) -> list[House]:
    """Plot D7 (Saptamamsha): Children & Progeny."""
    raw = astrodata.get_rashi_data()
    raw7 = {k: {'sign_num': int((v['lon']*7)%360/30)+1, 'lon': (v['lon']*7)%360, 'retro': v.get('retro',False)} for k,v in raw.items()}
    houses = _build_houses(raw7, house_system, astrodata)
    _plot_chart(houses, 'Saptamamsha Chart (D7)', 'Children & Grandchildren', show_retro=show_retro)
    return houses

def plot_navamsha_chart(astrodata: AstroData, house_system: str = 'whole_sign', show_retro: bool = False) -> list[House]:
    """Plot D9 (Navamsha): Marriage & Partnerships."""
    raw = astrodata.get_rashi_data()
    raw9 = {k: {'sign_num': int((v['lon']*9)%360/30)+1, 'lon': (v['lon']*9)%360, 'retro': v.get('retro',False)} for k,v in raw.items()}
    houses = _build_houses(raw9, house_system, astrodata)
    _plot_chart(houses, 'Navamsha Chart (D9)', 'Marriage & Partnerships', show_retro=show_retro)
    return houses


def plot_dashamamsha_chart(astrodata: AstroData, house_system: str = 'whole_sign', show_retro: bool = False) -> list[House]:
    """Plot D10 (Dashamamsha): Profession & Success."""
    raw = astrodata.get_rashi_data()
    raw10 = {k: {'sign_num': int((v['lon']*10)%360/30)+1, 'lon': (v['lon']*10)%360, 'retro': v.get('retro',False)} for k,v in raw.items()}
    houses = _build_houses(raw10, house_system, astrodata)
    _plot_chart(houses, 'Dashamamsha Chart (D10)', 'Profession & Social Status', show_retro=show_retro)
    return houses


def plot_dwadashamsha_chart(astrodata: AstroData, house_system: str = 'whole_sign', show_retro: bool = False) -> list[House]:
    """Plot D12 (Dwadashamsha): Parents & Heritage."""
    raw = astrodata.get_rashi_data()
    raw12 = {k: {'sign_num': int((v['lon']*12)%360/30)+1, 'lon': (v['lon']*12)%360, 'retro': v.get('retro',False)} for k,v in raw.items()}
    houses = _build_houses(raw12, house_system, astrodata)
    _plot_chart(houses, 'Dwadashamsha Chart (D12)', 'Parents & Ancestry', show_retro=show_retro)
    return houses


def plot_shodashamsha_chart(astrodata: AstroData, house_system: str = 'whole_sign', show_retro: bool = False) -> list[House]:
    """Plot D16 (Shodashamsha): Vehicles & Comforts."""
    raw = astrodata.get_rashi_data()
    raw16 = {k: {'sign_num': int((v['lon']*16)%360/30)+1, 'lon': (v['lon']*16)%360, 'retro': v.get('retro',False)} for k,v in raw.items()}
    houses = _build_houses(raw16, house_system, astrodata)
    _plot_chart(houses, 'Shodashamsha Chart (D16)', 'Vehicles & Daily Comforts', show_retro=show_retro)
    return houses


def plot_vimshamsha_chart(astrodata: AstroData, house_system: str = 'whole_sign', show_retro: bool = False) -> list[House]:
    """Plot D20 (Vimshamsha): Spiritual Undertakings."""
    raw = astrodata.get_rashi_data()
    raw20 = {k: {'sign_num': int((v['lon']*20)%360/30)+1, 'lon': (v['lon']*20)%360, 'retro': v.get('retro',False)} for k,v in raw.items()}
    houses = _build_houses(raw20, house_system, astrodata)
    _plot_chart(houses, 'Vimshamsha Chart (D20)', 'Spiritual Pursuits', show_retro=show_retro)
    return houses


def plot_chatuvimshamsha_chart(astrodata: AstroData, house_system: str = 'whole_sign', show_retro: bool = False) -> list[House]:
    """Plot D24 (Chatuvimshamsha): Education & Learning."""
    raw = astrodata.get_rashi_data()
    raw24 = {k: {'sign_num': int((v['lon']*24)%360/30)+1, 'lon': (v['lon']*24)%360, 'retro': v.get('retro',False)} for k,v in raw.items()}
    houses = _build_houses(raw24, house_system, astrodata)
    _plot_chart(houses, 'Chatuvimshamsha Chart (D24)', 'Education & Intellect', show_retro=show_retro)
    return houses


def plot_saptvimshamsha_chart(astrodata: AstroData, house_system: str = 'whole_sign', show_retro: bool = False) -> list[House]:
    """Plot D27 (Saptvimshamsha): Strengths & Weaknesses."""
    raw = astrodata.get_rashi_data()
    raw27 = {k: {'sign_num': int((v['lon']*27)%360/30)+1, 'lon': (v['lon']*27)%360, 'retro': v.get('retro',False)} for k,v in raw.items()}
    houses = _build_houses(raw27, house_system, astrodata)
    _plot_chart(houses, 'Saptvimshamsha Chart (D27)', 'Innate Strengths & Challenges', show_retro=show_retro)
    return houses


def plot_trishamsha_chart(astrodata: AstroData, house_system: str = 'whole_sign', show_retro: bool = False) -> list[House]:
    """Plot D30 (Trishamsha): Miseries & Troubles."""
    raw = astrodata.get_rashi_data()
    raw30 = {k: {'sign_num': int((v['lon']*30)%360/30)+1, 'lon': (v['lon']*30)%360, 'retro': v.get('retro',False)} for k,v in raw.items()}
    houses = _build_houses(raw30, house_system, astrodata)
    _plot_chart(houses, 'Trishamsha Chart (D30)', 'Miseries & Disasters', show_retro=show_retro)
    return houses


def plot_khavedamsha_chart(astrodata: AstroData, house_system: str = 'whole_sign', show_retro: bool = False) -> list[House]:
    """Plot D40 (Khavedamsha): Auspicious/Inauspicious Events."""
    raw = astrodata.get_rashi_data()
    raw40 = {k: {'sign_num': int((v['lon']*40)%360/30)+1, 'lon': (v['lon']*40)%360, 'retro': v.get('retro',False)} for k,v in raw.items()}
    houses = _build_houses(raw40, house_system, astrodata)
    _plot_chart(houses, 'Khavedamsha Chart (D40)', 'Major Life Events', show_retro=show_retro)
    return houses


def plot_akshavedamsha_chart(astrodata: AstroData, house_system: str = 'whole_sign', show_retro: bool = False) -> list[House]:
    """Plot D45 (Akshavedamsha): Overall Character."""
    raw = astrodata.get_rashi_data()
    raw45 = {k: {'sign_num': int((v['lon']*45)%360/30)+1, 'lon': (v['lon']*45)%360, 'retro': v.get('retro',False)} for k,v in raw.items()}
    houses = _build_houses(raw45, house_system, astrodata)
    _plot_chart(houses, 'Akshavedamsha Chart (D45)', 'General Conduct & Life Themes', show_retro=show_retro)
    return houses


def plot_shashtiamsha_chart(astrodata: AstroData, house_system: str = 'whole_sign', show_retro: bool = False) -> list[House]:
    """Plot D60 (Shashtiamsha): Karma & Destiny."""
    raw = astrodata.get_rashi_data()
    raw60 = {k: {'sign_num': int((v['lon']*60)%360/30)+1, 'lon': (v['lon']*60)%360, 'retro': v.get('retro',False)} for k,v in raw.items()}
    houses = _build_houses(raw60, house_system, astrodata)
    _plot_chart(houses, 'Shashtiamsha Chart (D60)', 'Past-life Karma & Destiny', show_retro=show_retro)
    return houses


# plot_lagna_chart, plot_moon_chart, plot_hora_chart,
# plot_drekkana_chart, plot_chaturthamsha_chart, plot_saptamamsha_chart, plot_dashamamsha_chart,
# plot_dwadashamsha_chart, plot_shodashamsha_chart, plot_vimshamsha_chart, plot_shashtiamsha_chart,
# plot_chatuvimshamsha_chart, plot_saptvimshamsha_chart, plot_trishamsha_chart, plot_khavedamsha_chart,
# plot_akshavedamsha_chart, plot_shashtiamsha_chart
