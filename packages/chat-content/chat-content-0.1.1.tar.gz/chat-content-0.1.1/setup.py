from setuptools import setup, find_packages

setup(
    name="chat-content",
    version="0.1.1",
    author="Karthik Sunil K",
    author_email="karthiksunil.me@gmail.com",
    description="Fetch responses from GCP Discovery Engine (Agent Builder Chat App)",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Karthik-Sunil-K/chat-content",
    packages=find_packages(),
    install_requires=[
        "google-api-core",
        "google-cloud-discoveryengine"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
