from cmath import e
import pynmea2


nmea_msg = {"sent_at": "2022-10-21T05:58:57.302217+00:00", "message": "$IIMWV,207,R,000.08,M,A*1D"}
print(nmea_msg["message"])
nmea_str = nmea_msg["message"]

nmea_parameters = {}

try:
    nmea_type_msg = nmea_str.split(",")[0].replace("$", "")

    if nmea_type_msg == "PASHR":
        PASHR_items = nmea_str.split(",")
        for idx, item in enumerate(PASHR_items):
            try:
                PASHR_items[idx] = float(PASHR_items[idx])
            except:
                pass

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

        # Debug
        print(msg.sentence_type)
        print(msg.fields)
        print(msg.data)
        print(repr(msg))

        if msg.sentence_type == "GGA":
            GGA = {
                "timestamp": msg.timestamp.isoformat(),
                "lon": float(msg.lon) / 100,
                "lon_dir": msg.lon_dir,
                "lat": float(msg.lat) / 100,
                "lat_dir": msg.lat_dir,
                "altitude": msg.altitude,
                "lat_dir": msg.lat_dir,
                "num_satellites": msg.num_sats,
                "gps_quality": msg.gps_qual,
            }
            nmea_parameters.update(GGA)

        elif msg.sentence_type == "RMC":
            RMC = {
                "datestamp": msg.datestamp.isoformat(),
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
                "rot": msg.rate_of_turn,
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
                "status": msg.status
            }
            nmea_parameters.update(MWV)

except Exception as e:
    print(e)
 

print("FINAL:", nmea_parameters)
from decimal import *
print(Decimal('207'))