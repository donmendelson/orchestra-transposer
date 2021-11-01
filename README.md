# orchestra-transposer

Converts between a FIX Orchestra file and other artifacts.

Initial implementation converts between Orchestra version 1.0 and Simple Binary Encoding (SBE) version 1.0.

### FIX standards and schemas

[fix-orchestra](https://github.com/FIXTradingCommunity/fix-orchestra)

[fix-simple-binary-encoding](https://github.com/FIXTradingCommunity/fix-simple-binary-encoding)

## Features

* Validate an Orchestra file against its XML schema.
* Access elements of an Orchestra file in "pythonic" data structures that are aware of XML Schema datatypes.
* Validate an SBE message schema against its XML schema.
* Access elements of an SBE message schema in "pythonic" data structures that are aware of XML Schema datatypes.
* Convert an Orchestra file to an SBE message schema. Support datatype customization.
* Convert an SBE message schema to an Orchestra file.

## Prerequisites

Requires [Python 3.9](https://www.python.org/downloads/release/python-390/) or later. (Earlier versions may work but have not been tested.)

Unit tests use the [pytest](https://docs.pytest.org/en/6.2.x/) framework.

Assuming that Python and pip are already installed, get started as follows:
1. Clone this Git repository
2. In the working directory, create a Python virtual environment, e.g. `python -m venv .venv`
3. Install required dependencies: `pip install -r requirements.txt`


## License

© Copyright 2021 FIX Protocol Limited

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.