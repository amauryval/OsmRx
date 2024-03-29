from enum import Enum


class OsmFeatureModes(Enum):
    vehicle = "vehicle"
    pedestrian = "pedestrian"
    poi = "poi"


class OsmFeatureTypes(Enum):
    way = "way"
    node = "node"


# overpass queries
osm_queries: dict = {
    OsmFeatureModes.vehicle: {
        "query": 'way["highway"~"^('
        "motorway|"
        "trunk|"
        "primary|"
        "secondary|"
        "tertiary|"
        "unclassified|"
        "residential|"
        "pedestrian|"
        "motorway_link|"
        "trunk_link|"
        "primary_link|"
        "secondary_link|"
        "tertiary_link|"
        "living_street|"
        "service|"
        "track|"
        "bus_guideway|"
        "escape|"
        "raceway|"
        "road|"
        "bridleway|"
        "corridor|"
        "path"
        ')$"]["area"!~"."]({geo_filter});',
        "directed_graph": True,
        "feature_type": OsmFeatureTypes.way
    },
    OsmFeatureModes.pedestrian: {
        "query": 'way["highway"~"^('
        "motorway|"
        "cycleway|"
        "primary|"
        "secondary|"
        "tertiary|"
        "unclassified|"
        "residential|"
        "pedestrian|"
        "motorway_link|"
        "primary_link|"
        "secondary_link|"
        "tertiary_link|"
        "living_street|"
        "service|"
        "track|"
        "bus_guideway|"
        "escape|"
        "road|"
        "footway|"
        "bridleway|"
        "steps|"
        "corridor|"
        "path"
        ')$"]["area"!~"."]({geo_filter});',
        "directed_graph": False,
        "feature_type": OsmFeatureTypes.way
    },
    OsmFeatureModes.poi: {
        "query": 'node[~"^(amenity)$"~"('
            "bar|biergarten|cafe|drinking_water|fast_food|ice_cream|food_court|pub|restaurant|college|driving_school"
            "|kindergarten|language_school|library|music_school|school|sport_school|toy_library|university|"
            "bicycle_parking|bicycle_repair_station|bicycle_rental|boat_rental|boat_sharing|"
            "bus_station|car_rental|car_sharing|car_wash|vehicle_inspection|charging_station|ferry_terminal|fuel|taxi|"
            "atm|bank|bureau_de_change|baby_hatch|clinic|doctors|dentist|hospital|nursing_home|pharmacy|social_facility"
            "|veterinary|arts_centre|brothel|casino|cinema|community_centre|gambling|nightclub|planetarium|"
            "public_bookcase|social_centre|stripclub|studio|bicycle_parking|bicycle_rental|swingerclub|theatre"
            "|animal_boarding|animal_shelter|conference_centre|courthouse|"
            "crematorium|dive_centre|embassy|fire_station|give_box|internet_cafe|monastery|photo_booth|place_of_worship"
            "|police|post_box|post_depot|post_office|prison|public_bath|ranger_station|recycling|refugee_site|	"
            "sanitary_dump_station|shelter|shower|telephone|toilets|townhall|vending_machine|waste_basket"
            "|waste_disposal|waste_transfer_station|watering_place|water_point"
            ')"]({geo_filter});'
            'node[~"^(shop)$"~"."]({geo_filter});',
        "feature_type": OsmFeatureTypes.node
    }
}
