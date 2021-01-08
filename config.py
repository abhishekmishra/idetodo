from lupa import LuaRuntime

_CONFIG_FILE = "idetodo.cfg"


def read_config():
    lua = LuaRuntime(unpack_returned_tuples=True)
    # print(lua.execute('''
    #     x = 10
    #     print(x)
    #     return x
    # '''))

    cfg = None

    with open(_CONFIG_FILE, 'r') as f:
        cfg_text = f.read()
        cfg = lua.execute(cfg_text)
        print(cfg.items())
        print(cfg["theme"])
    return cfg
