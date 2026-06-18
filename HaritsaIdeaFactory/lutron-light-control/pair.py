import asyncio
import os
from pathlib import Path

from dotenv import load_dotenv
from pylutron_caseta.pairing import async_pair

load_dotenv(Path(__file__).parent / ".env")

BRIDGE_HOST = os.environ["LUTRON_BRIDGE_HOST"]
CERTS_DIR = Path(__file__).parent / "certs"


async def main():
    CERTS_DIR.mkdir(exist_ok=True)

    print(f"Pairing with Lutron bridge at {BRIDGE_HOST}...")
    print()
    print(">>> Press the small button on the back of your Lutron bridge NOW <<<")
    print()

    data = await async_pair(BRIDGE_HOST)

    ca_path = CERTS_DIR / "caseta-bridge.crt"
    cert_path = CERTS_DIR / "caseta.crt"
    key_path = CERTS_DIR / "caseta.key"

    ca_path.write_text(data["ca"])
    cert_path.write_text(data["cert"])
    key_path.write_text(data["key"])

    print("Pairing successful! Certificates saved to ./certs/")
    print(f"  CA:   {ca_path}")
    print(f"  Cert: {cert_path}")
    print(f"  Key:  {key_path}")


if __name__ == "__main__":
    asyncio.run(main())
