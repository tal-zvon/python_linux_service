### Description

These are demos of various Linux services, written in Python.

### Install

  1. Create the `/opt/my_service` directory
  2. Copy one of the .py service files from `services/` (ex: `loop_service.py`) to `/opt/my_service`
    - Rename it to `service.py`
  3. Create virtual environment and install requirements into it
    - `cd /opt/my_service`
    - `python3 -m venv venv3`
    - `source venv3/bin/activate`
    - `pip install --upgrade pip`
    - `pip install -r requirements.txt`
  4. Copy `my_service.service` to `/etc/systemd/system/`
  5. Run `sudo systemctl start my_service` to start the service
  6. Run `sudo systemctl enable my_service` if you want it started at boot, every time

You can now see if your service is running with: `sudo systemctl status my_service`, or see its logs with `sudo journalctl -u my_service`.

At the moment, the `requirements.txt` is not necessary. The project doesn't
use any packages outside of the Python standard library. Eventually, I plan
to show some more advanced features that will use packages from PyPI.
