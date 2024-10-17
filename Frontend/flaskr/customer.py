# Imports
from datetime import datetime, timedelta

from flask import (Blueprint, flash, g, redirect, render_template, request, url_for)

from flaskr.auth import login_required
from flaskr.db import get_db
from flaskr.get_helper import Functionalities

bp = Blueprint('customer', __name__)


@bp.route('/')
def redirection():
    """
    This method checks which user type is logged in and in which status the user is and redirects to the right site.
    :return: Redirection to the proper website for the respective user.
    """
    if g.user is None:
        return redirect(url_for('auth.login'))

    if g.user_type == "deliverer":
        # Redirect to routesite for deliverer
        return redirect(url_for('deliverer.routesite'))

    if g.user['order_status'] == "not assigned":
        # Redirect to notassignedsite
        return redirect(url_for('customer.notassignedsite'))

    if g.user['order_status'] == "assigned":
        # Redirect to assignedsite
        return redirect(url_for('customer.assignedsite'))
    
    if g.user['order_status'] == "picked-up":
        # Redirect to ratingsite
        return redirect(url_for('customer.ratingsite'))

    else:
        return redirect(url_for('auth.login'))


@bp.route('/notassignedsite', methods=('GET', 'POST'))
@login_required('customer')
def notassignedsite():
    """
    This method handles all the functionalities of the landing page after the user has logged in, thus where
    the user can assign the parcel to a station.
    It contains all the filter functionalities which can be applied and the visualisation of the map.
    :return: The notassignedsite with the map and all the locations which are available for the next day
    (based on the selected filters).
    """

    # Verify the order status
    if g.user['order_status'] != "not assigned" and g.user['order_status'] != "assigned":
        return redirect(url_for('customer.redirection'))
    
    database = get_db()

    locations = database.execute(
        'SELECT station_id, latitude, longitude, adress, postal_code, timestamp_from'
        ' FROM locations'
        ).fetchall()
    
    stations = database.execute(
        'SELECT * FROM stations ').fetchall()
    
    current_day = datetime.now()
    next_day = current_day + timedelta(days=1)

    areas = {location[4] for location in locations}
    filter_times = {times[5].strftime("%H:%M") for times in locations}

    capacities = {
        (station['id'], station['date']): f"{station['current_weight']}/{station['max_weight']}"
        for station in stations
    }

    if request.method == 'POST':
        
        # Get selected date, convert it to date time, if not selected: date from tomorrow
        selected_date = request.form['selected_date']
        selected_date = datetime.strptime(selected_date, '%Y-%m-%d').date() if selected_date else next_day.date()

        # Check that selected date is valid, else tomorrows locs
        if selected_date <= current_day.date(): 
            flash('Selected pickup date not valid. Earliest pick up is tomorrow.', category="error")
            selected_date = next_day.date()

        # Get selected time and convert it to datetime object
        selected_time = request.form['selected_time']
        selected_time = datetime.strptime(selected_time, '%H:%M').time() if selected_time else ""

        # Filter by area
        selected_area = request.form['selected_area']
        if selected_area != "":
            locations = list(filter(lambda location: location["postal_code"] == selected_area, locations))
            flash(selected_area, category="filter")

    else:
        selected_date = next_day.date()
        selected_time = ""

    # Call time filter method
    locations, flash_message = Functionalities().time_filter(locations=locations, selected_date=selected_date, 
                                                             selected_time=selected_time)
    
    # Flash selected filter
    flash(flash_message, category="filter")

    # Call the map method with the corresponding configuration
    markercolors = {1: '#c24a4a', 2: '#4AC2A4', 3: '#c28c4a', 4: '#c24a9c', 5: '#4a54c2'}
    tooltip = "Click to select station {station_id}<br>Current capacity: {capacity}"
    icon_config = [
        {
            "icon": "cube", 
            "icon_shape": "marker",
            "border_color": markercolors[location["station_id"]],
            "background_color": markercolors[location["station_id"]]
        }
        for location in locations
    ]
    city_map = Functionalities().add_map(locations=locations, tooltips=tooltip, icon_configs=icon_config,
                                         capacities=capacities, popup=True)
        
    return render_template('customer/notassigned.html', map=city_map._repr_html_(),
                           current_time=current_day.strftime('%Y-%m-%d %H:%M:%S'),
                           areas=sorted(areas), filter_times=sorted(filter_times))


@bp.route('/save_coords', methods=['POST'])
def save_coords():
    """
    This method handles information from the post request, when a user clicks on the button of a location
    to assign the parcel. It extracts the latitude and longitude of the location, as well as the station_id,
    the date and capacity.
    Next the new capacity is calculated and if it does not exceed the maximum capacity of the station,
    the assignment is valid and the database is updated.
    :return: If capacity available, update of the database and redirection to assignedsite.
    Else redirection to notassignedsite and error message.
    """

    # Verify order status
    if g.user['order_status'] != "not assigned" and g.user['order_status'] != "assigned":
        return redirect(url_for('customer.redirection'))
    
    # Retrieve the information of the marker from the POST request
    station_id = request.form['station_id']
    date = request.form['date']
    capacity = request.form['capacity']

    # Get the capacity information and increase it
    cur_c = int(capacity.split('/')[0])
    max_c = int(capacity.split('/')[1])
    new_capacity = cur_c + 1

    # Check if station has enough capacity 
    if new_capacity <= max_c:

        database = get_db()
        database.execute("UPDATE orders "
                         "SET placement_date = ?, order_status = 'assigned', station_id = ? "
                         "WHERE id = ?;", (date, station_id, g.user['id']))
        database.execute("UPDATE stations "
                         "SET current_weight = ? "
                         "WHERE id = ?;", (new_capacity, station_id))
        database.commit()

    return redirect(url_for('customer.assignedsite'))


@bp.route('/assignedsite', methods=('GET', 'POST'))
@login_required('customer')
def assignedsite():
    """
    This method holds all the functionalities for the assignedsite, thus the site when the user already
    has assigned the parcel to a station.
    :return: The website with the map showing the locations of the assigned station and buttons which lead
    to the next steps in the assignment process.
    """

    # Verify order status is assigned, else error message and redirection
    if g.user['order_status'] != "assigned":
        flash('Please select a location with free capacity on the map before proceeding.', category="error")
        return redirect(url_for('customer.redirection'))

    # Database connection
    database = get_db()
    locations = database.execute(
        'SELECT * FROM locations '
        'WHERE station_id = ? AND DATE(timestamp_from) = ? ;', (g.user['station_id'], g.user['placement_date'])
        ).fetchall()
    
    stations = database.execute('SELECT * FROM stations ').fetchall()

    capacities = {
        (station['id'], station['date']): f"{station['current_weight']}/{station['max_weight']}"
        for station in stations
    }
    
    # Initialisation
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
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
        
    return render_template("customer/assigned.html", map=city_map._repr_html_(), current_time=current_time)


@bp.route('/openstation', methods=('GET', 'POST'))
@login_required('customer')
def openstation():
    """
    This method handles the functionalities of the open station button, which include the verification of the date
    and the update of the database.
    :return: Redirection to the ratingsite or back to the assignedsite if opening not possible yet.
    """

    # Verify the order status
    if g.user['order_status'] != "assigned":
        return redirect(url_for('customer.redirection'))

    # Get date and time information
    current_date = datetime.now()
    placement_date = datetime.strptime(g.user['placement_date'], "%Y-%m-%d")

    # Verify that parcel has been placed to today's date
    if placement_date > current_date:
        flash('Pickup not yet possible. Please check your selected date and time.', category="error")
        return redirect(url_for('customer.redirection'))

    # Round current time to time interval of our database
    hour = current_date.hour
    if 9 <= hour < 11:
        rounded_hour = 9
    elif 11 <= hour < 13:
        rounded_hour = 11
    elif 13 <= hour < 17:
        rounded_hour = 13
    else:
        rounded_hour = 17

    rounded_dt = current_date.replace(hour=rounded_hour, minute=0, second=0, microsecond=0)
    if rounded_dt > current_date:
        rounded_dt -= timedelta(hours=1)
    
    # Database connection to select location id
    database = get_db()
    result = database.execute('''
    SELECT l.id
    FROM locations l
    WHERE l.station_id = (
        SELECT o.station_id
        FROM orders o
        WHERE o.id = ?
    ) AND l.timestamp_from= ?
    ''', (g.user['id'], rounded_dt)).fetchone()

    if result is None:
        flash('Pickup not yet possible. Please check your selected date and time.', category="error")
        return redirect(url_for('customer.redirection'))

    # Update database with location id and 
    new_location_id = result[0]
    update_query = '''
        UPDATE orders
        SET order_status = 'picked-up', location_id = ?
        WHERE id = ?
    '''
    database.execute(update_query, (new_location_id, g.user['id']))
    database.commit()

    return redirect(url_for('customer.redirection'))


@bp.route('/deleteplacement', methods=('GET', 'POST'))
@login_required('customer')
def deleteplacement():
    """
    This method handles the functionalities of the delete placement button, which includes the update of the
    database and the redirection to the notassignedsite.
    :return: Redirection to the notassignedsite.
    """

    # Verify the order status
    if g.user['order_status'] != "assigned":
        return redirect(url_for('customer.redirection'))
    
    # Update the database: reduce the capacity and reset the placement_date (2000-01-01 is a placeholder for NULL)
    database = get_db()
    database.execute("UPDATE stations "
                     "SET current_weight = current_weight-1 "
                     "WHERE id = ?;", (g.user['station_id'],))
    database.execute("UPDATE orders "
                     "SET order_status = 'not assigned', placement_date = '2000-01-01', station_id = ? "
                     "WHERE id = ?;", (None, g.user['id']))
    database.commit()

    return redirect(url_for('customer.redirection'))


@bp.route('/ratingsite', methods=('GET', 'POST'))
@login_required('customer')
def ratingsite():
    """
    This method handles the functionalities of the ratingsite. It writes the feedback given by the user to the
    database and completes the assignment process.
    :return: Update of the database and redirection to the loginsite.
    """
    
    # Verify the order status
    if g.user['order_status'] != "picked-up":
        return redirect(url_for('customer.redirection'))
    
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    if request.method == 'POST':
        # Exception: error if not rating is given
        try:
            rating = request.form['rating']
        except KeyError:
            rating = ""
        review = request.form['review']

        # Case if rating and review given: Update database
        if rating != "" and review != "Further Feedback":
            database = get_db()
            database.execute("UPDATE orders "
                             "SET order_status = 'completed', placement_date = '2000-01-01', rating_value = ?, "
                             "review = ? "
                             "WHERE id = ?;", (rating, review, g.user['id']))
            database.commit()
            return redirect(url_for('customer.redirection'))
        
        # Case if only rating is given: Update database
        elif rating != "":
            database = get_db()
            database.execute("UPDATE orders "
                             "SET order_status = 'completed', placement_date = '2000-01-01', rating_value = ? "
                             "WHERE id = ?;", (rating, g.user['id']))
            database.commit()
            return redirect(url_for('customer.redirection'))
        
        # Error if no rating was given: not optional
        else:
            flash('Please select a rating before proceeding.', category="error")
            return redirect(url_for('customer.redirection'))

    return render_template("customer/rating.html", current_time=current_time)


@bp.route('/projectsite', methods=('GET', 'POST'))
def projectsite():
    """
    This method handles the redirection to the project website.
    :return: Redirection to the project website.
    """

    return render_template("project.html")
