from setuptools import setup, find_packages

setup(
    name='pythonclicker27',
    version='0.0.5',
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
    url='https://github.com/FJ27cool/PyClicker27',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Development Status :: 4 - Beta',
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Microsoft :: Windows',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'Natural Language :: English',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
        'Environment :: Console',
        'Environment :: Win32 (MS Windows)'
    ],
    keywords='autoclicker, python, clicker, automation, pyclicker27',
    license='MIT'
)