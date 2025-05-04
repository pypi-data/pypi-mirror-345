# UnitMCP Example: Raspberry Pi Control

## Purpose

This example demonstrates how to control Raspberry Pi hardware using the UnitMCP library. It showcases:

- Connecting to a Raspberry Pi running the UnitMCP server
- Controlling GPIO devices like LEDs, buttons, and traffic lights
- Real-time GPIO streaming from Raspberry Pi to client PC
- Loading configuration from YAML files
- Running automated hardware demos
- Implementing proper error handling and resource management

This example serves as a reference implementation for building Raspberry Pi-based hardware control applications with UnitMCP.

## Requirements

- Python 3.7+
- UnitMCP library (installed or in PYTHONPATH)
- Raspberry Pi with GPIO pins (or simulation mode)
- PyYAML (`pip install pyyaml`)
- Hardware components (optional):
  - LEDs
  - Push buttons
  - Resistors (220Ω for LEDs, 10kΩ for buttons)
  - Jumper wires

## Environment Variables

This example uses the following environment variables which can be configured in a `.env` file:

| Variable | Description | Default Value |
|----------|-------------|---------------|
| `RPI_HOST` | Hostname or IP address of the Raspberry Pi | `localhost` |
| `RPI_PORT` | Port number for the MCP server | `8080` |
| `LED_PIN` | GPIO pin number for the LED | `17` |
| `BUTTON_PIN` | GPIO pin number for the button | `27` |
| `RED_PIN` | GPIO pin for red traffic light | `17` |
| `YELLOW_PIN` | GPIO pin for yellow traffic light | `27` |
| `GREEN_PIN` | GPIO pin for green traffic light | `22` |
| `FAST_BLINK` | Duration for fast blinking in seconds | `0.1` |
| `SLOW_BLINK` | Duration for slow blinking in seconds | `0.5` |
| `SIMULATION_MODE` | Run in simulation mode without hardware | `false` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `STREAM_UPDATES` | Enable real-time GPIO state streaming | `true` |
| `UPDATE_INTERVAL` | Interval for GPIO state updates in ms | `100` |

## How to Run

```bash
# Run the hardware client with LED demo
python hardware_client.py --demo led

# Run the hardware client with button demo
python hardware_client.py --demo button

# Run the hardware client with traffic light demo
python hardware_client.py --demo traffic_light

# Run with custom host and port
python hardware_client.py --host 192.168.1.100 --port 8888

# Run the configuration automation example
python config_automation_example.py --config my_custom_config.yaml

# Run all examples in sequence
./run_examples.sh
```

## GPIO Streaming Setup

The UnitMCP library supports real-time streaming of GPIO pin states from a Raspberry Pi to a client PC. This allows you to monitor and respond to GPIO changes remotely.

### Server Setup (Raspberry Pi)

To set up the server on your Raspberry Pi:

```bash
# Start the server with GPIO streaming enabled
python server.py --stream-gpio --port 8080
```

### Client Setup (PC)

To connect to the Raspberry Pi and receive GPIO updates:

```bash
# Connect to the Raspberry Pi server and monitor GPIO changes
python client.py --host 192.168.1.100 --port 8080 --monitor-gpio
```

### GPIO Example

The `gpio_example.py` script demonstrates how to use the GPIO streaming functionality:

```bash
# Run the GPIO example with streaming enabled
python gpio_example.py --host 192.168.1.100 --port 8080 --stream
```

This will:
1. Connect to the Raspberry Pi server
2. Set up GPIO pins as specified
3. Establish a WebSocket connection for real-time updates
4. Display GPIO state changes as they occur
5. Allow you to send commands to control GPIO pins

## Example Output

### LED Demo

```
UnitMCP Raspberry Pi Hardware Client Example
===========================================
Running led demo...
2025-05-03 09:46:17,123 - RPiHardwareClient - INFO - Connecting to MCP server at localhost:8080
2025-05-03 09:46:17,234 - RPiHardwareClient - INFO - Connected to MCP server successfully
2025-05-03 09:46:17,345 - RPiHardwareClient - INFO - Running led demo
2025-05-03 09:46:17,456 - RPiHardwareClient - INFO - Setting up LED demo_led on pin 17
2025-05-03 09:46:17,567 - RPiHardwareClient - INFO - LED demo_led setup successful
2025-05-03 09:46:17,678 - RPiHardwareClient - INFO - Turning LED on
2025-05-03 09:46:17,789 - RPiHardwareClient - INFO - LED demo_led control successful
2025-05-03 09:46:18,901 - RPiHardwareClient - INFO - Blinking LED fast
2025-05-03 09:46:19,012 - RPiHardwareClient - INFO - LED demo_led control successful
2025-05-03 09:46:21,123 - RPiHardwareClient - INFO - Blinking LED slow
2025-05-03 09:46:21,234 - RPiHardwareClient - INFO - LED demo_led control successful
2025-05-03 09:46:24,345 - RPiHardwareClient - INFO - Turning LED off
2025-05-03 09:46:24,456 - RPiHardwareClient - INFO - LED demo_led control successful
Demo completed successfully: LED demo completed successfully
Disconnected from MCP server
```

### GPIO Streaming Example

```
UnitMCP GPIO Streaming Example
============================
Connecting to Raspberry Pi at 192.168.1.100:8080
Connected successfully
Setting up GPIO streaming...
Streaming connection established
Monitoring GPIO pins: [17, 27, 22]

[2025-05-03 13:30:45] GPIO Update: Pin 17 changed to HIGH
[2025-05-03 13:30:46] GPIO Update: Pin 17 changed to LOW
[2025-05-03 13:30:47] GPIO Update: Pin 27 changed to HIGH (Button pressed)
[2025-05-03 13:30:48] GPIO Update: Pin 27 changed to LOW (Button released)
[2025-05-03 13:30:49] GPIO Update: Pin 22 changed to HIGH

Sending command: Set pin 17 to HIGH
Command executed successfully
[2025-05-03 13:30:51] GPIO Update: Pin 17 changed to HIGH

Streaming session ended
Disconnected from server
```

### Configuration Automation

```
UnitMCP Configuration Automation Example
=======================================
Loading configuration from my_custom_config.yaml
Configuration loaded successfully
Connecting to MCP server at localhost:8080
Connected to MCP server
Setting up devices from configuration...
Setting up LED main_led on pin 17
Setting up button user_button on pin 27
Setting up traffic light traffic1 with pins 17, 27, 22
All devices set up successfully
Running automation sequence...
Step 1: Turn on main_led - Success
Step 2: Wait for button press - Waiting...
Button pressed! Continuing...
Step 3: Traffic light cycle - Success
Automation completed successfully
Disconnected from MCP server
```

## How GPIO Streaming Works

The GPIO streaming functionality works as follows:

1. **Server-side monitoring**: The server continuously monitors the state of GPIO pins on the Raspberry Pi
2. **WebSocket connection**: A WebSocket connection is established between the server and client
3. **Real-time updates**: When a GPIO pin state changes, the server sends an update to all connected clients
4. **Event-driven architecture**: Clients can register callbacks to be notified of specific GPIO changes
5. **Bidirectional communication**: Clients can also send commands to control GPIO pins

This approach provides several benefits:
- **Low latency**: Updates are sent immediately when changes occur
- **Reduced bandwidth**: Only state changes are transmitted, not continuous polling
- **Multiple clients**: Multiple clients can monitor the same GPIO pins
- **Scalability**: The system can handle many GPIO pins without performance degradation

## Additional Notes

- The `hardware_client.py` file provides a reusable client class for controlling Raspberry Pi hardware
- The `run_examples.sh` script shows how to run multiple examples in sequence
- All examples include proper error handling and resource cleanup
- The code is designed to be easily extended with additional hardware devices and control patterns
- The streaming functionality can be used for remote monitoring, automation, and IoT applications
