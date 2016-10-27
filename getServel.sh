#!/bin/bash

clear

#Dowload file list
echo "Downloading from servel"
wget http://web.servel.cl/archivos.xml 

#Cleaning data and obtain the file name
grep pdf archivos.xml | sed -e "s?<archcomuna>??" -e "s?</archcomuna>??"  -e "s/ //g"> files.txt
grep nomcomuna archivos.xml | sed -e "s?<nomcomuna>??" -e "s?</nomcomuna>??" -e "s/ //g"> comunas.txt

mkdir padron

rm archivos.xml

while read -r a && read -r b<&3; do
	#remove carriage return
	a=$(echo $a | tr -d '\r')
	b=$(echo $b | tr -d '\r')
	wget http://web.servel.cl/padron/$a -q --show-progress -O ./padron/$b.pdf
	echo "Saved $b.pdf"
done<files.txt  3<comunas.txt	






