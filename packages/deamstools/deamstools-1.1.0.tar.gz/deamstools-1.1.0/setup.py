from setuptools import setup, find_packages

with open("README.md", 'r') as f:
    description = f.read()

setup(
    name="deamstools",
    version="1.1.0",
    #description="Tools i made for my self! u can use em too",
    author="DEAMJAVA",
    author_email="deamminecraft3@gmail.com",
    packages=find_packages(),
    #install_requires=["pymysql", "sqlalchemy"],
    python_requires=">=3.12",
    entry_points={"console_scripts":["deamstools = deamstools:deamstools_check",
                                     "deamstools-license = deamstools:deamstools_license"]},
    #long_description=description,
    #long_description_content_type='text/markdown'
)
