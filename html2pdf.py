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
    'page-size': 'A4',
    'encoding': "UTF-8",
    "enable-local-file-access": True,
    'margin-top': '35mm',
    'margin-right': '2mm',
    'margin-bottom': '2mm',
    'margin-left': '1mm'
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
# deprecated
def fill_html_from_xml_data_v1(xml_datas,html_file, output_file):
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

        # Setting singular annotation annotations
        elements = soup.find_all(class_="annot")
        for element in elements:
            if element.get('id'):
                element_id_to_update = element.get('id')
                print(element_id_to_update)
                xml_value = root.find(f".//{element_id_to_update}")  # Match XML tag with PDF field name
                print(xml_value)
                updated_element_by_id(soup, element_id_to_update, xml_value.text)


        # Inserting the Recuring singular data
        rows_per_page = 2

        # Get the table body element
        table = soup.find('table',class_="annot_table")#soup.find('tbody')
        table_id = table.get('id')
        print(f"The id of the table is {table.get('id')}")
        table_body = table.find('tbody')
        print(f"The table body is {table_body}")
        # Check if <person> tags exist
        if root.findall('person'):
            # Insert rows and add page breaks
            row_count = 0
            for person in root.findall(table_id):
                row = soup.new_tag('tr')
                id_td = soup.new_tag('td')
                id_td.string = person.find('id').text
                name_td = soup.new_tag('td')
                name_td.string = person.find('name').text
                age_td = soup.new_tag('td')
                age_td.string = person.find('age').text

                row.append(id_td)
                row.append(name_td)
                row.append(age_td)
                table_body.append(row)
                print(row)
                row_count += 1

                # Add page break after certain rows
                if row_count % rows_per_page == 0:
                    page_break = soup.new_tag('tr', style="page-break-after: always;")
                    table_body.append(page_break)
        else:
            print("No <person> tags found in the XML data.")
    print(f"The table body is {table_body}")
    print(row_count)
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(str(soup))

def fill_html_from_xml_data(xml_datas,html_file, output_file):
    file_path =str(Path(current_app.config.root_path)/'templates'/'static')
    print(f"The filepath to pdfkit for assets in h2pdf - {file_path}")
    root = xml_datas
    with (open(html_file, 'r', encoding='utf-8') as file):
        soup = BeautifulSoup(file, 'html.parser')
        # Setting header images
        img_tag = soup.find('img', {'id': 'headerimg'})

        # Set the 'src' attribute if the tag is found
        if img_tag:
            img_tag['src'] = os.path.join(file_path,'header.png')

        # Setting singular annotation annotations
        for element in soup.find_all(attrs={"data-field": True}):
            field_name = element['data-field']  # Get the value of data-field
            xml_value = root.find(f".//{field_name}")  # Find the corresponding XML tag
            if xml_value is not None:
                element.string = xml_value.text  # Update the content
                print(f"Updated '{field_name}' to '{xml_value.text}'")
        # elements = soup.find_all(class_="annot")
        # for element in elements:
        #     if element is not None:
        #         element_id_to_update = element.get('id')
        #         matching_elements = soup.find_all(id=element_id_to_update)  # Find all elements with the given ID
        #         print("Matching Elements are")
        #         print(matching_elements)
        #         print(element_id_to_update)
        #         xml_value = root.find(f".//{element_id_to_update}")  # Match XML tag with PDF field name
        #         print(xml_value)
        #         for matching_element in matching_elements:
        #             updated_element_by_id(soup, element_id_to_update, xml_value.text)
        #

        # Inserting the Recuring singular data
        table = soup.find('table',class_="annot_table")#soup.find('tbody')
        divs_after_table = []

        # Collect all div elements following the annot_table
        if table:
            next_sibling = table.parent.find_next_sibling("div")
            while next_sibling:
                next_sibling_name = getattr(next_sibling, 'name', None)
                print(f"The name of next sibling {next_sibling.name}")
                if next_sibling_name in ['div','table']:
                    divs_after_table.append(next_sibling)
                    # next_sibling.extract()  # Remove it from the DOM
                next_sibling = next_sibling.find_next_sibling()

        print(f"Extracted {len(divs_after_table)} div(s) after the annot_table.")

        if table is not None:
            table_id = table.get('id')
            print(f"The id of the table is {table.get('id')}")
            thead = table.find('thead')
            header_cells = thead.find_all('th')  # Extract all header cells
            headers = [header.text.strip() for header in header_cells]
            # Use this
            # headers = []
            # for header in header_cells:
            #     data_field = header.get('data-field')  # Get the data-field attribute if it exists
            #     if data_field:  # Add to the list only if data-field exists
            #         headers.append(data_field)
            print(f"Extracted headers: {headers}")

            # Split rows into chunks and create separate tables
            rows_per_page = 10
            table_chunks = [root.findall(table_id)[i:i + rows_per_page] for i in
                            range(0, len(root.findall(table_id)), rows_per_page)]

            # Get the table body element

            for i, chunk in enumerate(table_chunks):
                new_table = soup.new_tag('table', attrs={'class': f'annot_table_{i}'})

                # Reuse the extracted headers
                new_thead = soup.new_tag('thead')
                header_row = soup.new_tag('tr')
                for header in headers:
                    th = soup.new_tag('th')
                    th.string = header
                    header_row.append(th)
                new_thead.append(header_row)
                new_table.append(new_thead)

                # Add rows for each person in the current chunk
                tbody = soup.new_tag('tbody')
                for person in chunk:
                    row = soup.new_tag('tr')
                    for header in headers:
                        cell = soup.new_tag('td')
                        value = person.find(header)  # Dynamically find the value based on the header
                        print(value)
                        cell.string = value.text if value is not None else ""  # Handle missing values gracefully
                        row.append(cell)
                    tbody.append(row)
                print("The TBody is ")
                print(tbody)
                new_table.append(tbody)
                soup.body.append(new_table)

                # Add a page break after the table
                if i < len(table_chunks) - 1:
                    page_break = soup.new_tag('div', style="page-break-after: always;")
                    soup.body.append(page_break)

            for div in divs_after_table:
                soup.body.append(div)
            table.extract()
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(str(soup))




# deprecated
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
    file_path = str(Path(current_app.config.root_path)/'templates'/'static')
    header_img = os.path.join(file_path, 'header.png')
    header_html_file_path = generate_header_html(header_img)
    options['header-html'] = header_html_file_path
    options['header-spacing'] = '0'  # Adjust spacing for header
    try:
        # Convert HTML to PDF
        pdfkit.from_file(input_html, output_pdf,configuration=config,options=options)
        print(f"PDF generated successfully: {output_pdf}")
    except Exception as e:
        print(f"An error occurred 2: {e}")


def generate_header_html(header_image_path: str) -> str:
    file_path =str(Path(current_app.config.root_path)/'templates'/'static')
    # print(f"The filepath to pdfkit for assets in h2pdf - {file_path}")
    header_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            .headert {{
                text-align: center;
                width: 100%;
            }}
            .headert img {{
                max-width: 100%;
                height: auto;
            }}
        </style>
    </head>
    <body>
        <div class="headert">
            <img src="{header_image_path}" alt="Header">
        </div>
    </body>
    </html>
    """
    # File to save the header HTML
    header_temp_file = os.path.join(file_path,"header_temp.html")

    # Check if the file exists
    if not os.path.exists(header_temp_file):
        with open(header_temp_file, 'w', encoding='utf-8') as file:
            file.write(header_html)

    return header_temp_file



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
