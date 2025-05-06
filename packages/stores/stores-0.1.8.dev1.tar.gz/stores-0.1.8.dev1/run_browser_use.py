import stores  # noqa


index = stores.indexes.LocalIndex(
    "/drive3/Silanthro/tools/basic-browser-use",
    create_venv=True,
    include=["basic_browser_use.stream_browser_agent_gui"],
)


async def collect():
    async for value in index.astream_execute(
        "basic_browser_use.stream_browser_agent_gui",
        {"task": "What are the latest OpenAI models?"},
    ):
        print(value)


# async def collect():
#     async for value in run_remote_tool(
#         "basic_browser_use.test",
#         "/drive3/Silanthro/tools/basic-browser-use",
#         stream=True,
#     ):
#         print(value)


# asyncio.run(collect())

for value in index.stream_execute(
    "basic_browser_use.stream_browser_agent_gui",
    {"task": "What are the latest OpenAI models?"},
):
    print(value)
