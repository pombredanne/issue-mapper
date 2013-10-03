#!/bin/bash
set -e
#inkscape --file=background1.svg --export-dpi=72 --export-png=../img/background1.png --export-width=1500 --export-area=0:0:600:315
#inkscape --file=background1.svg --export-dpi=72 --export-png=../img/background1.png --export-width=1500 --export-area=30:0:570:315
#inkscape --file=logo.svg --export-dpi=72 --export-png=../img/favicon.png --export-width=50
#inkscape --file=logo2.svg --export-dpi=72 --export-png=../img/favicon.png --export-width=16
IMG="../img/Great_Seal_of_the_United_States_obverse.png"
inkscape --file="Great_Seal_of_the_United_States_obverse.svg" --export-png=$IMG
convert $IMG -colorspace gray $IMG
convert $IMG -channel Alpha -evaluate Divide 10 $IMG