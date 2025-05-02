import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "tailscale_lambda_proxy",
    "version": "0.0.11",
    "description": "tailscale-lambda-proxy",
    "license": "Apache-2.0",
    "url": "https://github.com/rehanvdm/tailscale-lambda-proxy.git",
    "long_description_content_type": "text/markdown",
    "author": "rehanvdm<rehan.vdm+github-tailscale-lambda-proxy@gmail.com>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/rehanvdm/tailscale-lambda-proxy.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "tailscale_lambda_proxy",
        "tailscale_lambda_proxy._jsii"
    ],
    "package_data": {
        "tailscale_lambda_proxy._jsii": [
            "tailscale-lambda-proxy@0.0.11.jsii.tgz"
        ],
        "tailscale_lambda_proxy": [
            "py.typed"
        ]
    },
    "python_requires": "~=3.8",
    "install_requires": [
        "aws-cdk-lib>=2.150.0, <3.0.0",
        "constructs>=10.0.5, <11.0.0",
        "jsii>=1.106.0, <2.0.0",
        "publication>=0.0.3",
        "tailscale_lambda_extension>=0.0.8, <0.0.9",
        "typeguard>=2.13.3,<4.3.0"
    ],
    "classifiers": [
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: JavaScript",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Typing :: Typed",
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved"
    ],
    "scripts": []
}
"""
)

with open("README.md", encoding="utf8") as fp:
    kwargs["long_description"] = fp.read()


setuptools.setup(**kwargs)
