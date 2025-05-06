"""
WebSocket server for testing Force-Fusion dashboard with real-time data.

This module provides a simple WebSocket server that processes data
from connected clients and broadcasts it to all other clients.
"""

import argparse
import asyncio
import json
import logging
import os
import random
import sys
from datetime import datetime

import websockets

from force_fusion import config

# Test mode flag
TEST_MODE = False
TEST_INTERVAL = 0.1  # seconds (10Hz)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("/tmp/force_fusion_websocket.log"),
    ],
)
logger = logging.getLogger(__name__)

# Message log file for debugging
MESSAGE_LOG = os.path.expanduser("/tmp/force_fusion_messages.log")

# Connected clients set
connected_clients = set()


def log_message_to_file(message, client_addr=None):
    """Log a message to a file for debugging."""
    try:
        with open(MESSAGE_LOG, "a") as f:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
            client_info = f" from {client_addr}" if client_addr else ""
            f.write(f"[{timestamp}] Message{client_info}: {message[:100]}\n")
    except Exception as e:
        logger.error(f"Error writing to message log: {e}")


async def register_client(websocket):
    """Register a new client connection."""
    connected_clients.add(websocket)
    client_addr = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"
    logger.info(
        f"CLIENT CONNECTED: {client_addr}. Total clients: {len(connected_clients)}"
    )
    print(f"NEW CLIENT CONNECTED: {client_addr}")

    # Send immediate welcome message
    try:
        # Create a welcome message
        welcome_data = {
            "welcome": True,
            "timestamp": datetime.now().isoformat(),
            "message": "Welcome to Force-Fusion WebSocket Server",
            "clients_connected": len(connected_clients),
        }

        # Send it
        await websocket.send(json.dumps(welcome_data))
        logger.info(f"Sent welcome message to {client_addr}")

    except Exception as e:
        logger.error(f"Error sending welcome message: {e}")

    # If this is our first client and test mode is active, restart the generator
    if len(connected_clients) == 1 and TEST_MODE:
        logger.info(
            "First client connected while in test mode, ensuring generator is running"
        )
        asyncio.create_task(test_data_generator())


async def unregister_client(websocket):
    """Unregister a client that has disconnected."""
    if websocket in connected_clients:
        connected_clients.remove(websocket)
        client_addr = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"
        logger.info(
            f"Client disconnected from {client_addr}. Total clients: {len(connected_clients)}"
        )
    else:
        logger.warning("Attempted to unregister client that was not registered")


async def forward_message(sender, message):
    """Forward a message from one client to all other clients."""
    if len(connected_clients) < 1:
        # No clients to forward to
        logger.warning("No clients connected, cannot forward message!")
        return 0

    forwarded = 0
    clients_to_remove = set()

    # Print client addresses for debugging
    clients_str = ", ".join(
        [f"{c.remote_address[0]}:{c.remote_address[1]}" for c in connected_clients]
    )
    logger.info(f"Connected clients: {clients_str}")

    # Forward to ALL clients - including the GUI client
    sender_addr = (
        f"{sender.remote_address[0]}:{sender.remote_address[1]}"
        if sender
        else "BROADCAST"
    )
    for client in connected_clients:
        client_addr = f"{client.remote_address[0]}:{client.remote_address[1]}"
        try:
            logger.info(f"Forwarding message from {sender_addr} to {client_addr}")
            await client.send(message)
            log_message_to_file(message, f"forwarded {sender_addr} -> {client_addr}")
            forwarded += 1
        except websockets.exceptions.ConnectionClosed:
            logger.warning(f"Client {client_addr} connection closed during forwarding")
            clients_to_remove.add(client)
        except Exception as e:
            logger.error(f"Error forwarding to {client_addr}: {e}")
            clients_to_remove.add(client)

    # Remove closed connections
    for client in clients_to_remove:
        await unregister_client(client)

    return forwarded


async def handler(websocket):
    """Handle a WebSocket connection."""
    client_addr = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"
    logger.info(f"New connection from {client_addr}")
    print(f"### New WebSocket client connected from {client_addr} ###")
    await register_client(websocket)
    try:
        # Keep connection open, handling incoming messages
        async for message in websocket:
            # Process message
            try:
                # Log only a preview of the message to avoid log spam
                preview = message[:50] + "..." if len(message) > 50 else message
                logger.info(f"Message from {client_addr}: {preview}")
                print(f"### Received message from {client_addr} ###")
                log_message_to_file(message, client_addr)

                # Parse as JSON to validate it's a valid message
                json.loads(message)

                # Forward the message to all other clients
                forwarded = await forward_message(websocket, message)
                if forwarded > 0:
                    logger.info(f"Forwarded message to {forwarded} other clients")
                    print(f"### Forwarded message to {forwarded} other clients ###")
                else:
                    print(
                        "### No clients to forward message to - GUI may not be connected ###"
                    )

            except json.JSONDecodeError:
                logger.warning(f"Invalid JSON from {client_addr}: {message[:100]}")
            except Exception as e:
                logger.error(f"Error processing message: {e}")
    except websockets.exceptions.ConnectionClosedError as e:
        logger.info(f"Connection closed with error: {e}")
    except websockets.exceptions.ConnectionClosedOK:
        logger.info(f"Connection closed normally by client: {websocket.remote_address}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        await unregister_client(websocket)


def is_port_in_use(port, host="localhost"):
    """Check if a port is already in use."""
    import socket

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(1)
        return s.connect_ex((host, port)) == 0


def kill_existing_server(port, host="localhost"):
    """Attempt to kill any existing WebSocket server on the given port."""
    import platform
    import subprocess
    import time

    if not is_port_in_use(port, host):
        return False  # No server running

    logger.info(
        f"Detected existing server on port {port}, attempting to shut it down..."
    )

    # Different commands based on OS
    if platform.system() == "Windows":
        try:
            # On Windows, find the PID using the port and kill it
            subprocess.run(
                f"FOR /F \"tokens=5\" %a in ('netstat -aon ^| findstr :{port}') do taskkill /F /PID %a",
                shell=True,
            )
            time.sleep(1)
            return not is_port_in_use(port, host)
        except Exception as e:
            logger.error(f"Failed to kill existing server: {e}")
            return False
    else:
        try:
            # On Unix/Linux, use fuser to find and kill the process
            subprocess.run(["fuser", "-k", f"{port}/tcp"], check=False)
            time.sleep(1)
            return not is_port_in_use(port, host)
        except Exception as e:
            logger.error(f"Failed to kill existing server: {e}")
            return False


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="WebSocket server for Force-Fusion dashboard"
    )
    parser.add_argument(
        "--host",
        type=str,
        default=config.WS_HOST,
        help=f"Host to bind the WebSocket server to (default: {config.WS_HOST})",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=config.WS_PORT,
        help=f"Port to bind the WebSocket server to (default: {config.WS_PORT})",
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help=f"Enable test mode (broadcasts test data at {1 / TEST_INTERVAL}Hz)",
    )
    return parser.parse_args()


async def main(host, port, test_mode=False):
    """
    Start the WebSocket server.

    Args:
        host: Host to bind the server to
        port: Port to bind the server to
        test_mode: Whether to broadcast test data
    """
    # Set test mode flag
    global TEST_MODE
    TEST_MODE = test_mode

    if TEST_MODE:
        print("TEST MODE ACTIVE - Will broadcast test data at 10Hz")
        logger.info("Test mode enabled")

    # Check if port is already in use and try to kill existing server
    if is_port_in_use(port, host):
        killed = kill_existing_server(port, host)
        if killed:
            logger.info(f"Successfully shut down existing server on port {port}")
        else:
            logger.warning(
                f"Port {port} is still in use. Server might not start correctly."
            )
            print(
                f"Port {port} is already in use and could not be freed automatically."
            )
            print("Please manually stop any existing WebSocket server first.")

    # Create the WebSocket server
    try:
        server = await websockets.serve(handler, host, port)

        logger.info(f"WebSocket server started at ws://{host}:{port}")
        print(f"WebSocket server started at ws://{host}:{port}")

        # Start test data generator if test mode is enabled
        if TEST_MODE:
            print(
                f"Starting test data generator! Broadcasting at {1 / TEST_INTERVAL}Hz"
            )
            # Create and start the test data generator task
            asyncio.create_task(test_data_generator())
            print("Test data generator started successfully")

        # Wait for server to complete (never will unless interrupted)
        await server.wait_closed()
    except OSError as e:
        if e.errno == 98:  # Address already in use
            logger.error(f"Port {port} is already in use. Please use a different port.")
            print(
                f"Error: Port {port} is already in use. Please use a different port or stop the existing server."
            )
            return
        raise


def handle_signal(sig, frame):
    """Handle interrupt signals."""
    logger.info("Shutting down WebSocket server...")
    sys.exit(0)


async def test_data_generator():
    """Generate and broadcast test data periodically."""
    if not TEST_MODE:
        logger.info("Test mode not enabled, not starting test data generator")
        return

    logger.info("Starting test data generator...")
    print("Broadcasting test data every 0.1 seconds (10Hz).")

    # First message is always logged
    print("Sending first test data packet immediately!")

    counter = 0
    while True:
        try:
            # Generate test data similar to the client test script
            data = {
                "timestamp": datetime.now().isoformat(),
                "sim_id": counter,
                "latitude": 29.18825368942673 + (counter * 0.0001) % 0.01,
                "longitude": -81.04897348153887 - (counter * 0.0001) % 0.01,
                "speed": (counter * 5.0) % config.SPEED_MAX,
                "heading": (counter * 30.0) % 360,
                "acceleration_x": random.uniform(-2, 2),
                "acceleration_y": random.uniform(-1, 1),
                "pitch": random.uniform(-5, 5),
                "roll": random.uniform(-5, 5),
                "tire_forces": {
                    "FL": 2000 + random.uniform(-200, 200),
                    "FR": 2000 + random.uniform(-200, 200),
                    "RL": 2000 + random.uniform(-200, 200),
                    "RR": 2000 + random.uniform(-200, 200),
                },
            }

            # Convert to JSON
            message = json.dumps(data)

            # Always log the first 5 messages, then every 10th
            if counter < 5 or counter % 10 == 0:
                logger.info(f"Broadcasting test message {counter}")
                if counter < 5:
                    print(f"Test message {counter}: {message[:50]}...")

            # Broadcast to all clients - returns how many clients received it
            clients_reached = await forward_message(None, message)

            # Log client count periodically
            if counter < 5 or counter % 50 == 0:
                print(f"Message {counter} sent to {clients_reached} clients")

            # Increment counter
            counter += 1

            # Wait for next interval
            await asyncio.sleep(TEST_INTERVAL)

        except Exception as e:
            logger.error(f"Error in test data generator: {e}")
            print(f"Error generating test data: {e}")
            await asyncio.sleep(1)  # Wait a bit longer on error


if __name__ == "__main__":
    # Parse command-line arguments
    args = parse_args()

    # Register signal handlers for graceful shutdown
    import signal

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    # Start the asyncio event loop
    try:
        asyncio.run(main(args.host, args.port, args.test))
    except KeyboardInterrupt:
        logger.info("Server interrupted by user")
