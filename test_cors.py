import requests

def test_cors():
    url = "http://localhost:5000/api/auth/login"
    origin = "http://localhost:8081"
    headers = {
        "Origin": origin,
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "Content-Type"
    }
    
    print(f"Testing CORS for {url} with Origin: {origin}")
    try:
        # Test OPTIONS request (Preflight)
        resp = requests.options(url, headers=headers)
        print(f"Status Code: {resp.status_code}")
        print("Headers:")
        for k, v in resp.headers.items():
            if 'Access-Control' in k:
                print(f"  {k}: {v}")
                
        if resp.headers.get('Access-Control-Allow-Origin') == origin:
            print("\n✅ CORS Preflight check passed!")
        else:
            print("\n❌ CORS Preflight check failed! Origin not allowed.")
            
    except Exception as e:
        print(f"\n❌ Connection failed: {e}")
        print("Make sure the backend server is running on port 5000")

if __name__ == "__main__":
    test_cors()