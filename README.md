# Gesture-Recognition
This system implements a touchless Human–Computer Interaction (HCI) mechanism for controlling a media player using hand gestures. The solution leverages MediaPipe for real-time hand tracking and gesture recognition, deployed on a Raspberry Pi 5 (RPI5) as an edge computing device.

Project Summary: Hand Gesture HCI for Media Control
High-Efficiency Edge-Inference on Raspberry Pi 5

OVERVIEW
This project implements a Natural User Interface (NUI) for touchless media control. It utilizes 21-point
skeletal tracking and a Hierarchical Finite State Machine (HFSM) to provide near-zero latency
command mapping on edge devices.

DUAL-MODE CONTROL ARCHITECTURE
The system distinguishes between two primary interaction types:
• Static Control: Discrete state mapping (e.g., Open Palm for Play/Pause). Uses a temporal
median filter to ensure intent stability.
• Dynamic Control: Continuous modulation for variables like Volume and Scrubbing. Uses an
anchored control loop to calculate displacement (∆) for real-time frequency scaling.

TECHNICAL FEATURES
• 4-Layer Pipeline: Signal Conditioning, Feature Extraction (MediaPipe), State-Machine Logic,
and Asynchronous Execution.
• Scale Invariance: Centroid-based normalization allows operation from 30cm to 240cm.
• Temporal Filtering: 4-frame median filtering along with Exponential Moving Average(EMA) prevents inference jitter
• Buffer Flushing: Immediate queue reset during intent shifts for fast transitions.

PERFORMANCE DATA
• Accuracy: 96.0% + across all gestures.
• Throughput: 20+ FPS on Raspberry Pi 5.
• CPU Load: 16.9% (Peak Core Load).
• Latency: 160ms – 180ms total system lag.

GESTURE MAPPING
• Activation: Thumbs Up (Unlock System).
• VLC Controls gestures: Open Palm,Index, Spidey,Victory,Nice,Quad,Fist
• VLC Controls features: Play/Pause,Mute/Unmute,Volume control,Video nagivation seeking,Exit,Restart,Playback
Speed control,Playlist Control(prev/next video,shuffle and play in a loop),Miniplayer Videoes,Fullscreen Toggle,Aspect ratio changing,Screenshot
Screenrecording

REQUIREMENTS
• Hardware: Raspberry Pi 5, Lapcam web camera HD 720P LWC-042 (or equivalent).
• Libraries: MediaPipe, OpenCV, Pynput, NumPy.

Authors: Pushpal Bhar, Subhojit Khatua, Arghya Pratim Biswas (Feb 2026)