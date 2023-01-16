def classFactory(iface):
    from .geoapify_geocoder import GeoapifyGeocoder
    return GeoapifyGeocoder(iface=iface)
