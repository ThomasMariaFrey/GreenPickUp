# Imports
from datetime import datetime

import osmnx as ox

from flask import (Blueprint, flash, g, render_template, request)
from flaskr.auth import login_required
from flaskr.db import get_db
from flaskr.get_helper import Functionalities

bp = Blueprint('deliverer', __name__)


@bp.route('/routesite', methods=('GET', 'POST'))
@login_required('deliverer')
def routesite():
    """
    This method extracts all the routes of all deliverers for the current date. 
    Also, it handles selected filters and passes relevant information to the routesite website.
    :return: The routesite website with potentially applied filters 
    and a map with an overview of today's routes.
    """

    # Extract all locations and stations from database
    database = get_db()
    locations = database.execute('SELECT * FROM locations').fetchall()
    
    stations = database.execute('SELECT * FROM stations').fetchall()
    
    # Get relevant time stamps
    current_day = datetime.now()
    
    # Create dictionaries for filter options in the html file
    drivers = {(driver['id'], driver['driver_name']) for driver in stations}
    capacities = {
        (station['id'], station['date']): f"{station['current_weight']}/{station['max_weight']}"
        for station in stations
    }
    filter_times = {times[6].strftime("%H:%M") for times in locations}
    
    if request.method == 'POST':

        # Get selected date, convert it to date time, if not selected: date from today
        selected_date = request.form['selected_date']
        selected_date = datetime.strptime(selected_date, '%Y-%m-%d').date() if selected_date else current_day.date()

        # Get selected time and convert it to datetime object
        selected_time = request.form['selected_time']
        selected_time = datetime.strptime(selected_time, '%H:%M').time() if selected_time else ""

        # Filter by driver
        selected_driver = request.form['selected_driver']
        if selected_driver != "":
            selected_driver_name = next((name for station_id, name in drivers 
                                         if station_id == int(selected_driver)), None)
            flash(selected_driver_name, category="filter")
            locations = list(filter(lambda loc: str(loc["station_id"]) == selected_driver, locations))

    else:
        selected_date = current_day.date()
        selected_time = ""

    # Call time filter method
    locations, flash_message = Functionalities().time_filter(locations, selected_date, selected_time)

    # Flash selected date/time
    flash(flash_message, category="filter")

    # Call the map method with the corresponding configuration
    markercolors = {1: '#c24a4a', 2: '#4AC2A4', 3: '#c28c4a', 4: '#c24a9c', 5: '#4a54c2'}
    tooltip = "Station {station_id}<br>Capacity: {capacity}"
    icon_config = [
        {
            "icon": "arrow-down", 
            "icon_shape": "marker",
            "number": location["timestamp_from"].strftime("%H"),
            "border_color": markercolors[location["station_id"]],
            "background_color": markercolors[location["station_id"]]
        }
        for location in locations
    ]
    city_map = Functionalities().add_map(locations=locations, tooltips=tooltip, icon_configs=icon_config,
                                         capacities=capacities, polylines=True)

    return render_template("deliverer/routes.html", map=city_map._repr_html_(),
                           current_time=current_day.strftime('%Y-%m-%d %H:%M:%S'),
                           drivers=set(drivers), filter_times=sorted(filter_times))


@bp.route('/drivers_routesite', methods=('GET', 'POST'))
@login_required('deliverer')
def drivers_routesite():
    """
    This method extracts today's route of the driver, which is logged in.
    Also, it handles selected filters and passes relevant information to the drivers_routesite website.
    :return: The drivers_routesite website with potentially applied filters and a map with the shortest path of
    today's route of the logged in driver.
    """

    # Extract locations from database for the corresponding driver
    database = get_db()
    locations = database.execute('SELECT * FROM locations '
                                 'WHERE station_id=?', (g.user['id'], )
                                 ).fetchall()
    stations = database.execute('SELECT * FROM stations '
                                'WHERE id=?', (g.user['id'], )
                                ).fetchall()

    # Initialise Parameters which will be handed to the html file
    current_day = datetime.now()
    filter_times = {times[6].strftime("%H:%M") for times in locations}
    capacities = {
        (station['id'], station['date']): f"{station['current_weight']}/{station['max_weight']}"
        for station in stations
    }
    
    if request.method == 'POST':

        # Get selected type
        selected_type = request.form['selected_type']
        
        # Get selected date, convert it to date time, if not selected: date from today
        selected_date = request.form['selected_date']
        selected_date = datetime.strptime(selected_date, '%Y-%m-%d').date() if selected_date else current_day.date()

        # Get selected time and convert it to datetime object
        selected_time = request.form['selected_time']
        selected_time = datetime.strptime(selected_time, '%H:%M').time() if selected_time else ""

    else:
        selected_type = 'length'
        selected_date = current_day.date()
        selected_time = ""
    
    # Call time filter method
    locations, flash_message = Functionalities().time_filter(locations, selected_date, selected_time, route=True)

    # Flash selected filters
    flash(flash_message, category="filter")
    flash('route with shortest ' + selected_type, category="filter")

    # Creation of graph for the corresponding city
    graph = ox.graph_from_place("Stuttgart, Germany", network_type="bike", simplify=True)

    # Get the nearest nodes, compute the shortest path based on selected type, calculate length and time
    route_length = route_time = 0
    shortest_paths = []
    for i in range(len(locations)-1):
        source = Functionalities().get_nearest_node((float(locations[i]['latitude']), float(locations[i]['longitude']))) 
        target = Functionalities().get_nearest_node((float(locations[i+1]['latitude']),
                                                     float(locations[i+1]['longitude'])))
        if selected_type == 'travel_time':
            shortest_path, length, travel_time = \
                Functionalities().get_shortest_path(graph, source, target, 'travel_time')
        else:
            shortest_path, length, travel_time = \
                Functionalities().get_shortest_path(graph, source, target, 'length')
        shortest_paths.append(shortest_path)
        route_length += length
        route_time += travel_time
        
    # Call the map method with the corresponding configuration
    markercolors = {1: '#c24a4a', 2: '#4AC2A4', 3: '#c28c4a', 4: '#c24a9c', 5: '#4a54c2'}
    tooltip = "Station {station_id}<br>Capacity: {capacity}"
    icon_config = [
        {
            "icon": "arrow-down", 
            "icon_shape": "marker",
            "number": location["timestamp_from"].strftime("%H"),
            "border_color": markercolors[location["station_id"]],
            "background_color": markercolors[location["station_id"]]
        }
        for location in locations
    ]
    city_map = Functionalities().add_map(locations=locations, tooltips=tooltip, icon_configs=icon_config,
                                         capacities=capacities, shortest_paths=shortest_paths, graph=graph)

    return render_template("deliverer/drivers_route.html", map=city_map._repr_html_(),
                           current_time=current_day.strftime('%Y-%m-%d %H:%M:%S'), selected_date=selected_date,
                           filter_times=sorted(filter_times), route_length=round((route_length/1000), 2),
                           route_time=round(route_time, 2))
