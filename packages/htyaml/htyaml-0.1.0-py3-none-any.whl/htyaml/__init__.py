import click
import yaml

from bs4 import BeautifulSoup
from bs4.element import Tag


def encode_element(root: BeautifulSoup, parent: Tag, element: dict | list | str):
    if isinstance(element, dict):
        for key, value in element.items():
            if key.startswith("@"):
                # adding new attribute
                parent.attrs[key[1:]] = value
            else:
                # adding new child
                child = root.new_tag(key)
                parent.append(child)
                encode_element(root, child, value)

    if isinstance(element, list):
        for value in element:
            encode_element(root, parent, value)

    if isinstance(element, str):
        # Adding raw text
        text = root.new_string(element)
        parent.append(text)


@click.command()
@click.argument("input_file")
@click.argument("output_file", default="out.html")
def main(input_file: str, output_file: str):
    with open(input_file) as input_data:
        input_yaml = yaml.load(input_data, Loader=yaml.CLoader)

    doc = BeautifulSoup()
    encode_element(doc, doc, input_yaml)

    with open(output_file, "w") as out:
        out.write("<!DOCTYPE html>\n")
        out.write(doc.prettify())
