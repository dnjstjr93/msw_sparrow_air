#!/usr/bin/python3
import json, sys, serial, threading
# import paho.mqtt.client as mqtt

argv = sys.argv

# # my_lib_name = 'lib_sparrow_air'

# global lib_topic
# global lib_mqtt_client

# global missionPort
# global lteQ


# def on_connect(client,userdata,flags, rc):
#     if rc == 0:
#         print('[msw_mqtt_connect] connect to ', broker_ip)
#     else:
#         print("Bad connection Returned code=", rc)


# def on_disconnect(client, userdata, flags, rc=0):
# 	print(str(rc))


# def on_publish(client, userdata, mid):
#     print("In on_pub callback mid= ", mid)


# def on_subscribe(client, userdata, mid, granted_qos):
#     print("subscribed: " + str(mid) + " " + str(granted_qos))


# def on_message(client, userdata, msg):
#     print(str(msg.payload.decode("utf-8")))


# def msw_mqtt_connect(broker_ip, port):
#     global lib_topic
#     global lib_mqtt_client

#     lib_topic = ''

#     lib_mqtt_client = mqtt.Client()
#     lib_mqtt_client.on_connect = on_connect
#     lib_mqtt_client.on_disconnect = on_disconnect
#     lib_mqtt_client.on_publish = on_publish
#     lib_mqtt_client.on_message = on_message
#     lib_mqtt_client.connect(broker_ip, port)
#     # lib_mqtt_client.subscribe(lib_topic, 0)
#     lib_mqtt_client.loop_start()
#     return lib_mqtt_client


def missionPortOpening(missionPort, missionPortNum, missionBaudrate, missionLTE):
    # global lteQ
    global lib

    if (missionPort == None):
        try:
            missionPort = serial.Serial(missionPortNum, missionBaudrate, timeout = 2)
            print ('missionPort open. ' + missionPortNum + ' Data rate: ' + missionBaudrate)
            mission_thread = threading.Thread(
                target=missionPortData, args=(missionPort, missionLTE)
            )
            mission_thread.start()

            return missionPort

        except serial.SerialException as e:
            missionPortError(e)
        except TypeError as e:
            missionPortClose()
    else:
        if (missionPort.is_open == False):
            missionPortOpen()

            # lteQ.rssi = -Math.random()*100;
            container_name = lib["data"]
            data_topic = '/MUV/data/' + lib["name"] + '/' + container_name
            # send_data_to_msw(data_topic, lteQ)

def missionPortOpen():
    print('missionPort open!')
    missionPort.open()

def missionPortClose():
    global missionPort
    print('missionPort closed!')
    missionPort.close()


def missionPortError(err):
    print('[missionPort error]: ', err)


def airReqMessage(missionPort):
    if missionPort is not None:
        if missionPort.is_open:
            setcmd = "I"
            missionPort.write(setcmd)

def send_data_to_msw (data_topic, obj_data):
    lib_mqtt_client.publish(data_topic, obj_data)


def missionPortData(missionPort, missionLTE):
    global lteQ
    lteQ = dict()
    while True:
        airReqMessage(missionPort)
        missionStr = missionPort.readlines()

        arrLTEQ = missionStr[1].decode("utf-8").split(", ")
        
        print(arrLTEQ)

        # print ('lteQ: \n', lteQ)

        container_name = lib["data"][0]
        data_topic = '/MUV/data/' + lib["name"] + '/' + container_name
        lteQ = json.dumps(lteQ)

        send_data_to_msw(data_topic, lteQ)

        lteQ = dict()
        # print(lteQ)


if __name__ == '__main__':
    my_lib_name = 'lib_sparrow_air'

    try:
        lib = dict()
        with open(my_lib_name + '.json', 'r') as f:
            lib = json.load(f)
            lib = json.loads(lib)

    except:
        lib = dict()
        lib["name"] = my_lib_name
        lib["target"] = 'armv6'
        lib["description"] = "[name] [portnum] [baudrate]"
        lib["scripts"] = './' + my_lib_name + ' /dev/ttyUSB4 115200'
        lib["data"] = ['LTE']
        lib["control"] = []
        lib = json.dumps(lib, indent=4)
        lib = json.loads(lib)

        with open('./' + my_lib_name + '.json', 'w', encoding='utf-8') as json_file:
            json.dump(lib, json_file, indent=4)


    lib['serialPortNum'] = argv[0]
    lib['serialBaudrate'] = argv[1]

    broker_ip = 'localhost'
    port = 1883

    # msw_mqtt_connect(broker_ip, port)

    missionPort = None
    missionPortNum = lib["serialPortNum"]
    missionBaudrate = lib["serialBaudrate"]
    missionPortOpening(missionPortNum, missionBaudrate)
