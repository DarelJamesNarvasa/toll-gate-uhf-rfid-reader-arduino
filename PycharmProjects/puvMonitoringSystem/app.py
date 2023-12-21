from flask import Flask, render_template, request
from flask_mqtt import Mqtt
import json

import folium
from folium import plugins

from sqlalchemy import create_engine, Column, Float, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import os
import psycopg2

Base = declarative_base()

app = Flask(__name__)
app.config['MQTT_BROKER_URL'] = 'broker.emqx.io'
app.config['MQTT_BROKER_PORT'] = 1883
app.config['MQTT_USERNAME'] = 'msu_marawi_eee'
app.config['MQTT_PASSWORD'] = 'msu_marawi_eee'
app.config['MQTT_KEEPALIVE'] = 5
app.config['MQTT_TLS_ENABLED'] = False

topic = 'rakalmonitoring/p1'
mqtt = Mqtt(app)

# Define the database model
class Database(Base):
    __tablename__ = "database"
    id = Column(Integer, primary_key=True)
    latitude = Column(Float)
    longitude = Column(Float)
    rakalId = Column(Integer)
    date = Column(String)
    time = Column(String)
    type = Column(String)
    rfid = Column(String)

    def __init__(self, lat, long, rakalid, date, time, type, rfid):
        self.latitude = lat
        self.longitude = long
        self.rakalId = rakalid
        self.date = date
        self.time = time
        self.type = type
        self.rfid = rfid

    def __repr__(self):
        return (f"({self.latitude}, {self.longitude}, {self.rakalId},{self.date}, "
                f"{self.time}, {self.type}, {self.rfid})")

database_engine = create_engine("sqlite:///database.db", echo=True)
Base.metadata.create_all(bind=database_engine)
Database_Session = sessionmaker(bind=database_engine)
database_session = Database_Session()


mqtt.publish(topic, 'hello, I am from flask')

@mqtt.on_connect()
def handle_connect(client, userdata, flags, rc):
    mqtt.subscribe(topic)

@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):
    data = dict(
        topic=message.topic,
        payload=message.payload.decode()
    )

    try:
        json_data = json.loads(data['payload'])
    except json.JSONDecodeError as e:
        print(f"Failed to parse JSON: {e}")
        return

    latitude = float(json_data.get('latitude', 0.0))
    longitude = float(json_data.get('longitude', 0.0))
    rakalID = int(json_data.get('rakalID', None))
    date = json_data.get('date', None)
    time = json_data.get('time', None)
    type = json_data.get('type', None)
    rfid = json_data.get('rfid', None)

    print(f"Latitude: {latitude}, Longitude: {longitude}, RakalID: {rakalID}, Date: {date}, Time: {time}, Type: {type}, RFID: {rfid}")


    # Stored Database
    data = Database(latitude, longitude, rakalID, date, time, type, rfid)
    database_session.add(data)
    database_session.commit()

@app.route('/')
def index():

    # Device One
    deviceOne_results = database_session.query(Database).filter_by(rakalId=1).all()
    passengerOne_results = database_session.query(Database).filter_by(rakalId=1).filter(Database.rfid.isnot(None)).all()

    deviceOne_coordinates = [(loc.latitude, loc.longitude) for loc in deviceOne_results]
    if deviceOne_coordinates:
        deviceOne_length = len(deviceOne_coordinates)
        map1 = folium.Map(location=deviceOne_coordinates[deviceOne_length - 1], zoom_start=16)
        folium.PolyLine(deviceOne_coordinates, tooltip="Coast").add_to(map1)

        for marker in passengerOne_results:
            coord = [marker.latitude, marker.longitude]
            folium.Marker(
                location=coord,
                tooltip=f"{marker.rfid}",
                popup=f"Type:{marker.type} "
                      f"Date:{marker.date} Time:{marker.time}",
                icon=folium.Icon(icon="cloud")
            ).add_to(map1)

        # Convert the Folium map to HTML
        map1_html = map1._repr_html_()
    else:
        map1_html = ""

    ##############
    # Device Two
    deviceTwo_results = database_session.query(Database).filter_by(rakalId=2).all()
    passengerTwo_results = database_session.query(Database).filter_by(rakalId=2).filter(Database.rfid.isnot(None)).all()

    deviceTwo_coordinates = [(loc.latitude, loc.longitude) for loc in deviceTwo_results]

    if deviceTwo_coordinates:
        deviceTwo_length = len(deviceTwo_coordinates)
        map2 = folium.Map(location=deviceTwo_coordinates[deviceTwo_length - 1], zoom_start=16)
        folium.PolyLine(deviceTwo_coordinates, tooltip="Coast").add_to(map2)

        for marker in passengerTwo_results:
            coord = [marker.latitude, marker.longitude]
            folium.Marker(
                location=coord,
                tooltip=f"{marker.rfid}",
                popup=f"Type:{marker.type} "
                      f"Date:{marker.date} Time:{marker.time}",
                icon=folium.Icon(icon="cloud")
            ).add_to(map2)

        # Convert the Folium map to HTML
        map2_html = map2._repr_html_()
    else:
        map2_html = ""

    #######

    # Device Three
    deviceThree_results = database_session.query(Database).filter_by(rakalId=3).all()
    passengerThree_results = database_session.query(Database).filter_by(rakalId=3).filter(Database.rfid.isnot(None)).all()

    deviceThree_coordinates = [(loc.latitude, loc.longitude) for loc in deviceThree_results]
    if deviceThree_coordinates:
        deviceThree_length = len(deviceThree_coordinates)
        map3 = folium.Map(location=deviceThree_coordinates[deviceThree_length - 1], zoom_start=16)
        folium.PolyLine(deviceThree_coordinates, tooltip="Coast").add_to(map3)

        for marker in passengerThree_results:
            coord = [marker.latitude, marker.longitude]
            folium.Marker(
                location=coord,
                tooltip=f"{marker.rfid}",
                popup=f"Type:{marker.type} "
                      f"Date:{marker.date} Time:{marker.time}",
                icon=folium.Icon(icon="cloud")
            ).add_to(map3)

        # Convert the Folium map to HTML
        map3_html = map3._repr_html_()
    else:
        map3_html = ""

    return render_template('index.html', map1_html=map1_html, map2_html=map2_html, map3_html=map3_html,
                           passengerOne_results=passengerOne_results, passengerTwo_results=passengerTwo_results, passengerThree_results=passengerThree_results)


@app.route('/delete_data', methods=['POST'])
def delete_data():
    if request.method == 'POST':
        # Delete all records from the Database table
        database_session.query(Database).delete()
        database_session.commit()

    return "All data deleted successfully"

if __name__ == '__main__':
    app.run()
