"""setup.py"""

from setuptools import setup, find_packages

setup(
    name='python-rpa',
    version='0.0.4',
    packages=find_packages(),
    install_requires=[
        # 필요한 패키지를 여기에 나열합니다
    ],
    author='Shinyoung Kim',
    author_email='shinyoung.kim@hyundai-autoever.com',
    description='A description of your package',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://gitlab.hmg-corp.io/swdc/python-rpa',
    tests_require=[
        'pytest',  # 또는 원하는 테스트 프레임워크
    ],
    python_requires='>=3.9',
)
