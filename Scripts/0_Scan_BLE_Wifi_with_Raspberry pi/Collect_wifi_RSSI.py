from Scan_Wifi import *
import sys
import datetime
import time
import RPi.GPIO as GPIO
import threading
from threading import Thread
import requests
import json

csv_row = {}
devices = main()
# print devices
exact_mac = ['6A:5A:CF:8D:06:7E', '6C:AD:EF:4A:CF:4A', 'D4:6E:0E:59:99:E6', 'E8:94:F6:D9:0C:16',
             'D8:32:14:E4:6C:61']
# for i in range(1, len(devices)):
#     print devices[i][1]
#     print devices[i][3].split(' d')[0]
url = 'http://185.110.188.201:2020/recordloc'
device_id = "Ras_2ACBCB-RPI4B"

GPIO.setmode(GPIO.BCM)
GPIO.setup(26, GPIO.OUT)

dev_id = 0

# ##### az scenario 2 bee baad comment she
# f = open('../Dataset/Labeled_rssi_data_wifi.csv', 'w+')
f = open('../Dataset/UnLabeled_rssi_data_wifi.csv', 'w+')
f.write('location,date,b3001,b3002,b3003,b3004,b3005')
f.close()



def make_noise():
    while True:
        GPIO.output(26, GPIO.HIGH)
        time.sleep(0.1)
        GPIO.output(26, GPIO.LOW)
        time.sleep(4.9)


def collect_dataset():
    start_flag = True
    while start_flag:
        print '\n'
        print "----------"
        id_rssi = {}
        if len(csv_row) > 1:
            # start_time = time.time()
            all_keys = list(csv_row.keys())
            # print str(all_keys[0].split(' ')[1].split(':')[1]).zfill(2)
            # print all_keys[1]
            first_val = all_keys[0].split(' ')[1].split(':')
            second_val = all_keys[1].split(' ')[1].split(':')
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
            # f = open('../Dataset/Labeled_rssi_data_wifi.csv', 'a')
            f = open('../Dataset/UnLabeled_rssi_data_wifi.csv', 'a')

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

            stop_flag = True
            stop_counter = 0
            for id in exact_mac:
                if id not in id_rssi:
                    stop_counter += 1

            if stop_counter > 2:
                stop_flag = False


            if stop_flag == True:
                requests.post(url, data=json.dumps(myobj))
                f.write('\n' +
                        '?' + ',' + first_key + ',' +
                        str(csv_data[0]) + ',' + str(csv_data[1]) + ',' + str(csv_data[2]) + ',' + str(
                    csv_data[3]) + ',' + str(csv_data[4]))
                f.close()

                csv_row.pop(first_key)

            # print("--- %s seconds ---" % (time.time() - start_time))

        ############ comment she
        # time.sleep(5)

        times = datetime.datetime.now()
        devices = main()
        del devices[0]
        for wifi in devices:
            which_wifi = wifi[1]
            if which_wifi in exact_mac:
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
                    csv_row[csv_time] = {'id': [which_wifi], 'rssi': [[which_wifi, wifi[3].split(' d')[0]]]}
                elif which_wifi not in csv_row[csv_time]['id']:
                    csv_row[csv_time]['id'].append(which_wifi)
                    csv_row[csv_time]['rssi'].append([which_wifi, wifi[3].split(' d')[0]])
                # elif which_wifi in csv_row[csv_time]['id']:
                #     csv_row[csv_time]['rssi'].append([which_wifi, wifi[3].split(' d')[0]])
        print 'each row : '
        print csv_row


if __name__ == '__main__':
    # time.sleep(30)
    Thread(target=collect_dataset).start()
    Thread(target=make_noise).start()
