from setuptools import setup, find_packages

setup(
    name="racconfuncs",          # Package name (lowercase, hyphens)
    version="0.1.2",            # Version (semantic versioning)
    author="l319836",
    description="Package for automating Raccon functions with Python based on Selenium",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=[
    'selenium>=4.0.0',  # For all Selenium functionality (WebDriver, By, WebDriverWait, etc.)
    'requests>=2.25.0',  # For HTTP requests (if you use `requests` directly)
    ],
    python_requires=">=3.6",       # Python version compatibility
)