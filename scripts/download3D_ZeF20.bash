#!/bin/bash

directory="../downloads/3D_ZeF20"

mkdir ../downloads
mkdir $directory

wget -q -O $directory/3DZeF20.zip --progress=bar --show-progress -c https://motchallenge.net/data/3DZeF20.zip
