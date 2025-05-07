from mcp.server.fastmcp import FastMCP

mcp = FastMCP("pokemon")

@mcp.tool()
def get_pokemon_info(name: str) -> str:

    if name == "皮卡丘":
        return "名字：皮卡丘 别名：黄皮耗子 攻击方式：尾巴放电1"
    if name == "杰尼龟":
        return "名字：杰尼龟 别名：海龟宝可梦 攻击方式：壳体保护2"
    if name == "妙蛙种子":
        return "名字：妙蛙种子 别名：种子宝可梦 攻击方式：妙蛙花3"

    return "信息不存在"
def main() -> None:
    print("Hello from mcp-wxdemo1-server!")
    print(get_pokemon_info("皮卡丘"))
    mcp.run(transport='stdio')


