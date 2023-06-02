from setuptools import setup

package_name = 'control'

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
    description='Scripts that control syringe pumps using GCode and input from computer vision',
    license='License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
        	'keycontrol = control.keypress_control:main',
        	'teleoppump = control.teleop_pumps:main',
        	'pid	    = control.PID_node:main',
        	'control   = control.control_node:main',
        ],
    },
)
