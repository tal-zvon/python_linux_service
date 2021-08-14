### Description

These are demos of various Linux services, written in Python.

### Install

1. Create the `/opt/my_service` directory
    - `sudo mkdir /opt/my_service`
    - Note: You may need to change this directory's ownership and/or
    permissions at this point, depending on who you want to be able to
    view/edit these files. For the below steps to work, you'll either need
    to run them as root, or to have modified permissions here

2. Copy `lib.py` and `service.py` to `/opt/my_service`
    - `cp -v lib.py service.py /opt/my_service/service.py`

3. Copy one of the `.py` main files from `main_scripts/` to `/opt/my_service/` and rename it to `main.py`
    - `cp -v main_scripts/simple_main.py /opt/my_service/main.py`

4. Create virtual environment and install requirements into it
    - `cd /opt/my_service`
    - `python3 -m venv venv3`
    - `source venv3/bin/activate`
    - `pip install --upgrade pip`
    - `pip install -r requirements.txt`

5. Copy `my_service.service` to `/etc/systemd/system/`

6. Run `sudo systemctl start my_service` to start the service

7. Run `sudo systemctl enable my_service` if you want it started at boot, every time

You can now see if your service is running with: `sudo systemctl status my_service`, or see its logs with `sudo journalctl -u my_service`.

At the moment, the `requirements.txt` is not necessary. The project doesn't
use any packages outside of the Python standard library. Eventually, I plan
to show some more advanced features that will use packages from PyPI.
