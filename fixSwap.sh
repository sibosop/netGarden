#!/bin/bash
cd $HOME/GitProjects/netGarden
sudo cp dphys-swapfile /etc/dphys-swapfile
sudo /etc/init.d/dphys-swapfile stop
sudo /etc/init.d/dphys-swapfile start
