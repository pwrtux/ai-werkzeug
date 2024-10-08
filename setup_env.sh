#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Print commands and their arguments as they are executed
set -x

# Clone the repository
git clone https://github.com/ostris/ai-toolkit.git

# Change to the ai-toolkit directory
cd ai-toolkit

# Update submodules
git submodule update --init --recursive

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate

# Install torch
pip install torch

# Install requirements
pip install -r requirements.txt

# Upgrade specific packages
pip install --upgrade accelerate transformers diffusers huggingface_hub

# Login to Hugging Face
if [ -n "$HUGGINGFACE_TOKEN" ]; then
    echo "Logging in to Hugging Face..."
    echo -e "n\nn" | huggingface-cli login #--token $HUGGINGFACE_TOKEN
else
    echo "HUGGINGFACE_TOKEN environment variable is not set. Skipping Hugging Face login."
fi

# Print CUDA information
echo "=========="
echo "== CUDA =="
echo "=========="
nvidia-smi

echo "Dependency Setup completed successfully!"
echo "Hugging Face login completed (if token was provided)."
