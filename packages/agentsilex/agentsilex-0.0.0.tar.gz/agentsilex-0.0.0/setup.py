from setuptools import setup, find_packages

setup(
    name="agentsilex",
    version="0.0.0",
    author="Xiaoquan Kong",
    author_email="u1mail2me@gmail.com",
    description="An intuitive agent development framework",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/howl-anderson/agentsilex", 
    packages=find_packages(),
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    python_requires=">=3.6",
) 