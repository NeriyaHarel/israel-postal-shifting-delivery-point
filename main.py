from pathlib import Path
from typing import NamedTuple
from src.delivery_point import DeliveryPoint
from src.distance_calculator import HaversineDistanceCalc, Distance
from src.exceptions import GeocoderError
from src.geocoder import NominatimGeocoder, Geocoder
import logging
from src.routing_engine import get_routing_link, Vehicle
from src.file_reader import file_reader_factory
import argparse
from src.utils import print_progress_bar


def setup_logging(log_file: str):
    if log_file:
        # file logging, the setup is a bit more complicated
        # as we log text in hebrew
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)
        handler = logging.FileHandler(log_file, 'w','utf-8')
        handler.setFormatter(logging.Formatter('%(asctime)s %(name)s %(message)s',"%Y-%m-%d %H:%M:%S"))
        root_logger.addHandler(handler)
    else:
        logging.basicConfig(level=logging.INFO)


class PointWithDistance(NamedTuple):
    point: DeliveryPoint
    distance: Distance


def add_geolocation(geocoder: Geocoder, point: DeliveryPoint):
    """
    Search for the geolocation of the given point and update the point with the geolocation
    Args:
        geocoder (Geocoder): The geocoder that will be used to search for the geolocation
        point (DeliveryPoint): The point to search for

    Returns:
        None - the point is updated in place

    """
    logging.info(f'Searching for {point}')
    try:
        point.geolocation = geocoder.search_structured(point.address)
        return
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
    print(f'---- Welcome to the delivery points suggestion system ----')
    # initialization
    distance_calc = HaversineDistanceCalc()
    geocoder = NominatimGeocoder()

    current_location = input('Enter your current location\n>')
    current_location = geocoder.search_string(current_location)
    print(f'[+] Your current location is: {current_location}')

    cache_file = Path(args.cache_file)
    delivery_points = load_points(Path(args.data_file), cache_file)


    missing_geo = [point.to_dict() for point in delivery_points if not point.geolocation]
    search_missing = False
    if missing_geo:
        print(f'[+] Found {len(missing_geo)} points without geolocation')
        print('Would you like to search for the missing geolocation?')
        inp = input('y/N\n>')
        if inp.lower() == 'y':
            search_missing = True
    cache_file_handler = file_reader_factory(cache_file.suffix)

    if search_missing:
        print_progress_bar(0, 1, prefix='[+] Fetching Geolocation Data:',
                           suffix=f'0/{len(delivery_points)}', length=50, printEnd='')
        for i, point in enumerate(delivery_points):
            if not point.geolocation:
                add_geolocation(geocoder, point)
                # save the geolocation to the cache file
                # we do it on every iteration so we don't lose the progress
                # and yes it's not the most efficient way but it's the simplest
                points_as_dict = [point.to_dict() for point in delivery_points]
                cache_file_handler.save(cache_file, points_as_dict)
            else:
                logging.debug(f'Geolocation already exists for {point} ')
            print_progress_bar(i + 1, len(delivery_points),
                               prefix='[+] Fetching Geolocation Data:',
                               suffix=f'{i + 1}/{len(delivery_points)}', length=50,
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
        print('-' * 50)
        print(point_with_distance.point)
        if point_with_distance.point.branch_name:
            print(point_with_distance.point.branch_name)
        if point_with_distance.point.description:
            print(point_with_distance.point.description)
        print(f'Distance: {point_with_distance.distance}')
        print("Route: ", get_routing_link(
            current_location, point_with_distance.point.geolocation, Vehicle.CAR))


if __name__ == '__main__':
    args_p = argparse.ArgumentParser()
    args_p.add_argument('--data_file', default='delivery points.json',
                        help='Path to the file with delivery points taken from the post office website it will stay unchanged')
    args_p.add_argument('--cache_file', default='delivery points meta.json',
                        help='Path to the cache file with delivery points you can specify a json a csv file')

    args_p.add_argument('--log_file',
                        help='Path to the log file if not specified the log will be printed to the console')

    args = args_p.parse_args()
    setup_logging(args.log_file)
    main()
