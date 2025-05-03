# ewoksscxrd

The **ewoksscxrd** project is a Python library designed to provide workflow tasks for Single-Crystal X-Ray Diffraction (SC-XRD) Data Processing using Ewoks (Extensible Workflow System). 

## Installation

By default, at the ESRF, `ewoksscxrd` should be installed on Ewoks workers using an Ansible script by the DAU team. 
If you wish to install `ewoksscxrd` manually, ensure you have Python 3.8+ and `pip` installed. You can install the library directly from PyPI:

```sh
pip install ewoksscxrd
```

Alternatively, to install from source, clone this repository and run:

```sh
git clone https://gitlab.esrf.fr/workflow/ewoksapps/ewoksscxrd.git
cd ewoksscxrd
pip install -e .
```

## Quickstart Guide

### Running an `ewoksscxrd` Workflow

## How-To Guides

For detailed instructions on various tasks, please refer to the How-To Guides section in the documentation, which covers topics like:

- Configuration of the workflow
- Running the workflow locally
- Using the API to run specific tasks


## Documentation
Comprehensive documentation, including an API reference, tutorials, and conceptual explanations, can be found in the [docs directory](./doc) or online at the [ReadTheDocs page](https://ewoksscxrd.readthedocs.io).


## Contributing
Contributions are welcome! To contribute, please:

1. Clone the repository and create a new branch for your feature or fix.
2. Write tests and ensure that the code is well-documented.
3. Submit a merge request for review.

See the `CONTRIBUTING.md` file for more details.

## License
This project is licensed under the MIT License. See the `LICENSE.md` file for details.

## Support
If you have any questions or issues, please open an issue on the GitLab repository or contact the support team via a data [data processing request ticket](https://requests.esrf.fr/plugins/servlet/desk/portal/41).
