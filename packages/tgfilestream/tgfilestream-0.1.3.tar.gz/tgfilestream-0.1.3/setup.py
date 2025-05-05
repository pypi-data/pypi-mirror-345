import setuptools

from tgfilestream import __version__

try:
    with open("README_PIP.md", encoding="utf-8") as f:
        long_desc =  f.read()
except IOError:
    long_desc = "Failed to read README.md"

extras = {
    "env": ["python-dotenv>=0.20"],
    "fast": ["cryptg>=0.2"],
}

extras["all"] = sorted({dep for deps in extras.values() for dep in deps})

setuptools.setup(
    name="tgfilestream",
    version='0.1.3',
    url="https://mau.dev/tulir/TGFileStream",

    author="Tulir Asokan",
    author_email="tulir@maunium.net",

    description="A Telegram bot that can stream Telegram files to users over HTTP.",
    long_description=long_desc,
    long_description_content_type="text/markdown",

    packages=setuptools.find_packages(),
    include_package_data=True,

    install_requires=[
        "aiohttp>=3",
        "telethon>=1.10",
        "yarl>=1",
    ],
    extras_require=extras,
    python_requires="~=3.7",

    license="AGPL-3.0-or-later",
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
        "Framework :: AsyncIO",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    entry_points="""
        [console_scripts]
        tgfilestream=start
    """,
)
