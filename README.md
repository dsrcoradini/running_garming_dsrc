This project is a data analysis test. It consists of three main components: the API, the CSV converter, and the analyser.

**API – api_call_fit_file**  
Located in the project1 root folder.  
This script retrieves FIT data from Garmin and downloads it to your computer or repository.  
You must provide your email and password, but credentials are not stored.  
The API supports downloading up to 1000 activities. A potential improvement would be to define a date window for more precise filtering.

**CSV Converter – convert_fit_to_csv**  
Located in the fit_file folder.  
This script converts FIT files to CSV format. The current version focuses on a few metrics (time, heart rate, distance).  
Depending on your watch or gadgets, you can modify the code to extract additional metrics if needed.

**Analyser – analyser.py**  
Currently, the analyser groups runs into specific categories.  
Future work will explore more innovative approaches for deeper data analysis.
