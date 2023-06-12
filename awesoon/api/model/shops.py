from flask_restx import fields


prompt_model = {
    "prompt": fields.String(required=True)
}
