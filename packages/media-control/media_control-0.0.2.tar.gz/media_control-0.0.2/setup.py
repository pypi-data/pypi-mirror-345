from setuptools import setup
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="media_control",
    version="0.0.2",
    description="Application to access media controls on your device",
    author="sleepingsaint",
    url="https://github.com/sleepingsaint/media_control",
    include_package_data=True,
    install_requires=[
        "Flask",
        "flask-socketio",
        "pyautogui",
        "pillow",
        "qrcode",
        "volume-control"
    ],
    entry_points={
        'console_scripts': ['media-control=media_control.__init__:main']
    }, 
    long_description=long_description,
    long_description_content_type="text/markdown"
)