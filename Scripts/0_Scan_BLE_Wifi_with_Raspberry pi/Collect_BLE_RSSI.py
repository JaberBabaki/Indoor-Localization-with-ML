import Scan_BLE as scan_ble
import sys
import datetime
import bluetooth._bluetooth as bluez
import time
import RPi.GPIO as GPIO
from threading import Thread
import requests
import json

url = 'http://185.110.188.201:2020/recordloc'
device_id = "Ras_2ACBCB-RPI4B"

GPIO.setmode(GPIO.BCM)
GPIO.setup(26, GPIO.OUT)

dev_id = 0
try:
    sock = bluez.hci_open_dev(dev_id)
    print "Ble scan start"

except:
    print "There is not access to BLE devices"
    sys.exit(1)

scan_ble.hci_le_set_scan_parameters(sock)
scan_ble.hci_enable_le_scan(sock)

# ##### az scenario 2 bee baad comment she
# f = open('../Dataset/..Dataset/Labeled_rssi_data.csv', 'w+')
# f = open('../Dataset/..Dataset/UnLabeled_rssi_data.csv', 'w+')
# f.write('location,date,beacon1,beacon2,beacon3,beacon4,beacon5')
# f.close()

exact_mac = ['c5:79:7a:8c:1c:81', 'de:23:66:2f:69:4f', 'c3:fd:af:e3:fe:7f',
             'd4:9a:ec:67:8d:cf',
             'e6:70:03:08:32:65']
csv_row = {}


def make_noise():
    while True:
        GPIO.output(26, GPIO.HIGH)
        time.sleep(0.1)
        GPIO.output(26, GPIO.LOW)
        time.sleep(4.9)



def collect_dataset():
    counter = 0
    while True:

        print '\n'
        print "----------"

        id_rssi = {}

        if len(csv_row) > 1:

            # start_time = time.time()
            all_keys = list(csv_row.keys())
            # print str(all_keys[0].split(' ')[1].split(':')[1]).zfill(2)
            # print all_keys[1]
            # all_keys[0].split(' ')[1].split(':')[1] = str(all_keys[0].split(' ')[1].split(':')[1]).zfill(2)
            # all_keys[1].split(' ')[1].split(':')[1] = str(all_keys[1].split(' ')[1].split(':')[1]).zfill(2)
            # all_keys[0].split(' ')[1].split(':')[2] = str(all_keys[0].split(' ')[1].split(':')[2]).zfill(2)
            # all_keys[1].split(' ')[1].split(':')[2] = str(all_keys[1].split(' ')[1].split(':')[2]).zfill(2)
            first_val = all_keys[0].split(' ')[1].split(':')
            second_val = all_keys[1].split(' ')[1].split(':')
            # first_val[1] = int(str(first_val[1]).zfill(2))
            # second_val[1] = int(str(second_val[1]).zfill(2))
            # print first_val
            # print second_val
            # print '&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&'
            # print all_keys[0]
            # print all_keys[1]
            if all_keys[1].split(' ')[2] != all_keys[0].split(' ')[2] and second_val[0] != 12:
                second_val[0] += 12
            # print first_val
            # print '********'
            # print second_val
            # print '********'
            if (first_val[0] * 3600 + first_val[1] * 60 + first_val[2]) < (
                    second_val[0] * 3600 + second_val[1] * 60 + second_val[2]):
                first_key = all_keys[0]
            else:
                first_key = all_keys[1]

            # first_key.split(' ')[1].split(':')[1] = str(first_key.split(' ')[1].split(':')[1]).zfill(2)
            # first_key.split(' ')[1].split(':')[2] = str(first_key.split(' ')[1].split(':')[2]).zfill(2)
            #### save to csv
            for item in csv_row[first_key]['rssi']:
                if item[0] not in id_rssi:
                    id_rssi[item[0]] = {'rssi': [int(item[1])], 'time': first_key}
                else:
                    id_rssi[item[0]]['rssi'].append(int(item[1]))
            for id in id_rssi:
                id_rssi[id]['rssi'] = sum(id_rssi[id]['rssi']) / len(id_rssi[id]['rssi'])
            print id_rssi
            print '\n'
            csv_data = []
            for id in exact_mac:
                if id in id_rssi:
                    csv_data.append(id_rssi[id]['rssi'])
                else:
                    csv_data.append(-200)

            #### save to csv
            f = open('../Dataset/..Dataset/Labeled_rssi_data.csv', 'a')
            # f = open('../Dataset/..Dataset/UnLabeled_rssi_data.csv', 'a')

            devs = []
            for o in range(len(exact_mac)):
                devs.append({'longitude': 0,
                             'latitude': 0,
                             'altitude': 0,
                             'mac_addr': exact_mac[o],
                             'rssi': csv_data[o]
                             })
            myobj = {
                "device_id": device_id,
                "number_of_devices": len(exact_mac),
                "devices": devs,
            }

            requests.post(url, data=json.dumps(myobj))
            f.write('\n' +
                    '?' + ',' + first_key + ',' +
                    str(csv_data[0]) + ',' + str(csv_data[1]) + ',' + str(csv_data[2]) + ',' + str(
                csv_data[3]) + ',' + str(csv_data[4]))
            f.close()

            csv_row.pop(first_key)
            counter += 1
            # print("--- %s seconds ---" % (time.time() - start_time))
            print 'counter / 5: '
            print counter/5
            print 'counter: '
            print counter

        returnedList = scan_ble.parse_events(sock, 1)
        ############ comment she
        # time.sleep(5)

        times = datetime.datetime.now()
        for beacon in returnedList:
            which_ble = beacon.split(',')
            if which_ble[0] in exact_mac:
                hour = times.hour
                if hour > 11 and hour != 12:
                    hour -= 12
                    csv_time = str(times.month) + '-' + str(times.day) + '-' + str(times.year) + ' ' + str(
                        hour) + ':' + str(
                        times.minute).zfill(2) + ':' + str(times.second).zfill(2) + ' ' + 'PM'
                elif hour > 11 and hour == 12:
                    csv_time = str(times.month) + '-' + str(times.day) + '-' + str(times.year) + ' ' + str(
                        hour) + ':' + str(
                        times.minute).zfill(2) + ':' + str(times.second).zfill(2) + ' ' + 'PM'
                else:
                    csv_time = str(times.month) + '-' + str(times.day) + '-' + str(times.year) + ' ' + str(
                        hour) + ':' + str(
                        times.minute).zfill(2) + ':' + str(times.second).zfill(2) + ' ' + 'AM'
                if csv_time not in csv_row:
                    csv_row[csv_time] = {'id': [which_ble[0]], 'rssi': [[which_ble[0], which_ble[5]]]}
                elif which_ble[0] not in csv_row[csv_time]['id']:
                    csv_row[csv_time]['id'].append(which_ble[0])
                    csv_row[csv_time]['rssi'].append([which_ble[0], which_ble[5]])
                elif which_ble[0] in csv_row[csv_time]['id']:
                    csv_row[csv_time]['rssi'].append([which_ble[0], which_ble[5]])
                    # mean = 0
                    # for item in csv_row[csv_time][which_ble[0]]:
                    #     mean += item
                    # [csv_time][which_ble[0]]
                # print datetime.datetime.now()
        # print csv_row


if __name__ == '__main__':
    # time.sleep(60)
    Thread(target=collect_dataset).start()
    Thread(target=make_noise).start()
