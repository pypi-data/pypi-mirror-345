print("""

# server.py

from xmlrpc.server import SimpleXMLRPCServer
import threading

# Factorial function
def factorial(n):
    if n == 0 or n == 1:
        return 1
    else:
        return n * factorial(n - 1)

# Shutdown function
def shutdown():
    print("Shutting down the server...")
    threading.Thread(target=server.shutdown).start()
    return "Server is shutting down."

# Server setup
server = SimpleXMLRPCServer(("localhost", 8000), allow_none=True)
print("Server is listening on port 8000...")

# Register functions
server.register_function(factorial, "factorial")
server.register_function(shutdown, "shutdown")

# Start the server
server.serve_forever()




# client.py


import xmlrpc.client

# Connect to the server
proxy = xmlrpc.client.ServerProxy("http://localhost:8000/")

# User interaction loop
while True:
    user_input = input("Enter a number to compute its factorial (or type 'exit' to quit): ").strip()

    if user_input.lower() == 'exit':
        try:
            print(proxy.shutdown())
        except:
            print("Server already shut down.")
        break

    try:
        num = int(user_input)
        result = proxy.factorial(num)
        print(f"Factorial of {num} is {result}")
    except ValueError:
        print("Please enter a valid integer or 'exit'.")



""")
