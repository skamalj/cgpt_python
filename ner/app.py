from flask import Flask, jsonify, request, abort
from flask_cors import CORS,cross_origin
import os, requests

app = Flask(__name__)

TEMPLATES_DIRECTORY = "ner/templates"
def register_ner_routes(app):
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

    @app.route('/ner', methods=['POST'])
    @cross_origin()
    def ner_route():
        try:
            entity_prompt = 'Please extract the following fields from the provided text. Return extracted fields as json\n\n'
            ner_data = request.get_json()  # Assuming JSON data is sent in the request
            filename = ner_data.get('filename')
            temperature = ner_data.get('temperature')
            template_definition = ner_data.get('template_definition')
            print(ner_data)

            # Make a request to the /summary endpoint using the requests library
            summary_response = requests.post(
                'http://localhost:5000/summarize',  # Replace with the actual URL of your summary endpoint
                json={
                    'file_location': filename,
                    'temperature': temperature,
                    'entity_prompt': f'{entity_prompt}{template_definition}\n\n',
                    'summary_type': 'entity_extraction'

                }
            )

            if summary_response.status_code == 200:
                summary_data = summary_response.json()
                # Process summary_data or return it as needed
                return jsonify(summary_data)
            else:
                return jsonify(error="Error occurred while calling /summary"), 500

        except Exception as e:
            print(e)
            return jsonify(error=str(e)), 500

if __name__ == '__main__':
    app.run(debug=True)
