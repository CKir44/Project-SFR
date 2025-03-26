🚀 Project SFR: Security & Facial Recognition

Welcome to Project SFR, a gesture-controlled facial recognition system designed for home security and interactive AI experimentation. Built using Python and Docker, this project lets you run real-time facial and gesture recognition, with options for automatic cloud syncing via NextCloud.

🛠️ Features

Face Recognition

Recognizes pre-registered faces via photos in the headshots/ directory

Runs facial recognition every 30 seconds for 10 seconds to reduce load

Gesture Control

✊ Closed Fist: Zooms in (elastic zoom that returns on release)

🤚 Finger Counter: Hold up numbers (e.g. 3 → 4 → 6 = "346")

Performance

Threaded Python logic ensures smooth, concurrent processes

Lightweight optimizations for lower-end systems

Cloud Integration (Optional)

Auto-upload video footage to a NextCloud instance via WebDAV (disabled by default)

Docker Deployment

Packaged in a container for easy portability and no setup hassle

📦 Docker Quick Start

Pull the container:

docker pull cr44reed/ddfr-final:latest

Run the container:

docker run -it --rm \
  --device=/dev/video0 \
  -v $(pwd)/recordings:/app/recordings \
  -v $(pwd)/headshots:/app/headshots \
  cr44reed/ddfr-final:latest

⚠️ Ensure your webcam is accessible as /dev/video0 and adjust if needed.

📁 Folder Structure

Aiproj/
├── face_detection.py         # Main script
├── test.py                   # Camera index test
├── Dockerfile                # Container setup
├── requirements.txt          # Project dependencies
├── headshots/                # User headshot images (used for recognition)
├── recordings/               # Auto-saved video outputs
├── .gitignore                # Git exclusions

✍️ Customizing Recognition

To register new users:

Add a .jpg or .png file with a clear face to the headshots/ directory.

Name the file as the user's name (e.g., kirby.jpg).

Restart the container.

🔐 Optional NextCloud Sync

To enable automatic cloud saving:

Edit the face_detection.py and fill in these variables:

NEXTCLOUD_URL = ""
NEXTCLOUD_USERNAME = ""
NEXTCLOUD_PASSWORD = ""

📬 Contact

Open to collaboration or feedback! Feel free to reach out or fork the project.

