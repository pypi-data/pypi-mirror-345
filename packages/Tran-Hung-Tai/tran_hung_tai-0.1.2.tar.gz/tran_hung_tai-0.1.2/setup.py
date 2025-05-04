from setuptools import setup, find_packages

setup(
    name='Tran-Hung-Tai',  # Đổi tên ở đây
    version='0.1.2',
    packages=find_packages(),
    install_requires=[
        'requests',
        'tqdm'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
    ],
)
