from setuptools import setup, find_packages

setup(
    name='Shadercraft',
    version='0.0.1',
    description='Node grap editor for prototyping shaders',
    author='Dan Wulczynski',
    url='https://github.com/RealDanTheMan/shadercraft',
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'shadercraft=shadercraft.app:Main'
        ]
    }
)