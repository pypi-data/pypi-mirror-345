import asyncio

import stores


def func():
    yield "Hello"
    yield 51
    yield "Good Bye"


async def func_d():
    for i in range(3):
        await asyncio.sleep(0.5)
        yield f"sleep {i}"


index = stores.Index(
    ["silanthro/todoist"], include={"silanthro/todoist": ["todoist.func"]}
)

print(index.tools)
quit()


# for i in index.tools[1]():
#     print(i)

print(index.execute("todoist.func_d"))


for i in index.stream_execute("todoist.func_d"):
    print(i)
