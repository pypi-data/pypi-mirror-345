from setuptools import setup, find_packages

setup(
    name='secure-gen-tk',
    version='0.1.2',
    description='Генератор паролей с графическим интерфейсом на tkinter',
    author='ALohaV2',
    author_email='pyutilsverif@gmail.com',
    packages=find_packages(include=['secure_gen_tk', 'secure_gen_tk.*']),
    include_package_data=True,
    python_requires='>=3.7',
    entry_points={
        'console_scripts': [
            'secure-gen-tk=secure_gen_tk.app:start_app'
        ]
    }
)
