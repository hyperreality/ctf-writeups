#!/bin/bash

read x;
y=`md5sum $x`;
echo $y | cut -c1-32;

