from setuptools import setup, find_packages

setup(
    name='portfolio_ai',  # The name of your package
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'gitpython',  # Include dependencies if necessary
    ],
    entry_points={
        'console_scripts': [
            'portfolio_ai_setup=portfolio_ai.installer:run_setup',  # Command to run the setup
        ],
    },
    include_package_data=True,  # Include non-Python files (like setup.sh)
    description='AI-powered portfolio project setup script',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='saurabh tiwari',
    author_email='saurabhin2it@gmail.com',
    url='https://github.com/in2itsaurabh/portfolio_ai',  # Replace with your GitHub link
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
    ],
)

