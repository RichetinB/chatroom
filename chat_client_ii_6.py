import asyncio
import aioconsole

IP = "185.157.247.84"
PORT = 13337

async def send_pseudo(writer):
    pseudo = input("Choose a pseudo: ")
    message = f"Hello|{pseudo}"
    writer.write(message.encode())
    await writer.drain()  # Modifier ici pour attendre de manière asynchrone

async def async_input(writer):
    while True:
        message = await aioconsole.ainput("Enter message: ")
        writer.write(message.encode())
        await writer.drain()

async def async_receive(reader):
    while True:
        data = await reader.read(1024)
        if not data:
            print("Disconnected from the server. Exiting.")
            break
        print(data.decode())

async def main():
    reader, writer = await asyncio.open_connection(host=IP, port=PORT)

    # Send the chosen pseudo to the server
    await send_pseudo(writer)

    # Start the asynchronous tasks
    input_task = asyncio.create_task(async_input(writer))
    receive_task = asyncio.create_task(async_receive(reader))

    # Wait for any of the tasks to complete
    await asyncio.wait([input_task, receive_task], return_when=asyncio.FIRST_COMPLETED)

    # Close the connection when any of the tasks is done
    writer.close()
    await writer.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())
