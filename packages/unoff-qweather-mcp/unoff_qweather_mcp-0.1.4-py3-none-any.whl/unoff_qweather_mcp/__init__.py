from .qweather import mcp

__all__ = ["qweather"]

def main():
    mcp.run()

if __name__ == "__main__":
    main()