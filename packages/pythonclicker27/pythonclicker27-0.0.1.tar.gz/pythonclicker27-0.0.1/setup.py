from setuptools import setup, find_packages

setup(
    name='pythonclicker27',
    version='0.0.1',
    description='A simple and easy-to-use autoclicker library for Python',
    packages=find_packages(include=['pyclicker27', 'pyclicker27.*']),
    python_requires='>=3.6',
    install_requires=[
        'pyautogui>=0.9.53',   # pyautogui is a dependency for pyclicker27
        'pynput>=1.7.3',       # pynput is a dependency for pyclicker27
        'keyboard>=0.13.5',    # keyboard is a dependency for pyclicker27
        'mouse>=0.7.1',        # mouse is a dependency for pyclicker27
        'pywin32>=300'         # pywin32 is a dependency for pyclicker27
    ],
    author='FJ27cool',
    long_description=open('README.txt').read(),
    long_description_content_type='text/plain',
    url='https://github.com/FJ27cool/PyClicker27'
)