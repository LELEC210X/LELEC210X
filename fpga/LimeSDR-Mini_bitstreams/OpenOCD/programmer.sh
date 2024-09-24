#!/bin/bash

if [[ $1 == "FT2232H" ]]; then
	openocd -f ./adapters/ft2232h.conf -c "jtag newtap 10m16 tap -expected-id 0x31030dd -irlen 8; init; svf ./LimeSDR-Mini_lms7_lelec210x.svf; exit;"
elif [[ $1 == "FT232H" ]]; then
  	openocd -f ./adapters/ft232h.conf -c "jtag newtap 10m16 tap -expected-id 0x31030dd -irlen 8; init; svf ./LimeSDR-Mini_lms7_lelec210x.svf; exit;"
elif [[ $1 == "OLIMEX" ]]; then
	openocd -f ./adapters/olimex.conf -c "jtag newtap 10m16 tap -expected-id 0x31030dd -irlen 8; init; svf ./LimeSDR-Mini_lms7_lelec210x.svf; exit;"
elif [[ $1 == "DISTORTEC" ]]; then
	openocd -f ./adapters/olimex.conf -c "jtag newtap 10m16 tap -expected-id 0x31030dd -irlen 8; init; svf ./LimeSDR-Mini_lms7_lelec210x.svf; exit;"
elif [[ $1 == "FT232R" ]]; then
	openocd -f ./adapters/ft232r.conf -c "jtag newtap 10m16 tap -expected-id 0x31030dd -irlen 8; init; svf ./LimeSDR-Mini_lms7_lelec210x.svf; exit;"
else 
	echo "No matching adapters!"
	echo "Usage: ./programmer.sh ADAPTER_NAME"
	echo "Supported Adapters: FT2232H, FT232H, FT232R, OLIMEX & DISTORTEC"
fi
