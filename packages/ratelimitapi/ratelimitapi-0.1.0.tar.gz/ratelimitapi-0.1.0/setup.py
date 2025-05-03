from setuptools import setup, find_packages

setup(
    name="ratelimitapi",
    version="0.1.0",
    description="Rate limiting middleware for APIs",
    author="Edward",
    author_email="edward@ratelimitapi.com",
    url="https://ratelimitapi.com",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.0",
    ],
    keywords=[
        "ratelimit",
        "middleware",
        "api",
        "rate limiting",
        "rate",
        "limit",
        "rate-limit",
        "throttling"
    ],
    license="MIT",
)
