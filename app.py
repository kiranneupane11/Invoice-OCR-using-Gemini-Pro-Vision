from flask import Flask, render_template, jsonify,request
import google.generativeai as genai
import os
from flask_cors import CORS
import base64, io
from PIL import Image
from werkzeug.exceptions import BadRequest


credential_path = u"C:\\Users\\Dell\\Desktop\\Credential File\\cred_file_key.json"
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credential_path
genai.configure(api_key=os.getenv("API_KEY"))

app = Flask(__name__)

CORS(app, origins=['http://127.0.0.1:5500'],
     methods=['GET', 'POST', 'PUT', 'DELETE'],
     headers=['Content-Type'])

# popularSignatures = {
#     'iVBORw0KGgo': 'image/png',
#     '/9j/': 'image/jpg',
#     'Qk02U': 'image/bmp',
#     '/xff/d8/ff/': 'image/jpeg',
#     'UklGR': 'image/webp',
# }

# def getMimeType(base64EncodedString):
#     for sign in popularSignatures:
#         if base64EncodedString.startswith(sign):
#             return popularSignatures[sign]
#     return None


@app.route('/',methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/ocr', methods=['POST'])
def ocr():
    try:
        data = request.json['image']
        # print("Image data:", image_data)

        # Get the image MIME type        
        # mimeType = getMimeType(data)

        # Decode the image data
        image_data = base64.b64decode(data)

        # Open the image using PIL
        img = Image.open(io.BytesIO(image_data))
        print("Image opened successfully")

        img_bytes = io.BytesIO()
        img.save(img_bytes, format='WEBP')
        img_webp = img_bytes.getvalue()

        image={
            "mime_type":'image/webp',
            "data":img_webp
        }

        # Predefined-Prompt for OCR
        prompt = """
        You’re an experienced data extraction specialist with a keen eye for detail and precision. Your expertise in parsing structured data from various sources is unmatched, and you take pride in converting complex information into easily understandable formats. Your task is to extract invoice data from the provided image and convert it into JSON format. If an item name does not have a price, you should join it to the preceding item name.
        Please fill in the necessary details:
        - Date of the invoice: ________
        - Vendor details: ________
        - Item details with price: ________
        - Subtotal: ________
        - Taxes: ________
        - Total amount: ________
        Remember, accuracy is key in this task. Ensure that the JSON format captures all relevant information correctly, including any adjustments made for items without prices. Be thorough in your extraction process and maintain the integrity of the data.
        For example, if the invoice contains items like -
        - Item 1: Pen
        - Item 2: Notebook - Price: $5
        - Item 3: Pencil
        - Item 4: Eraser - Price: $2
        The JSON format should represent this as:
        {
        "items": [
        {"name": "Pen"},
        {"name": "Notebook", "price": "$5"},
        {"name": "Pencil"},
        {"name": "Eraser - Price: $2"}
        ],
        "subtotal": "$7",
        "taxes": "$1",
        "total": "$8"
        }
        """

        model_behavior = """You are a specialist in comprehending receipts.
                            Input images in the form of receipts will be provided to you,
                            and your task is to display the content of the input image while following the prompt instructions meticulously."""
        
        prompt_parts=[prompt,image,model_behavior]

        #Import and Load Model
        model = genai.GenerativeModel("gemini-pro-vision")
        response = model.generate_content(prompt_parts)
        return jsonify({"response": response.text})

    except BadRequest:
        print("Bad request")
        print(request.data)
        print(request.headers)
        return jsonify({"error": "Bad request"}), 400
    except KeyError as e:
        print("KeyError:", e)
        print(request.json)
        return jsonify({"error": "KeyError: 'image'"}), 400
    except Exception as e:
        print("Exception:", e)
        return jsonify({"error": "Internal Server Error"}), 500

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)  
    

