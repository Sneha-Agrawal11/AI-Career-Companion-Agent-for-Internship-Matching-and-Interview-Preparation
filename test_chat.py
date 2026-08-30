import sys
import os
import traceback
sys.path.insert(0, os.path.abspath('.'))

from app.services.chat_service import ChatService

try:
    service = ChatService()
    print('Testing retrieve_context...')
    context = service.retrieve_context('What features does InternMatch provide?')
    print(f'Context length: {len(context)}')
    
    print('Testing Groq generation...')
    has_key = "GROQ_API_KEY" in os.environ
    print(f'GROQ_API_KEY present: {has_key}')
    if has_key:
        print(f'Length of key: {len(os.environ["GROQ_API_KEY"])}')
        
    response = service.generate_response('What features does InternMatch provide?', [])
    print(f'Response: {response}')
except Exception as e:
    traceback.print_exc()
