from flask import Flask, jsonify, request, abort
from flask_cors import CORS,cross_origin
import os

app = Flask(__name__)

TEMPLATES_DIRECTORY = "templates"

@app.route('/templates', methods=['GET'])
@cross_origin()
def get_templates():
    templates = {}

    # Read template data from files in the templates directory
    for filename in os.listdir(TEMPLATES_DIRECTORY):
        if filename.endswith(".txt"):
            template_name = os.path.splitext(filename)[0]
            template_path = os.path.join(TEMPLATES_DIRECTORY, filename)
            with open(template_path, 'r') as template_file:
                template_definition = template_file.read()
                templates[template_name] = template_definition

    return jsonify(templates)

@app.route('/template', methods=['POST'])
@cross_origin()
def create_template():
    try:
        data = request.json
        template_name = data.get('name')
        template_definition = data.get('definition')

        if not template_name or not template_definition:
            return jsonify(message="Both 'name' and 'definition' are required"), 400

        template_filename = template_name + ".txt"
        template_path = os.path.join(TEMPLATES_DIRECTORY, template_filename)

        with open(template_path, 'w') as template_file:
            template_file.write(template_definition)

        # Get updated list of templates
        updated_templates = get_templates().json

        return jsonify(message=f"Template '{template_name}' created successfully", templates=updated_templates), 201

    except Exception as e:
        print(e)
        return jsonify(message="An error occurred while creating the template"), 500

if __name__ == '__main__':
    app.run(debug=True)
