# DietApp Frontend

## Overview

This is the frontend application for the DietApp, built with Next.js. It provides a user interface for managing medical reports, viewing AI-powered health insights, and handling user authentication and onboarding.

## Features

- **User Authentication:** Secure login and registration.
- **Medical Report Management:** Upload, view, and manage medical reports.
- **Dynamic Report Display:** Renders medical reports dynamically from JSON data, including Markdown content.
- **AI-Powered Health Insights:** Generates and displays health insights based on medical data using a backend API.
- **Onboarding Process:** Guides new users through initial setup, including medical information and profile creation.
- **Responsive Design:** Built with Tailwind CSS and Shadcn UI for a modern and responsive user experience.
- **Dockerized Deployment:** Easily deployable using Docker containers.

## Installation

### Prerequisites

Before you begin, ensure you have the following installed:

- [Node.js](https://nodejs.org/en/download/) (LTS version recommended)
- [npm](https://www.npmjs.com/get-npm) (comes with Node.js)
- [Docker](https://www.docker.com/get-started) (for containerized deployment)

### Local Development Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/anamul94/DietGeniusAI.git
    cd DietGeniusAI/dietapp-frontend
    ```

2.  **Install dependencies:**
    ```bash
    npm install
    ```

3.  **Create environment file:**
    Copy the example environment file and update it with your backend API URL. By default, it points to `http://localhost:8000`.
    ```bash
    cp .env.example .env
    ```
    Open `.env` and modify `NEXT_PUBLIC_API_URL` if your backend is hosted elsewhere.

4.  **Run the development server:**
    ```bash
    npm run dev
    ```
    The application will be accessible at `http://localhost:3000`.

### Docker Deployment

This project includes a `Dockerfile` and a `Makefile` for easy Docker integration.

1.  **Ensure your `.env` file is configured** as described in the local setup section.

2.  **Build the Docker image:**
    This command builds the Docker image, passing the `NEXT_PUBLIC_API_URL` from your `.env` file as a build argument.
    ```bash
    make build
    ```
    *Note: If you change `NEXT_PUBLIC_API_URL` in `.env` after building, you'll need to rebuild the image.* 

3.  **Run the Docker container:**
    This command runs the application in a Docker container, mapping port 3000 and injecting environment variables from your `.env` file.
    ```bash
    make run
    ```
    The application will be accessible at `http://localhost:3000`.

4.  **Stop the container:**
    ```bash
    make stop
    ```

5.  **Clean up (remove Docker image):**
    ```bash
    make clean
    ```

## Usage

Once the application is running, navigate to `http://localhost:3000` in your web browser. You can:

- **Sign In/Sign Up:** Access the authentication pages.
- **Onboarding:** Complete the initial profile setup.
- **View Reports:** See your uploaded medical reports, dynamically rendered.
- **Get Insights:** Generate AI-powered health insights based on your data.

## API Endpoints

The frontend interacts with the following backend API endpoints:

- `/api/medical-reports/medical`: For fetching medical reports (GET, with pagination).
- `/api/medical-reports/memory-test`: For generating medical insights (POST).

Ensure your backend service is running and accessible at the `NEXT_PUBLIC_API_URL` configured in your `.env` file.

## Contributing

Contributions are welcome! Please feel free to open issues or submit pull requests.

## License

This project is licensed under the MIT License.
