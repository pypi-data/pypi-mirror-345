from setuptools import setup, find_packages

VERSION = '0.0.1'

# Setting up
setup(
    name="aicmo",
    version=VERSION,
    author="Jayr Castro",
    author_email="jayrcastro.py@gmail.com",
    description="A package for using aicmo functions and tools",
    long_description_content_type="text/markdown",
    long_description='A package for using aicmo functions and tools, includes scraping, openai with an options where you can use it in a serverless application such as AWS Lambda and GCP Cloud Function',
    packages=find_packages(),
    install_requires=[
        "openai==1.75.0",
        "scrapingbee==2.0.1",
        "requests==2.32.3",
        "boto3==1.37.37",
        "tiktoken==0.9.0",
        "opencv-python-headless==4.11.0.86",
        "beautifulsoup4==4.13.4",
        "numpy==2.2.4",
        "python-dotenv==1.1.0",
        "typesense==1.0.3"
    ],
    keywords=[
        'aicmo'
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.12",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)