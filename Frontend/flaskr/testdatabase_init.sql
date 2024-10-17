--run query to set up a sample database structure with sample entrys

--initializing database:
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS stations;
DROP TABLE IF EXISTS locations;

CREATE TABLE stations (
  id INTEGER NOT NULL, 
  driver_name TEXT NOT NULL, 
  date DATE NOT NULL,
  current_weight INTEGER DEFAULT 0, 
  max_weight INTEGER,
  PRIMARY KEY (id, date) 
);

CREATE TABLE locations (
  id INTEGER PRIMARY KEY AUTOINCREMENT, 
  station_id INTEGER, 
  latitude TEXT,
  longitude TEXT,
  adress TEXT,
  postal_code TEXT,
  timestamp_from TIMESTAMP,
  FOREIGN KEY (station_id) REFERENCES stations (id) 
);

CREATE TABLE orders (
  id TEXT PRIMARY KEY, 
  order_status TEXT NOT NULL,
  arrival_date TEXT,
  placement_date TEXT,
  station_id INTEGER, 
  location_id INTEGER,
  rating_value INTEGER,
  review TEXT,
  FOREIGN KEY (location_id) REFERENCES locations (id), 
  FOREIGN KEY (station_id) REFERENCES stations (id) 
);

--adding stations:
INSERT INTO stations (id, driver_name, date, current_weight, max_weight)
VALUES (1, 'Bodo', date('now'), 17, 20);
INSERT INTO stations (id, driver_name, date, current_weight, max_weight)
VALUES (2, 'Dominik', date('now'), 15, 20);
INSERT INTO stations (id, driver_name, date, current_weight, max_weight)
VALUES (3, 'David', date('now'), 16, 20);
INSERT INTO stations (id, driver_name, date, current_weight, max_weight)
VALUES (4, 'Lisa', date('now'), 10, 20);
INSERT INTO stations (id, driver_name, date, current_weight, max_weight)
VALUES (5, 'Günther', date('now'), 20, 20);

INSERT INTO stations (id, driver_name, date, current_weight, max_weight)
VALUES (1, 'Bodo', date('now', '+1 day'), 2, 20);
INSERT INTO stations (id, driver_name, date, current_weight, max_weight)
VALUES (2, 'Dominik', date('now', '+1 day'), 18, 20);
INSERT INTO stations (id, driver_name, date, current_weight, max_weight)
VALUES (3, 'David', date('now', '+1 day'), 5, 20);

INSERT INTO stations (id, driver_name, date, current_weight, max_weight)
VALUES (4, 'Lisa', date('now', '+2 day'), 3, 20);
INSERT INTO stations (id, driver_name, date, current_weight, max_weight)
VALUES (5, 'Günther', date('now', '+2 day'), 20, 20);

--adding locations for today: 
INSERT INTO locations (station_id, latitude, longitude, postal_code, timestamp_from)
VALUES (1, 48.7871439, 9.1942394, 70190, date('now') || ' 09:00:00');
INSERT INTO locations (station_id, latitude, longitude, postal_code, timestamp_from)
VALUES (1, 48.7888885, 9.2221463, 70188, date('now') || ' 11:00:00');
INSERT INTO locations (station_id, latitude, longitude, postal_code, timestamp_from)
VALUES (1, 48.7654129, 9.1687765, 70178, date('now') || ' 13:00:00');
INSERT INTO locations (station_id, latitude, longitude, postal_code, timestamp_from)
VALUES (1, 48.7787224, 9.1631452, 70176, date('now') || ' 15:00:00');
INSERT INTO locations (station_id, latitude, longitude, postal_code, timestamp_from)
VALUES (1, 48.7420057, 9.1335685, 70569, date('now') || ' 17:00:00');

INSERT INTO locations (station_id, latitude, longitude, postal_code, timestamp_from)
VALUES (2, 48.7284415, 9.1319437, 70567, date('now') || ' 09:00:00');
INSERT INTO locations (station_id, latitude, longitude, postal_code, timestamp_from)
VALUES (2, 48.7161176, 9.1184311, 70565, date('now') || ' 11:00:00');
INSERT INTO locations (station_id, latitude, longitude, postal_code, timestamp_from)
VALUES (2, 48.7391736, 9.1520677, 70597, date('now') || ' 13:00:00');
INSERT INTO locations (station_id, latitude, longitude, postal_code, timestamp_from)
VALUES (2, 48.7566096, 9.2524489, 70329, date('now') || ' 15:00:00');
INSERT INTO locations (station_id, latitude, longitude, postal_code, timestamp_from)
VALUES (2, 48.7023374, 9.2181474, 70599, date('now') || ' 17:00:00');

INSERT INTO locations (station_id, latitude, longitude, postal_code, timestamp_from)
VALUES (3, 48.838755, 9.1601316, 70435, date('now') || ' 09:00:00');
INSERT INTO locations (station_id, latitude, longitude, postal_code, timestamp_from)
VALUES (3, 48.813515, 9.2122332, 70376, date('now') || ' 11:00:00');
INSERT INTO locations (station_id, latitude, longitude, postal_code, timestamp_from)
VALUES (3, 48.8048522, 9.211316, 70372, date('now') || ' 13:00:00');
INSERT INTO locations (station_id, latitude, longitude, postal_code, timestamp_from)
VALUES (3, 48.830499, 9.1865954, 70437, date('now') || ' 15:00:00');
INSERT INTO locations (station_id, latitude, longitude, postal_code, timestamp_from)
VALUES (3, 48.8072059, 9.1921575, 70376, date('now') || ' 17:00:00');

INSERT INTO locations (station_id, latitude, longitude, postal_code, timestamp_from)
VALUES (4, 48.7607697, 9.1508357, 70199, date('now') || ' 09:00:00');
INSERT INTO locations (station_id, latitude, longitude, postal_code, timestamp_from)
VALUES (4, 48.7789852, 9.2493127, 70327, date('now') || ' 11:00:00');
INSERT INTO locations (station_id, latitude, longitude, postal_code, timestamp_from)
VALUES (4, 48.7662897, 9.2003314, 70184, date('now') || ' 13:00:00');
INSERT INTO locations (station_id, latitude, longitude, postal_code, timestamp_from)
VALUES (4, 48.7988356, 9.2103661, 70190, date('now') || ' 15:00:00');
INSERT INTO locations (station_id, latitude, longitude, postal_code, timestamp_from)
VALUES (4, 48.7808582, 9.1882041, 70182, date('now') || ' 17:00:00');

INSERT INTO locations (station_id, latitude, longitude, postal_code, timestamp_from)
VALUES (5, 48.8141606, 9.1259997, 70499, date('now') || ' 09:00:00');
INSERT INTO locations (station_id, latitude, longitude, postal_code, timestamp_from)
VALUES (5, 48.8237061, 9.1235715, 70499, date('now') || ' 11:00:00');
INSERT INTO locations (station_id, latitude, longitude, postal_code, timestamp_from)
VALUES (5, 48.8159355, 9.1138908, 70499, date('now') || ' 13:00:00');
INSERT INTO locations (station_id, latitude, longitude, postal_code, timestamp_from)
VALUES (5, 48.8202714, 9.1194412, 70499, date('now') || ' 15:00:00');
INSERT INTO locations (station_id, latitude, longitude, postal_code, timestamp_from)
VALUES (5, 48.8081994, 9.1854554, 70191, date('now') || ' 17:00:00');

--adding locations for tomorrow:
INSERT INTO locations (station_id, latitude, longitude, postal_code, timestamp_from)
VALUES (1, 48.7871439, 9.1942394, 70190, date('now', '+1 day') || ' 09:00:00');
INSERT INTO locations (station_id, latitude, longitude, postal_code, timestamp_from)
VALUES (1, 48.7888885, 9.2221463, 70188, date('now', '+1 day') || ' 11:00:00');
INSERT INTO locations (station_id, latitude, longitude, postal_code, timestamp_from)
VALUES (1, 48.7654129, 9.1687765, 70178, date('now', '+1 day') || ' 13:00:00');
INSERT INTO locations (station_id, latitude, longitude, postal_code, timestamp_from)
VALUES (1, 48.7787224, 9.1631452, 70176, date('now', '+1 day') || ' 15:00:00');
INSERT INTO locations (station_id, latitude, longitude, postal_code, timestamp_from)
VALUES (1, 48.7420057, 9.1335685, 70569, date('now', '+1 day') || ' 17:00:00');

INSERT INTO locations (station_id, latitude, longitude, postal_code, timestamp_from)
VALUES (2, 48.7284415, 9.1319437, 70567, date('now', '+1 day') || ' 09:00:00');
INSERT INTO locations (station_id, latitude, longitude, postal_code, timestamp_from)
VALUES (2, 48.7161176, 9.1184311, 70565, date('now', '+1 day') || ' 11:00:00');
INSERT INTO locations (station_id, latitude, longitude, postal_code, timestamp_from)
VALUES (2, 48.7391736, 9.1520677, 70597, date('now', '+1 day') || ' 13:00:00');
INSERT INTO locations (station_id, latitude, longitude, postal_code, timestamp_from)
VALUES (2, 48.7566096, 9.2524489, 70329, date('now', '+1 day') || ' 15:00:00');
INSERT INTO locations (station_id, latitude, longitude, postal_code, timestamp_from)
VALUES (2, 48.7023374, 9.2181474, 70599, date('now', '+1 day') || ' 17:00:00');

INSERT INTO locations (station_id, latitude, longitude, postal_code, timestamp_from)
VALUES (3, 48.838755, 9.1601316, 70435, date('now', '+1 day') || ' 09:00:00');
INSERT INTO locations (station_id, latitude, longitude, postal_code, timestamp_from)
VALUES (3, 48.813515, 9.2122332, 70376, date('now', '+1 day') || ' 11:00:00');
INSERT INTO locations (station_id, latitude, longitude, postal_code, timestamp_from)
VALUES (3, 48.8048522, 9.211316, 70372, date('now', '+1 day') || ' 13:00:00');
INSERT INTO locations (station_id, latitude, longitude, postal_code, timestamp_from)
VALUES (3, 48.830499, 9.1865954, 70437, date('now', '+1 day') || ' 15:00:00');
INSERT INTO locations (station_id, latitude, longitude, postal_code, timestamp_from)
VALUES (3, 48.8072059, 9.1921575, 70376, date('now', '+1 day') || ' 17:00:00');

-- locations for today + 2 days
INSERT INTO locations (station_id, latitude, longitude, postal_code, timestamp_from)
VALUES (4, 48.7607697, 9.1508357, 70199, date('now', '+2 day') || ' 09:00:00');
INSERT INTO locations (station_id, latitude, longitude, postal_code, timestamp_from)
VALUES (4, 48.7789852, 9.2493127, 70327, date('now', '+2 day') || ' 11:00:00');
INSERT INTO locations (station_id, latitude, longitude, postal_code, timestamp_from)
VALUES (4, 48.7662897, 9.2003314, 70184, date('now', '+2 day') || ' 13:00:00');
INSERT INTO locations (station_id, latitude, longitude, postal_code, timestamp_from)
VALUES (4, 48.7988356, 9.2103661, 70190, date('now', '+2 day') || ' 15:00:00');
INSERT INTO locations (station_id, latitude, longitude, postal_code, timestamp_from)
VALUES (4, 48.7808582, 9.1882041, 70182, date('now', '+2 day') || ' 17:00:00');

INSERT INTO locations (station_id, latitude, longitude, postal_code, timestamp_from)
VALUES (5, 48.8141606, 9.1259997, 70499, date('now', '+2 day') || ' 09:00:00');
INSERT INTO locations (station_id, latitude, longitude, postal_code, timestamp_from)
VALUES (5, 48.8237061, 9.1235715, 70499, date('now', '+2 day') || ' 11:00:00');
INSERT INTO locations (station_id, latitude, longitude, postal_code, timestamp_from)
VALUES (5, 48.8159355, 9.1138908, 70499, date('now', '+2 day') || ' 13:00:00');
INSERT INTO locations (station_id, latitude, longitude, postal_code, timestamp_from)
VALUES (5, 48.8202714, 9.1194412, 70499, date('now', '+2 day') || ' 15:00:00');
INSERT INTO locations (station_id, latitude, longitude, postal_code, timestamp_from)
VALUES (5, 48.8081994, 9.1854554, 70191, date('now', '+2 day') || ' 17:00:00');

--adding orders:
INSERT INTO orders (id, order_status, arrival_date)
VALUES ('Linda', 'not assigned', date('now', '+1 day'));
INSERT INTO orders (id, order_status, arrival_date, placement_date, station_id)
VALUES ('Max', 'assigned', date('now'), date('now'), 4);
INSERT INTO orders (id, order_status, arrival_date, placement_date, location_id, station_id)
VALUES ('John', 'picked-up', date('now'), date('now'), 4, 5);
