from setuptools import setup, find_packages

setup(
    name='PyDoxing',
    version='8.8.9',
    description='none',
    author='anonymous',
    author_email='none@example.com',
    packages=find_packages(include=['PyDoxing', 'PyDoxing.*']),
    include_package_data=True,
    python_requires='>=3.7',
    entry_points={
        'console_scripts': [
            'PyDoxing=PyDoxing.app:start_app',  # Запуск приложения через команду 'PyDoxing'
        ],
    },
)
