def simulate_flood(bbox, elevation_threshold=10):
    """
    Simulate flood zones based purely on elevation threshold.

    Parameters
    ----------
    bbox : ee.Geometry
        Bounding box of area to simulate.
    elevation_threshold : float or None
        Elevation threshold in meters. If None, auto-calculated from 5th percentile.

    Returns
    -------
    ee.Image
        Binary flood mask image (1 = flooded, 0 = dry), clipped to bbox.
    """
    import ee

    # Load Copernicus DEM
    dem = ee.ImageCollection("COPERNICUS/DEM/GLO30") \
            .mosaic() \
            .select("DEM") \
            .rename("elevation")

    # Add buffer to prevent edge artifacts
    buffered_bbox = bbox.buffer(500)
    dem_clipped = dem.clip(buffered_bbox)
    dem_masked = dem_clipped.updateMask(dem_clipped.mask().And(dem_clipped.gt(0)))

    # Auto-calculate threshold if not provided
    if elevation_threshold is None:
        stats = dem_masked.reduceRegion(
            reducer=ee.Reducer.percentile([5]),
            geometry=bbox,
            scale=30,
            maxPixels=1e8
        )
        elevation_threshold = stats.getNumber("elevation")
        print("[simulate_flood] Auto-calculated threshold (5th percentile):", elevation_threshold.getInfo())
    else:
        print(f"[simulate_flood] Using elevation threshold: {elevation_threshold}m")

    flood = dem_masked.lt(elevation_threshold).selfMask().rename("Flood")
    return flood.clip(bbox)

    

import ee
import geemap

ee.Initialize()

def delineate_watershed_gee(bbox, pour_point, accumulation_threshold=1000):
    """
    Returns the watershed polygon as an ee.FeatureCollection.
    """
    import ee

    flow_acc = ee.Image("MERIT/Hydro/v1_0_1").select("upa").clip(bbox.buffer(500))
    streams = flow_acc.gt(accumulation_threshold)

    pt = ee.Geometry.Point(pour_point)
    search_area = pt.buffer(300)
    snapped = streams.reduceToVectors(
        geometry=search_area,
        geometryType='centroid',
        scale=90,
        maxPixels=1e8
    ).geometry()

    snapped_point = ee.Algorithms.If(snapped.isEmpty(), pt, snapped)
    source = ee.Image().toByte().paint(ee.Geometry(snapped_point), 1)

    watershed_mask = flow_acc.gte(accumulation_threshold).cumulativeCost(
        source=source,
        maxDistance=1e7
    ).lt(500)

    watershed_fc = watershed_mask.selfMask().reduceToVectors(
        geometry=bbox,
        scale=90,
        geometryType='polygon',
        maxPixels=1e8
    )

    return watershed_fc

