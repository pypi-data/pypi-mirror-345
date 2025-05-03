from setuptools import setup, find_packages  # ✅ 꼭 필요함

setup(
    name='zylosystems-zylo',
    version='0.1.1',
    packages=find_packages(include=["zylo", "zylo.*"]),
    include_package_data=True,
    package_data={'zylo': ['static/docs/**/*']},
    install_requires=['Flask'],
    entry_points={
        'console_scripts': [
            'zylo=zylo.cli:main',  # ← 여기서 'zylo' 명령어를 main()에 연결!
        ],
    },
)