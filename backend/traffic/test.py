import socket
def get_local_ip():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))  
            local_ip = s.getsockname()[0]  
        return local_ip
    except Exception as e:
        return f"Error: {e}"
    
print(get_local_ip())