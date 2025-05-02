from tdmclient import ClientAsync

if __name__ == "__main__":

    with ClientAsync() as client:

        async def prog():
            with await client.lock() as node:
                while True:
                    str = input("System sound id (0-8 or exit): ")
                    if str == "exit":
                        break
                    try:
                        i = int(str)
                        error = await node.compile(f"leds_top = [0,0,32]")
                        if error is not None:
                            print(f"Compilation error: {error['error_msg']}")
                        else:
                            await node.watch(events=True)
                            error = await node.run()
                            if error is not None:
                                print(f"Error {error['error_code']}")
                    except ValueError:
                        print("Unexpected value")
                    client.process_waiting_messages()

        client.run_async_program(prog)