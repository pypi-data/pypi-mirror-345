from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    LONG_DESCRIPTION = fh.read()



setup(
    name = "abzagent",
    version="0.2",
    packages=find_packages(),
    install_requires=[
        "google-generativeai",
        "python-dotenv",
    ],
    author="Abu Bakar",
    author_email="abubakarbinzohaib@gmail.com",
    description="The Fastest Way to build AI Agent Using Gemini.",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
)