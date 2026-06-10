#!/bin/bash

set -e

echo "=============================="
echo "   INSTALLING DEPENDENCIES"
echo "=============================="

# MacOS
brew services install mongodb-community
brew services enable mongodb-community
brew services start mongodb-community

pip install -r requirements.txt

echo -e "\nDone!"
