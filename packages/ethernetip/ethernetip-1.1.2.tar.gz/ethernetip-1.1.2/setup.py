import setuptools

package_name = 'ethernetip'
description = 'Basic EtherNet/IP scanner'
readme = open('README.md').read()
requirements = ['dpkt']

# PyPI Readme
long_description = open('README.md').read()

setuptools.setup(name=package_name,
                 version="1.1.2",
                 author="Sebastian Block",
                 author_email="sebastian.block@world-wi.de",
                 url="https://codeberg.org/paperwork/python-ethernetip",
                 description=description,
                 long_description=long_description,
                 package_dir={"": "src"},
                 packages=setuptools.find_packages(where="src"),
                 install_requires=requirements,
                 license='MIT',
                 zip_safe=False,
                 classifiers=['Development Status :: 4 - Beta',
                              'Intended Audience :: Developers',
                              'License :: OSI Approved :: MIT License',
                              'Natural Language :: English',
                              'Programming Language :: Python :: 2.7',
                              'Programming Language :: Python :: 3.5',
                              'Programming Language :: Python :: 3.6',
                              'Programming Language :: Python :: 3.7',
                              'Programming Language :: Python :: 3.8',
                              'Programming Language :: Python :: 3.9',
                              'Programming Language :: Python :: 3.10',
                              'Programming Language :: Python :: 3.11',
                              'Programming Language :: Python :: 3.12'])
