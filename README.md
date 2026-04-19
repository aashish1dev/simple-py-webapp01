# simple-py-webapp01
A Simple Python Web App

## Description
This is a basic Flask-based Python web application that displays a simple web page with information about the app. Users can update the app details via a form on the page.

## Setup
1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Run the application locally:
   ```
   python app.py
   ```

3. Open your browser and navigate to `http://127.0.0.1:5000/` to view the app.

### Docker Compose
This repo includes a `Dockerfile` and `docker-compose.yml` for container deployment.

Create a local `.env` file from `.env.example`:
```bash
cp .env.example .env
```

Then start the app with Docker Compose:
```bash
docker compose up --build
```

Open `http://127.0.0.1:5000/` to verify the containerized app.

## Features
- Displays app name, version, description, and author.
- User-updatable page via a form with inputs for App Name, Description, and Person Name.
- Simple HTML template with basic styling.
- Comprehensive test suite including functional and security tests.

## Testing
Run the tests locally:
```
pytest tests/
```

The test suite includes:
- 5 functional tests for app behavior.
- 5 security tests for XSS, HTML, JS, and CSS injection prevention.

## CI/CD Deployment to Private EC2
This repository includes a GitHub Actions workflow for automatic deployment to a private EC2 instance.

### Prerequisites
- An EC2 instance with Docker and Docker Compose installed.
- AWS Systems Manager (SSM) agent installed and running on the EC2 instance.
- An IAM role attached to the instance with `AmazonSSMManagedInstanceCore` and permissions for CloudWatch Logs.
- The repository cloned on the EC2 instance at the path specified in `DEPLOY_PATH` env var in the workflow.

### Using AWS SSM for Private EC2 Deployment
Private EC2 instances (in private subnets) cannot be directly accessed from the internet on port 22. To enable GitHub Actions deployment:

#### Option 1: Use a Bastion Host (Recommended for SSH)
1. Launch a public EC2 instance as a bastion host in a public subnet.
2. Configure security groups:
   - Bastion: Allow SSH (port 22) from your IP and GitHub Actions IPs (if restricted).
   - Private EC2: Allow SSH from the bastion's security group.
3. Set up SSH key forwarding or agent forwarding.
4. Update the workflow to SSH to the bastion first, then to the private instance.
   - Use a custom script in the action, e.g.:
     ```
     ssh -o ProxyCommand="ssh -W %h:%p ec2-user@bastion-host" ec2-user@private-host "commands"
     ```
   - Add `BASTION_HOST` secret for the bastion IP.

#### Option 2: Use AWS Systems Manager (SSM)
1. Ensure SSM agent is installed on the private EC2 (pre-installed on Amazon Linux 2+).
2. Attach an IAM role to the EC2 with `AmazonSSMManagedInstanceCore` policy and CloudWatch Logs permissions.
3. In GitHub Actions, use AWS CLI with SSM:
   - Add secrets: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION`, `INSTANCE_ID`, `CLOUDWATCH_LOG_GROUP`, `APP_SECRET_KEY`.
   - The workflow will generate `.env` on the instance and deploy the app with Docker Compose.
   - This runs commands via SSM without needing port 22 open.

Choose the option that fits your infrastructure. For private instances, SSM is the recommended and safer choice.

### Setup Secrets in GitHub
In your GitHub repository, go to Settings > Secrets and variables > Actions and add these secrets:
- `DEPLOY_PATH`: The app deploy path on the EC2 instance, e.g. `/home/ec2-user/simple-py-webapp01`.
- `AWS_ACCESS_KEY_ID`: AWS access key ID for SSM execution.
- `AWS_SECRET_ACCESS_KEY`: AWS secret access key for SSM execution.
- `AWS_REGION`: AWS region for your EC2/CloudWatch resources.
- `INSTANCE_ID`: The EC2 instance ID to target with SSM.
- `CLOUDWATCH_LOG_GROUP`: CloudWatch Logs group name for Docker container logs.
- `APP_SECRET_KEY`: Flask secret key used by the app.

### Deployment
On push to the `main` branch, the workflow will:
1. Run the test suite.
2. Configure AWS credentials.
3. Build and push the tested Docker image to ECR.
4. Use SSM to deploy the tested image on the private EC2 instance with Docker Compose.

The workflow no longer runs `git pull` on the EC2 instance. It deploys the tested image from ECR using `docker compose pull` and `docker compose up -d`.
4. Pull the latest code, write `.env`, build the Docker image, and start the app with Docker Compose.

The Docker Compose setup sends application logs to CloudWatch via the `awslogs` driver. Ensure the EC2 instance has an IAM role with CloudWatch Logs permissions and Docker Compose installed.

Ensure the app path in the workflow script matches your EC2 setup.
