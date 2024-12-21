import os
import pdfkit
from bs4 import BeautifulSoup
import tempfile
from datetime import datetime
from pathlib import Path
from flask import current_app
path_wkhtmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)
options = {
    "enable-local-file-access": True,
}

from lxml import etree

def updated_element_by_id(soup : BeautifulSoup, element_id: str, new_value: str):
    try:
        element = soup.find(id=element_id)
        if element:
            element.string = new_value
            print(f"Updated element with id='{element_id}' to '{new_value}'.")
        else:
            print(f"No element found with id='{element_id}'.")

        print(f"Updated HTML saved to.")
        return soup
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def fill_html_from_xml_data(xml_datas,html_file, output_file):
    file_path =str(Path(current_app.config.root_path)/'templates'/'static')
    print(f"The filepath to pdfkit for assets in h2pdf - {file_path}")
    root = xml_datas
    with open(html_file, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')
        # Setting header images
        img_tag = soup.find('img', {'id': 'headerimg'})

        # Set the 'src' attribute if the tag is found
        if img_tag:
            img_tag['src'] = os.path.join(file_path,'header.png')

        # Setting annotations
        elements = soup.find_all(class_="annot")
        for element in elements:
            if element.get('id'):
                element_id_to_update = element.get('id')
                print(element_id_to_update)
                xml_value = root.find(f".//{element_id_to_update}")  # Match XML tag with PDF field name
                print(xml_value)
                updated_element_by_id(soup, element_id_to_update, xml_value.text)

    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(str(soup))



def fill_html_from_xml(xml_datas,html_file, output_file):
    # Parse  XML file

    with open(xml_datas, 'r') as xml_file:
        xml_tree = etree.parse(xml_file)
        root = xml_tree.getroot()
        with open(html_file, 'r', encoding='utf-8') as file:
            soup = BeautifulSoup(file, 'html.parser')
            elements = soup.find_all(class_="annot")
            for element in elements:
                if element.get('id'):
                    element_id_to_update = element.get('id')
                    print(element_id_to_update)
                    xml_value = root.find(f".//{element_id_to_update}")  # Match XML tag with PDF field name
                    print(xml_value)
                    updated_element_by_id(soup, element_id_to_update, xml_value.text)

    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(str(soup))

def html_to_pdf(input_html: str, output_pdf: str):
    try:
        # Convert HTML to PDF
        pdfkit.from_file(input_html, output_pdf,configuration=config,options=options)
        print(f"PDF generated successfully: {output_pdf}")
    except Exception as e:
        print(f"An error occurred 2: {e}")

def generate(xml_data,template_name):
    # Generate a timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    # Use the timestamp in a filename
    filename = f"file_{timestamp}.pdf"
    output_pdf = os.path.join("requests_files",filename)   # Output filled PDF

    # Load the HTML file
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".html", mode="w", encoding="utf-8") as temp_file:
            temp_file_path = temp_file.name
            print(f"Temporary HTML file created at: {temp_file_path}")
            fill_html_from_xml_data(xml_data, template_name, temp_file_path)
            html_to_pdf(temp_file_path, output_pdf)
            print("Written file succesfully")
            print(temp_file_path)
            print(template_name)
            print(f"Final output pdf file {output_pdf}")

    except Exception as e:
        print(f"An error occurred: {e}")
        raise Exception("Error in mapping the template")

    return(filename)
