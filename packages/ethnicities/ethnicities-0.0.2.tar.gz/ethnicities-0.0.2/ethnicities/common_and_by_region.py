from .common import COMMON
from .by_region import BY_REGION

# Intersection of common and region-specific lists
COMMON_AND_BY_REGION = {
    region: [eth for eth in group if eth in COMMON]
    for region, group in BY_REGION.items()
}
