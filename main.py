from flask import Flask
from bot import register_bot_routes
from summarization import register_summary_routes
from qna import register_qna_routes
from ner import register_ner_routes

app = Flask(__name__)

# Register routes from different modules
register_bot_routes(app)
register_summary_routes(app)
register_qna_routes(app)
register_ner_routes(app)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
