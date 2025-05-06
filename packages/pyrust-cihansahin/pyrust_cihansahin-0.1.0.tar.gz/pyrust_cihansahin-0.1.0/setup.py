from setuptools import setup, find_packages

if "__main__" == __name__:
    try:
        setup(
            name="pyrust_cihansahin",
            packages=find_packages(),
        
        )
    except:  # noqa
        print(
            "\n\nAn error occurred while building the project, "
            "please ensure you have the most updated version of setuptools, "
            "setuptools_scm and wheel with:\n"
            "   pip install -U setuptools setuptools_scm wheel\n\n"
        )
        raise
