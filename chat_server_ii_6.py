import asyncio

global CLIENTS
CLIENTS = {}

async def handle_client(reader, writer):
    client_address = writer.get_extra_info('peername')
    print(f"Received connection from {client_address}")

    # Receive the initial message containing the pseudo
    pseudo_data = await reader.read(1024)
    if not pseudo_data:
        return
    pseudo_message = pseudo_data.decode()
    
    # Check if the client is new
    if pseudo_message.startswith("Hello|"):
        pseudo = pseudo_message.split("|")[1]

        # Check if the pseudo is already taken
        if pseudo in [info["pseudo"] for info in CLIENTS.values()]:
            print(f"Pseudo '{pseudo}' is already taken. Closing connection.")
            writer.close()
            return

        # Add client information to CLIENTS dictionary
        CLIENTS[client_address] = {"r": reader, "w": writer, "pseudo": pseudo}
        print(f"New client joined: {pseudo}")

        # Broadcast the arrival announcement
        for addr, client_info in CLIENTS.items():
            if addr != client_address:
                announcement = f"Annonce: {pseudo} a rejoint la chatroom"
                client_info["w"].write(announcement.encode())
                await client_info["w"].drain()

    try:
        while True:
            data = await reader.read(1024)
            if not data:
                break
            message = data.decode()

            # Check for the disconnection message
            if message == "":
                break

            for addr, client_info in CLIENTS.items():
                if addr != client_address:
                    sender_pseudo = CLIENTS[client_address]["pseudo"]
                    broadcast_message = f"\n{sender_pseudo} a dit : {message}"
                    client_info["w"].write(broadcast_message.encode())
                    await client_info["w"].drain()

    finally:
        print(f"{CLIENTS[client_address]['pseudo']} has left the chatroom.")
        del CLIENTS[client_address]
        writer.close()

async def main():
    server = await asyncio.start_server(
        handle_client, '185.157.247.84', 13337)

    addr = server.sockets[0].getsockname()
    print(f'Serving on {addr}')

    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())
