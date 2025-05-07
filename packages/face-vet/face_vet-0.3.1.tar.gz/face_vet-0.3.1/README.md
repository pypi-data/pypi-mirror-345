# **face-vet**

`face-vet` is a comprehensive Python library designed to validate the authenticity and quality of images. It performs multiple checks, including face detection, image quality assessment, depth analysis, and tampering detection (e.g., overlayed text such as timestamps or watermarks). This package is particularly useful for fraud detection, identity verification, and ensuring image authenticity across various applications.

## 🚀 Key Features

- **Face Detection**: Identifies whether an image contains a face, aiding in the detection of manipulated or irrelevant images.
- **Image Quality Check**: Analyzes the sharpness and overall quality of the image, flagging blurry or poorly captured images.
- **Text Detection**: Uses Optical Character Recognition (OCR) to detect overlaid text, such as timestamps, watermarks, or branding.
- **Tampering Detection**: Combines multiple checks to assess the authenticity of an image and detect potential signs of tampering.
- **Depth Detection (Eye-Nose Distance)**: Leverages facial landmarks to detect unusual eye-to-nose distances, which can indicate manipulation or fake images.

## 📦 Installation

To install `face-vet`, simply use `pip`:

```bash
pip install face-vet
