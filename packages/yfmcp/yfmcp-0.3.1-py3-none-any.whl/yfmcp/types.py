from typing import Literal

SearchType = Literal[
    "all",
    "quotes",
    "news",
]


TopType = Literal[
    "top_etfs",
    "top_mutual_funds",
    "top_companies",
    "top_growth_companies",
    "top_performing_companies",
]


Sector = Literal[
    "basic-materials",
    "communication-services",
    "consumer-cyclical",
    "consumer-defensive",
    "energy",
    "financial-services",
    "healthcare",
    "industrials",
    "real-estate",
    "technology",
    "utilities",
]
