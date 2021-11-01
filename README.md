# pysbeorchestra

Translates between Orchestra and Simple Binary Encoding (SBE) files. Initial implementation covers Orchestra version 1.0 and SBE version 1.0.

### FIX standards and schemas

[fix-orchestra](https://github.com/FIXTradingCommunity/fix-orchestra)

[fix-simple-binary-encoding](https://github.com/FIXTradingCommunity/fix-simple-binary-encoding)

## Features

* Validate an Orchestra file against its XML schema.
* Validate an SBE message schema against its XML schema.
* Access elements of an SBE message schema in "pythonic" data structures that are aware of XML Schema datatypes.
* Access elements of an Orchestra file in "pythonic" data structures that are aware of XML Schema datatypes.
* Convert an Orchestra file to an SBE message schema. Support datatype customization.
* Convert an SBE message schema to an Orchestra file.

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