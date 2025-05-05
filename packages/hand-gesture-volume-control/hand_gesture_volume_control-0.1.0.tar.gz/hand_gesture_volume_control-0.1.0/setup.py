from setuptools import setup, find_packages

setup(
    name='hand-gesture-volume-control',
    version='0.1.0',
    author='Rania Elkholy',
    description='التحكم في حجم الصوت من خلال حركة اليد باستخدام MediaPipe و pycaw',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    packages=find_packages(),
    install_requires=[
        'opencv-python',
        'mediapipe',
        'pycaw',
        'comtypes'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Microsoft :: Windows',
    ],
    python_requires='>=3.7',
)
