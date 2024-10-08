
## AI Werkzeug: Dataset Creator and Environment Setup

AI Werkzeug is a powerful tool for creating LoRA (Low-Rank Adaptation) datasets from images, generating captions, and setting up the necessary environment for AI image processing tasks. I use this preparing data for [ai-toolkit](https://github.com/ostris/ai-toolkit)

### Features

- Convert CR2 files to JPG format
- Generate captions for images using ollama API (minicpm-v vision model)
- Create LoRA datasets with sequentially named image and caption pairs
- Rename existing image and caption files
- Automated environment setup with Git repository initialization

### Prerequisites

- Python 3.10+
- Git
- Some data

### Quick Start

Clone the repository:
```
git clone https://github.com/pwrtux/ai-werkzeug
cd ai-werkzeug
```

#### Usage
```
Usage: ai-werkzeug.py [OPTIONS]

Options:
--input-folder TEXT             Path to the input folder containing images
--output-folder TEXT            Path to the output folder for the dataset
--prefix TEXT                   Prefix for output file names
--rename-only                   Only rename images without generating captions
--start INTEGER                 Starting number for renaming
--order [asc|desc]              Renaming order (ascending or descending)
--image-formats TEXT            Comma-separated list of image formats to process
--dry-run                       Perform a dry run without actually renaming files or generating captions
--help                          Show this message and exit
```


### Examples

1. Create a LoRA dataset with captions:
   ```
   python ai-werkzeug.py --input-folder ./raw_images --output-folder ./lora_dataset --prefix lora_
   ```

2. Rename existing files without generating captions:
   ```
   python ai-werkzeug.py --input-folder ./existing_dataset --output-folder ./renamed_dataset --prefix new_ --rename-only
   ```

3. Perform a dry run to see what changes would be made:
   ```
   python ai-werkzeug.py --input-folder ./images --output-folder ./output --dry-run
   ```

### Environment Setup Script

The `setup_env.sh` script automates the following tasks:
- Clones the AI toolkit repository
- Sets up a Python virtual environment
- Installs required dependencies
- Configures CUDA for GPU support
- Logs in to Hugging Face (requires token in environment variable)


Run the environment setup script:
```
chmod +x setup_env.sh
./setup_env.sh
```

I use this mainly in Runpod or similar CloudGPU environments.



### Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### Acknowledgments

- Thanks to the Ostris the founder of [ai-toolkit](https://github.com/ostris/ai-toolkit) for his amazing work.


