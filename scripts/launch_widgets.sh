#!/bin/bash

# 1. Top-Left Wing: Bold large clock with seconds (Cyan -C 6, bold -b)
kitty --class="widget_tl" -e tty-clock -s -c -C 6 -b &

# 2. Right Wing: CAVA (audio visualizer)
kitty --class="widget_tr" -e cava &

# 3. Bottom Vertex: Unimatrix Rain (Urdu Alphabet Matrix Rain)
kitty --class="widget_bottom" -e ~/dotfiles/scripts/unimatrix -a -c green -s 95 -l u -u 'ابپتٹثجچحخدڈذرڑزژسشصضطظعغفقکگلمنںوہھیے' &
