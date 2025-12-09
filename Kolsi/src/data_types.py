from dataclasses import dataclass

@dataclass
class ArcData:
    source: str
    target: str
    capacity: float
    var_cost: float
    fixed_cost: float

@dataclass
class CommodityData:
    cid: str
    origin: str
    destination: str
    quantity: float
    quality_name: str
    color: str = "#000000" # Default color for visualization