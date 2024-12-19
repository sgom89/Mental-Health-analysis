Mental Health Data Analysis Web Application
This web application is designed to analyze and visualize mental health data. It provides an interactive interface for exploring a dataset, performing statistical analysis, and examining correlations between various factors related to mental health.


Features
Data Preview: View a sample of the dataset along with column information and basic statistics.
Data Analysis: Perform statistical analysis on selected columns, including histograms for both categorical and numerical data.
Correlation Analysis: Explore relationships between different categories in the dataset with interactive visualizations.
Visualizations: Utilizes Plotly to create interactive bar charts, pie charts, and heatmaps.
Technical Stack
Backend: Python with Flask framework
Data Processing: Pandas for data manipulation and analysis
Visualization: Matplotlib, Seaborn, and Plotly
Frontend: HTML templates with JavaScript for dynamic content


Usage
Run the application:
text
python app.py

Open a web browser and navigate to http://localhost:5000


Use the navigation menu to explore different features of the application:
View Data: Examine dataset preview and statistics
Analyze: Perform statistical analysis on specific columns
Correlation: Explore correlations between different categories
Project Structure
app.py: Main Flask application file
templates/: Directory containing HTML templates
static/: Directory for static files (CSS, JavaScript)
MentalHealthDataset.csv: Dataset file (It is included as a ZIP file)


Contributing
Contributions to improve the application are welcome. Please follow these steps:
Fork the repository
Create a new branch (git checkout -b feature-branch)
Make your changes and commit (git commit -am 'Add some feature')
Push to the branch (git push origin feature-branch)
Create a new Pull Request
