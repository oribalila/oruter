from pathlib import Path

from router import Router


if __name__ == "__main__":
    directory = Path(__file__).resolve().parent
    router = Router(directory / "routing_table.txt")
    router.capture_packet()
