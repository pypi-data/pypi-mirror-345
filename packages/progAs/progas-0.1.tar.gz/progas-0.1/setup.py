from setuptools import setup, find_packages

setup(
    name='progAs',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'requests',
        # Diğer bağımlılıklar (örneğin: 'opencv-python', 'pyserial' vb.)
    ],
    author='ProgAs',
    description='ProgAs plugin for controlling Android devices via Python',
    long_description_content_type='text/markdown',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
