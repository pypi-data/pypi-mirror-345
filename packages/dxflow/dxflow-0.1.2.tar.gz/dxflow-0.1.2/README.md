# dxflow SDK

The `dxflow` SDK is a Python package designed to streamline scientific discovery by providing a seamless, user-friendly, and collaborative environment for scientific computing. It enables easy access and management of the DiPhyx cloud computing platform's resources, including computational workflows, data storage, and project management.

## Features

- **Cluster Management**: Efficiently manage computation clusters, including creation, modification, and deletion.
- **Data Storage**: Simplified access and management of cloud storage solutions for scientific data.
- **Authentication and Authorization**: Secure access control using the dxflow authentication system.
- **Project and Collaboration Tools**: Tools to facilitate project management and collaboration among scientists.
- **Computational Workflow Management**: Create, execute, and monitor computational pipelines.

## Installation

Install `dxflow` using pip:

```bash
pip install dxflow
```

## Quick Start

Here's how to get started with the `dxflow` SDK:

1. **Create a Session**:

```python
from dxflow.session import Session

dxs = Session(email="YOUR@EMAIL", password="YOUR_DIPHYX_PASSWORD")
```

2. **Compute Manager**:

```python
compute = dxs.get_compute_manager()
compute.list()
```

3. **Compute Storage**:

```python
c_u = compute.get_unit("you_compute_unit_name")
c_u.storage.list()
```

## Documentation

For detailed documentation on all features and functionalities, please refer to [our documentation](#).

## Contributing

We welcome contributions from the community, including bug reports, feature requests, and code contributions. Please see our [contributing guidelines](CONTRIBUTING.md) for more information.

## Support

If you encounter any problems or have questions, please file an issue on our GitHub repository or contact our support team at support@diphyx.com.

