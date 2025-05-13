from acudpclient.client import ACUDPClient

# Replace with your server address and port if needed
client = ACUDPClient()
client.listen()

while True:
    event = client.get_next_event(call_subscribers=False)
    print(event)