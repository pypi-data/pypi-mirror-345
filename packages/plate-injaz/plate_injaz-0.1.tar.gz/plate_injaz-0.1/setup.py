from setuptools import setup, find_packages

setup(
    name='plate_injaz',  # اسم المكتبة
    version='0.1',
    packages=find_packages(),  # هذا يحدد المجلدات التي سيتم تضمينها في الحزمة
    install_requires=[
        'requests',  # مكتبة للتعامل مع HTTP
        'Flask',     # مكتبة Flask
        'werkzeug',  # مكتبة للعمل مع الملفات
    ],
    description='مكتبة للتعرف على لوحات السيارات من الصور باستخدام API Plate Recognizer.',
    author='injaz',
    author_email='tameenijo@gmail.com',
    # url='https://github.com/اسم المستخدم هنا/plate_injaz',  # رابطك الخاص في GitHub (اختياري)
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
