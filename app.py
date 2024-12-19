from flask import Flask, render_template, request, jsonify
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64
import numpy as np
import plotly.graph_objs as go

app = Flask(__name__)

# Load the dataset
df = pd.read_csv('MentalHealthDataset.csv')

@app.route('/')
def index():
    try:
        return render_template('index.html')
    except Exception as e:
        app.logger.error(f"Error rendering index: {e}")
        return f"An error occurred: {e}", 500

@app.route('/data')
def view_data():
    # Data preview
    data_preview = df.head().to_dict('records')
    columns = df.columns.tolist()

    # Column information
    column_info = [
        {"name": "Gender", "type": "Categorical", "description": "Gender of the participant"},
        {"name": "Country", "type": "Categorical", "description": "Country of residence"},
        {"name": "Occupation", "type": "Categorical", "description": "Participant's occupation"},
        {"name": "self_employed", "type": "Boolean", "description": "Whether the participant is self-employed"},
        {"name": "family_history", "type": "Boolean", "description": "Family history of mental health issues"},
        {"name": "treatment", "type": "Boolean", "description": "Whether the participant has sought treatment"},
        {"name": "Days_Indoors", "type": "Numeric", "description": "Number of days spent indoors"},
        {"name": "Growing_Stress", "type": "Categorical", "description": "Level of growing stress"},
        {"name": "Changes_Habits", "type": "Categorical", "description": "Changes in habits"},
        {"name": "Mental_Health_History", "type": "Boolean", "description": "History of mental health issues"},
        {"name": "Mood_Swings", "type": "Categorical", "description": "Frequency of mood swings"},
        {"name": "Coping_Struggles", "type": "Categorical", "description": "Level of struggle in coping"},
        {"name": "Work_Interest", "type": "Categorical", "description": "Level of interest in work"},
        {"name": "Social_Weakness", "type": "Categorical", "description": "Level of social weakness"},
        {"name": "mental_health_interview", "type": "Boolean", "description": "Willingness to discuss mental health in an interview"},
        {"name": "care_options", "type": "Boolean", "description": "Awareness of mental health care options"}
    ]

    # Basic statistics for numeric columns
    numeric_columns = [col for col in df.columns if np.issubdtype(df[col].dtype, np.number)]
    basic_stats = []
    for col in numeric_columns:
        stats = df[col].describe()
        basic_stats.append({
            "name": col,
            "count": stats['count'],
            "mean": round(stats['mean'], 2),
            "median": round(df[col].median(), 2),
            "std": round(stats['std'], 2),
            "min": stats['min'],
            "max": stats['max']
        })

    # Data quality information
    total_rows = len(df)
    missing_values = df.isnull().sum().to_dict()

    return render_template('view_data.html', 
                           data=data_preview, 
                           columns=columns, 
                           column_info=column_info,
                           basic_stats=basic_stats, 
                           total_rows=total_rows, 
                           missing_values=missing_values)

@app.route('/analyze', methods=['GET', 'POST'])
def analyze():
    columns = df.columns.tolist()
    return render_template('analyze.html', columns=columns)

@app.route('/analyze_data', methods=['POST'])
def analyze_data():
    try:
        column = request.form['column']
        
        # Check if the column exists
        if column not in df.columns:
            return jsonify({'error': 'Column not found'}), 400
        
        # Calculate statistics
        stats = df[column].describe().to_dict()
        
        # Handle different data types
        if df[column].dtype == 'object':
            # For categorical data
            value_counts = df[column].value_counts().to_dict()
            histogram_data = [{
                'x': list(value_counts.keys()),
                'y': list(value_counts.values()),
                'type': 'bar',
                'name': column
            }]
        else:
            # For numerical data
            hist, bin_edges = np.histogram(df[column].dropna(), bins='auto')
            histogram_data = [{
                'x': bin_edges.tolist(),
                'y': hist.tolist(),
                'type': 'bar',
                'name': column
            }]
        
        return jsonify({
            'statistics': stats,
            'histogram': histogram_data
        })
    except Exception as e:
        app.logger.error(f"An error occurred: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.errorhandler(Exception)
def handle_exception(e):
    return jsonify(error=str(e)), 500

@app.route('/correlation', methods=['GET'])
def correlation():
    columns = [col for col in df.columns if col != 'timestamp']
    return render_template('correlation.html', columns=columns)

@app.route('/get_options', methods=['POST'])
def get_options():
    category = request.form['category']
    options = df[category].unique().tolist()
    return jsonify({'options': options})

@app.route('/analyze_correlation', methods=['POST'])
def analyze_correlation():
    try:
        data = request.json
        categories = [data[f'category{i}'] for i in range(1, 5) if f'category{i}' in data]
        options = [data[f'option{i}'] for i in range(1, 5) if f'option{i}' in data]
        
        # Filter the dataframe based on selected options
        df_filtered = df.copy()
        for category, option in zip(categories, options):
            if option != 'All':
                df_filtered = df_filtered[df_filtered[category] == option]
        
        # Get counts for each combination of options
        counts = df_filtered.groupby(categories).size().reset_index(name='count')
        
        # Prepare data for plotting
        bar_data = [{
            'x': counts[categories[0]].tolist(),
            'y': counts['count'].tolist(),
            'type': 'bar',
            'name': 'Count'
        }]

        pie_data = [{
            'values': counts['count'].tolist(),
            'labels': counts[categories].apply(lambda row: ' - '.join(row.values.astype(str)), axis=1).tolist(),
            'type': 'pie',
            'name': 'Categories'
        }]

        heatmap_data = [{
            'z': [counts['count'].tolist()],
            'x': counts[categories[-1]].tolist(),
            'y': [' - '.join(categories[:-1])],
            'type': 'heatmap',
            'colorscale': 'Viridis'
        }]

        layout = {
            'bar': {
                'title': f'Correlation: {" vs ".join(categories)}',
                'xaxis': {'title': categories[0]},
                'yaxis': {'title': 'Count'},
            },
            'pie': {
                'title': f'Correlation: {" vs ".join(categories)}',
            },
            'heatmap': {
                'title': f'Correlation Heatmap: {" vs ".join(categories)}',
                'xaxis': {'title': categories[-1]},
                'yaxis': {'title': ' - '.join(categories[:-1])}
            }
        }
        
        # Prepare analysis text
        total = len(df_filtered)
        analysis_text = f"<h3>Correlation Analysis</h3>"
        analysis_text += f"<p>Total records: {total}</p>"
        analysis_text += "<ul>"
        for _, row in counts.iterrows():
            count = row['count']
            percentage = (count / total) * 100
            category_values = ' - '.join(row[categories].astype(str))
            analysis_text += f"<li>{category_values}: {count} ({percentage:.2f}%)</li>"
        analysis_text += "</ul>"
        
        return jsonify({
            'plot_data': {
                'bar': bar_data,
                'pie': pie_data,
                'heatmap': heatmap_data
            },
            'layout': layout,
            'analysis_text': analysis_text
        })
    except Exception as e:
        return jsonify(error=str(e)), 500
    

if __name__ == '__main__':
    app.run(debug=True)