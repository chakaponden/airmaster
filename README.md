This script provides polling mechanism with json output for Weeksky Instruments Air Master 2 AM7 p indoor air quality detector, if equipped with wifi module.

Single request:

python3 ./scrape.py -h 192.168.88.13

Continous poll:

python3 ./scrape.py -h 192.168.88.13 poll


Example output:
```
❯ python3 ./scrape.py
{
    "PM2.5": "10",
    "PM10": "12",
    "HCHO": "0.10",
    "TVOC": "1.13",
    "CO2": "655",
    "TEMP": "23.90",
    "RH": "63.00"
}
```

# AirMaster AM7 plus Wi-Fi protocol: #
## connect ##
1. you -> AirMaster: 0000000303000006
2. AirMaster -> you: 000000030f000007000a4d54464c50464d475244
3. you -> AirMaster: 000000030f000008000a4d54464c50464d475244
4. AirMaster -> you: 000000030400000900
5. AirMaster -> you: 000000031a0000910407ff09646400c8001d00210001000f01a014820eba00

## request data ##
1. you -> AirMaster: 0000000303000015
2. AirMaster -> you: 0000000303000016
3. AirMaster -> you: 000000031a0000910407ff09646400c8001d00210001000f01a014820eba00
