from setuptools import setup, find_packages

setup(
    name="persian_calendar_picker",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "jdatetime",
    ],
    author="Your Name",
    author_email="your.email@example.com",
    description="یک ویجت انتخاب تاریخ شمسی برای Tkinter",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/persian_calendar_picker",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)