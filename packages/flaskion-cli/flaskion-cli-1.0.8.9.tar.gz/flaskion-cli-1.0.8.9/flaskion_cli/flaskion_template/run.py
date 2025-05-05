from app import create_app

# Create the application instance using the factory function
app = create_app()

if __name__ == "__main__":
    # Run the development server
    app.run(debug=True)