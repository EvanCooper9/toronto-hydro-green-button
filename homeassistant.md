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
5. Run the script daily via cron (i.e. at 1:00 am when the previous day's data becomes available)
```
0 1 * * * /./<path to script>/import_toronto_hydro.sh
```
6. Install and seutp the [home-assistant-green-button](https://github.com/rhounsell/home-assistant-green-button/tree/dev)
> Note: as of November 16th 2025, make sure to use the `dev` branch

7. Add the [Folder Watcher](https://www.home-assistant.io/integrations/folder_watcher) integration, and point to the output file, i.e. `/config/energy_data/toronto_hydro.xml`.

8. Add an automation to call `green_button.import_espi_xml` when the file changes
```
alias: Import Toronto Hydro data
description: ""
triggers:
  - trigger: state
    entity_id:
      - event.folder_watcher_config_energy_data
conditions: []
actions:
  - action: green_button.import_espi_xml
    metadata: {}
    data:
      xml_file_path: energy_data/toronto_hydro.xml
mode: single
```

