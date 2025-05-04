# Getting started

To get started with the OpenHydroponics project, you will need a Raspberry Pi and some basic knowledge of Python programming. Follow these steps to set up your environment:

1. **Set up your Raspberry Pi**:
    - Install the latest version of Raspberry Pi OS on your SD card.
    - Boot up your Raspberry Pi and complete the initial setup.

2. **Install Python**:
    - Ensure Python is installed on your Raspberry Pi. You can check this by running `python3 --version` in the terminal.
    - If Python is not installed, you can install it using the following command:
      ```sh
      sudo apt-get update
      sudo apt-get install python3
      ```

3. **Set up a virtual environment**:
    - It is recommended to use a virtual environment to manage your Python packages. Create a virtual environment with:
      ```sh
      python3 -m venv openhydroponics-env
      ```
    - Activate the virtual environment:
      ```sh
      source openhydroponics-env/bin/activate
      ```

4. **Install required Python packages**:
    - Navigate to the project directory and install the required packages using pip:
      ```sh
      pip install git+https://gitlab.com/openhydroponics/sw/openhydroponics.git
      ```

5. **Run the project**:
    - You can now run the OpenHydroponics software using:
      ```sh
      python main.py
      ```

By following these steps, you should have a working setup of the OpenHydroponics project on your Raspberry Pi.
