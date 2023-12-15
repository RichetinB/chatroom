import asyncio
import websockets

global CLIENTS
CLIENTS = {}

async def handle_client(websocket, path):
    client_address = websocket.remote_address
    print(f"Received connection from {client_address}")

    if client_address in CLIENTS:
        print(f"Client {client_address} is already connected. Ignoring.")
        return

    CLIENTS[client_address] = {}
    CLIENTS[client_address]["ws"] = websocket
 

    pseudo_message = await websocket.recv()

    if pseudo_message.startswith("Hello|"):
        pseudo = pseudo_message.split("|")[1]

        if pseudo in [info.get("pseudo") for info in CLIENTS.values() if "pseudo" in info]:
            print(f"Pseudo '{pseudo}' is already taken. Closing connection.")
            del CLIENTS[client_address]
            return

        CLIENTS[client_address]["pseudo"] = pseudo
        print(f"New client joined: {pseudo}")

        for addr, client_info in CLIENTS.items():
            if addr != client_address:
                announcement = f"Annonce: {pseudo} a rejoint la chatroom"
                await client_info["ws"].send(announcement)

    try:
        while True:
            message = await websocket.recv()

            for addr, client_info in CLIENTS.items():
                if addr != client_address and "pseudo" in CLIENTS[client_address]:
                    sender_pseudo = CLIENTS[client_address]["pseudo"]
                    broadcast_message = f"\n{sender_pseudo} a dit : {message}"
                    await client_info["ws"].send(broadcast_message)

    except (websockets.exceptions.ConnectionClosedError, websockets.exceptions.ConnectionClosedOK):
     pass


    finally:
        print(f"Connection from {client_address} closed.")
        if client_address in CLIENTS:
            pseudo = CLIENTS[client_address].get("pseudo", "Unknown")
            del CLIENTS[client_address]

            # Broadcast the departure announcement
            for addr, client_info in CLIENTS.items():
                announcement = f"Annonce: {pseudo} a quitté la chatroom"
                await client_info["ws"].send(announcement)


async def main():
    async with websockets.serve(
        handle_client, '185.157.247.84', 13337,
    ):
        print("Serving on ws://185.157.247.84:13337")

        await asyncio.Future()
if __name__ == "__main__":
    asyncio.run(main())
