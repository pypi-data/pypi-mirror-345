from os.path import dirname
from os.path import join
import setuptools


def readme() -> str:
    """Utility function to read the README file.
    Used for the long_description.  It's nice, because now 1) we have a top
    level README file and 2) it's easier to type in the README file than to put
    a raw string in below.
    :return: content of README.md
    """
    return open(join(dirname(__file__), "README.md")).read()


setuptools.setup(
    name="streamlit-video-editor",
    use_scm_version={
        "write_to": "streamlit_video_editor/_version.py",
        "write_to_template": '__version__ = "{version}"',
    },
    setup_requires=['setuptools_scm'],
    author="Carlos André Antunes",
    author_email="",
    description="A Streamlit custom component to display a simple video editor.",
    long_description=readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/antunsz/streamlit-video-editor",
    project_urls={
        "Github":"https://github.com/antunsz/streamlit-video-editor"
    },
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "streamlit >= 0.70",
    ],
)