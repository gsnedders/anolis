from setuptools import setup, find_packages

setup(
    # Basic project info
    name = "anolis",
    version = "1.0",
    packages = find_packages(),
    scripts = ["anolis"],
    install_requires = ["html5lib>=0.10", "lxml>=2"],
    
    # Useless metadata cruft
    author = "Geoffrey Sneddon",
    author_email = "geoffers@gmail.com",
    url = "http://anolis.gsnedders.com",
    license = "MIT",
    description = "HTML document post-processor",
    long_description = """Anolis is an HTML document post-processor that takes
                          an input HTML file, adds section numbers, a table
                          of contents, and cross-references, and writes the
                          output to another file.""",
    download_url = "http://anolis.gsnedders.com",
    classifiers = [
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2",
        "Topic :: Text Processing :: Markup :: HTML"
    ]
)
