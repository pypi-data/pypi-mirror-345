from view import View
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)

# Add view path
View.add_path('resources/views')

# Test data
test_data = {
    'title': 'Test Page',
    'items': [
        {'name': 'Item 1'},
        {'name': 'Item 2'}
    ]
}

# Try to render a view
try:
    result = View.make('test', test_data)
    print("Rendered output:")
    print(result)
except Exception as e:
    print(f"Error: {str(e)}") 