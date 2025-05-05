import math
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import swisseph as swe

from .astro_chart import House
from .astro_data import AstroData
from .houses import equal_houses, get_house_cusps

# Layout definitions
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
CENTERS = [
    (190,75),(100,30),(30,75),(90,150),
    (30,225),(90,278),(190,225),(290,278),
    (360,225),(290,150),(360,75),(290,30)
]
PLANET_ABBR = {
    'sun':'Su','moon':'Mo','mercury':'Me','venus':'Ve',
    'mars':'Ma','jupiter':'Ju','saturn':'Sa','uranus':'Ur',
    'neptune':'Ne','pluto':'Pl','north_node':'Ra','south_node':'Ke'
}


def _build_houses(raw: dict, house_system: str, astrodata: AstroData) -> list[House]:
    """
    Build House objects from raw positions, including retrograde flag.
    """
    asc_lon = raw['ascendant']['lon']
    sign0   = raw['ascendant']['sign_num']

    # Determine house cusps
    if house_system == 'equal':
        cusps = equal_houses(asc_lon)
    else:
        flags = swe.FLG_SWIEPH | swe.FLG_SPEED | swe.FLG_SIDEREAL
        _, ascmc = swe.houses_ex(
            astrodata.julian_day,
            astrodata.lat,
            astrodata.lon,
            b'B', flags
        )
        mc = ascmc[1]
        cusps = get_house_cusps(
            house_system, asc_lon,
            JD=astrodata.julian_day,
            lat=astrodata.lat,
            lon=astrodata.lon,
            mc=mc
        )

    # Initialize houses
    houses = []
    s = sign0
    for _ in range(12):
        h = House(s)
        houses.append(h)
        s = 1 if s == 12 else s + 1
    houses[0].is_asc = True

    # Assign planets
    for name, info in raw.items():
        if name == 'ascendant':
            continue
        lon = info['lon']
        retro = info.get('retro', False)
        for i in range(12):
            start, end = cusps[i], cusps[(i+1) % 12]
            in_house = (start <= lon < end) if end > start else (lon >= start or lon < end)
            if in_house:
                houses[i].planets[name] = {'lon': lon, 'retro': retro}
                break
    return houses


def _plot_chart(houses: list[House], title: str, description: str, show_retro: bool = False):
    """
    Draw the chart with optional retrograde superscript.
    """
    fig, ax = plt.subplots(figsize=(6,6))
    fig.suptitle(title, fontsize=18)
    ax.set_xlim(0,400); ax.set_ylim(0,300)
    ax.set_aspect('equal'); ax.axis('off'); ax.invert_yaxis()

    # draw houses
    for verts in HOUSE_VERTICES:
        ax.add_patch(Polygon(verts, closed=True, fill=False, edgecolor='black'))

    # annotate
    for i, h in enumerate(houses):
        cx, cy = CENTERS[i]
        ax.text(cx, cy, str(h.sign_num), ha='center', va='center', fontsize=16)
        for j, (pl, dat) in enumerate(h.planets.items()):
            angle = 2 * math.pi * j / max(len(h.planets),1)
            x = cx + 15 * math.cos(angle)
            y = cy + 15 * math.sin(angle)
            deg = int(dat['lon'] % 30)
            label = f"{PLANET_ABBR.get(pl,pl[:2])} {deg}°"
            if show_retro and dat.get('retro', False):
                label = f"{label}$^{{Re}}$"
            ax.text(x, y, label, ha='center', va='center', fontsize=10, weight='bold')

    fig.text(0.5, 0.02, description, ha='center', fontsize=12)
    plt.show()


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


# # astrokundali/plotter.py
# import math
# import matplotlib.pyplot as plt
# from matplotlib.patches import Polygon
# import swisseph as swe
# from .astro_chart import House
# from .astro_data import AstroData
# from .houses import equal_houses, get_house_cusps

# # Layout definitions
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
# PLANET_ABBR = {
#     'sun':'Su','moon':'Mo','mercury':'Me','venus':'Ve',
#     'mars':'Ma','jupiter':'Ju','saturn':'Sa','uranus':'Ur',
#     'neptune':'Ne','pluto':'Pl','north_node':'Ra','south_node':'Ke'
# }


# def _build_houses(raw, house_system, astrodata):
#     """
#     Internal: build House objects from raw rashi or divisional data.
#     """
#     asc_lon = raw['ascendant']['lon']
#     sign0   = raw['ascendant']['sign_num']
#     # Determine cusps
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
#     houses = []
#     s = sign0
#     for _ in range(12):
#         h = House(s)
#         houses.append(h)
#         s = 1 if s == 12 else s + 1
#     houses[0].is_asc = True
#     for name, info in raw.items():
#         if name == 'ascendant': continue
#         lon = info['lon']
#         for i in range(12):
#             a, b = cusps[i], cusps[(i+1)%12]
#             in_house = (a <= lon < b) if b > a else (lon >= a or lon < b)
#             if in_house:
#                 houses[i].planets[name] = lon
#                 break
#     return houses


# def _plot_chart(houses, title, description):
#     """
#     Helper to render a chart with title and description.
#     """
#     fig, ax = plt.subplots(figsize=(6,6))
#     fig.suptitle(title, fontsize=18)
#     ax.set_xlim(0,400); ax.set_ylim(0,300)
#     ax.set_aspect('equal'); ax.axis('off'); ax.invert_yaxis()
#     for verts in HOUSE_VERTICES:
#         ax.add_patch(Polygon(verts, closed=True, fill=False, edgecolor='black'))
#     for i, h in enumerate(houses):
#         cx, cy = CENTERS[i]
#         ax.text(cx, cy, str(h.sign_num), ha='center', va='center', fontsize=16)
#         for j, (pl, lon) in enumerate(h.planets.items()):
#             θ = 2*math.pi*j/max(len(h.planets),1)
#             x = cx + 15*math.cos(θ); y = cy + 15*math.sin(θ)
#             deg = int(lon % 30)
#             ax.text(x, y, f"{PLANET_ABBR.get(pl,pl[:2])} {deg}°",
#                     ha='center', va='center', fontsize=10, weight='bold')
#     fig.text(0.5, 0.02, description, ha='center', fontsize=12)
#     plt.show()


# def plot_lagna_chart(astrodata: AstroData, house_system: str = 'whole_sign'):
#     raw = astrodata.get_rashi_data()
#     houses = _build_houses(raw, house_system, astrodata)
#     plot_lagna = 'Main Kundali'
#     _plot_chart(houses, 'Lagna Chart', plot_lagna)
#     return houses


# def plot_moon_chart(astrodata: AstroData, house_system: str = 'whole_sign'):
#     # Moon Chart (D1 with Moon as ascendant)
#     chart = AstroChart(astrodata, house_system)
#     houses = chart.moonChart()  # existing moonChart method
#     _plot_chart(houses, 'Chandra Chart - Moon Chart', 'Chandra/Moon-based chart')
#     return houses


# def plot_hora_chart(astrodata: AstroData, house_system: str = 'whole_sign'):
#     # Hora Chart (D2 with Lagna as ascendant)
#     raw = astrodata.get_rashi_data()
#     raw2 = {k: {'sign_num': int((v['lon']*2)%360/30)+1, 'lon': (v['lon']*2)%360} for k,v in raw.items()}
#     houses = _build_houses(raw2, house_system, astrodata)
#     _plot_chart(houses, 'Hora Chart', 'Prosperity, Wealth')
#     return houses


# def plot_drekkana_chart(astrodata: AstroData, house_system: str = 'whole_sign'):
#     # Drekkana Chart (D3 with Lagna as ascendant)
#     raw = astrodata.get_rashi_data()
#     raw3 = {k: {'sign_num': int((v['lon']*3)%360/30)+1, 'lon': (v['lon']*3)%360} for k,v in raw.items()}
#     houses = _build_houses(raw3, house_system, astrodata)
#     _plot_chart(houses, 'Drekkana Chart', 'Drekkana Chart: Siblings, their lives and well being')
#     return houses


# def plot_chaturthamsha_chart(astrodata: AstroData, house_system: str = 'whole_sign'):
#     # Chaturthamsha Chart (D4 with Lagna as ascendant)
#     raw = astrodata.get_rashi_data()
#     raw4 = {k: {'sign_num': int((v['lon']*4)%360/30)+1, 'lon': (v['lon']*4)%360} for k,v in raw.items()}
#     houses = _build_houses(raw4, house_system, astrodata)
#     _plot_chart(houses, 'Chaturthamsha Chart', 'Chaturthamsha Chart: Luck and Residence')
#     return houses


# def plot_saptamamsha_chart(astrodata: AstroData, house_system: str = 'whole_sign'):
#     # Saptamamsha Chart (D7 with Lagna as ascendant)
#     raw = astrodata.get_rashi_data()
#     raw7 = {k: {'sign_num': int((v['lon']*7)%360/30)+1, 'lon': (v['lon']*7)%360} for k,v in raw.items()}
#     houses = _build_houses(raw7, house_system, astrodata)
#     _plot_chart(houses, 'Saptamamsha Chart', 'Saptamamsha Chart: Children, Grand Children')
#     return houses


# def plot_dashamamsha_chart(astrodata: AstroData, house_system: str = 'whole_sign'):
#     # Dashamamsha Chart (D10 with Lagna as ascendant)
#     raw = astrodata.get_rashi_data()
#     raw10 = {k: {'sign_num': int((v['lon']*10)%360/30)+1, 'lon': (v['lon']*10)%360} for k,v in raw.items()}
#     houses = _build_houses(raw10, house_system, astrodata)
#     _plot_chart(houses, 'Dashamamsha Chart', 'Dashamamsha Chart: Profession, Success of all matters')
#     return houses


# def plot_dwadashamsha_chart(astrodata: AstroData, house_system: str = 'whole_sign'):
#     # Dwadashamsha Chart (D12 with Lagna as ascendant)
#     raw = astrodata.get_rashi_data()
#     raw12 = {k: {'sign_num': int((v['lon']*12)%360/30)+1, 'lon': (v['lon']*12)%360} for k,v in raw.items()}
#     houses = _build_houses(raw12, house_system, astrodata)
#     _plot_chart(houses, 'Dwadashamsha Chart', 'Dwadashamsha Chart: Parents, their lives and well being')
#     return houses


# def plot_shodashamsha_chart(astrodata: AstroData, house_system: str = 'whole_sign'):
#     # Shodashamsha Chart (D16 with Lagna as ascendant)
#     raw = astrodata.get_rashi_data()
#     raw16 = {k: {'sign_num': int((v['lon']*16)%360/30)+1, 'lon': (v['lon']*16)%360} for k,v in raw.items()}
#     houses = _build_houses(raw16, house_system, astrodata)
#     _plot_chart(houses, 'Shodashamsha Chart', 'Shodashamsha Chart: Ones relationship to Vehicles')
#     return houses


# def plot_vimshamsha_chart(astrodata: AstroData, house_system: str = 'whole_sign'):
#     # Vimshamsha Chart (D20 with Lagna as ascendant)
#     raw = astrodata.get_rashi_data()
#     raw20 = {k: {'sign_num': int((v['lon']*20)%360/30)+1, 'lon': (v['lon']*20)%360} for k,v in raw.items()}
#     houses = _build_houses(raw20, house_system, astrodata)
#     _plot_chart(houses, 'Vimshamsha Chart', 'Vimshamsha Chart: Spiritual undertakings')
#     return houses


# def plot_chatuvimshamsha_chart(astrodata: AstroData, house_system: str = 'whole_sign'):
#     # Chatuvimshamsha Chart (D24 with Lagna as ascendant)
#     raw = astrodata.get_rashi_data()
#     raw24 = {k: {'sign_num': int((v['lon']*24)%360/30)+1, 'lon': (v['lon']*24)%360} for k,v in raw.items()}
#     houses = _build_houses(raw24, house_system, astrodata)
#     _plot_chart(houses, 'Chatuvimshamsha Chart', 'Chatuvimshamsha Chart: Education, Learning, Brains')
#     return houses


# def plot_saptvimshamsha_chart(astrodata: AstroData, house_system: str = 'whole_sign'):
#     # Saptvimshamsha Chart (D27 with Lagna as ascendant)
#     raw = astrodata.get_rashi_data()
#     raw27 = {k: {'sign_num': int((v['lon']*27)%360/30)+1, 'lon': (v['lon']*27)%360} for k,v in raw.items()}
#     houses = _build_houses(raw27, house_system, astrodata)
#     _plot_chart(houses, 'Saptvimshamsha Chart', 'Saptvimshamsha Chart: Strengths and weaknesses')
#     return houses


# def plot_trishamsha_chart(astrodata: AstroData, house_system: str = 'whole_sign'):
#     # Trishamsha Chart (D30 with Lagna as ascendant)
#     raw = astrodata.get_rashi_data()
#     raw30 = {k: {'sign_num': int((v['lon']*30)%360/30)+1, 'lon': (v['lon']*30)%360} for k,v in raw.items()}
#     houses = _build_houses(raw30, house_system, astrodata)
#     _plot_chart(houses, 'Trishamsha Chart', 'Trishamsha Chart: Miseries, Troubles, Disasters')
#     return houses


# def plot_khavedamsha_chart(astrodata: AstroData, house_system: str = 'whole_sign'):
#     # Khavedamsha Chart (D40 with Lagna as ascendant)
#     raw = astrodata.get_rashi_data()
#     raw40 = {k: {'sign_num': int((v['lon']*40)%360/30)+1, 'lon': (v['lon']*40)%360} for k,v in raw.items()}
#     houses = _build_houses(raw40, house_system, astrodata)
#     _plot_chart(houses, 'Khavedamsha Chart', 'Khavedamsha Chart: Auspicious/Inauspicious Events')
#     return houses


# def plot_akshavedamsha_chart(astrodata: AstroData, house_system: str = 'whole_sign'):
#     # Akshavedamsha Chart (D45 with Lagna as ascendant)
#     raw = astrodata.get_rashi_data()
#     raw45 = {k: {'sign_num': int((v['lon']*45)%360/30)+1, 'lon': (v['lon']*45)%360} for k,v in raw.items()}
#     houses = _build_houses(raw45, house_system, astrodata)
#     _plot_chart(houses, 'Akshavedamsha Chart', 'Akshavedamsha Chart: All things—Overall')
#     return houses


# def plot_shashtiamsha_chart(astrodata: AstroData, house_system: str = 'whole_sign'):
#     # Shashtiamsha Chart (D60 with Lagna as ascendant)
#     raw = astrodata.get_rashi_data()
#     raw60 = {k: {'sign_num': int((v['lon']*60)%360/30)+1, 'lon': (v['lon']*60)%360} for k,v in raw.items()}
#     houses = _build_houses(raw60, house_system, astrodata)
#     _plot_chart(houses, 'Shashtiamsha Chart', 'Shashtiamsha Chart: All things—Overall')
#     return houses
# plot_lagna_chart, plot_moon_chart, plot_hora_chart,
# plot_drekkana_chart, plot_chaturthamsha_chart, plot_saptamamsha_chart, plot_dashamamsha_chart,
# plot_dwadashamsha_chart, plot_shodashamsha_chart, plot_vimshamsha_chart, plot_shashtiamsha_chart,
# plot_chatuvimshamsha_chart, plot_saptvimshamsha_chart, plot_trishamsha_chart, plot_khavedamsha_chart,
# plot_akshavedamsha_chart, plot_shashtiamsha_chart
# D1 = Moon = 1
# D2 = Hora = 2
# D3 = Drekkana = 3
# D4 = Chaturthamsha = 4
# D5 = Panchamsha = 5