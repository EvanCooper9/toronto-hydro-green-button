# Homeassistant instructions

1. Clone this repo somewhere on your machine that runs homeassistant
2. Setup the package
```
python -m venv . && source bin/activate && pip install .
```
3. Create a directory somewhere within your homeassistant configuration folder
```
mkdir <path to homeassistant>/energy_data
```
4. Add a script to this folder for running this (run it now to get data)
```
#!/bin/bash
source <path to clone>/bin/activate
python <path to clone>/toronto_hydro_green_button.py --username USERNAME --password PASSWORD --account-id ACCOUNT_ID --sp-id SP_ID --output toronto_hydro.xml --browser chrome
deactivate
```
5. Run the script daily via cron (i.e. at 12:05 am when yesterday's data becomes available)
```
5 0 * * * /./<path to script>/import_toronto_hydro.sh
```
6. Install and seutp the [home-assistant-green-button](https://github.com/rhounsell/home-assistant-green-button/tree/dev)
> Note: as of November 16th 2025, make sure to use the `dev` branch

7. Add an automation to call `green_button.import_espi_xml` every day, after the script runs(i.e. at 12:10 am)
```
alias: Import energy data
description: ""
triggers:
  - trigger: time
    at: "00:10:00"
    weekday:
      - sun
      - mon
      - tue
      - wed
      - thu
      - fri
      - sat
conditions: []
actions:
  - action: green_button.import_espi_xml
    metadata: {}
    data:
      xml_file_path: energy_data/toronto_hydro.xml
mode: single

```

