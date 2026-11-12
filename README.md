# FlaskScale — Flask REST API on Kubernetes

FlaskScale is a containerized Flask REST API deployed on Kubernetes using Minikube. It demonstrates horizontal pod autoscaling, MongoDB persistence, health checks, resource limits, and Kubernetes service discovery.

## Features

- Flask REST API served using Gunicorn.
- MongoDB 7 with persistent storage and application-user authentication.
- Docker image built for the Flask application.
- Kubernetes Deployment with two initial replicas.
- CPU-based Horizontal Pod Autoscaler (HPA), targeting 70% utilization with a minimum of 2 and maximum of 5 replicas.
- Startup, liveness, and readiness probes.
- CPU and memory requests and limits.
- Internal ClusterIP service for MongoDB and NodePort service for Flask.
- Non-root application container.

## Technology Stack

Python, Flask, Gunicorn, MongoDB, Docker, Kubernetes, Minikube, kubectl, and Metrics Server.

## Architecture

Client → Flask NodePort Service → Flask Deployment → MongoDB ClusterIP Service → MongoDB StatefulSet → Persistent Volume Claim → Persistent Volume.

The HPA monitors CPU utilization and adjusts the number of Flask replicas within the configured limits.

## API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | Welcome message and UTC timestamp |
| GET | `/healthz` | Application health check |
| GET | `/ready` | Readiness check, including MongoDB connectivity |
| GET | `/data` | Retrieve application data |
| POST | `/data` | Store application data |
| GET | `/stress?iterations=500000` | Generate CPU load for autoscaling tests when enabled |

## Prerequisites

- Python 3.11
- Docker Desktop
- Minikube
- kubectl
- A running Kubernetes Metrics Server

## Run Locally

Create and activate a virtual environment, then install dependencies:

```bash
python -m venv .venv
pip install -r requirements.txt
python -m app.app
```

Configure MongoDB connectivity using the environment variables expected by the application. The local MongoDB instance must be accessible before testing database-dependent endpoints.

## Build the Docker Image

```bash
docker build -t flaskscale:1.0 .
```

## Deploy to Minikube

Start the cluster and load the local image:

```bash
minikube start
minikube image load flaskscale:1.0
```

Apply the Kubernetes resources in dependency order:

```bash
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/secrets.yaml
kubectl apply -f k8s/mongodb-init-config.yaml
kubectl apply -f k8s/mongodb.yaml
kubectl rollout status statefulset/mongodb -n flaskscale
kubectl apply -f k8s/flask.yaml
kubectl apply -f k8s/hpa.yaml
```

The `k8s/secrets.yaml` file is a local-only file and must be created using your own credentials. Do not commit it to GitHub. The namespace must exist before namespaced resources are applied.

## Verify the Deployment

```bash
kubectl get pods -n flaskscale
kubectl get deployments -n flaskscale
kubectl get services -n flaskscale
kubectl get pvc -n flaskscale
kubectl get hpa -n flaskscale
kubectl top pods -n flaskscale
```

Access the API locally through port forwarding:

```bash
kubectl port-forward -n flaskscale service/flask-service 8080:5000
```

In another terminal, test the endpoints:

```bash
curl http://localhost:8080/healthz
curl http://localhost:8080/ready
curl http://localhost:8080/
```

## Autoscaling

The HPA uses CPU utilization relative to the CPU requests of the Flask containers. It is configured for 2–5 replicas and a 70% CPU utilization target. CPU load tests can demonstrate scaling behavior.

## Testing

Run the project's automated tests using the test command appropriate for the files in the `tests/` directory. Validate health, readiness, database connectivity, persistent storage, and autoscaling behavior.

## Security Notes

- Never commit credentials, `.env` files, or populated Kubernetes Secrets.
- Replace example passwords with strong, locally supplied credentials.
- MongoDB is exposed internally using a ClusterIP service.
- The Flask application container runs as a non-root user.

## Deployment Scope

This project has been verified on a local Minikube cluster. A public production deployment requires a remotely accessible Kubernetes cluster, suitable persistent storage, a container registry, and appropriate networking and secrets management.

## License

Add a license if you intend to distribute this project publicly.
