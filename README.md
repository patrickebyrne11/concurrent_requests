# Python CLI Program with Docker, Proxies, and Concurrency

This project is a Python CLI tool that performs asynchronous API requests using Docker, proxies, and concurrency. It allows for rate-limited concurrent requests, retries in case of failure, and proxy rotation. 

---

## Project Setup

Before running the program, ensure that you have all the necessary tools and dependencies installed, including **Python**, **Docker**, and the required Python libraries.

### Prerequisites

- Python 3.x
- Docker

### Install Python Dependencies

Make sure you have Python 3.x installed on your system, then use `pip` to install the required libraries:
```bash
pip install asyncio aiofiles argparse
```
# Input and Proxy Files

The program requires two input files:

1. Input Data (input.txt): Contains the data to send as API requests.
2. Proxy List (addresses.txt): Contains the list of proxy addresses to use for requests.

## Input Data (input.txt)
Each line of the file contains an input that will be passed to the API.
Example (input.txt):

txt
```
data1
data2
data3
```
## Proxy List (addresses.txt)
Each line of this file contains a proxy address that will be rotated through for each API request.

Example (addresses.txt):

txt
```
http://proxy1:port
http://proxy2:port
http://proxy3:port
```
# Building Docker Image
To run the CLI program, ensure that your Docker container is set up and running.

## Step 1: Build the Docker Image
First, build the Docker image using your Dockerfile:

bash
```
docker build -t your_image_name .
```
## Step 2: Run the Docker Container
Start a container from the image:

bash
```
docker run -d --name your_container_name your_image_name
```
Make sure to update the script with the correct container ID if it's different.

# Running the Program
Once Docker is set up and running, you can execute the CLI program using the following command:

bash
```
python your_script.py --input_file input.txt --proxies_file addresses.txt --output_file output.txt
```
## Command Arguments
* --input_file: Path to the input.txt file that contains the API input data.
* --proxies_file: Path to the addresses.txt file that contains the proxy addresses.
* --output_file: Path to the output.txt file where successful API responses will be written.

## Example Command
bash
```
python cli_program.py --input_file input.txt --proxies_file addresses.txt --output_file output.txt
```
This command will run the API requests asynchronously, use proxies, and save the output to output.txt.

# Testing the Program
You can test the program in two ways:

## Unit Testing
Add unit tests for individual functions, such as exec_docker_command, to test different scenarios like HTTP status codes (200, 503, etc.).

## Manual Testing
You can manually run the program with a small set of inputs and proxies to verify:
* API requests are executed concurrently.
* Proxy rotation is working.
* Successful results are written to the output.txt file.
# Debugging and Logs
If an error occurs during execution, it will be logged in the console. Possible errors include:
* Proxy failures
* HTTP status code checks (200 for success, 503 for retry)
## Adjusting Retry Settings
You can adjust the retry behavior by modifying the max_retries and retry_delay parameters in the script.

# Cleanup
Once testing is complete, stop and remove the Docker container to free up resources:

bash
```
docker stop your_container_name
docker rm your_container_name
```
# Conclusion
This Python CLI program leverages Docker, proxies, and asynchronous programming to efficiently handle multiple API requests. By following the instructions, you can build, test, and run the program in your own environment.



