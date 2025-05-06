
text = '''import xmlrpc.client
# Connect to the server
Proxy=
xmlrpc.client.ServerProxy("http://localhost:8000/")

# Input integer from user
num = int(input("Enter an integer to compute its factorial: "))

# Call the remote factorial function
result = proxy.factorial(num)

print(f"The factorial of {num} is: {result}")





Rpc_server.py

from xmlrpc.server import SimpleXMLRPCServer
import math
def factorial(n):
    if n < 0:
        return "Invalid input: Negative number"
    if n == 0 or n == 1:
        return 1
    else:
        return n * factorial(n - 1)

# Set up the RPC server
server = SimpleXMLRPCServer(("localhost", 8000))
print("RPC Server listening on port 8000...")

# Register the factorial function
server.register_function(factorial, "factorial")

# Run the server
server.serve_forever()'''

print(text)
 

