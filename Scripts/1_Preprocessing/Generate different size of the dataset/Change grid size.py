import pandas as pd


def convert_grid_size(input_file, output_file):
    df_early = pd.read_csv(input_file)
    early_location = df_early.iloc[:, 0].copy()
    final_location = early_location

    for i in range(len(early_location)):
        if int(early_location[i] / 10) % 2 == 0:
            final_location[i] = (int(early_location[i] / 10) - 1) * 10 + early_location[i] % 10

    df_early['location'] = final_location
    df_early.to_csv(output_file, index=False)


input_file = 'input data/BLE_rssi_V3.csv'
output_file = 'output data/BLE_rssi_V11.csv'
convert_grid_size(input_file, output_file)
