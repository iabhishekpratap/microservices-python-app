# Video to Audio Converter Microservice

A Python-based microservice application that converts video files to audio format, deployed on Kubernetes with Helm.

## Architecture

- **Auth Service**: JWT authentication with PostgreSQL
- **Convert Service**: Processes videos from RabbitMQ, stores audio in MongoDB
- **Gateway Service**: API endpoints (login/upload/download)
- **Notification Service**: Email alerts on conversion completion

## Prerequisites

- Kubernetes cluster (EKS)
- Helm
- Docker
- Python 3
- AWS CLI v2
- kubectl

## Deployment

1. **Install Databases**:
   ```bash
   # MongoDB
   helm install mongo ./Helm_charts/MongoDB
  
   # PostgreSQL
   helm install postgres ./Helm_charts/Postgres
   ```

2. **Configure Databases**:
   - Create auth table in PostgreSQL
   - Set up RabbitMQ queues (mp3, video)

3. **Deploy Microservices**:
   ```bash
   kubectl apply -f ./src/[service-name]/manifest/
   ```

## API Usage

1. **Login**:
   ```bash
   curl -X POST http://<node-ip>:30002/login -u <email>:<password>
   ```

2. **Upload Video**:
   ```bash
   curl -X POST -F 'file=@video.mp4' -H 'Authorization: Bearer <JWT>' http://<node-ip>:30002/upload
   ```

3. **Download Audio**:
   ```bash
   curl --output audio.mp3 -X GET -H 'Authorization: Bearer <JWT>' http://<node-ip>:30002/download?fid=<file-id>
   ```

## Port Configuration

Open these ports in security group:
- 30002: Gateway
- 30003: PostgreSQL
- 30005: MongoDB

## Default Credentials

- PostgreSQL: `absk/root`
- MongoDB: `absk/root`
- RabbitMQ: `guest/guest`

## Support

For issues, please open a GitHub ticket.
