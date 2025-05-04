if __name__ == "__main__":
    from setuptools import setup, find_packages

    setup(
        name='pygameControls',
        version='0.1.12',
        packages=find_packages(),
        install_requires=[],
        author='Jan Lerking',
        author_email='',
        description='A simple controller class for pygame.',
        long_description=open('README.md').read(),
        long_description_content_type='text/markdown',
        url='',
        classifiers=[
                    'Programming Language :: Python :: 3',
                    'License :: OSI Approved :: MIT License',
                    'Operating System :: OS Independent',
                    ],
        python_requires='>=3.12',
    )