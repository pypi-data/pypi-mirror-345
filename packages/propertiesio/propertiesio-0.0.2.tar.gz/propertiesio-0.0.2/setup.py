import setuptools

with open("README.md", encoding="utf-8") as fh:
	long_description = fh.read()

setuptools.setup(
	name="propertiesio",
	version="0.0.2",
	author="chenxi12",
	author_email="chenxi201412@outlook.com",
	description="properties",
	long_description=long_description,
	long_description_content_type="text/markdown",
	url="https://github.com/zhangjiahuichenxi/propertiesio",
	packages=setuptools.find_packages(),
	classifiers=[
	"Programming Language :: Python :: 3",
	"License :: OSI Approved :: BSD License",
	"Operating System :: OS Independent",
	],
	python_requires='>=3.6',
)
