from setuptools import setup

package_name = 'vision'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='bram',
    maintainer_email='bramo@live.nl',
    description='Computer vision using OpenCV',
    license='License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
        	'dino	    = vision.dinolite:main',
        	'drop_find = vision.droplet_node:main',
        ],
    },
)
