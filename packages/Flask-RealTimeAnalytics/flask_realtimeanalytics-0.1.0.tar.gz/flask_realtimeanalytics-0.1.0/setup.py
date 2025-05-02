from setuptools import setup, find_packages

setup(
    name="Flask-RealTimeAnalytics",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "flask_realtime_analytics": ["templates/*.html"],
    },
    install_requires=[
        "Flask>=2.0.0",
        "Flask-SocketIO>=5.3.0",
        "python-socketio>=5.7.0",
        "SQLAlchemy>=1.4.0",
    ],
    author="Tony Rolfe",
    author_email="tony.rolfe@ibm.com",
    description="A Flask extension for real-time analytics dashboards",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/TonyRolfe/flask-realtime-analytics",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Framework :: Flask",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.6",
)