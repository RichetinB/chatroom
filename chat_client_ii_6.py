import asyncio
import aioconsole

IP = "185.157.247.84"
PORT = 13337

async def send_pseudo(writer):
    pseudo = await aioconsole.ainput("Choose a pseudo: ")
    message = f"Hello|{pseudo}"
    writer.write(message.encode())
    await writer.drain()

async def async_input(writer):
    while True:
        message = await aioconsole.ainput("Enter message: ")
        writer.write(message.encode())
        await writer.drain()

async def async_receive(reader):
    while True:
        data = await reader.read(1024)
        if not data:
            print("Server disconnected. Exiting.")
            break
        print(data.decode())

async def main():
    reader, writer = await asyncio.open_connection(host=IP, port=PORT)

    await send_pseudo(writer)

    input_task = asyncio.create_task(async_input(writer))
    receive_task = asyncio.create_task(async_receive(reader))

    await asyncio.gather(input_task, receive_task)

if __name__ == "__main__":
    asyncio.run(main())
