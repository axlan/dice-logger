#!/usr/bin/env sh

python dice_logger.py --host=192.168.1.110 -o /datadir&

python plot_http_server.py -o /datadir&

wait
