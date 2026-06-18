import asyncio
import json
import os
from pathlib import Path

from dotenv import load_dotenv
from pylutron_caseta.smartbridge import Smartbridge

load_dotenv(Path(__file__).parent / ".env")

BRIDGE_HOST = os.environ["LUTRON_BRIDGE_HOST"]
CERTS_DIR = Path(__file__).parent / "certs"


async def main():
    bridge = Smartbridge.create_tls(
        BRIDGE_HOST,
        str(CERTS_DIR / "caseta.key"),
        str(CERTS_DIR / "caseta.crt"),
        str(CERTS_DIR / "caseta-bridge.crt"),
    )
    await bridge.connect()

    devices = bridge.get_devices()
    print(json.dumps(devices, indent=2))

    await bridge.close()


if __name__ == "__main__":
    asyncio.run(main())
