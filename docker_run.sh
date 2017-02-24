#!/bin/bash
# Script to launch Docker container for running validation tests

# get SSH key for login
docker run -t validation_examples:py2 /bin/cat /home/docker/.ssh/id_rsa > docker_key_py2

# run container
docker run -d -p 2222:22 --name=validation -v ~/dev:/home/docker/dev -v ~/Projects:/home/docker/projects validation_examples:py2 &
echo "ssh -Y -i ./docker_key_py2 -p 2222 docker@localhost"
