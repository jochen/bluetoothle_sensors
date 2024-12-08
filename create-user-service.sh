#!/bin/bash
#

APP=bluetoothle_sensors
START=monitor.py

export START

mkdir -p ~/.config/systemd/user

cat $APP.service | envsubst | tee ~/.config/systemd/user/$APP.service

systemctl --user enable $APP

systemctl --user start $APP

sudo loginctl enable-linger pi


echo "get output with:"
echo "journalctl --user -xfu $APP"

