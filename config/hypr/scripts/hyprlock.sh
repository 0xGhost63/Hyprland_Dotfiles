#!/bin/bash
qs -c ii ipc call lock activate || pidof hyprlock || hyprlock
