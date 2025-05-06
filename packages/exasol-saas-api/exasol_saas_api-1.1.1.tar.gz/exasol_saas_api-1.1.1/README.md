# SaaS API for Python

API enabling Python applications connecting to Exasol database SaaS instances and using their SaaS services.

The model layer of this API is generated from the OpenAPI specification in JSON format of the SaaS API https://cloud.exasol.com/openapi.json using [openapi-python-client](https://github.com/openapi-generators/openapi-python-client).

A GitHub action will check each morning if the generated model layer is outdated.

See
* [User Guide](doc/user_guide/user-guide.md)
* [Developer Guide](doc/developer_guide/developer_guide.md)
