# Crowsnest-connector-mqtt-nmea

A crowsnest microservice for connecting to NMEA MQTT stream and parsing NMEA to JSON.

## How it works

For now, this microservice just does the basics.

- Connects to MQTT broker 
- Transform 0183 NMEA sentences to JSON
- Wraps into a brefv message over MQTT the RAW NMEA and JSON parsed data

### Typical setup: docker-compose.mqtt-nmea.yml

```yaml
version: "3"
services:
  multicast-nmea:
    image: ghcr.io/mo-rise/crowsnest-connector-mqtt-nmea:latest
    restart: unless-stopped
    network_mode: "host"

```

## Development setup

To setup the development environment:

```bash
    python3 -m venv venv
    source ven/bin/activate
```

Install everything thats needed for development:

```bash
    pip install -r requirements_dev.txt
```

To run the linters:

```bash
    black main.py tests
    pylint main.py
```

To run the tests:

```bash
    no automatic tests yet...
```

Add brefv as submodule:

```bash
git submodule add <url>

# Once the project is added to your repo, you have to init and update it.
git submodule init
git submodule update

```

Credit to https://github.com/Knio/pynmea2

## License

Apache 2.0, see [LICENSE](./LICENSE)

## Extra Notes NMEA parser to brefv

Messages types

```bash
(Not parsed to brefv)
$GNGSA,M,1,04,06,07,09,11,16,20,,,,,,1.53,1.09,1.07,1*0F
<GSA(
    mode='M', (M= Manual, A=Automatic)
    mode_fix_type='1', (Fix type: 1=Not available, 2=2D, 3=3D)

    sv_id01='04', sv_id02='06', sv_id03='07', sv_id04='09'
    sv_id05='11', sv_id06='16', sv_id07='20', sv_id08='', sv_id09=''
    sv_id10='', sv_id11='', sv_id12='',

    pdop='1.53', (PDOP 0.5 to 99.9)
    hdop='1.09', (HDOP 0.5 to 99.9)
    vdop='1.07' (VDOP 0.5 to 99.9)
    ) data=['1']>


--------
(TODO)
GGA – Global positioning system (GPS) fix data
$GNGGA,114835.60,5742.5522736,N,01156.8392494,E,5,15,1.1,5.18,M,35.78,M,,*77
<GGA(
    timestamp=datetime.time(11, 48, 35, 600000),  (UTC)
    lat='5742.5522736', (Latitude, the format is ddmm.mmmmmmm)
    lat_dir='N', (hemisphere, N or S )
    lon='01156.8392494', (Longitude, the format is dddmm.mmmmmmm)
    lon_dir='E', (hemisphere, E or W)
    gps_qual=5, (GPS quality indicator:
                    0: GNSS fix not available
                    1: GNSS fix valid
                    4: RTK fixed ambiguities
                    5: RTK float ambiguities
                )
    num_sats='15', (Number of satellites used, Fixed length 01 for single digits)

    horizontal_dil='1.1', (HDOP, XX.X Variable/fixed length 1 digit after dot, variable before)
    altitude=5.18,  (Altitude geoid height)
    altitude_units='M',  (Unit of altitude)
    geo_sep='35.78',
    geo_sep_units='M',
    age_gps_data='',
    ref_station_id='')>


--------
(TODO)
PASHR – Attitude Data
$PASHR,114835.60,027.23,T,-75.83,,,3.158,,4.831,1,*22
<ASHRATT(
    _r='R',
    1) timestamp=datetime.time(11, 48, 35, 600000), (UTC)
    2) true_heading=27.23, (Degrees)
    3) is_true_heading='T',
    4) roll=-75.83, (Degrees)
    5) pitch=None, (Degrees)
    6) heading=None,
    7) roll_accuracy=3.158, (Degrees)
    8) pitch_accuracy=None,
    9) heading_accuracy=4.831, (Degrees, standard deviation)
    aiding_status=Decimal('1'), (0: No position 1: RTK float position 2: RTK fixed position)
    imu_status=None)>


--------
RMC – Recommended minimum specific GNSS data
$GNRMC,114835.60,A,5742.5522736,N,01156.8392494,E,,,191022,,W,D,V*61
<RMC(
    timestamp=datetime.time(11, 48, 35, 600000),
    status='A',
    lat='5742.5522736',
    lat_dir='N',
    lon='01156.8392494',
    lon_dir='E',
    spd_over_grnd=None,
    true_course=None,
    datestamp=datetime.date(2022, 10, 19),
    mag_variation='',
    mag_var_dir='W')
    data=['D', 'V']>

--------
VTG – Course over ground and ground speed
$GNVTG,,T,,M,,N,,K,A*3D
<VTG(
    true_track=None,
    true_track_sym='T',
    mag_track=None,
    mag_track_sym='M',
    spd_over_grnd_kts=None,
    spd_over_grnd_kts_sym='N',
    spd_over_grnd_kmph=None,
    spd_over_grnd_kmph_sym='K',
    faa_mode='A')>


--------
PASHR  – Attitude Data
$PASHR,114835.60,027.23,T,-75.83,,,3.158,,4.831,1,*22
<ASHRATT(
    _r='R',
    timestamp=datetime.time(11, 48, 35, 600000),
    true_heading=27.23,
    is_true_heading='T',
    roll=-75.83, pitch=None,
    heading=None,
    roll_accuracy=3.158,
    pitch_accuracy=None,
    heading_accuracy=4.831,
    aiding_status=Decimal('1'),
    imu_status=None)>


--------
$GNZDA,114835.60,19,10,2022,,*7F
<ZDA(
    timestamp=datetime.time(11, 48, 35, 600000),
    day=19,
    month=10,
    year=2022,
    local_zone=None,
    local_zone_minutes=None)>

--------
$GNGST,114835.60,,,,,0.264,0.170,0.334*47
<GST(
    timestamp=datetime.time(11, 48, 35, 600000),
    rms=None,
    std_dev_major=None,
    std_dev_minor=None,
    orientation=None,
    std_dev_latitude=0.264,
    std_dev_longitude=0.17,
    std_dev_altitude=0.334)>

--------
$GNTHS,27.23,V*3A
('Unknown sentence type GNTHS,', '$GNTHS,27.23,V*3A')

--------
(TODO)
$GNROT,0.0,V*38
<ROT(rate_of_turn='0.0', status='V')>

Windobserver-65

$IIMWV,207,R,000.08,M,A*1D
MWV
(('Wind angle', 'wind_angle', <class 'decimal.Decimal'>), ('Reference', 'reference'), ('Wind speed', 'wind_speed', <class 'decimal.Decimal'>), ('Wind speed units', 'wind_speed_units'), ('Status', 'status'))
['207', 'R', '000.08', 'M', 'A']

<MWV(
    wind_angle=Decimal('207'), (Degrees 0 to 359)
    reference='R',  (R= Relative / T=True)
    wind_speed=Decimal('0.08'), 
    wind_speed_units='M', (K=Knots / M=Meter per second)
    status='A' (A= Data valid / V= Invalid)
    )>

```
