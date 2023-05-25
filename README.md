# Project: ARES and ČSU Data Enrichment with Redis Caching

Welcome to the Fun Project! This project aims to enhance the accessibility and usability of ARES (Administrative Register of Economic Subjects) and ČSU (Czech Statistical Office) data. It uses Redis for caching to improve the speed and efficiency of data retrieval. By leveraging this project, you can retrieve and analyze data from ARES and ČSU in a more convenient and user-friendly manner than using their official APIs.

## Installation

To get started with the Fun Project, follow these steps:

1. Clone the repository:

```bash
git clone https://github.com/your-username/fun-project.git
cd fun-project
```
2. Install the required dependencies:

```bash
pip install -r requirements.txt

```
3. Install and configure Redis:

```bash
# For Ubuntu
sudo apt-get install redis-server

# For MacOS
brew install redis

# Start Redis server
redis-server

```
The project uses a Redis server running on localhost with the default port 6379. If your Redis server runs on a different host or port, you can specify the REDIS_HOST_NAME environment variable.

4. Run the application:
```bash
export REDIS_HOST_NAME=your_redis_host
```

## Features

- Retrieve company information from ARES based on the company's identification number (IČO).
- Fetch and analyze statistical data from ČSU to gain insights into various economic indicators.
- Enrich ARES data with additional information from ČSU to provide a more comprehensive view of companies.
- Utilize Redis caching to reduce response time and load on external APIs.


## Usage

1. Open the Fun Project in your web browser.
2. Enter the company's identification number (IČO) to retrieve ARES data.
3. Explore the different endpoints to fetch and analyze ČSU statistical data.
4. Enjoy the enhanced experience of accessing and visualizing data from ARES and ČSU!

## License

[MIT](https://choosealicense.com/licenses/mit/)