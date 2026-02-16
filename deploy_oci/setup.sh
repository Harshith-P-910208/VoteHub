#!/bin/bash

# Oracle Cloud Ubuntu Deployment Script for College VoteHub
# This script automates the setup of Python, Nginx, and Gunicorn

echo "🚀 Starting deployment setup on Oracle Cloud..."

# 1. Update system
sudo apt update && sudo apt upgrade -y

# 2. Install dependencies
sudo apt install -y python3-pip python3-venv nginx git curl

# 3. Clone the repository (User needs to replace this with their own repo if different)
# cd /home/ubuntu
# git clone https://github.com/Harshith-P-910208/VoteHub.git
# cd VoteHub

# 4. Setup Virtual Environment
python3 -m venv venv
source venv/bin/activate

# 5. Install Python packages
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn whitenoise

# 6. Setup environment variables (User will need to edit this)
if [ ! -f .env ]; then
    echo "Creating .env template..."
    cp .env.example .env 2>/dev/null || touch .env
    echo "DEBUG=False" >> .env
    echo "ALLOWED_HOSTS=*" >> .env
fi

# 7. Collect Static Files
python3 manage.py collectstatic --noinput

# 8. Configure Firewall (Oracle Cloud specific)
# Oracle Ubuntu uses 'iptables' by default instead of 'ufw'
sudo iptables -I INPUT 6 -p tcp --dport 80 -j ACCEPT
sudo iptables -I INPUT 6 -p tcp --dport 443 -j ACCEPT
sudo netfilter-persistent save

echo "✅ Setup complete. Please configure Nginx and Systemd files."
