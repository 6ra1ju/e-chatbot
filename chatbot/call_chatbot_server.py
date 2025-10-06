#!/usr/bin/env python3
"""
Call Chatbot Server - Django calls this script
"""

import sys
import requests

def call_chatbot_server(message: str):
    """Call the running chatbot server"""
    try:
        response = requests.post(
            'http://localhost:8001/chat',
            json={'message': message},
            timeout=300 
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get('response', 'No response')
        else:
            return f"Error: {response.status_code}"
            
    except requests.exceptions.ConnectionError:
        return "❌ Chatbot server chưa chạy. Vui lòng chạy: python3 simple_chatbot_server.py"
    except requests.exceptions.Timeout:
        return "⏱️ Chatbot timeout"
    except Exception as e:
        return f"❌ Error: {str(e)}"

if __name__ == "__main__":
    if len(sys.argv) > 1:
        message = sys.argv[1]
        response = call_chatbot_server(message)
        print(response)
    else:
        print("Usage: python call_chatbot_server.py <message>")

