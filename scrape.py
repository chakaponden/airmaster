import socket
import binascii
import sys
import struct
import json
import itertools

# AirMaster AM7 Wi-Fi protocol:
# 1. connect
# you -> AirMaster 0000000303000006
# AirMaster -> you 000000030f000007000a4d54464c50464d475244
# you -> AirMaster 000000030f000008000a4d54464c50464d475244
# AirMaster -> you 000000030400000900
# AirMaster -> you 000000031a0000910407ff09646400c8001d00210001000f01a014820eba00

# 2. request data
# you -> AirMaster 0000000303000015
# AirMaster -> you 0000000303000016
# AirMaster -> you 000000031a0000910407ff09646400c8001d00210001000f01a014820eba00

if "poll" in sys.argv:
    poll = True
else:
    poll = False

if "-h" in sys.argv:
    host = sys.argv[sys.argv.index("-h")+1]
else:
    host = '192.168.88.13'

if "-p" in sys.argv:
    port = sys.argv[sys.argv.index("-p")+1]
else:
    port = 12416

def airmaster_connect(host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(30)
    s.connect((host, int(port)))

    # you -> AirMaster 0000000303000006
    pair_message = bytes.fromhex('0000000303000006')
    s.settimeout(None)
    s.sendall(pair_message)
    # AirMaster -> you 000000030f000007000a4d54464c50464d475244
    pair_response = s.recv(1024)
    #print("pair_response: " + pair_response.hex())

    # you -> AirMaster 000000030f000008000a4d54464c50464d475244
    handshake_message = bytearray(pair_response)
    confirmation_byte = handshake_message[7] + 1;
    handshake_message = handshake_message[0:7] + confirmation_byte.to_bytes(1, byteorder="big") + handshake_message[8:]; 
    s.sendall(handshake_message)
    # AirMaster -> you 000000030400000900
    handshake_response = s.recv(1024)
    #print("handshake_response: " + handshake_response.hex())

    # AirMaster -> you 000000031a0000910407ff09646400c8001d00210001000f01a014820eba00
    data = s.recv(1024)
    # do not handle AirMaster response
    #if len(data) > 29:
    #    decode(data)

    return s

def airmaster_request_data(s, timeout):
    # you -> AirMaster 0000000303000015
    request_data = bytes.fromhex('0000000303000015')
    s.settimeout(timeout)
    s.sendall(request_data)
    # AirMaster -> you 0000000303000016
    data = s.recv(1024)
    if data.hex() == '0000000303000016':
        # AirMaster -> you 000000031a0000910407ff09646400c8001d00210001000f01a014820eba00
        data = s.recv(1024)
    return data

def decode(data):
    labels = {
        17: "PM2.5",
        19: "PM10",
        21: "HCHO",
        22: "hide",
        23: "TVOC",
        24: "CO2",
        26: "TEMP",
       # 27: "TEMP",
        28: "RH"
    }
    types = {
        17: "H",
        19: "H",
        24: ">H",
        26: ">H",
        #27: ">H",
        28: ">H"
    }
    sensors = { }
    bytemap = list(itertools.chain(range(17,21,2), range(21, 24, 1), range(24, 26, 2), range(26, 28, 2), range(28, 31, 2)))
    for index, bytenum in enumerate(bytemap):
        if len(bytemap) <= index + 1:
            continue
        datasize = bytemap[index+1]-bytenum

        if bytenum in labels:
            label = labels[bytenum]
        else:
            label = str(bytenum)

        if bytenum in types:
            datatype = types[bytenum]
        elif datasize == 2:
            datatype = 'e'
        elif datasize == 1:
            datatype = 'B'
        
        try:
            prepend = sensors[label] + "."
        except:
            prepend = ""
        try:
            val = str(struct.unpack(datatype,data[bytenum:bytemap[index+1]])[0])
            if datatype == "B" and len(val) == 1 and val != "0":
                val = "0" + val
            if label == "hide":
                continue
            if label in ["HCHO", "TVOC", "RH"]:
                val = str("%.2f" % (float(val) / 100))
            if label == "TEMP":
                val = str("%.2f" % (float(val) / 100 - 35))
            sensors[label] = prepend + val
        except:
            print(str(datasize) + ' ' + str(bytenum))
    
    print(json.dumps(sensors, indent=4))

# re initiate connection only if:
# 1. we are trying to connect for the first time
# 2. last time we did not get data we expected (> 29 bytes)
reconnect = True
while True:
    if reconnect:
        s = airmaster_connect(host, port)
    response_data = airmaster_request_data(s, 60)
    if len(response_data) > 29:
        reconnect = False
        decode(response_data)
        if not poll:
            break
    else:
        reconnect = True
        s.close()
