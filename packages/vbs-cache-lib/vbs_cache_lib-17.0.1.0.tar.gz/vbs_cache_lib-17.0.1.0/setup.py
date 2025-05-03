from setuptools import setup, find_packages

setup(
    name="vbs-cache-lib",  # 🔥 Use hyphens not underscores
    version="17.0.1.0",
    description="Vision Business Solution Custom Caching Pluggable caching library (Redis, Postgres, File, etc.)",
    author="Syed Saad Hussain",
    author_email="saadlink24@gmail.com",
    url="https://github.com/saad2401/vbs-cache-lib",  # optional
    packages=find_packages(),
    install_requires=[
        "psycopg2-binary",
        "pymysql",
        "pyodbc",
        "redis"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
