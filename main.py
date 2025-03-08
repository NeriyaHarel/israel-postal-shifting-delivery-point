from pathlib import Path
from typing import NamedTuple
from delivery_point import DeliveryPoint
from distance_calculator import HaversineDistanceCalc, Distance
from exceptions import GeocoderError
from geocoder import NominatimGeocoder, Geocoder
import logging
from routing_engine import get_routing_link, Vehicle
from file_reader import file_reader_factory
import argparse

from utils import print_progress_bar

# add logging to file
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
handler = logging.FileHandler('delivery_points.log', 'w', 'utf-8') # or whatever
handler.setFormatter(logging.Formatter('%(name)s %(message)s')) # or whatever
root_logger.addHandler(handler)

class PointWithDistance(NamedTuple):
    point: DeliveryPoint
    distance: Distance


def add_geolocation(geocoder: Geocoder, point: DeliveryPoint):
    logging.info(f'Searching for {point}')
    try:
        point.geolocation = geocoder.search_string(str(point))
        return
    except GeocoderError as e:
        logging.error(f'Error while searching for {point}: {e}')
    logging.info("Trying to search for the city and street")
    try:
        point.geolocation = geocoder.search_string(
            f'{point.city}, {point.street}')
    except GeocoderError as e:
        logging.error(f'Error while searching for {point}: {e}')

def load_points(data_file: Path, cache_file: Path) -> list[DeliveryPoint]:
    """
    Load points from the data file and cache file if it exists
    the cache file is used to store the geolocation of the points
    so we don't have to search for them again
    Args:
        data_file: A path to the file with delivery points
        cache_file: A path to the file with cached delivery points

    Returns:
        list[DeliveryPoint]: A list of delivery points

    """
    points_without_meta = file_reader_factory(data_file.suffix).load(data_file)
    if cache_file.exists():
        cache_file_handler = file_reader_factory(cache_file.suffix)
        cached_points = cache_file_handler.load(cache_file)
    else:
        cached_points = []
    delivery_points = {DeliveryPoint.from_dict(point) for point in cached_points}
    for point in points_without_meta:
        delivery_point = DeliveryPoint.from_dict(point)
        if delivery_point not in delivery_points:
            delivery_points.add(delivery_point)

    return list(delivery_points)

def main():
    print(f'---- Welcome to the delivery points system ----')
    # initialization
    distance_calc = HaversineDistanceCalc()
    geocoder = NominatimGeocoder()

    current_location = input('Enter your current location\n>')
    current_location = geocoder.search_string(current_location)
    print(f'[+] Your current location is: {current_location}')

    cache_file = Path(args.cache_file)
    delivery_points = load_points(Path(args.data_file), cache_file)

    cache_file_handler = file_reader_factory(cache_file.suffix)

    print_progress_bar(0, 1, prefix='[+] Fetching Geolocation Data:',suffix=f'{i+1}/{len(delivery_points)}', length=50,printEnd='')
    for i, point in enumerate(delivery_points):
        if not point.geolocation:
            add_geolocation(geocoder, point)
            # save the geolocation to the cache file
            # we do it on every iteration so we don't lose the progress
            # and yes it's not the most efficient way but it's the simplest
            points_as_dict = [point.to_dict() for point in delivery_points]
            cache_file_handler.save(cache_file, points_as_dict)
        else:
            logging.info(f'Geolocation for {point} already exists')
        print_progress_bar(i + 1, len(delivery_points), prefix='[+] Fetching Geolocation Data:', suffix=f'{i+1}/{len(delivery_points)}', length=50,
                           printEnd='')

    # calculate distance and sort
    delivery_points = [point for point in delivery_points if point.geolocation]
    delivery_points_with_distance = [
        PointWithDistance(point,
                          distance_calc.distance(current_location, point.geolocation))
        for point in delivery_points
    ]
    delivery_points_with_distance.sort(key=lambda x: x.distance)
    top_10_points = delivery_points_with_distance[:10]
    for point_with_distance in top_10_points:
        print(point_with_distance.point)
        print(f'Distance: {point_with_distance.distance}')
        print("Route: ", get_routing_link(
                  current_location, point_with_distance.point.geolocation,Vehicle.CAR)
              )


if __name__ == '__main__':
    args_p = argparse.ArgumentParser()
    args_p.add_argument('--data_file', default='delivery points.json',
                        help='Path to the file with delivery points taken from the post office website it will stay unchanged')
    args_p.add_argument('--cache_file', default='delivery points meta.json',
                        help='Path to the cache file with delivery points you can specify a json a csv file')

    args = args_p.parse_args()
    main()
