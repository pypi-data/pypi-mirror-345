#!/usr/bin/env python3
"""
Direct test client for Force-Fusion dashboard.

This script connects directly to the WebSocket server and sends test data
to diagnose connection issues.
"""

import asyncio
import json
import logging
import random
import sys
from datetime import datetime

import websockets

# Import config for constants like SPEED_MAX
from force_fusion import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


async def send_test_data(uri="ws://localhost:8765"):
    """
    Connect to WebSocket server and send test data.

    Args:
        uri: WebSocket server URI
    """
    while True:  # Outer loop for reconnection
        try:
            logger.info(f"Connecting to {uri}...")

            async with websockets.connect(
                uri, ping_interval=20, ping_timeout=30
            ) as websocket:
                logger.info("Connected to server")

                # Send test messages continuously with 0.2 second delay between them
                i = 0
                while True:  # Loop indefinitely
                    # Create simple test data
                    data = {
                        "timestamp": datetime.now().isoformat(),
                        "sim_id": i,
                        "latitude": 29.18825368942673 + (i * 0.0001) % 0.01,
                        "longitude": -81.04897348153887 - (i * 0.0001) % 0.01,
                        "speed": (i * 5.0) % config.SPEED_MAX,
                        "heading": (i * 30.0) % 360,
                        "acceleration_x": random.uniform(-1, 1),
                        "acceleration_y": random.uniform(-1, 1),
                        "acceleration_z": random.uniform(-1, 1),
                        "pitch": random.uniform(-5, 5),
                        "roll": random.uniform(-5, 5),
                        "tire_forces": {
                            "FL": 2000 + random.uniform(-200, 200),
                            "FR": 2000 + random.uniform(-200, 200),
                            "RL": 2000 + random.uniform(-200, 200),
                            "RR": 2000 + random.uniform(-200, 200),
                        },
                    }

                    # Convert to JSON string
                    message = json.dumps(data)

                    # Control logging verbosity with DEBUG_MODE
                    if (
                        config.DEBUG_MODE or i % 10 == 0
                    ):  # Log every 10th message if not in debug mode
                        # Log only a preview to avoid excessive logging
                        log_preview = message[:50] + (
                            "..." if len(message) > 50 else ""
                        )
                        logger.info(f"Sending test message {i}: {log_preview}")

                    # Send message
                    await websocket.send(message)

                    # Wait a shorter time before sending the next message (5Hz by default)
                    await asyncio.sleep(0.2)

                    i += 1  # Increment counter

        except websockets.exceptions.ConnectionClosed as e:
            logger.error(f"Connection closed: {e}")
            logger.info("Reconnecting in 1 seconds...")
            await asyncio.sleep(1)
        except Exception as e:
            logger.error(f"Error: {e}")
            logger.info("Reconnecting in 1 seconds...")
            await asyncio.sleep(1)


async def main():
    """Main entry point."""
    # Use command line arg as URI if provided
    uri = sys.argv[1] if len(sys.argv) > 1 else "ws://localhost:8765"

    # Run the test client
    await send_test_data(uri)


if __name__ == "__main__":
    asyncio.run(main())
