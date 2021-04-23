import pandas as pd
from RSSI_Filter_methods import *


def filter_noise(filter_method, file_name):
    file = pd.read_csv(file_name)
    early_data = file
    end_of_file_name = file_name.split('input data/BLE_rssi_Before_Filter_')[1]
    print(end_of_file_name)
    if filter_method == 'kalman_filter':
        resulted_data = early_data
        for i in range(5):
            signal = file['beacon' + str(i + 1)]
            signal_kalman_filter = kalman_filter(signal, A=1, H=1, Q=1.6, R=6)
            for j in range(len(signal_kalman_filter)):
                if j > 0:
                    signal_kalman_filter[j] = signal_kalman_filter[j][0]
                resulted_data['beacon' + str(i + 1)][j] = signal_kalman_filter[j]
        resulted_data.to_csv('output data/BLE_rssi_after_Kalman_Filter_' + end_of_file_name, index=False)

    elif filter_method == 'particle_filter':
        resulted_data = early_data
        for i in range(5):
            signal = file['beacon' + str(i + 1)]
            # print(signal)
            signal_particle_filter = particle_filter(signal, quant_particles=100, A=1, H=1, Q=1.6,
                                                     R=6)  # BLE_rssi_V10.csv
            for j in range(len(signal_particle_filter)):
                resulted_data['beacon' + str(i + 1)][j] = signal_particle_filter[j]
        resulted_data.to_csv('output data/BLE_rssi_after_Particle_Filter_' + end_of_file_name, index=False)

    elif filter_method == 'gray_filter':
        resulted_data = early_data
        for i in range(5):
            signal = file['beacon' + str(i + 1)]
            signal_gray_filter = gray_filter(signal, N=8)
            for j in range(len(signal_gray_filter)):
                # print('signal_gray_filter[j] : ')
                # print(signal_gray_filter[j])
                if np.isnan(signal_gray_filter[j]):
                    resulted_data['beacon' + str(i + 1)][j] = early_data['beacon' + str(i + 1)][j]
                else:
                    resulted_data['beacon' + str(i + 1)][j] = signal_gray_filter[j]

        resulted_data.to_csv('output data/BLE_rssi_after_Gray_Filter_' + end_of_file_name, index=False)

    elif filter_method == 'fft_filter':
        resulted_data = early_data
        for i in range(5):
            signal = file['beacon' + str(i + 1)]
            signal_fft_filter = fft_filter(signal, N=10, M=1)
            for j in range(len(signal_fft_filter)):
                resulted_data['beacon' + str(i + 1)][j] = signal_fft_filter[j]
        resulted_data.to_csv('output data/BLE_rssi_after_FFT_Filter_' + end_of_file_name, index=False)

    else:
        print('Error : Invalid name for filtering method')


file_name = 'input data/BLE_rssi_Before_Filter_Grid_1.5m_2.5m.csv'
# file_name = 'input data/BLE_rssi_Before_Filter_Grid_1.5m_1.25m.csv'
# filter_noise('kalman_filter', file_name)
# filter_noise('particle_filter', file_name)
filter_noise('gray_filter', file_name)
# filter_noise('fft_filter', file_name)
