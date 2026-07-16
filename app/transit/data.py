from dataclasses import dataclass


@dataclass(frozen=True)
class Zone:
    name: str
    keywords: tuple[str, ...]
    mode_sequence: tuple[str, ...]
    base_minutes: int
    gate: str


@dataclass(frozen=True)
class City:
    city_id: str
    label: str
    stadium: str
    parking_policy: str
    zones: tuple[Zone, ...]
    disruption: str | None


CITIES: dict[str, City] = {
    "nynj": City(
        city_id="nynj",
        label="New York / New Jersey",
        stadium="MetLife Stadium",
        parking_policy="No general spectator parking; NJ Transit rail and official shuttles only.",
        zones=(
            Zone(
                "Manhattan / Penn Station", ("manhattan", "penn", "midtown"),
                ("NJ Transit rail", "stadium shuttle"), 55, "East",
            ),
            Zone("Secaucus Junction area", ("secaucus",), ("NJ Transit rail",), 25, "North"),
            Zone("Newark", ("newark",), ("NJ Transit rail", "stadium shuttle"), 40, "West"),
        ),
        disruption=None,
    ),
    "dallas": City(
        city_id="dallas",
        label="Dallas",
        stadium="AT&T Stadium",
        parking_policy="Charter buses run from Trinity Railway Express (TRE) stations to stadium hubs.",
        zones=(
            Zone("Downtown Dallas", ("downtown", "dallas"), ("TRE rail", "charter bus"), 45, "South"),
            Zone("Victory Station area", ("victory",), ("TRE rail", "charter bus"), 35, "South"),
            Zone("CentrePort / DFW Airport", ("dfw", "airport", "centreport"), ("TRE rail", "charter bus"), 30, "West"),
        ),
        disruption="TRE midday service reduced 20%; add 10 minutes buffer.",
    ),
    "miami": City(
        city_id="miami",
        label="Miami",
        stadium="Hard Rock Stadium",
        parking_policy="Metrorail to stadium shuttle recommended over driving due to limited on-site parking.",
        zones=(
            Zone("Downtown Miami", ("downtown", "miami", "brickell"), ("Metrorail", "stadium shuttle"), 50, "North"),
            Zone("Miami Gardens area", ("gardens",), ("stadium shuttle",), 15, "North"),
            Zone("Fort Lauderdale", ("lauderdale",), ("Tri-Rail", "stadium shuttle"), 60, "East"),
        ),
        disruption=None,
    ),
    "losangeles": City(
        city_id="losangeles",
        label="Los Angeles",
        stadium="SoFi Stadium",
        parking_policy="LA Metro C Line to Inglewood station; limited on-site parking requires pre-purchase.",
        zones=(
            Zone(
                "Downtown LA / Union Station", ("downtown", "union", "dtla"),
                ("Metro C Line", "stadium shuttle"), 45, "East",
            ),
            Zone("LAX / Airport area", ("lax", "airport"), ("shuttle bus",), 20, "West"),
            Zone(
                "Santa Monica / Westside", ("santa monica", "westside"),
                ("Metro E Line", "stadium shuttle"), 50, "North",
            ),
        ),
        disruption=None,
    ),
    "houston": City(
        city_id="houston",
        label="Houston",
        stadium="NRG Stadium",
        parking_policy="METRORail Red Line to NRG Park/Fannin South; park-and-ride lots available.",
        zones=(
            Zone("Downtown Houston", ("downtown", "houston"), ("METRORail", "stadium shuttle"), 30, "North"),
            Zone("Galleria / Uptown", ("galleria", "uptown"), ("shuttle bus",), 25, "East"),
            Zone("IAH Airport area", ("iah", "airport", "bush"), ("shuttle bus",), 55, "North"),
        ),
        disruption=None,
    ),
    "seattle": City(
        city_id="seattle",
        label="Seattle",
        stadium="Lumen Field",
        parking_policy="Light rail and Sound Transit recommended; stadium is in the SoDo district near transit hubs.",
        zones=(
            Zone("Downtown Seattle", ("downtown", "seattle", "pike"), ("Link light rail",), 10, "North"),
            Zone("Sea-Tac Airport area", ("seatac", "airport"), ("Link light rail",), 35, "South"),
            Zone("University District", ("university", "u-district"), ("Link light rail",), 20, "North"),
        ),
        disruption=None,
    ),
    "philadelphia": City(
        city_id="philadelphia",
        label="Philadelphia",
        stadium="Lincoln Financial Field",
        parking_policy="SEPTA Broad Street Line to NRG station; limited parking in the Sports Complex.",
        zones=(
            Zone(
                "Center City / 30th St Station", ("center", "downtown", "30th"),
                ("SEPTA subway", "stadium shuttle"), 25, "East",
            ),
            Zone("Philadelphia Airport", ("airport", "phl"), ("SEPTA regional rail", "shuttle bus"), 30, "South"),
            Zone("University City", ("university", "drexel", "penn"), ("SEPTA subway",), 20, "East"),
        ),
        disruption=None,
    ),
    "mexico_city": City(
        city_id="mexico_city",
        label="Mexico City",
        stadium="Estadio Azteca",
        parking_policy=(
            "Metro Line 2 to Tasqueña then tram; ride-share pick-up/drop-off zones around Calzada de Tlalpan."
        ),
        zones=(
            Zone("Centro Histórico / Zócalo", ("centro", "zocalo", "downtown"), ("Metro Line 2", "tram"), 45, "North"),
            Zone("Polanco / Chapultepec", ("polanco", "chapultepec"), ("Metro", "shuttle bus"), 40, "West"),
            Zone("AICM Airport", ("airport", "aicm", "aeropuerto"), ("Metro", "shuttle bus"), 50, "East"),
        ),
        disruption=None,
    ),
    "guadalajara": City(
        city_id="guadalajara",
        label="Guadalajara",
        stadium="Estadio Akron",
        parking_policy="Macrobús Line 1 to Zapopan hub, then shuttle; parking outside the exclusion zone.",
        zones=(
            Zone("Centro Histórico", ("centro", "downtown"), ("Macrobús", "shuttle bus"), 35, "South"),
            Zone("Zona Rosa / Chapultepec", ("zona rosa", "chapultepec"), ("shuttle bus",), 25, "South"),
            Zone("GDL Airport", ("airport", "gdl", "aeropuerto"), ("shuttle bus",), 40, "East"),
        ),
        disruption=None,
    ),
    "monterrey": City(
        city_id="monterrey",
        label="Monterrey",
        stadium="Estadio BBVA",
        parking_policy="Metrorrey Line 1 to Guadalupe station; stadium shuttle from designated hubs.",
        zones=(
            Zone("Centro / Macroplaza", ("centro", "downtown", "macroplaza"), ("Metrorrey", "shuttle bus"), 30, "West"),
            Zone("San Pedro Garza García", ("san pedro", "garza"), ("shuttle bus",), 25, "West"),
            Zone("MTY Airport", ("airport", "mty", "aeropuerto"), ("shuttle bus",), 35, "North"),
        ),
        disruption=None,
    ),
    "toronto": City(
        city_id="toronto",
        label="Toronto",
        stadium="BMO Field",
        parking_policy="TTC streetcar 509/511 from Union Station; GO Transit from surrounding cities.",
        zones=(
            Zone("Union Station / Downtown", ("downtown", "union", "toronto"), ("TTC streetcar",), 15, "East"),
            Zone(
                "Pearson Airport area", ("pearson", "airport", "yyz"),
                ("UP Express", "TTC subway", "streetcar"), 50, "East",
            ),
            Zone("Midtown / Yonge-Bloor", ("midtown", "yonge", "bloor"), ("TTC subway", "streetcar"), 25, "East"),
        ),
        disruption=None,
    ),
    "vancouver": City(
        city_id="vancouver",
        label="Vancouver",
        stadium="BC Place",
        parking_policy="SkyTrain Expo/Canada Line to Stadium-Chinatown station; street parking very limited.",
        zones=(
            Zone("Downtown Vancouver", ("downtown", "vancouver", "gastown"), ("SkyTrain",), 8, "North"),
            Zone("YVR Airport / Richmond", ("yvr", "airport", "richmond"), ("Canada Line",), 30, "South"),
            Zone("Burnaby / Metrotown", ("burnaby", "metrotown"), ("Expo Line",), 20, "East"),
        ),
        disruption=None,
    ),
    "san_francisco": City(
        city_id="san_francisco",
        label="San Francisco Bay Area",
        stadium="Levi's Stadium",
        parking_policy="VTA light rail to Great America station; Caltrain + shuttle from San Francisco.",
        zones=(
            Zone(
                "Downtown San Francisco", ("san francisco", "downtown", "embarcadero"),
                ("Caltrain", "VTA light rail"), 60, "North",
            ),
            Zone("San Jose / Downtown", ("san jose",), ("VTA light rail",), 20, "South"),
            Zone("SFO Airport", ("sfo", "airport"), ("Caltrain", "VTA light rail"), 55, "North"),
        ),
        disruption=None,
    ),
    "kansas_city": City(
        city_id="kansas_city",
        label="Kansas City",
        stadium="Arrowhead Stadium",
        parking_policy="Dedicated shuttle buses from downtown and Park-and-Ride lots; tailgating lots require pass.",
        zones=(
            Zone("Downtown KC / Union Station", ("downtown", "kansas", "union"), ("shuttle bus",), 25, "West"),
            Zone("Country Club Plaza", ("plaza",), ("shuttle bus",), 20, "West"),
            Zone("KCI Airport", ("kci", "airport"), ("shuttle bus",), 40, "North"),
        ),
        disruption=None,
    ),
    "atlanta": City(
        city_id="atlanta",
        label="Atlanta",
        stadium="Mercedes-Benz Stadium",
        parking_policy="MARTA rail to Vine City or GWCC/CNN Center stations; stadium is transit-adjacent.",
        zones=(
            Zone("Downtown Atlanta / Five Points", ("downtown", "atlanta", "five points"), ("MARTA rail",), 10, "East"),
            Zone("Midtown / Peachtree", ("midtown", "peachtree"), ("MARTA rail",), 15, "East"),
            Zone("Hartsfield-Jackson Airport", ("airport", "hartsfield", "atl"), ("MARTA rail",), 30, "South"),
        ),
        disruption=None,
    ),
    "boston": City(
        city_id="boston",
        label="Boston",
        stadium="Gillette Stadium",
        parking_policy="MBTA Commuter Rail to Foxborough event service; pre-paid parking passes for on-site lots.",
        zones=(
            Zone(
                "Downtown Boston / South Station", ("downtown", "boston", "south station"),
                ("MBTA commuter rail",), 50, "North",
            ),
            Zone("Back Bay / Copley", ("back bay", "copley"), ("MBTA commuter rail",), 55, "North"),
            Zone("Providence", ("providence",), ("MBTA commuter rail",), 35, "South"),
        ),
        disruption=None,
    ),
}


def match_zone(city: City, free_text: str) -> Zone:
    text = free_text.lower()
    for zone in city.zones:
        if any(keyword in text for keyword in zone.keywords):
            return zone
    return city.zones[0]
