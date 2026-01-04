#!/bin/bash
cd /volume1/keyapp/keys-management-eere || exit 1
git pull
docker restart django-keyapp-python-1
