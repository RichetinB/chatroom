import asyncio
import aioconsole
import websockets

IP = "185.157.247.84"
PORT = 13337

async def send_pseudo(websocket):
    pseudo = await aioconsole.ainput("Choose a pseudo: ")
    message = f"Hello|{pseudo}"
    await websocket.send(message)

async def async_input(websocket):
    while True:
        message = await aioconsole.ainput("Enter message: ")
        await websocket.send(message)

async def async_receive(websocket):
    while True:
        data = await websocket.recv()
        if not data:
            print("Server disconnected. Exiting.")
            break
        print(data)

async def main():
    async with websockets.connect(f"ws://{IP}:{PORT}") as websocket:
        await send_pseudo(websocket)

        input_task = asyncio.create_task(async_input(websocket))
        receive_task = asyncio.create_task(async_receive(websocket))

        await asyncio.gather(input_task, receive_task)

if __name__ == "__main__":
    asyncio.run(main())
