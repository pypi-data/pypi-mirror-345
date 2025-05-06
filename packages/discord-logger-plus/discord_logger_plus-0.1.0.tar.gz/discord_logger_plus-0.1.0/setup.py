from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="discord_logger_plus",
    version="0.1.0",
    author="Masaru Jasano",
    author_email="me@mjasano.com",
    description="A smarter logger library with discord webhook and supabase",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mjasano/discord_logger_plus",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.1",
        "supabase>=1.0.3",
        "python-dotenv>=0.19.0",
    ],
    project_urls={
        "Bug Reports": "https://github.com/mjasano/discord_logger_plus/issues",
        "Source": "https://github.com/mjasano/discord_logger_plus",
    },
) 