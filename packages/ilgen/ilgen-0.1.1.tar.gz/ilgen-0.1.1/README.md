# ILGen - The Instance List Generator

A Python script for "translating" a list of application instances from an instances.json to a Markdown table.

## Installation

To install the script, you can clone the repository and run the following command:

```bash
pip install .
```

## Usage

First, ensure that you have an `instances.json` file. The file should have the following structure:

```json
[
    {
        "name": "Instance 1",
        "url": "https://example.com",
        "provider": {
            "name": "Provider 1",
            "url": "https://provider1.com"
        },
        "location": "AT", // This is the ISO 3166-1 alpha-2 country code
        "notes": "This is a note."
    },
    {
        …
    }
]
```

Also ensure that you have a `README.md` file with the following placeholder:

```markdown
<!-- START_INSTANCE_LIST -->
<!-- END_INSTANCE_LIST -->
```

To use the script, you can run the following command:

```bash
ilgen
```

This will insert the data from the instances.json file into the placeholder in the README.md file.

### Filters

You can add filters to the placeholder to only include instances that match the filter. For example, you can add the following filter to only include instances from Austria:

```markdown
<!-- START_INSTANCE_LIST location:eq="AT" -->
<!-- END_INSTANCE_LIST -->
```

You can also add multiple filters by separating them with a space. These types of filters are combined with an AND operation. For example, you can add the following filter to only include instances from Austria that have a note:

```markdown
<!-- START_INSTANCE_LIST location:eq="AT" notes:neq="" -->
<!-- END_INSTANCE_LIST -->
```

The following filters are available:

- `eq`: Equal to
- `ne`: Not equal to
- `lt`: Less than
- `lte`: Less than or equal to
- `gt`: Greater than
- `gte`: Greater than or equal to
- `contains`: Contains
- `startswith`: Starts with
- `endswith`: Ends with

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.