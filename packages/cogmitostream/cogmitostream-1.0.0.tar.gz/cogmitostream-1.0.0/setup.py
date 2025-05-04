from setuptools import setup, find_packages

setup(
    name="cogmitostream",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "undetected-chromedriver",
        "soundfile",
        "soundcard",
        "mtranslate",
        "speechrecognition",
        "ollama",
        "customtkinter",
        "python-telegram-bot",
        "nest_asyncio",
        "certifi"
    ],
    author="Aytunç Yalnız",
    description="Yayınlar için AI destekli otomatik konuşan bot",
    long_description="AI destekli canlı yayın etkileşim botu. Kick ve Twitch gibi platformlarda kullanılabilir.",
    long_description_content_type="text/markdown",
    url="https://github.com/senin-kendi-repo-urlin",  # GitHub URL’n varsa buraya
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)
