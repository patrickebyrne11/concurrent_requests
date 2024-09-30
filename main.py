import subprocess
import asyncio
from asyncio import Semaphore
import random
import aiofiles  # for asynchronous file handling
import argparse  # for CLI arguments

# Limit the number of concurrent requests to 30
semaphore = Semaphore(30)

# Hardcoded container ID
CONTAINER_ID = "d6ff4d76942c85d145e406f4ce5fd07bdf210d431e8b2ff17156a87f772d780e"

# Asynchronously execute the Docker command using proxies
async def exec_docker_command(api_input, proxies, output_file, max_retries=5, retry_delay=5):
    async with semaphore:  # Ensure only 30 requests are running at the same time
        retries = 0
        proxy_index = 0

        while retries < max_retries:
            # Rotate through the list of proxies
            proxy = proxies[proxy_index % len(proxies)]
            command = f"docker exec {CONTAINER_ID} curl -x {proxy} 'http://localhost:3000/api/data?input={api_input}'"
            
            try:
                # Run the curl command asynchronously using asyncio's subprocess
                process = await asyncio.create_subprocess_shell(
                    command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
                )
                stdout, stderr = await process.communicate()

                if process.returncode == 0:
                    # Successful response, check status code through the same proxy
                    status_check_command = (
                        f"docker exec {CONTAINER_ID} curl -x {proxy} -s -o /dev/null -w '%{{http_code}}' "
                        f"'http://localhost:3000/api/data?input={api_input}'"
                    )
                    status_process = await asyncio.create_subprocess_shell(
                        status_check_command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
                    )
                    status_code, _ = await status_process.communicate()
                    status_code = status_code.decode().strip()

                    if status_code == "200":
                        print(f"Command Output for {api_input} using proxy {proxy}:")
                        print(stdout.decode())

                        # Write the successful request to output.txt asynchronously
                        async with aiofiles.open(output_file, 'a') as f:
                            await f.write(f"{api_input} {stdout.decode()}\n")

                        return stdout.decode()

                    elif status_code == "503":
                        # Service Unavailable, retry with another proxy
                        print(f"Service Unavailable (503) for {api_input} using proxy {proxy}. Retrying...")
                        retries += 1
                        await asyncio.sleep(retry_delay)  # Wait before retrying
                        proxy_index += 1  # Try the next proxy

                    else:
                        # For other status codes, terminate with exception
                        raise Exception(f"Request failed for {api_input} with status code: {status_code}")

                else:
                    # Handle proxy failure (non-zero return code from curl)
                    print(f"Proxy {proxy} failed for {api_input}, retrying with next proxy...")
                    retries += 1
                    await asyncio.sleep(retry_delay)
                    proxy_index += 1  # Move to the next proxy

            except Exception as e:
                # Log any exceptions and move to the next proxy
                print(f"Error with proxy {proxy}: {e}")
                retries += 1
                await asyncio.sleep(retry_delay)
                proxy_index += 1  # Rotate to the next proxy

        # If all retries are exhausted, raise an exception
        raise Exception(f"Max retries reached for {api_input}. Request could not be completed.")

# Function to read inputs and proxies, and execute API calls concurrently
async def run_concurrent_requests(input_file, proxies_file, output_file):
    # Read inputs from input.txt
    with open(input_file, 'r') as f:
        inputs = [line.strip() for line in f.readlines()]

    # Read proxies from proxies.txt
    with open(proxies_file, 'r') as f:
        proxies = [line.strip() for line in f.readlines()]

    # Create a list of asynchronous tasks for concurrent execution
    tasks = []
    for api_input in inputs:
        tasks.append(exec_docker_command(api_input, proxies, output_file))
    
    # Run tasks concurrently with rate limiting using asyncio.gather
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    # Create an argument parser
    parser = argparse.ArgumentParser(description="API request automation with Docker, proxies, and concurrency")

    # Add arguments for input.txt, addresses.txt, and output.txt
    parser.add_argument(
        '--input_file', 
        required=True, 
        help="Path to the input.txt file with API input data"
    )
    parser.add_argument(
        '--proxies_file', 
        required=True, 
        help="Path to the addresses.txt file with proxy addresses"
    )
    parser.add_argument(
        '--output_file', 
        required=True, 
        help="Path to the output.txt file where successful results will be written"
    )

    # Parse the arguments
    args = parser.parse_args()

    try:
        # Run the concurrent requests using asyncio with rate limiting and proxy rotation
        asyncio.run(run_concurrent_requests(args.input_file, args.proxies_file, args.output_file))
    except Exception as e:
        print(f"An error occurred: {e}")
