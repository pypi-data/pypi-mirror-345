import setuptools
with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name='atomfoxapi',
    version='1.2.5',
    author='mc_c0rp',
    author_email='mc.c0rp@icloud.com',
    description='ATOM API | R08',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/mc-c0rp/atomfoxapi',
    project_urls={
        'Documentation': 'https://github.com/mc-c0rp/atomfoxapi/blob/main/README.md',
    },
    packages=['atomfoxapi'],
    include_package_data=True,
    python_requires='>=3.9',
)
