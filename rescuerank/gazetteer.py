"""Tiny demo gazetteer of Chennai-area localities.

Coordinates are APPROXIMATE area centres, good enough for a demo map.
A production build should replace this with OpenStreetMap Nominatim plus a
local landmark list (see the roadmap in the README).
"""

# canonical name: (lat, lon, [aliases, lower-case; Tamil script allowed])
PLACES = {
    "Velachery": (12.9815, 80.2180, ["velachery", "velacheri", "vilachery", "வேளச்சேரி"]),
    "Pallikaranai": (12.9340, 80.2130, ["pallikaranai", "pallikarani", "பள்ளிக்கரணை"]),
    "Manali New Town": (13.1850, 80.2650, ["manali new town"]),
    "Manali": (13.1667, 80.2667, ["manali"]),
    "Tambaram": (12.9249, 80.1000, ["tambaram", "thambaram", "தாம்பரம்"]),
    "Adyar": (13.0012, 80.2565, ["adyar", "அடையாறு"]),
    "Mudichur": (12.9010, 80.0720, ["mudichur", "முடிச்சூர்"]),
    "Sholinganallur": (12.9010, 80.2279, ["sholinganallur", "shozhinganallur"]),
    "Besant Nagar": (13.0003, 80.2667, ["besant nagar", "besantnagar"]),
    "Mylapore": (13.0368, 80.2676, ["mylapore", "mylai"]),
    "T Nagar": (13.0418, 80.2341, ["t nagar", "t.nagar", "thyagaraya nagar"]),
    "Saidapet": (13.0213, 80.2231, ["saidapet"]),
    "Perungudi": (12.9650, 80.2461, ["perungudi"]),
    "Washermanpet": (13.1143, 80.2890, ["washermanpet"]),
}
