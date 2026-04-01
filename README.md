# Image-based Mass Spectrometry Sampling Application

This application is designed to perform automated image-based sampling with a liquid micro junction-surface sampling probe (LMJ-SSP), fisheye camera, and a 3D printer. Users are able to take photos of sample slides, define sampling regions, and collect timestamped positional data of the probe. The user must configure their hardware setup through camera lens undistortion, camera pose estimation, and probe-to-camera offset calculation. With this application, users can define custom sampling regions and save timestamped positional data files for temporal MS data alignment in post-processing.

This project was developed as part of CISC 498 at Queen's University (Winter 2026) for the Queen's Chemistry Department.


# 🛠️ Installation steps

  Download Python 3.11.0 from https://www.python.org/downloads/release/python-3110/

  - When installer opens click the checkbox to add python 3.11 to path

  - Click install now

After installing python

  - Open Command Prompt (Terminal on Mac)

  - Copy the file path to requirements.txt


In command prompt, paste this command along with the folder address and press the "Enter" key

    pip install -r {path to requirements.txt, without braces}

If you do not have pip installed, paste this command and retry the previous step

    python get-pip.py


If needed, paste this command 

    python -m pip install --upgrade pip setuptools wheel

If needed, paste this command

    pip install --upgrade pip

# ⚙️ Running the application

Run the Application.py file through your IDE (e.g. Visual Studio Code) or with your Python launcher. 
You may also run the application by pasting the following commands in your terminal:

```
cd {path to repository folder}
python3 Application.py
```

# Credits
Legacy 3D Printer Control Application by [Kai Dalen](https://github.com/KDalen)
Dynamic Rendering by [Madison MacNeil](https://github.com/madisonmacneil)
