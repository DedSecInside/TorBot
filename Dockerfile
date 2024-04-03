# Use an official Python 3.11.4 image as the base
FROM python:3.11.4

# Set a working directory within the container
WORKDIR /app

# Clone the TorBot repository from GitHub
RUN git clone https://github.com/DedSecInside/TorBot.git /app

# Install dependencies
RUN pip install -r /app/requirements.txt

# Set the SOCKS5_PORT environment variable
ENV SOCKS5_PORT=9050

# Expose the port specified in the .env file
EXPOSE $SOCKS5_PORT

# Run the TorBot script
CMD ["poetry", "run", "python", "torbot"]
# Example way to run the container:
# docker run --network="host" your-image-name poetry run python torbot -u https://www.example.com --depth 2 --visualize tree --save json
