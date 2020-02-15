#!/bin/bash

source ~/.profile
echo "$DOCKERHUB_PASS" | docker login --username $DOCKERHUB_USER --password-stdin
docker pull fabdulkarim/portofolio:fbe-IMG_VER
docker stop finalpro
docker rm finalpro
docker run -d --name finalpro -p 5000:5000 fabdulkarim/portofolio:fbe-IMG_VER