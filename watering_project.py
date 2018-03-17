"""PyCon Project - Using Micropython to water the garden"""


from urequests import get
from ujson import loads
import network
from machine import Pin
import time


def get_date():
    """Returns the date in YYYY-MM-DD format."""
    yql_url = "http://query.yahooapis.com/v1/public/yql?q=select%20item%20from%20weather.forecast%20where%20woeid%20%3D%20818717&format=json&env=store%3A%2F%2Fdatatables.org%2Falltableswithkeys"  
    result = get(yql_url)
    data = loads(result.text)
    created = data['query']['created'].split("T")
    date = created[0]
    del yql_url, result, data, created
    return date

def get_hours():
    """Returns the current hours as an integer."""
    yql_url = "http://query.yahooapis.com/v1/public/yql?q=select%20item%20from%20weather.forecast%20where%20woeid%20%3D%20818717&format=json&env=store%3A%2F%2Fdatatables.org%2Falltableswithkeys"
    
    result = get(yql_url)
    data = loads(result.text)
    created = data['query']['created'].split("T")
    hours = int(created[1][0:2]) + 1
    del yql_url, result, data, created
    return hours


def get_minutes():
    """Returns the current minutes as an integer."""
    yql_url = "http://query.yahooapis.com/v1/public/yql?q=select%20item%20from%20weather.forecast%20where%20woeid%20%3D%20818717&format=json&env=store%3A%2F%2Fdatatables.org%2Falltableswithkeys"

    result = get(yql_url)
    data = loads(result.text)
    created = data['query']['created'].split("T")
    minutes = int(created[1][3:5])
    del yql_url, result, data, created
    return minutes


def weather_suitable_for_watering():
    """Uses the Yahoo Weather API to check for weather."""
    yql_url = "http://query.yahooapis.com/v1/public/yql?q=select%20item%20from%20weather.forecast%20where%20woeid%20%3D%20818717&format=json&env=store%3A%2F%2Fdatatables.org%2Falltableswithkeys"
    
    result = get(yql_url)
    data = loads(result.text)
    print("A")
    print(data)
    if 20 <= get_hours() < 23:  # Evening - Check forecast for tomorrow.
        weather_code = data['query']['results']['channel']['item']['forecast'][1]['code']
        del yql_url, result, data, created
        return weather_code in [19, 20, 21, 22, 26, 27, 28, 29, 30, 31, 32,
                                33, 34, 36]
    else:  # Morning - Check forecast for today.
        print("b")
        weather_code = data['query']['results']['channel']['item']['forecast'][0]['code']
        print("c")
        del yql_url, result, data, created
        return weather_code in [19, 20, 21, 22, 26, 27, 28, 29, 30, 31, 32,
                                33, 34, 36]
                            


def valve_turn_on():
    """Activates the water flow."""
    pin_valve.value(1)
    

def valve_turn_off():
    """Deactivates the water flow."""
    pin_valve.value(0)


def water():
    """Waters the soil for a set amount of time."""
    global days_since_watering, last_day_watered
    if days_since_watering >= 4:
        valve_turn_on()
        time.sleep(300)  # Water on for 5 minutes
        valve_turn_off()
        days_since_watering = 0
        last_day_watered = get_date()


def sensor_selfcheck():
    """Checks tha data from last 4 days and decides
    whether sensor is functional. still WIP"""
    global sensor_data
    """
    sum_total = 0
    if len(sensor_data) >= 4:
        for i in range(4):
            sum_total += sensor_data[-i]
        if sum_total > 0:
            return True
        else:
            return False
    else:  # Not enough data
        # return True
        pass
    """
    return True


def sensor():
    """Checks the humidity of the soil and activates
    the watering facility if the conditions will be right."""
    global sensor_data, last_day_checked, days_since_watering, last_day_watered, days_elapsed 
    decision = pin_sensor
    if last_day_checked == get_date():
        sensor_data[-1] += decision
        last_day_checked = get_date()
    else:
        sensor_data.append(0)
        sensor_data += decision
        del sensor_data[0]

    # sensor_data = [0, 1, 0, 1] - each value is the the sum of all data collected during one day
    if sensor_selfcheck():  # Sensor working properly
        if decision == 0:  # Wet soil - no need to water
            time.sleep(900)  # Sleep for 15 minutes
            if last_day_watered != get_date():
                days_since_watering += 1

        else:  # Dry soil - need to water
            if not wlan.isconnected():  # Internet not accessible
                water()
            else:                   # Internet accessible
                if weather_suitable_for_watering():
                    water()
                else:
                    time.sleep(900)  # Sleep for 15 minutes
                    if last_day_watered != get_date():
                        days_since_watering += 1

    else:  # Sensor not working
        if wlan.isconnected():
            if weather_suitable_for_watering():
                water()
        else:
            water()

    checker()  # In the end always call checker again


def checker():
    """The main function, checks whether the time is in the desired interval,
    if not it sleeps until the time is right."""
    if 20 <= get_hours() < 23 or 5 <= get_hours() < 7:
        sensor()
    else:
        actual_hours = get_hours()
        actual_minutes = get_minutes()
        if 7 <= get_hours() < 20:  # Sleep until 20:00
            desired_hours = 20
            hours_difference = desired_hours - actual_hours
            minutes_difference = 0
            if hours_difference > 0:
                hours_difference -= 1
                minutes_difference = 60 - actual_minutes
            remaining_seconds = (hours_difference * 3600) + (minutes_difference * 60)
            time.sleep(remaining_seconds)
            sensor()
        else:  # Sleep until 5:00
            desired_hours = 5
            hours_difference = 0
            if actual_hours == 23:
                minutes_difference = 60 - actual_minutes
                hours_difference += 5
            else:  # Between 0:00 and 4:59
                minutes_difference = 60 - actual_minutes
                hours_difference = desired_hours - actual_hours - 1
            remaining_seconds = (hours_difference * 3600) + (minutes_difference * 60)
            time.sleep(remaining_seconds)
            sensor()

# ------ Main Programme ------

wlan = network.WLAN(network.STA_IF) # vytvori interface
wlan.active(True)       # aktivuje interface
while not wlan.isconnected():
    wlan.connect("SSID", "password") # pripoj sa k sieti
    while not wlan.isconnected():
        pass

sensor_data = [0]
days_since_watering = 0
last_day_checked = get_date()
days_elapsed = 0

print(weather_suitable_for_watering())
print(get_date())
print(get_hours())
print(get_minutes())

checker()
