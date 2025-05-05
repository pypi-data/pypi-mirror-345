import json
import re
import argparse
import pycountry

EU_COUNTRIES = [
    "AT",  # Austria
    "BE",  # Belgium
    "BG",  # Bulgaria
    "HR",  # Croatia
    "CY",  # Cyprus
    "CZ",  # Czech Republic
    "DK",  # Denmark
    "EE",  # Estonia
    "FI",  # Finland
    "FR",  # France
    "DE",  # Germany
    "GR",  # Greece
    "HU",  # Hungary
    "IE",  # Ireland
    "IT",  # Italy
    "LV",  # Latvia
    "LT",  # Lithuania
    "LU",  # Luxembourg
    "MT",  # Malta
    "NL",  # Netherlands
    "PL",  # Poland
    "PT",  # Portugal
    "RO",  # Romania
    "SK",  # Slovakia
    "SI",  # Slovenia
    "ES",  # Spain
    "SE",  # Sweden
]

URL_HEADING = "URL"
PROVIDER_HEADING = "Provided by"
COUNTRY_HEADING = "Country"
NOTES_HEADING = "Notes"


def parse_string_to_dict(s):
    # Regular expression to match key=value pairs and standalone keys
    pattern = re.compile(r'([\w:]+)=("[^"]*"|\S+)|(\w+)')

    # Initialize the dictionary
    result = {}

    # Find all matches
    matches = pattern.findall(s)

    for match in matches:
        if match[0]:  # Key-value pair
            key = match[0]
            value = match[1]
            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1]  # Remove the surrounding quotes
            # Attempt to cast numeric values
            try:
                value = int(value)
            except ValueError:
                try:
                    value = float(value)
                except ValueError:
                    pass
            result[key] = value
        elif match[2]:  # Standalone key
            result[match[2]] = None

    return result


def parse_arguments(content):
    """Extract keyword arguments from all start tags."""
    matches = re.findall(r"<!-- START_INSTANCE_LIST(.*?)-->", content)
    return [
        {"_raw": match.strip(), **parse_string_to_dict(match.strip())}
        for match in matches
    ]


def get_filtered_data(data, filters):
    """Filter the data based on the provided filters."""
    for field, filter_data in filters.items():
        operator = filter_data["operator"]
        value = filter_data["value"]

        if operator == "eq":
            data = [instance for instance in data if instance.get(field) == value]
        elif operator == "ne":
            data = [instance for instance in data if instance.get(field) != value]
        elif operator == "lt":
            data = [instance for instance in data if instance.get(field) < value]
        elif operator == "lte":
            data = [instance for instance in data if instance.get(field) <= value]
        elif operator == "gt":
            data = [instance for instance in data if instance.get(field) > value]
        elif operator == "gte":
            data = [instance for instance in data if instance.get(field) >= value]
        elif operator == "contains":
            data = [
                instance
                for instance in data
                if value.lower() in instance.get(field, "").lower()
            ]
        elif operator == "startswith":
            data = [
                instance
                for instance in data
                if instance.get(field, "").lower().startswith(value.lower())
            ]
        elif operator == "endswith":
            data = [
                instance
                for instance in data
                if instance.get(field, "").lower().endswith(value.lower())
            ]

    return data


def generate_table_for_data(data):
    """Generate a markdown table for the filtered data."""
    max_url_length = len(URL_HEADING)
    max_provider_length = len(PROVIDER_HEADING)
    max_country_length = len(COUNTRY_HEADING)
    max_notes_length = len(NOTES_HEADING)

    for instance in data:
        location_code = instance["location"]
        instance["country"] = (
            f"{pycountry.countries.get(alpha_2=location_code).name} {pycountry.countries.get(alpha_2=location_code).flag}"
        )

        if location_code in EU_COUNTRIES:
            instance["country"] += " 🇪🇺"

        url_length = len(f"[{instance['name']}]({instance['url']})")
        provider_length = len(
            f"[{instance['provider']['name']}]({instance['provider']['url']})"
        )
        country_length = len(instance["country"])
        notes_length = len(instance.get("notes", ""))

        max_url_length = max(max_url_length, url_length)
        max_provider_length = max(max_provider_length, provider_length)
        max_country_length = max(max_country_length, country_length)
        max_notes_length = max(max_notes_length, notes_length)

    rows = [
        f"| [{instance['name']}]({instance['url']}){" " * (max_url_length - len(f"""[{instance['name']}]({instance['url']})"""))} | [{instance['provider']['name']}]({instance['provider']['url']}){" " * (max_provider_length - len(f"""[{instance['provider']['name']}]({instance['provider']['url']})"""))} | {instance['country']:<{max_country_length}} | {instance.get('notes', ''):<{max_notes_length}} |"
        for instance in data
    ]

    header = f"| {URL_HEADING:<{max_url_length}} | {PROVIDER_HEADING:<{max_provider_length}} | {COUNTRY_HEADING:<{max_country_length}} | {NOTES_HEADING:<{max_notes_length}} |"
    separator = f"| {'-' * max_url_length} | {'-' * max_provider_length} | {'-' * max_country_length} | {'-' * max_notes_length} |"

    return "\n".join([header, separator] + rows)


def update_readme_file(instance_file="instances.json", readme_file="README.md"):
    with open(readme_file, "r") as f:
        content = f.read()

    with open(instance_file, "r") as f:
        data = json.load(f)

    content_sections = []

    previous_end = 0

    for match in re.finditer(
        r"<!-- START_INSTANCE_LIST(.*?)-->(.*?)<!-- END_INSTANCE_LIST -->",
        content,
        flags=re.DOTALL,
    ):
        start, end = match.span()
        pre_content = content[previous_end:start]
        content_sections.append(pre_content)

        arg_string = match.group(1).strip()
        parsed_args = parse_string_to_dict(arg_string)

        filters = {
            field: {"operator": operator, "value": value}
            for argument, value in parsed_args.items()
            if ":" in argument
            for field, operator in [argument.split(":")]
        }

        filtered_data = get_filtered_data(data, filters)
        table_content = generate_table_for_data(filtered_data)

        # Reconstruct the match part with the filtered content and arguments
        content_sections.append(
            f"<!-- START_INSTANCE_LIST {arg_string} -->\n\n{table_content}\n\n<!-- END_INSTANCE_LIST -->"
        )

        previous_end = end

    # Add any trailing content after the last match
    content_sections.append(content[previous_end:])

    # Write the updated content back to the file
    with open(readme_file, "w") as f:
        f.write("".join(content_sections))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--instance-file",
        default="instances.json",
        help="The path to the JSON file containing the instance data",
    )
    parser.add_argument(
        "--readme-file",
        default="README.md",
        help="The path to the markdown file to update with the instance data",
    )
    args = parser.parse_args()

    update_readme_file(args.instance_file, args.readme_file)


if __name__ == "__main__":
    main()
