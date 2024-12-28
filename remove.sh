#!/bin/sh
echo ">>> installing kodi needs privileges >>> no password set yet? >>> simply enter 'passwd'" 
sudo steamos-readonly disable
sudo -S pacman -R --noconfirm  kodi-addon-inputstream-adaptive kodi-addon-inputstream-rtmp kodi-addon-peripheral-joystick kodi-addon-visualization-shadertoy kodi-addon-screensaver-pingpong
sudo -S pacman -R --noconfirm kodi-platform kodi
#rm -R /home/deck/.kodi
sudo steamos-readonly enable

