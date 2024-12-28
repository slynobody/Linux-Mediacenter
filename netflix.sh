#!/bin/sh
echo ">>> background: https://github.com/CastagnaIT/plugin.video.netflix/wiki/Login-with-Authentication-key'" 
echo "<<<<<<<<<<<<<<<"
echo "--> Brave-Browser needs to be installed for this! (through appstore) <----"
echo "<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<"
echo "Follow the instructions on screen, after you have created the file, you have to open it with Netflix add-on by choosing the login with "Authentication key"."
echo "Remember to delete the Authentication key file after login. After generating the file you can use it to login to Netflix add-on on all your devices."
python ./NFAuthenticationKey.py 
cp NFAuthentication.Key /home/deck/Desktop
