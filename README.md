### Description

These are demos of various Linux services, written in Python.

### Demo

You can see me going over the different sections, and installing it here: https://youtu.be/hg-YWVz6J-Y

### Install

1. Create the `/opt/my_service` directory
    - `sudo mkdir /opt/my_service`
    - Note: You may need to change this directory's ownership and/or
    permissions at this point, depending on who you want to be able to
    view/edit these files. For the below steps to work, you'll either need
    to run them as root, or to have modified permissions here

2. Copy `lib.py` and `service.py` to `/opt/my_service`
    - `cp -v lib.py service.py /opt/my_service/`

3. Copy one of the `.py` main files from `main_scripts/` to `/opt/my_service/` and rename it to `main.py`
    - `cp -v main_scripts/simple_main.py /opt/my_service/main.py`

4. Create virtual environment and install requirements into it
    - `python3 -m venv /opt/my_service/venv3`
    - `source /opt/my_service/venv3/bin/activate`
    - `pip install --upgrade pip`
    - `pip install -r requirements.txt`

5. Copy `my_service.service` to `/etc/systemd/system/`
    - `cp -v my_service.service /etc/sytemd/system/`

6. Start the service
    - `sudo systemctl start my_service`

7. Enable the service at boot (so it starts when the system starts)
    - `sudo systemctl enable my_service`

You can now see if your service is running with: `sudo systemctl status my_service`, or see its logs with `sudo journalctl -u my_service`.

### Alternative Service

`service.py` is designed to run `main()` at regular intervals. In addition
to that, if you would like the ability to signal your service that it's
time to run without waiting for the next time it's scheduled to run
`main()`, have a look at `alternative_service.py`.

### Note

At the moment, the `requirements.txt` is not necessary. The project doesn't
use any packages outside of the Python standard library. Eventually, I plan
to show some more advanced features that will use packages from PyPI.
