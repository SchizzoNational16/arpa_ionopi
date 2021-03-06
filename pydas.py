#!/usr/bin/python3
# pylint: disable=locally-disabled, broad-except, line-too-long
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
#  Copyright (c) 1995-2019, Ecometer s.n.c.
#  Author: Paolo Saudin.
#
#  Desc : Collect data from temperature sensors
#  File : pydas.py
#
#  Date : 2019-03-04 15:31
# ----------------------------------------------------------------------
""" Setup
    sudo apt-get install python3-pip
    pip3 install -r requirements.txt
    mkdir -p ~/bin/pydas/
    scp -r /cygdrive/c/Dev/locations/net_ecometer/Prodotti/Sferalabs/iono/python/* pi@192.168.168.221:~/bin/pydas/
    python3 ~./bin/pydas/pydas.py
"""
import os
import logging
import logging.handlers
import platform
import time
from datetime import datetime
import threading
# custom
from functions import create_log, clear_screen, unix_time
from iono_w1 import IonoW1
import config

def polling(module, conf):
    """ polling """
    logging.debug("Function polling")
    while True:

        # check for mean
        now = datetime.now()

        # get the total seconds
        ptime = unix_time(now)

        # check for new mean
        if int(ptime / conf['store_time']) == (ptime / conf['store_time']):
            # new mean
            logging.info("*** New mean ***")

            # store values to csv file
            module.store_ced_data_csv()

        # check for new polling
        if int(ptime / conf['polling_time']) == (ptime / conf['polling_time']):

            # new polling
            logging.info("--- New polling ---")

            # # switch led on
            # #module.set_led_status(True)
            # #module.set_relay_status(1, True)
            # #module.set_open_collector_status(1, True)

            # # polling
            # module.get_digital_input()
            # module.get_analog_input()
            # module.get_relay_output()
            # module.get_open_collector_output()
            # module.get_one_wire_input()

            # # store values to csv file
            # module.store_data_csv()

            # # append new temperature data
            # # to make later mean on store_time
            # module.append_temperature()

            # # analyse current alarm
            # module.analyze_alarm()

            # # reset digital inputs events status
            # module.reset_digital_input_events()

            # # switch led off
            # #module.set_led_status(False)
            # #module.set_relay_status(1, False)
            # #module.set_open_collector_status(1, False)

            #
            # arpa stations
            #
            if conf['use_ai']:
                module.get_analog_input()

            if conf['use_io']:
                module.get_digital_input()

            if conf['use_1w']:
                module.get_one_wire_input()

            # append new data to make later mean on store_time
            # needed by store_ced_data_csv() function
            module.append_ced_data_arrays()

            # store values to csv file
            module.store_data_csv()

            # analyse current alarm
            module.analyze_alarm()

            # wait to avoid further calls in the same second
            time.sleep(1.5)

        # sleep
        time.sleep(0.1)

def main():
    """ Main function """
    module = None
    try:

        # Clear
        clear_screen()

        # Logging debug | DEBUG INFO
        create_log(logging.DEBUG)

        # Start
        now = datetime.now()
        logging.info("Program start @ %s on %s", now.strftime("%Y-%m-%d %H:%M:%S"), platform.system())

        # path
        data_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data')
        if not os.path.exists(data_path):
            os.mkdir(data_path)
        config.main['data_path'] = data_path

        ftp_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'ftp')
        if not os.path.exists(ftp_path):
            os.mkdir(ftp_path)
        config.main['ftp_path'] = ftp_path

        # create main module object
        logging.info("Creating main iono object...")
        module = IonoW1(config.main)

        # start main loop
        logging.info("Starting main thread")
        main_thread = threading.Thread(target=polling, daemon=True, args=[module, config.main])
        main_thread.start()

        # loop forever waiting for user ctrl+c to exit
        while True:
            time.sleep(0.1)

    except KeyboardInterrupt:
        pass
    except Exception as ex:
        logging.critical("An exception was encountered in main(): %s", str(ex))
    finally:
        if module:
            module.cleanup()
        logging.info("End")

if __name__ == '__main__':
    main()
