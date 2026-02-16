# Oracle Cloud Deployment Guide (Ubuntu)

This folder contains the necessary scripts and configuration files to deploy the **College VoteHub** system on an Oracle Cloud OCI instance.

## 📋 Prerequisites
1. An Oracle Cloud Account.
2. A Compute Instance (Ubuntu 22.04 or 24.04 recommended).
3. Public IP address and SSH access.

## 🚀 Step 1: Open Ports in Oracle Console
Before logging into the VM, you **MUST** open port 80 (HTTP) in the Oracle Cloud Dashboard:
1. Go to **Compute** -> **Instances** -> Click your instance.
2. Click on the **Subnet** link under Primary VNIC.
3. Click on **Default Security List**.
4. Click **Add Ingress Rules**.
5. Add rule: **Source CIDR: 0.0.0.0/0**, **IP Protocol: TCP**, **Destination Port Range: 80**.
6. (Optional) Repeat for Port 443 if using SSL.

## 🛠️ Step 2: Setup on VM
SSH into your instance and run:
```bash
sudo apt update && sudo apt install git -y
git clone https://github.com/Harshith-P-910208/VoteHub.git
cd VoteHub
chmod +x deploy_oci/setup.sh
./deploy_oci/setup.sh
```

## ⚙️ Step 3: Configure Gunicorn
Copy the service files:
```bash
sudo cp deploy_oci/gunicorn.socket /etc/systemd/system/
sudo cp deploy_oci/gunicorn.service /etc/systemd/system/
sudo systemctl start gunicorn.socket
sudo systemctl enable gunicorn.socket
```

## 🌐 Step 4: Configure Nginx
1. Edit the file: `nano deploy_oci/nginx.conf` and replace `YOUR_PUBLIC_IP_OR_DOMAIN` with your instance's IP.
2. Copy to Nginx:
```bash
sudo cp deploy_oci/nginx.conf /etc/nginx/sites-available/votehub
sudo ln -s /etc/nginx/sites-available/votehub /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx
```

## 🔑 Environment Variables
Don't forget to edit your `.env` file on the server with your production credentials (MongoDB, Email, etc.).
