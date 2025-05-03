from setuptools import setup

setup(
    name='typejutsu',
    version='1.3',
    py_modules=['typejutsu'],
    entry_points={
        'console_scripts': [
            'typejutsu = typejutsu:main',
        ],
    },
)
