from setuptools import setup, find_packages

setup(
    name="a2apay",
    version="1.0.0",
    author="Dwiref Sharma",
    author_email="dwirefz@hotmail.com",
    description="Secure, modular microtransaction framework for agent-to-agent (A2A) and agent-to-resource (MCP) payments.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/DwirefS/a2a_payments_framework",
    packages=find_packages(include=["a2apay", "a2apay.*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires='>=3.8',
    install_requires=[
        "pytest",
        "flake8"
    ],
    include_package_data=True,
)