from setuptools import setup, find_packages

setup(
    name='lial_user',  # Replace with your package’s name
    version='1.2.4',
    packages=find_packages(include=['lial_user']),
    install_requires=[
        'pyodbc',
        'mysql-connector-python'
    ],
    author='SIGIER Luc',  
    author_email='l.sigier@lialrioz.fr',
    description='Une librairie de fonctions pour intéragir avec la base de données des utilisateurs du LIAL',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',

)