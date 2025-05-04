from setuptools import setup, find_packages
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read()
setup(
    name = 'terminal_video_player_py',
    version = '1.0.2',
    author = '',
    author_email = '',
    license = '',
    description = 'A cli to play videos in the terminal.',
    long_description = long_description,
    long_description_content_type = "text/markdown",
    url = '',
    py_modules = ['terminal_video_player_py', 'to_ascii', 'vid_info'],
    packages = find_packages(),
    install_requires = [requirements],
    python_requires='>=3.9',
    classifiers=[
    ],
    entry_points = '''
        [console_scripts]
        tvp=terminal_video_player_py:main
    '''
)
