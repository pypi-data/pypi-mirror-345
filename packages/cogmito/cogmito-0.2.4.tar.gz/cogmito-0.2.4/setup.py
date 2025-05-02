from setuptools import setup, find_packages

setup(
    name="cogmito",
    version="0.2.4",
    author="Aytunç",
    description="AI destekli yayın ve otomasyon botu",
    packages=find_packages(),
    install_requires=[
        "certifi",
        "soundcard",
        "soundfile",
        "mtranslate",
        "ollama",
        "selenium",
        "undetected-chromedriver",
        "SpeechRecognition",
        "python-telegram-bot",
        'nest_asyncio',
    ],
    python_requires=">=3.9,<3.10",
    entry_points={
        "console_scripts": [
            "cogmito=cogmito.main:baslat"
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3.9",
        "Operating System :: OS Independent",
    ],
)
