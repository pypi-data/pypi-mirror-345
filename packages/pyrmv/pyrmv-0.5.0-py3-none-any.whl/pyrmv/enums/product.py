from enum import auto

from .auto_name import AutoNameProduct


class Product(AutoNameProduct):
    """Enumeration used to declare types of transport."""

    ICE = auto()
    "The Intercity Express (commonly known as ICE) is a system of high-speed trains predominantly running in Germany."

    IC = auto()
    "InterCity (commonly abbreviated IC on timetables and tickets) is the classification applied to certain long-distance passenger train services in Europe. Such trains (in contrast to regional, local, or commuter trains) generally call at major stations only."

    EC = auto()
    'EuroCity, abbreviated as EC, is a cross-border train category within the European inter-city rail network. In contrast to trains allocated to the lower-level "IC" (InterCity) category, EC trains are international services that meet 20 criteria covering comfort, speed, food service, and cleanliness.'

    R = auto()
    "Regional rail, also known as local trains and stopping trains, are passenger rail services that operate between towns and cities. These trains operate with more stops over shorter distances than inter-city rail, but fewer stops and faster service than commuter rail."

    RB = auto()
    "The Regionalbahn (lit. Regional train; abbreviated RB) is a type of local passenger train (stopping train) in Germany. It is similar to the Regionalzug (R) and Regio (R) train categories in neighboring Austria and Switzerland, respectively."

    RE = auto()
    "In Germany, Luxembourg and Austria, the Regional-Express (RE, or in Austria: REX) is a type of regional train. It is similar to a semi-fast train, with average speed at about 70-90 km/h (top speed often 160 km/h) as it calls at fewer stations than Regionalbahn or S-Bahn trains, but stops more often than InterCity services."

    SBAHN = auto()
    "The S-Bahn is the name of hybrid urban-suburban rail systems serving a metropolitan region in German-speaking countries. Some of the larger S-Bahn systems provide service similar to rapid transit systems, while smaller ones often resemble commuter or even regional rail. The term derives from Schnellbahn, Stadtbahn or Stadtschnellbahn."

    UBAHN = auto()
    "A U-Bahn (short for subway, underground express train or metropolitan) is a usually underground, rail-bound means of transport for urban public transport (ÖPNV, city transport)."

    TRAM = auto()
    "A tram (also known as a streetcar or trolley in North America) is a rail vehicle that travels on tramway tracks on public urban streets; some include segments on segregated right-of-way."

    BUS = auto()
    "A bus (contracted from omnibus, with variants multibus, motorbus, autobus, etc.) is a road vehicle that carries significantly more passengers than an average car or van."

    BUS2 = auto()
    "Also a bus, but now idea why it exists anyway."

    FERRY = auto()
    "A ferry is a ship used to carry passengers, and sometimes vehicles and cargo, across a body of water."

    TAXI = auto()
    "A taxi, also known as a taxicab or simply a cab, is a type of vehicle for hire with a driver, used by a single passenger or small group of passengers, often for a non-shared ride."

    BAHN = auto()
    "Rail transport (also known as train transport) is a means of transport that transfers passengers and goods on wheeled vehicles running on rails, which are located on tracks. In contrast to road transport, where the vehicles run on a prepared flat surface, rail vehicles (rolling stock) are directionally guided by the tracks on which they run."
