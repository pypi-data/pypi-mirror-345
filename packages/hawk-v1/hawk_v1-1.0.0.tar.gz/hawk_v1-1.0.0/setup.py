from setuptools import setup, find_packages
import os
import sys

# Create directories if they don't exist
os.makedirs('hawk_extension/extension', exist_ok=True)
os.makedirs('hawk_extension/extension/model', exist_ok=True)
os.makedirs('hawk_extension/extension/icons', exist_ok=True)
os.makedirs('hawk_extension/templates', exist_ok=True)
os.makedirs('hawk_extension/static', exist_ok=True)

# Create a minimal README if it doesn't exist
if not os.path.exists('README.md'):
    with open('README.md', 'w', encoding='utf-8') as f:
        f.write("# H.A.W.K - High-Accuracy Wordsmithing Kernel\n\n"
                "A Chrome extension that enhances your prompts using a built-in, "
                "lightweight language model. H.A.W.K works completely offline and "
                "requires no API keys or external services.")

# Get long description safely
try:
    with open("README.md", 'r', encoding='utf-8') as f:
        long_description = f.read()
except Exception:
    long_description = "H.A.W.K - AI Prompt Enhancer for Chrome"

setup(
    name="hawk-v1",
    version="1.0.0",
    author="HAWK Team",
    author_email="info@hawk-extension.com",
    description="H.A.W.K - High-Accuracy Wordsmithing Kernel - Chrome Extension Installer",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hawk-team/hawk-extension",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'hawk_extension': [
            'extension/*',
            'extension/model/*',
            'extension/icons/*',
            'static/*',
            'templates/*'
        ],
    },
    install_requires=[
        'flask>=2.0.0',
        'waitress>=2.0.0',
        'packaging>=21.0',
    ],
    entry_points={
        'console_scripts': [
            'hawk-installer=hawk_extension.server:main',
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
) 