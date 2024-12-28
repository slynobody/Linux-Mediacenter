#!/bin/sh
echo ">>> installing kodi needs privileges >>> no password set yet? >>> simply enter 'passwd'" 
sudo steamos-readonly disable
sudo pacman-key --init
sudo pacman-key --populate archlinux
sudo pacman-key --populate holo
sudo pacman -S  gstreamer-vaapi gst-plugin-pipewire gst-plugins-bad-libs gst-plugins-good gst-plugins-ugly python-websocket-client kodi  kodi-addon-inputstream-adaptive kodi-addon-inputstream-rtmp kodi-addon-peripheral-joystick kodi-addon-visualization-shadertoy kodi-addon-screensaver-pingpong --overwrite '*'
steamos-add-to-steam /usr/bin/kodi
cp -R ./.kodi /home/deck
sudo steamos-readonly enable
echo "---------------------------------
echo "want surround on your headphones? also install https://github.com/slynobody/SteamOS-surround
echo "-----------------------------------------------------------------------------------------------------------------------"
echo "if  you plan to use netflix, please !also install firefox through the App-Store! (needed to get credentials)"
echo "-----------------------------------------------------------------------------------------------------------------------"

