from django.shortcuts import render
from django.http import JsonResponse, StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import subprocess
import sys
import os
from .models import Product

def product_list(request):
    """Get all products"""
    products = Product.objects.all()
    data = []
    
    for product in products:
        product_data = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'original_price': product.original_price,
            'discount': product.discount,
            'rating': product.rating,
            'sold_count': product.sold_count,
            'image': product.image,
            'labels': product.get_labels_list()
        }
        data.append(product_data)
    
    return JsonResponse(data, safe=False)

def product_detail(request, product_id):
    """Get specific product by ID"""
    try:
        product = Product.objects.get(id=product_id)
        data = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'original_price': product.original_price,
            'discount': product.discount,
            'rating': product.rating,
            'sold_count': product.sold_count,
            'image': product.image,
            'labels': product.get_labels_list()
        }
        return JsonResponse(data)
    except Product.DoesNotExist:
        return JsonResponse({'error': 'Product not found'}, status=404)

@csrf_exempt
@require_http_methods(["POST"])
def create_product(request):
    """Create a new product"""
    try:
        data = json.loads(request.body)
        product = Product.objects.create(
            name=data['name'],
            price=data['price'],
            original_price=data.get('original_price'),
            discount=data.get('discount'),
            rating=data.get('rating'),
            sold_count=data.get('sold_count'),
            image=data.get('image')
        )
        
        # Set labels if provided
        if 'labels' in data:
            product.set_labels_list(data['labels'])
            product.save()
        
        return JsonResponse({
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'original_price': product.original_price,
            'discount': product.discount,
            'rating': product.rating,
            'sold_count': product.sold_count,
            'image': product.image,
            'labels': product.get_labels_list()
        }, status=201)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
@require_http_methods(["POST"])
def chatbot_chat(request):
    """Chat with the AI chatbot using streaming response"""
    try:
        data = json.loads(request.body)
        message = data.get('message', '')
        
        if not message:
            return JsonResponse({'error': 'Message is required'}, status=400)
        
        # Path to the chatbot script
        chatbot_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'chatbot')
        api_script_path = os.path.join(chatbot_path, 'call_chatbot_server.py')
        
        # Check if files exist
        if not os.path.exists(api_script_path):
            return JsonResponse({'error': f'Script not found: {api_script_path}'}, status=500)
        
        # Run the chatbot script
        process = subprocess.Popen(
            [sys.executable, api_script_path, message],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=chatbot_path
        )
        
        # No timeout - let it run as long as needed
        stdout, stderr = process.communicate()
        
        # Log for debugging
        print(f"[DEBUG] Return code: {process.returncode}")
        print(f"[DEBUG] Stdout: {stdout[:200] if stdout else 'None'}")
        print(f"[DEBUG] Stderr: {stderr[:200] if stderr else 'None'}")
        
        if process.returncode == 0:
            response_text = stdout.strip()
            if response_text:
                return JsonResponse({
                    'response': response_text,
                    'status': 'success'
                })
            else:
                return JsonResponse({
                    'response': 'Không có phản hồi từ chatbot.',
                    'status': 'error'
                })
        else:
            error_msg = stderr.strip() if stderr else "Unknown error"
            # Return first 500 chars of error for debugging
            return JsonResponse({
                'response': f'Xin lỗi, có lỗi xảy ra. Vui lòng thử lại.',
                'error_details': error_msg[:500],
                'status': 'error'
            })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
