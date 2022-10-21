from copy import error
import logging
from typing import Any
import warnings
import threading
import socket
import struct
import pynmea2
import pytz
import json

from datetime import datetime, timezone
from streamz import Stream
from environs import Env
from paho.mqtt.client import Client as MQTT

from brefv_spec.envelope import Envelope

# Reading config from environment variables
env = Env()
MQTT_BROKER_HOST: str = env("MQTT_BROKER_HOST", "localhost")
MQTT_BROKER_PORT: int = env.int("MQTT_BROKER_PORT", 1883)
MQTT_CLIENT_ID: str = env("MQTT_CLIENT_ID", None)
MQTT_TRANSPORT: str = env("MQTT_TRANSPORT", "tcp")
MQTT_TLS: bool = env.bool("MQTT_TLS", False)
MQTT_USER: str = env("MQTT_USER", None)
MQTT_PASSWORD: str = env("MQTT_PASSWORD", None)
MQTT_TOPIC_NMEA_IN: str = env("MQTT_TOPIC_NMEA_IN", "CROWSNEST/SEAHORSE/NMEA0183/WIND")
MQTT_TOPIC_JSON_OUT: str = env("MQTT_TOPIC_JSON_OUT", "CROWSNEST/SEAHORSE/WIND/0/JSON")


# Setup logger
LOG_LEVEL = env.log_level("LOG_LEVEL", logging.INFO)
logging.basicConfig(level=LOG_LEVEL)
logging.captureWarnings(True)
warnings.filterwarnings("once")
LOGGER = logging.getLogger("crowsnest-connector-upd-nmea")


# Create mqtt client and configure it according to configuration
mq = MQTT(client_id=MQTT_CLIENT_ID, transport=MQTT_TRANSPORT)
mq.username_pw_set(MQTT_USER, MQTT_PASSWORD)
if MQTT_TLS:
    mq.tls_set()
mq.enable_logger(LOGGER)


def to_brefv_raw(in_msg):
    """Raw in message to brefv envelope"""

    envelope = Envelope(
        sent_at=datetime.now(timezone.utc).isoformat(),
        message=in_msg,
    )
    LOGGER.debug("Assembled into brefv envelope: %s", envelope)
    return envelope.json()


def to_mqtt(payload: Any, topic: str):
    """Publish a payload to a mqtt topic"""

    LOGGER.debug("Publishing on %s with payload: %s", topic, payload)
    try:
        mq.publish(
            topic,
            payload,
        )
    except Exception:  # pylint: disable=broad-except
        LOGGER.exception("Failed publishing to broker!")


def on_message(client, userdata, message):
    LOGGER.info("New Message...")

    msg = message.payload.decode("utf-8")
    payload = json.loads(msg)
    LOGGER.info(payload)

    if "message" in payload:
        nmea_str = payload["message"]
        print("nmea_str", nmea_str)
        source.emit(nmea_str)


def listen_mqtt_nmea_0183():
    """Init MQTT topic input"""
    LOGGER.info("HERE")

    mq = MQTT(client_id=MQTT_CLIENT_ID, transport=MQTT_TRANSPORT)
    mq.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT)
    mq.subscribe(MQTT_TOPIC_NMEA_IN)
    LOGGER.info("HERE 2" )
   
    mq.on_message = on_message

    mq.loop_forever()


def pars_nmea(nmea_msg):
    """Parsing ANavS NMEA sentences"""

    nmea_list = []
    nmea_parameters = {}
    # Check message format (TODO) 
    # if type(nmea_msg) == bytes:
    #     nmea_parameters = {}
    #     nmea_msg = nmea_msg.decode("utf-8")
    #     nmea_list = nmea_msg.split("\r")
    # nmea_str = "$" + nmea_str.split("$")[-1]

    nmea_str = nmea_msg["message"]
    nmea_list.append(nmea_list)

    for nmea_str in nmea_list:
        
        try:
            nmea_type_msg = nmea_str.split(",")[0].replace("$", "")

            if nmea_type_msg == "PASHR":
                PASHR_items = nmea_str.split(",")

                for idx, item in enumerate(PASHR_items):
                    try:
                        PASHR_items[idx] = float(item)
                    except:
                        pass  # Ignoring numbers

                PASHR = {
                    "heading": PASHR_items[2],
                    "roll": PASHR_items[4],
                    "pitch": PASHR_items[5],
                    "roll_accuracy": PASHR_items[7],
                    "heading_accuracy": PASHR_items[9],
                }
                nmea_parameters.update(PASHR)

            else:

                msg = pynmea2.parse(nmea_str)

                if msg.sentence_type == "GGA":

                    # Longitude +(North) or -(South)
                    longitude = float(msg.lon) / 100  # to dd.mmmmm
                    long_deg_min = ((longitude % 1) * 100) / 60  # Minute to degrees
                    longitude = int(longitude) + long_deg_min

                    if msg.lon_dir == "S":
                        longitude = -longitude

                    # Latitude +(East) or -(West)
                    latitude = float(msg.lat) / 100  # to degrees
                    lat_deg_min = ((latitude % 1) * 100) / 60  # Minute to degrees
                    latitude = int(latitude) + lat_deg_min
                    if msg.lon_dir == "W":
                        latitude = -latitude

                    GGA = {
                        "longitude": longitude,
                        "latitude": latitude,
                        "altitude": float(msg.altitude),
                        "num_satellites": int(msg.num_sats),
                        "gps_quality": int(msg.gps_qual),
                    }
                    nmea_parameters.update(GGA)

                elif msg.sentence_type == "RMC":

                    msg_UTC = msg.datestamp.isoformat() + " " + msg.timestamp.isoformat()
                    msg_UTC = datetime.strptime(msg_UTC, "%Y-%m-%d %H:%M:%S.%f")
                    msg_UTC = pytz.utc.localize(msg_UTC)

                    RMC = {
                        "timestamp": msg_UTC,
                    }
                    nmea_parameters.update(RMC)

                elif msg.sentence_type == "VTG":
                    VTG = {
                        "sog": msg.spd_over_grnd_kts,
                        "cog": msg.true_track,
                    }
                    nmea_parameters.update(VTG)

                elif msg.sentence_type == "ROT":
                    ROT = {
                        "rot": float(msg.rate_of_turn),
                    }
                    nmea_parameters.update(ROT)

                elif msg.sentence_type == "GST":
                    GST = {
                        "std_dev_altitude": msg.std_dev_altitude,
                        "std_dev_longitude": msg.std_dev_longitude,
                        "std_dev_latitude": msg.std_dev_latitude,
                    }
                    nmea_parameters.update(GST)

                elif msg.sentence_type == "MWV":
                    MWV = {
                        "wind_angle": float(msg.wind_angle),
                        "reference": msg.reference,
                        "wind_speed": float(msg.wind_speed),
                        "wind_speed_units": msg.wind_speed_units,
                        "status": msg.status,
                    }
                nmea_parameters.update(MWV)

        except Exception as e:
            LOGGER.error(e)

    LOGGER.info(nmea_parameters)
    return nmea_parameters


def to_brefv_nmea(GNSS_parameters):
    """NMEA in message to brefv envelope"""

    # TODO: Modify to brefv format

    envelope = Envelope(
        sent_at=datetime.now(timezone.utc).isoformat(),
        message=GNSS_parameters,
    )
    LOGGER.debug("Assembled into brefv envelope: %s", envelope)
    return envelope.json()


if __name__ == "__main__":

    # Build pipeline
    LOGGER.info("Building pipeline...")
    source = Stream()

    # MQTT stream: RAW NMEA --> JSON NMEA
    pipe_to_brefv_json = source.map(pars_nmea).map(to_brefv_raw).sink(to_mqtt, topic=MQTT_TOPIC_JSON_OUT)

    LOGGER.info("Connecting to MQTT broker...")
    mq.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT)

    # MAIN listener
    LOGGER.info("Setting up MQTT listener...")
    listen_mqtt_nmea_0183()

    # Socket Multicast runs in the foreground so we put the MQTT stuff in a separate thread
    # threading.Thread(target=mq.loop_forever, daemon=True).start()
    