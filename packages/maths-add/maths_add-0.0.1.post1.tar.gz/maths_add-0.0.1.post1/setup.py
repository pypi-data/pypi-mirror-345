from setuptools import setup,find_packages

setup(
	name='maths_add',
	version='0.0.1post1',
	platforms=["win_amd64"],
	description='A extended math library',
	long_description=open('README.md',encoding="utf-8").read(),
	long_description_content_type='text/markdown',
	author='fourth-dimensional_universe',
	author_email='3817201131@qq.com',
	url='https://github.com/fourth-dimensional/maths_add',
	license='MIT',
	classifiers=[
		'Programming Language :: Python :: 3',
		'License :: OSI Approved :: MIT License',
		'Operating System :: OS Independent',
	],
	packages=find_packages(),
	python_requires='>=3.7,!=3.10',
	install_requires=[
		'pycryptodome',
		'cryptography'
	]
	)




