#!/bin/bash
set -e  # Exit immediately if any command fails

# Clean up previous tempdir if exists
rm -rf tempdir

# Create new directory and copy ALL files (including hidden) except tempdir itself
mkdir tempdir
#rsync -a --exclude=tempdir ./ tempdir/  # Note: Using ./ and no trailing slash
shopt -s dotglob
for item in * .[^.]*; do
    if [[ "$item" != "tempdir" ]]; then
        cp -r "$item" tempdir/
    fi
done
shopt -u dotglob

echo "FROM python" >> tempdir/Dockerfile
echo "RUN pip install ansible" >> tempdir/Dockerfile
echo "COPY . /home/myapp/" >> tempdir/Dockerfile
echo "EXPOSE 5050" >> tempdir/Dockerfile

# Verify essential files were copied
if [ ! -f tempdir/Dockerfile ]; then
    echo "Error: Dockerfile not found after copy!"
    exit 1
fi

# Build and run
cd tempdir
docker build -t cfgen .
docker run -t -d -p 5050:5050 --name cfgenrunning cfgen
docker ps -a