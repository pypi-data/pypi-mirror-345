from setuptools import setup, find_packages


install_requires = [
    "requests>=2.0.0",
    "websocket-client>=1.0.0",
    "pandas>=1.0.0",
    "numpy>=1.0.0",
    "python-socketio[client]==5.13.0",
    "python-dotenv==1.1.0",
    "openai==1.75.0",
    "google-generativeai==0.8.5",
]
setup(
    name="llumo",
    version="0.1.8",
    description="Python SDK for interacting with the Llumo ai API.",
    author="Llumo",
    author_email="product@llumo.ai",
    packages=find_packages(),
    install_requires=install_requires,
    python_requires=">=3.7",
    include_package_data=True,
    url="https://www.llumo.ai/",
    license="Proprietary",
)
