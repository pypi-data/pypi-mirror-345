"""
Example usage of the RateLimitAPI Python package

This example demonstrates how to use the RateLimitAPI package with different
Python web frameworks.
"""

# Example with a simple Request object
class SimpleRequest:
    def __init__(self, method, url, headers):
        self.method = method
        self.url = url
        self.headers = headers

# Flask example
def flask_example():
    print("=== Flask Example ===")
    try:
        from flask import Flask, request, jsonify
        from ratelimitapi import is_rate_limited
        
        print("""
# Flask Integration Example
from flask import Flask, request, jsonify
from ratelimitapi import is_rate_limited

app = Flask(__name__)

@app.route('/api/resource')
def api_resource():
    # Check for rate limiting
    limited_response = is_rate_limited(request, "rlimit_your_token_here")
    if limited_response:
        response_body, status_code, headers = limited_response
        return jsonify(response_body), status_code, headers
        
    # Process the request normally
    return jsonify({"message": "Request processed successfully"})
        """)
    except ImportError:
        print("Flask is not installed. Install with: pip install flask")

# Django example
def django_example():
    print("\n=== Django Example ===")
    try:
        print("""
# Django Integration Example
from django.http import JsonResponse
from ratelimitapi import is_rate_limited

def api_view(request):
    # Check for rate limiting
    limited_response = is_rate_limited(request, "rlimit_your_token_here")
    if limited_response:
        response_body, status_code, headers = limited_response
        response = JsonResponse(response_body, status=status_code)
        for key, value in headers.items():
            response[key] = value
        return response
        
    # Process the request normally
    return JsonResponse({"message": "Request processed successfully"})
        """)
    except Exception as e:
        print(f"Error: {e}")

# FastAPI example
def fastapi_example():
    print("\n=== FastAPI Example ===")
    try:
        print("""
# FastAPI Integration Example
from fastapi import FastAPI, Request, Response
from ratelimitapi import is_rate_limited

app = FastAPI()

@app.get("/api/resource")
async def api_resource(request: Request):
    # Check for rate limiting
    limited_response = is_rate_limited(request, "rlimit_your_token_here")
    if limited_response:
        response_body, status_code, headers = limited_response
        
        # Create a FastAPI response with appropriate status and headers
        response = Response(
            content=json.dumps(response_body),
            media_type="application/json",
            status_code=status_code
        )
        
        # Add headers
        for key, value in headers.items():
            response.headers[key] = value
            
        return response
        
    # Process the request normally
    return {"message": "Request processed successfully"}
        """)
    except ImportError:
        print("FastAPI is not installed. Install with: pip install fastapi")

if __name__ == "__main__":
    print("RateLimitAPI Python Package Usage Examples\n")
    
    # Show generic example
    print("=== Basic Usage Example ===")
    print("""
from ratelimitapi import is_rate_limited

def handle_request(request):
    limited_response = is_rate_limited(request, "rlimit_your_token_here")
    if limited_response:
        response_body, status_code, headers = limited_response
        # Return the 429 response if rate-limited
        return create_response(response_body, status_code, headers)
        
    # Continue with normal request handling if not rate-limited
    # ...
    """)
    
    # Framework-specific examples
    flask_example()
    django_example()
    fastapi_example()
