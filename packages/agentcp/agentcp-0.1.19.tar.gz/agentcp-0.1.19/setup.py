from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="agentcp",
    packages=find_packages(where="."),
    package_dir={"": "."},
    version="0.1.19",
    description="连接Au互联网络的库，让你的应用可以连接到Au网络",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="liwenjiang",
    author_email="19169495461@163.com",
    url="https://github.com/yourusername/server-message",
    package_data={
        'agentid.db': ['*.db', '*.py'],  # 包含db目录下的所有.db和.py文件
    },
    include_package_data=True,
    install_requires=[
        "cryptography>=3.4.7",  # 示例依赖项
        "requests>=2.26.0",     # 示例依赖项
        "websocket-client>=1.2.1",     # 示例依赖项
        "python-dotenv>=0.19.0",     # 示例依赖项
        "asyncio>=3.4.3",     # 示例依赖项
        "typing-extensions>=4.0.1",     # 示例依赖项
    ],
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Networking",
    ],
    keywords="Agent Communication Protocol",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/server-message/issues",
        "Source": "https://github.com/yourusername/server-message",
    },
)