# Changes in Unified Repository
This describes the changes of the Unified Repository after the transition from Basic to Orchestra as source. The repository is backward compatible but there are still some differences between the files.

## Phrases
The repository and phrases files no longer contain empty phrases, for example field usage descriptions for field references in messages, groups, and components.

## Pedigree
Pedigree information is no longer defined both for the `component` element and the nested `repeatingGroup` element. It follows Orchestra and is now only provided in the `component` element.

## Component Types
Orchestra does not have component types. There is no longer a distinction between Block and ImplicitBlock, between BlockRepeating and ImplicitBlockRepeating. XMLDataBlock is provided as Block.[This could be an issue, to be analyzed]

## NumInGroup Fields
see GitHub issue #13

## Examples in Datatypes
Examples have been removed from the definition of datatypes into the phrases file.

## Enum Groups
Unified no longer has empty `group` attributes.
[Seems to be a bug in Basic as it is not consistent within a single field -> enter SPEC issue]

## Default Presence Attribute
The attribute `required`defaults to zero. Unified no longer provides this value explicitly.
