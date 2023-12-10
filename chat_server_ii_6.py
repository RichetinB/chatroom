import asyncio

global CLIENTS
CLIENTS = {}

async def handle_client(reader, writer):
    client_address = writer.get_extra_info('peername')
    print(f"Received connection from {client_address}")

    if client_address in CLIENTS:
        print(f"Client {client_address} is already connected. Ignoring.")
        writer.close()
        return

    CLIENTS[client_address] = {}
    CLIENTS[client_address]["r"] = reader
    CLIENTS[client_address]["w"] = writer

    pseudo_data = await reader.read(1024)
    if not pseudo_data:
        return

    pseudo_message = pseudo_data.decode()

    if pseudo_message.startswith("Hello|"):
        pseudo = pseudo_message.split("|")[1]

        if pseudo in [info.get("pseudo") for info in CLIENTS.values() if "pseudo" in info]:
            print(f"Pseudo '{pseudo}' is already taken. Closing connection.")
            writer.close()
            del CLIENTS[client_address]
            return

        CLIENTS[client_address]["pseudo"] = pseudo
        print(f"New client joined: {pseudo}")

        for addr, client_info in CLIENTS.items():
            if addr != client_address:
                announcement = f"Annonce: {pseudo} a rejoint la chatroom"
                client_info["w"].write(announcement.encode())
                await client_info["w"].drain()

    try:
        while True:
            data = await reader.read(1024)
            if not data:
                # Handle disconnection
                break

            message = data.decode()

            for addr, client_info in CLIENTS.items():
                if addr != client_address and "pseudo" in CLIENTS[client_address]:
                    sender_pseudo = CLIENTS[client_address]["pseudo"]
                    broadcast_message = f"\n{sender_pseudo} a dit : {message}"
                    client_info["w"].write(broadcast_message.encode())
                    await client_info["w"].drain()

    finally:
        print(f"Connection from {client_address} closed.")
        if client_address in CLIENTS:
            pseudo = CLIENTS[client_address].get("pseudo", "Unknown")
            del CLIENTS[client_address]

            # Broadcast the departure announcement
            for addr, client_info in CLIENTS.items():
                announcement = f"Annonce: {pseudo} a quitté la chatroom"
                client_info["w"].write(announcement.encode())
                await client_info["w"].drain()

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
