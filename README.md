This is a demo of a Linux service, written in Python.

Install:
  1. Create the `/opt/my_service` directory
  2. Copy `service.py` to `/opt/my_service`
  3. Copy `my_service.service` to `/etc/systemd/system/`
  4. Run `sudo systemctl start my_service` to start the service
  5. Run `sudo systemctl enable my_service` if you want it started at boot, every time
  
You can now see if your service is running with: `sudo systemctl status my_service`, or see its logs with `sudo journalctl -u my_service`.

At the moment, the `requirements.txt` is not necessary. The project doesn't use any packages outside of the Python standard library. Eventually, I plan to show some more advanced features that will use packages from PyPI.
