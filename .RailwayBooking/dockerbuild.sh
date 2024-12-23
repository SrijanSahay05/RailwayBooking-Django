docker-compose down --volumes --remove-orphans
docker system prune -af
docker volume prune -f
docker network prune -f
sudo systemctl restart docker
docker-compose -f docker-compose.prod.yml up --build
