#!/bin/bash

ENV_DIR="./virtual-env/deploy/"

echo ""
echo "Creating fresh virtual env directory -> $ENV_DIR"
rm-rf "$ENV_DIR"
mkdir -p ENV_DIR

# Setup Python virtual environment
echo "Initialising virtual environment"
virtualenv $ENV_DIR
source "$ENV_DIR/bin/activate"

PYTHON_LOCATION=$(which python)
PIP_LOCATION=$(which pip)

echo ""
echo "- - - - - - - - - - - - - - - - -"
echo "Virtual environment active"
echo "Python: $PYTHON_LOCATION"
echo "Pip: $PIP_LOCATION"
echo ""

# Install ShaderCraft editable package and its dependencies
echo "Intalling dependencies"
echo ""
pip install -r requirements.txt
echo ""
echo "Installing shadercraft package"
pip install -e .
echo ""
SHADERCRAFT_LOCATION=$(pip show shadercraft)

# Run ShaderCraft
echo "ShaderCraft: $SHADERCRAFT_LOCATION"
echo "Running ShaderCraft"
echo ""
python -m shadercraft
