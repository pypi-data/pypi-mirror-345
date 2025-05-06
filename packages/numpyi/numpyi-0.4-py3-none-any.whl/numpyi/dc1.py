code = '''
#server.py
from xmlrpc.server import SimpleXMLRPCServer
import threading

def factorial(n):
    if n==0 or n==1:
        return 1
    else:
        return n*factorial(n-1)
    
def shutdown():
    print("Shutting down server...")
    threading.Thread(target=server.shutdown).start()
    return "Server shut down."

server = SimpleXMLRPCServer(("localhost", 8000), allow_none=True)
print("Server is listening on port 8000")
server.register_function(factorial, "factorial")
server.register_function(shutdown, "shutdown")
server.serve_forever()

**************************************************************
#client.py
from xmlrpc.client import ServerProxy

proxy = ServerProxy("http://localhost:8000/")

while True:
    user_input = input("Enter a number to compute it's factorial (or type 'exit' to close)").strip()

    if user_input.lower() == 'exit':
        try:
            print(proxy.shutdown())
        except:
            print("Server is already shut")
        break

    try:
        num = int(user_input)
        result = proxy.factorial(num)
        print(f"Factorial of {num} is {result}")
    except ValueError:
        print("Enter a valid number")
'''
print(code)