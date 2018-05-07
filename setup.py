import setuptools


REQUIREMENTS = [
	'future==0.16.0',
	'requests==2.18.4',
]


setuptools.setup(
	name='viberbot',
	classifiers=[
		'Development Status :: 5 - Production/Stable',
		'License :: OSI Approved :: Apache Software License',
		'Programming Language :: Python :: 3.5',
		'Programming Language :: Python :: 3.6',
	],
	license='Apache',
	install_requires=REQUIREMENTS,
	packages=[
		'viberbot',
		'viberbot.api',
		'viberbot.api.messages',
		'viberbot.api.messages.data_types',
		'viberbot.api.viber_requests',
	],
	setup_requires=['setuptools_scm'],
	url='https://github.com/Viber/viber-bot-python',
	use_scm_version={"root": ".", "relative_to": __file__},
	version=None,
)
