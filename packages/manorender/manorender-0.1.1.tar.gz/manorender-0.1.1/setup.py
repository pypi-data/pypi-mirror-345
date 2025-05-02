from setuptools import setup, find_packages

setup(
    name="manorender",
    version="0.1.1",
    packages=find_packages(),
    install_requires=[
        "numpy>=1.21.0",
        "Pillow>=8.3.0",
        "pythreejs>=2.3.0",
        "scipy>=1.7.0",
        "imageio>=2.9.0",
        "PyOpenGL>=3.1.0",
        "PyGLM>=1.7.0"
    ],
    author="PlazmaDevelopment",
    author_email="contact@plazmadev.com",
    description="Powerful 3D rendering engine with advanced features",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url="https://github.com/PlazmaDevelopment/manorender",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Visualization",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ],
    python_requires='>=3.7',
    extras_require={
        'dev': [
            'pytest>=6.2.0',
            'pytest-cov>=2.12.0',
            'black>=21.5b0',
            'isort>=5.9.0',
            'flake8>=3.9.0',
            'mypy>=0.812'
        ],
        'docs': [
            'sphinx>=4.0.0',
            'sphinx-rtd-theme>=0.5.0',
            'sphinx-autodoc-typehints>=1.12.0'
        ]
    },
    entry_points={
        'console_scripts': [
            'manorender=manorender.cli:main',
            'mano-render=manorender.cli:main',  # Alternatif komut
            'mano-renderer=manorender.cli:main'  # Alternatif komut
        ]
    },
    package_data={
        'manorender': [
            'data/*',
            'shaders/*',
            'textures/*',
            'examples/*'
        ]
    },
    include_package_data=True,
    project_urls={
        'Bug Reports': 'https://github.com/zubag/manorender/issues',
        'Source': 'https://github.com/zubag/manorender',
        'Documentation': 'https://manorender.readthedocs.io'
    }
)
