# Remaining Features TODO

## 1. Container Management (Remaining)
- **Web Console**: A "Web Console" tab/modal to execute commands inside the container (`docker exec -it`).

## 2. Image Management
- **Local Image List**: Display ID, Tag, Size, and Creation Date.
- **Pull Image**: Search bar or text input to pull images directly from Docker Hub or private registries.
- **Cleanup Tools**: "Prune" button to delete unused (dangling) images.
- **Build UI**: Ability to upload a Dockerfile and build a custom image directly from the panel.

## 3. Volume & Networking
- **Volume CRUD**: List all volumes, view mount points, and delete unused ones.
- **Network Manager**:
    - Visualize container-network associations.
    - Create custom networks.
    - Connect/Disconnect containers via UI.

## 4. Advanced "Production" Features
- **Docker Compose Support**: YAML editor to paste `docker-compose.yml` and run "Up"/"Down".
- **Stats & Monitoring**: Live sparklines/gauges for CPU %, Memory Usage, and Network I/O (using `docker stats`).
- **Auto-Update**: Integration with Watchtower (or custom logic) to auto-pull and restart containers.
- **Registry Manager**: Save credentials for private registries.
- **Template Snippets**: Save favorite Compose snippets.

## 5. Swarm Setup (Cluster Management)
- **Join Tokens**: Display Manager/Worker tokens.
- **Node Promotions**: Promote/Demote buttons.
- **Service Management**: CRUD for Swarm Services (Replicas, Update Strategies, Placement Constraints).
