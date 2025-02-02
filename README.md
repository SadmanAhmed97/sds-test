<h1>Guidelines to run the project</h1>

<p>Install the virtual environment first</p>
<p>Execute the command</p>
<code>pip install -r requirements.txt</code>

<h3>Folder: Hotel Comparison</h3>
<p>This is where both the scrapers are written. Each scraper has to be run individually. To run the scripts, first ensure you are in the same level as the scrapy.cfg file, then execute the following commands</p>

<h5>Booking.com</h5>
<code>scrapy crawl booking</code>

<h5>Agoda</h5>
<code>scrapy crawl agoda</code>

<h3>Folder: Backend</h3>
<p>This is a simple backend service built with FastApi. To run the service, execute the following command</p>
<code>uvicorn main:app --reload</code>
<br>
<br>
<p>Server running at: http://127.0.0.1:8000/docs</p>
