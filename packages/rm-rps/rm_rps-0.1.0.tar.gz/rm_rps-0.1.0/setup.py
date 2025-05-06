from setuptools import setup, find_packages

setup(
    name="rm-rps",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,  # لضمان تضمين الملفات مثل الصور
    install_requires=[
        "opencv-python",
        "cvzone",
        "mediapipe"
    ],
    entry_points={
        'console_scripts': [
            'rmrps = rm_rps.game:main',  # لتشغيل اللعبة من الطرفية
        ],
    },
    package_data={
        'rm_rps': ['Resources/*.png'],  # تضمين ملفات الصور داخل الحزمة
    },
    author="اسمك",
    author_email="t276032900094@gmail.com",
    description="لعبة حجر ورقة مقص باستخدام تتبع اليد",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
