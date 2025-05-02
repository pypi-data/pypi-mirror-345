#!/bin/bash
# quick script to install uv in a CI script
#- COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
#TODO: uv version as arg
echo "Installing uv ..."
wget -q https://github.com/astral-sh/uv/releases/download/0.6.11/uv-x86_64-unknown-linux-gnu.tar.gz
tar xf uv-x86_64-unknown-linux-gnu.tar.gz
mv uv-x86_64-unknown-linux-gnu/uv uv-x86_64-unknown-linux-gnu/uvx /usr/local/bin/
rm -Rf uv-x86_64-unknown-linux-gnu*
uv --version
