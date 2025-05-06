import stores  # noqa

index = stores.Index(
    ["silanthro/python-sandbox"],
    # env_var={
    #     "silanthro/python-sandbox": {
    #         "DENO_PATH": "/drive3/Silanthro/tools/python-sandbox/deno"
    #     }
    # },
)
print(index.tools)

# for value in index.stream_execute("sandbox.run_code", {"code": "1+1"}):
#     print(value)

print(
    index.execute(
        "sandbox.run_code",
        kwargs={
            "timeout": 5,
            "code": "def is_prime(n):\n    if n <= 1:\n        return False\n    for i in range(2, int(n**0.5) + 1):\n        if n % i == 0:\n            return False\n    return True\n\nprimes = []\nnum = 2\nwhile len(primes) < 10:\n    if is_prime(num):\n        primes.append(num)\n    num += 1\n\nsum(primes)",
        },
    )
)
