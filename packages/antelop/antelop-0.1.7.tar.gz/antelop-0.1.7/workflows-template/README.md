# Antelop Workflow Configurations

This repository contains the Nextflow configuration files and scripts for all Antelop workflows. These configurations are essential for running Antelop's cluster preprocessing and analysis routines.

## Overview

The workflows in this collection are designed to be installed and managed through Antelop's workflow installation scripts. They provide standardized configurations for:

- Pipeline parameters
- Resource allocation
- Install directories
- Containerised dependencies

## Requirements

These workflows require the following to be preinstalled on the system:

- An up-to-date Linux operating system
- SLURM workload manager
- Singularity/apptainer containerisation software

## Installation

Do not install these configurations manually. Instead, use the official Antelop installation process as described in the [Antelop Documentation](https://antelop.readthedocs.io/en/latest/developer/repo.html).

The proper installation method ensures:
- Correct file placement
- Parameter/path validation
- Container creation
- Binaries installation

## Usage

After installation via the documented method, the workflows will be available through the Antelop interfaces. For specific usage instructions, refer to the individual workflow documentation in the Antelop documentation.

## Support

For issues related to these configurations, please:
1. Verify you've installed using the official method
2. Double check your requirements, and configuration parameters
3. Submit an issue through the official Antelop GitHub issues

## License

MIT License

Copyright (c) 2024 Antelope Project Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
