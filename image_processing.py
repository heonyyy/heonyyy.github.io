# image_processing.py
import os
import openai
import requests
from PIL import Image
import io, base64
from rembg import remove
from flask import Blueprint, request, jsonify, send_file, session
from flask_login import login_required, current_user
from models import db, UserImage

# 블루프린트
process_text = Blueprint('process_text', __name__)

# 배경 제거 함수
def remove_background_transparent(img):
    result = remove(img)
    return result

# 이미지 생성 엔드포인트
@process_text.route('/process_text', methods=['POST'])
@login_required
def process_text_route():
    user_id = session.get('user_id')
    if user_id:
        print(f"Request data: {request.json}")
        data = request.json
        text = data['text']
        mode = data.get('mode', 'FullImage')

        client = openai.OpenAI(api_key="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")

        if mode == 'Sticker':
            response = client.images.generate(
                model="dall-e-3",
                prompt=f"[[아무것도 없는 투명한 배경에 {text}를 색이 있는 스티커 형식.]]",
                size="1024x1024",
                quality="standard",
                n=1,
            )
        elif mode == 'FullImage':
            response = client.images.generate(
                model="dall-e-3",
                prompt=text,
                size="1024x1024",
                quality="standard",
                n=1,
            )
        else:
            return jsonify({'error': 'Invalid mode'}), 400
        
        generated_image_url = response.data[0].url
        
        # 이미지 파일 저장
        try:
            image_data = requests.get(generated_image_url).content
            image = Image.open(io.BytesIO(image_data))

            if mode == 'Sticker':
                # 배경 제거 및 투명화 처리
                transparent_img = remove_background_transparent(image)
                
                # 이미지를 바이너리 데이터로 변환
                img_byte_arr = io.BytesIO()
                transparent_img.save(img_byte_arr, format='PNG')
                img_byte_arr = img_byte_arr.getvalue()
            else:
                # 이미지를 바이너리 데이터로 변환
                img_byte_arr = io.BytesIO()
                image.save(img_byte_arr, format='PNG')
                img_byte_arr = img_byte_arr.getvalue()
            
            # 이미지를 데이터베이스에 저장
            new_image = UserImage(user_id=current_user.id, image_data=img_byte_arr)
            db.session.add(new_image)
            db.session.commit()
            
            # 이미지를 Base64 인코딩하여 데이터 URL 형식으로 반환
            image_data = base64.b64encode(img_byte_arr).decode('utf-8')
            image_url = f"data:image/png;base64,{image_data}"
            return jsonify({'imageUrl': image_url})

        except Exception as e:
            print(f"Error processing image: {str(e)}")
            return jsonify({'error': 'Failed to process image'}), 500
    else:
        return jsonify({'error': 'Unauthorized'}), 401


# 이미지 전체 조회 엔드포인트
@process_text.route('/images', methods=['GET'])
@login_required
def get_user_images():
    user_id = current_user.id
    images = UserImage.query.filter_by(user_id=user_id).all()
    image_data_list = []

    for image in images:
        image_data = io.BytesIO(image.image_data)
        image_data_list.append(base64.b64encode(image_data.getvalue()).decode('utf-8'))

    return jsonify({'images': image_data_list})

# 이미지 개별 조회 엔드포인트
@process_text.route('/image/<int:image_id>', methods=['GET'])
@login_required
def get_image(image_id):
    image = UserImage.query.get(image_id)

    if image and image.user_id == current_user.id:
        image_data = io.BytesIO(image.image_data)
        return send_file(image_data, mimetype='image/png')
    else:
        return jsonify({'error': 'Image not found or unauthorized'}), 404