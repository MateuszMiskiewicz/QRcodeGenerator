# Low-Level QR Code Generator (Python)

A fully functional QR Code generator (Versions 1-5) implemented from scratch in pure Python. This project was developed to explore the internal mechanics of the ISO/IEC 18004 standard, including Galois Field theory, Reed-Solomon error correction, and matrix masking algorithms.

##Features
* **Byte Encoding:** Converts raw text/URLs into a valid QR bitstream.
* **Error Correction (ECC):** Full implementation of Reed-Solomon encoding to ensure data integrity even if the code is partially damaged.
* **Smart Masking:** Implements all 8 standard QR masks with an automated **Penalty Scoring** system (Rules N1-N4) to select the most readable pattern.
* **Dynamic GUI:** A user-friendly interface built with Tkinter for data input.
* **Modular Architecture:** Clean separation between mathematical logic, matrix manipulation, and UI.



##Project Structure
The project is modularized to reflect the stages of QR generation:
* `gf_256.py` – $GF(2^8)$ Galois Field arithmetic (log/exp tables).
* `reed_solomon.py` – Polynomial generation and ECC codeword calculation.
* `matrix.py` – Matrix initialization, placement of fixed patterns (Finder, Timing, Alignment), and the masking engine.
* `data_encode.py` – Text-to-binary conversion and version management.
* `gui.py` – The Tkinter-based input window.
* `display.py` – Visual rendering of the final QR matrix using a Tkinter Canvas.

##Installation & Usage

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/YourUsername/qr-generator-python.git](https://github.com/YourUsername/qr-generator-python.git)
   cd qr-generator-python
