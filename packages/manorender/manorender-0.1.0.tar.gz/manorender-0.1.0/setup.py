from setuptools import setup, find_packages
from pathlib import Path

# Proje dizinini bul
PROJECT_DIR = Path(__file__).parent

# README dosyasını oku
with open(PROJECT_DIR / "README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="manorender",
    version="0.1.0",
    description="Powerful 3D rendering engine for Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/zubag/manorender",
    author="Zubag",
    author_email="zubag@example.com",
    license="MIT",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Multimedia :: Graphics :: 3D Rendering",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="3d render graphics engine python",
    packages=find_packages(),
    python_requires=">=3.7",
    install_requires=[
        'numpy>=1.21.0',
        'Pillow>=8.3.0',
        'pythreejs>=2.3.0',
        'scipy>=1.7.0',  # Bilimsel hesaplamalar için
        'trimesh>=3.19.0',  # 3D mesh işlemleri için
        'PyOpenGL>=3.1.0',  # OpenGL desteği için
        'PyQt5>=5.15.0',  # GUI desteği için
        'PyQtWebEngine>=5.15.0'  # Web tabanlı render desteği için
    ],
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
