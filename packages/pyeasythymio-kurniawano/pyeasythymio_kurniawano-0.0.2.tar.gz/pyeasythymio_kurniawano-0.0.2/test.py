from tdmclient import ClientAsync

if __name__ == "__main__":

    with ClientAsync() as client:

        async def prog():
            with await client.lock() as node:
                    try:
                        error = await node.compile(f"call leds.top(32,0,32)")
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