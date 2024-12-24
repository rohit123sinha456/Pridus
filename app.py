import os
from flask import Flask, request, jsonify, render_template, send_file, current_app
from html2pdf import generate,generate_html
from lxml import etree
from flask_cors import CORS


def main(xml,template):
    filename = generate(xml,os.path.join(app.config['template_path'], template+".html"))
    print('filename = ',filename)
    return {"filename": filename}

def main_html(xml,template):
    filename = generate_html(xml,os.path.join(app.config['template_path'], template+".html"))
    print('filename = ',filename)
    return {"filename": filename}

app = Flask(__name__,static_folder='templates/static',)
CORS(app)


app.config['template_path'] = "templates"
if not os.path.exists("requests_files"):
    os.makedirs("requests_files")

@app.route('/upload-xml/<template>', methods=['POST'])
def upload_xml(template):
    try:
        xml_tree = None
        # Get the raw XML data from the request body
        xml_data = request.data
        if not xml_data:
            return jsonify({"error": "No XML data provided in the request body"}), 400

        # Parse the XML data
        try:
            xml_tree = etree.fromstring(xml_data)
            print("XML data parsed successfully")
        except etree.XMLSyntaxError as e:
            return jsonify({"error": f"Invalid XML format: {str(e)}"}), 400

        result = main(xml_tree,template)
        print("c")
        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


@app.route('/upload-xml-html/<template>', methods=['POST'])
def upload_xml_html(template):
    try:
        xml_tree = None
        # Get the raw XML data from the request body
        xml_data = request.data
        if not xml_data:
            return jsonify({"error": "No XML data provided in the request body"}), 400

        # Parse the XML data
        try:
            xml_tree = etree.fromstring(xml_data)
            print("XML data parsed successfully")
        except etree.XMLSyntaxError as e:
            return jsonify({"error": f"Invalid XML format: {str(e)}"}), 400

        result = main_html(xml_tree,template)
        print("c")
        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500



@app.route("/print/<name>")
def printpdf(name):
    url = "/reqpdf/"+name#+".pdf"
    html_template = "showandprint.html"
    return render_template(html_template,url=url)

@app.route("/reqpdf/<path:filename>")
def serve_pdf(filename):
    pdf_path = os.path.join("requests_files", filename)
    return send_file(pdf_path, mimetype="application/pdf")

@app.route("/reqhtml/<path:filename>")
def serve_html(filename):
    pdf_path = os.path.join("requests_files_html", filename)
    return send_file(pdf_path, mimetype="text/html")

if __name__ == "__main__":
    app.run(debug=True,host="0.0.0.0",port=5000)
