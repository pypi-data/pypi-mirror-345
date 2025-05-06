from setuptools import setup, find_packages

setup(
    name='sufetron',  # Change the name here to Sufetron
    version='0.1',  # Version can stay the same unless you want to update it
    description='AI-powered HTTP request firewall for Flask apps',  # Keep this description, or adjust if you want
    author='ghayth-bouzayeni',  # Add your real name here
    author_email='bouzayanighayth@gmail.com',  # Your email
    packages=find_packages(),  # This will automatically find your package
    install_requires=[  # Install Flask and requests as dependencies
        'Flask',
        'requests'
    ],
    classifiers=[  # Python version and OS compatibility
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    
    python_requires='>=3.6',  # Ensuring Python 3.6 and above
)
