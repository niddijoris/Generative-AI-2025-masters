# AI Media Cover Generation Project

## 1. Project Overview
This repository contains the results and workflow for generating professional-grade media covers using Generative AI. The project specifically focuses on creating a **Book Cover**, a **Vinyl Album**, and a **DVD Box Art** using local AI tools on Apple Silicon hardware.

## 2. Hardware and Environment
- **Device:** MacBook Pro M1
- **RAM:** 16GB Unified Memory
- **Software:** ComfyUI
- **Backend:** MPS (Metal Performance Shaders) for GPU acceleration

## 3. Model Specifications
- **Base Architecture:** SDXL Turbo
- **Specific Model:** Z-Image-Turbo
- **Weight Formats:**
  - **GGUF:** Used for memory optimization (Q4/Q5 variants) to fit within the 16GB RAM limit
- **Weight Dtype:** fp16 or fp8_e5m2 (due to fp8_e4m3fn MPS backend limitations)

## 4. Generation Settings (Optimized for M1)
To achieve high-quality results in under 60 seconds per image, the following KSampler settings were used:
- **Steps:** 8–10
- **CFG Scale:** 1.0–1.5
- **Sampler:** dpmpp_sde
- **Scheduler:** karras

## 5. Case Studies & Prompts

### A. Book Cover: _The Lord of the Rings_
- **Prompt:** Professional high-end book cover for "The Lord of the Rings", epic fantasy aesthetic, a single glowing golden ring floating above the dark volcanic crags of Mount Doom, fiery orange lava glowing in the background, misty atmosphere, intricate elven engravings on the ring, cinematic lighting, 8k resolution, ultra-detailed textures.
- **Resolution:** 640 × 1024 (Portrait)

### Orginal 
![Image](https://github.com/user-attachments/assets/4c7b5c17-bcc2-4bda-86c9-eef459958253)

### Created
<img width="640" height="1024" alt="Image" src="https://github.com/user-attachments/assets/1991a54b-a90f-49bf-8bb3-ebeb4f956f6d" />

### B. Vinyl Album: _Millennium_ (Backstreet Boys)
- **Prompt:** Vinyl record album cover inspired by Backstreet Boys Millennium, late 90s futuristic pop aesthetic, five male silhouettes walking through a bright white high-tech futuristic hallway, clean minimalist design, soft glowing blue and white lights, y2k aesthetic, sharp focus, professional digital art, sleek and polished finish.
- **Resolution:** 1024 × 1024 (Square)

### Orginal 
![Image](https://github.com/user-attachments/assets/8161a40b-0797-49bd-bc7d-73cbaec68c8a)

### Created
<img width="1024" height="1024" alt="Image" src="https://github.com/user-attachments/assets/e77c1607-bd3d-4cfd-abee-d42bd94f1b12" />

### C. DVD Box Art: _Dinotopia_
- **Prompt:** DVD box art for "Dinotopia", bold cinematic title text "DINOTOPIA" at the top, a majestic hidden utopian city where humans and dinosaurs live together, sun-drenched waterfalls, a large Brachiosaurus walking through a marketplace, lush tropical greenery, golden hour lighting, cinematic adventure movie style, 3D render, vibrant colors, 8k resolution.
- **Resolution:** 1024 × 720 (Landscape)

### Orginal 
![Image](https://github.com/user-attachments/assets/a3c3976a-cde5-4a3d-92ed-08c34b1c55b7)

### Created
<img width="1024" height="1024" alt="Image" src="https://github.com/user-attachments/assets/34d7e581-a278-4879-85a9-51b338197c22" />

## 6. Optimization Workflow
- **GGUF Node Integration:** Installed ComfyUI-GGUF to utilize quantized Unet weights.
- **Memory Management:** Implemented split-cross-attention and Manual Garbage Collection to prevent out-of-memory errors on the MPS backend.
- **Dtype Adjustments:** Switched from unsupported float8_e4m3fn to default/fp16 to ensure compatibility with Apple's Metal drivers.

## Conclusion
While running high-end diffusion models on a laptop remains a challenging task due to hardware constraints, this project demonstrates the critical importance of model optimization. Achieving a result in 2 hours and 25 minutes highlights the gap between local consumer hardware and dedicated high-performance computing, yet it proves that with the right configurations like GGUF and Turbo-sampling, creative exploration is possible even in constrained environments.
### that images
<img width="680" height="1024" alt="Image" src="https://github.com/user-attachments/assets/96da11cf-11c0-4f40-b0d1-7b41bf169196" />
<img width="240" height="240" alt="Image" src="https://github.com/user-attachments/assets/fffb6b11-d6ef-4ac1-ba46-1a6200549884" />
<img width="640" height="1024" alt="Image" src="https://github.com/user-attachments/assets/b72102a3-1cf0-4821-a764-ce6d71d4580b" /> 

