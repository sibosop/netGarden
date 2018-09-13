# netGarden
Multidevice autonomic music player

NetGarden runs on raspiberry pi's though any platform that has all the interface libraries will work

The laster versions of the pi make setup much easier. Password and network setup is done in the configuration startup dialogs. This is assuming that you copy the latest NOOBS packages to the sim card and do full setup. 

You still need to enable ssh from the terminal using
* `sudo raspi-config`

* if the HDMI screen does not fill out to the edges then
* uncomment this line
  * disable_overscan=1
    
* turn off screen blanking
 * vi /home/pi/.config/lxsession/LXDE-pi/autostart 
 * add lines
   * @xset s noblank
   * @xset s off 
   * @xset -dpms
 * `sudo vi /etc/kbd/config` 
 * set `BLANK_TIME=0`
 * set `POWERDOWN_TIME=0`
 * Load screensaver program (see below) disable in perferences
 * 
 
#### setting up unit for run
 * To minimize the writes to the sd card, the image directories are being mounted tmpfs:
 * `sudo mv /etc/fstab /etc/fstab.old`
 * `sudo cp /home/pi/GitProjects/artDisplay/fstab /etc/fstab`
 * check the log file daily since the directory is now smaller, change weekly to daily
 * `sudo vi /etc/logrotate.conf`
 * to start at boot
  * `crontab -e`
  * add these lines
   * `MAILTO=""`
   * `@reboot sleep 60; /home/pi/GitProjects/netGarden/server/gardenWrap.sh`
   * `@reboot; /home/pi/GitProjects/netGarden/utils/asoundConfig.py`
 * with any luck the system will start after reboot
 * unclutter removes cursor. You may need to run unclutter -display :0.0 once
