from setuptools import setup, find_packages

setup(
    name="persian-calendar-picker-v2",
    version="0.2",
    packages=find_packages(),
    install_requires=[
        "jdatetime",
    ],
    author="abbas",
    author_email="bmnswry27@gmail.com",
    description="یک ویجت انتخاب تاریخ شمسی برای Tkinter",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown"
)