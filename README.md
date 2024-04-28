# A multimodal architecture with shared encoder that uses spectrograms for audio
## Course Project, CSCI 535, Spring 2024
Contributors - Sai Anuroop Kesanapalli, Riya Ranjan, Aashi Goyal, Wilson Tan

#### Usage
> :warning: To be continuously modified as we make progress!
* Install ```ffmpeg```<br>
  ```$ brew install ffmpeg``` (macOS)<br>
  ```$ sudo apt-get install ffmpeg``` (Linux)<br>
  ```$ python3 -m pip install ffmpeg``` (conda)

* Run ```flv_to_wav.py``` to convert FLV video files of CREMA-D to WAV audio files<br>
  ```$ python3 flv_to_wav.py input_folder output_folder```

* Install ```librosa```<br>
  ```$ python3 -m pip install librosa```
  
* Run ```wav_to_melspec.py``` to convert WAV audio files to Mel spectrograms<br>
  ```$ python3 wav_to_melspec.py input_folder output_folder```

* Install ```torch```, ```torchvision```, ```pillow```<br>
  ```$ python3 -m pip install torch torchvision pillow```
  > TODO: Bundle all requirements for the pipeline into a single ```requirements.txt```
  
* Run ```melspec_to_features_cnn.py``` to extract features out of Mel spectrograms using ResNet-18 (fine-tuned on Mel spectrograms) <br>
  ```$ python3 -m melspec_to_features_cnn.py input_folder```
  <!-- > TODO: Explore the features extracted using pre-trained ResNet-18, think about training ResNet-18 on the Mel spectrograms / corresponding video files / both -->

#### Findings

* Experiment: Check performance of pre-trained Vgg16 on Mel spectrograms generated from a subset of CREMA-Dspectrograms
    * Model: models.vgg16(pretrained=True)
    * Number of classes: ```3``` (ANG, SAD, HAP)
    <!-- * Model fine-tuned on: averaged one-second granular frames -->
    * Total number of samples: ```273```
    <!-- * Number of train samples: ```191``` -->
    * Number of test samples: ```82```
    * Batch size: ```32```
    <!-- * lr: ```0.001``` -->
    * Loss: ```nn.CrossEntropyLoss()```
    <!-- * Train epochs: ```50``` -->
    * Results:
        <!-- * Train Loss: ```0.5809```  -->
        <!-- * Train Accuracy: ```0.9686``` -->
        * Test Loss: ```1.1027```
        * Test Accuracy: ```0.3537```
    * Reproduce:
        * Notebook: [```notebooks/pretrained/melspec_to_features_pretrained_cnn.ipynb```](https://github.com/ksanu1998/multimodal_course_project/blob/aashi/notebooks/pretrained/melspec_to_features_pretrained_cnn.ipynb)
        * Script: [```scripts/pretrained/melspec_to_features_pretrained_cnn.py```](https://github.com/ksanu1998/multimodal_course_project/blob/aashi/scripts/pretrained/melspec_to_features_pretrained_cnn.py)
        <!-- * Saved Model: [ResNet18_video_50_32_0.001](https://drive.google.com/file/d/1aZ4IMVIlKW8Qq-EvaVwd-7YKSm8obUXa/view?usp=drive_link) -->

* Experiment: Check performance of pre-trained Vgg16 on faces cropped out of middle frames extracted out of videos from a subset of CREMA-D
    * Model: models.vgg16(pretrained=True)
    * Number of classes: ```3``` (ANG, SAD, HAP)
    <!-- * Model fine-tuned on: averaged one-second granular frames -->
    * Total number of samples: ```273```
    <!-- * Number of train samples: ```191``` -->
    * Number of test samples: ```82```
    * Batch size: ```32```
    <!-- * lr: ```0.0001``` -->
    * Loss: ```nn.CrossEntropyLoss()```
    <!-- * Train epochs: ```50``` -->
    * Results:
        <!-- * Train Loss: ```0.5809```  -->
        <!-- * Train Accuracy: ```0.9686``` -->
        * Test Loss: ```1.0919```
        * Test Accuracy: ```0.3902```
    * Reproduce:
        * Notebook: [```notebooks/pretrained/video_to_features_pretrained_cnn.ipynb```](https://github.com/ksanu1998/multimodal_course_project/blob/aashi/notebooks/pretrained/video_to_features_pretrained_cnn.ipynb)
        * Script: [```scripts/pretrained/video_to_features_pretrained_cnn.py```](https://github.com/ksanu1998/multimodal_course_project/blob/aashi/scripts/pretrained/video_to_features_pretrained_cnn.py)
        <!-- * Saved Model: [ResNet18_video_50_32_0.001](https://drive.google.com/file/d/1aZ4IMVIlKW8Qq-EvaVwd-7YKSm8obUXa/view?usp=drive_link) -->

* Experiment: Fine-tune Vgg16 on Mel spectrograms generated from a fullscale of CREMA-D
    * Model: models.vgg16(pretrained=True)
    * Number of classes: ```3``` (ANG, SAD, HAP)
    * Model fine-tuned on: Mel spectrograms
    * Total number of samples: ```7473```
    * Number of train samples: ```5231```
    * Number of test samples: ```2242```
    * Batch size: ```32```
    * lr: ```0.0001```
    * Loss: ```nn.CrossEntropyLoss()```
    * Train epochs: ```50```
    * Results:
        * Train Loss: ```1.4038``` 
        * Train Accuracy: ```0.6366```
        * Test Loss: ```1.5259```
        * Test Accuracy: ```0.5120```
    * Reproduce:
        * Notebook: [```notebooks/finetuned-individual/melspec_to_features_cnn.ipynb```](https://github.com/ksanu1998/multimodal_course_project/blob/aashi/notebooks/finetuned-individual/melspec_to_features_cnn(2).ipynb)
        * Script: [```scripts/finetuned-individual/melspec_to_features_cnn.py```](https://github.com/ksanu1998/multimodal_course_project/blob/aashi/scripts/finetuned-individual/melspec_to_features_cnn(2).py)
    <!-- * Saved Model: [vgg16_melspec_50_32_0.001](https://drive.google.com/file/d/1HXjd7Ej0L4NJLfzxH0L8taDTXRGoGBML/view?usp=drive_link) -->

* Experiment: Fine-tune Vgg16 on faces cropped out of middle frames extracted out of videos from a fullscale of CREMA-D
    * Model: models.vgg16(pretrained=True)
    * Number of classes: ```3``` (ANG, SAD, HAP)
    * Model fine-tuned on: faces cropped out of middle frames
    * Total number of samples: ```7473```
    * Number of train samples: ```5231```
    * Number of test samples: ```2242```
    * Batch size: ```32```
    * lr: ```0.00001```
    * Loss: ```nn.CrossEntropyLoss()```
    * Train epochs: ```50```
    * Results:
        * Train Loss: ```1.0952``` 
        * Train Accuracy: ```0.9495```
        * Test Loss: ```1.3337```
        * Test Accuracy: ```0.7040```
    * Reproduce:
        * Notebook: [```notebooks/finetuned-individual/video_to_features_cnn.ipynb```](https://github.com/ksanu1998/multimodal_course_project/blob/aashi/notebooks/finetuned-individual/video_to_features_cnn.ipynb)
        * Script: [```scripts/finetuned-individual/video_to_features_cnn.py```](https://github.com/ksanu1998/multimodal_course_project/blob/aashi/scripts/finetuned-individual/video_to_features_cnn.py)
          <!-- * Saved Model: [vgg16_video_50_32_0.00001](https://drive.google.com/file/d/1aZ4IMVIlKW8Qq-EvaVwd-7YKSm8obUXa/view?usp=drive_link) -->

* Experiment: Check cross performance of Vgg16 finetuned with Mel spectrograms on videos 
   <!-- * Model: model.load_state_dict(torch.load('/content/drive/MyDrive/csci535/models/ResNet18_melspec_50_32_0.001'))-->
    * Number of classes: ```3``` (ANG, SAD, HAP)
    <!-- * Model fine-tuned on: averaged one-second granular frames -->
    * Total number of samples: ```273```
    <!-- * Number of train samples: ```191``` -->
    * Number of test samples: ```82```
    * Batch size: ```32```
    <!-- * lr: ```0.001``` -->
    * Loss: ```nn.CrossEntropyLoss()```
    <!-- * Train epochs: ```50``` -->
    * Results:
        <!-- * Train Loss: ```0.5809```  -->
        <!-- * Train Accuracy: ```0.9686``` -->
        * Test Loss: ```1.2138```
        * Test Accuracy: ```0.3049```
    * Reproduce:
        * Notebook: [```notebooks/finetuned-cross/video_to_features_audio_cnn.ipynb```](https://github.com/ksanu1998/multimodal_course_project/blob/aashi/notebooks/finetuned-cross/video_to_features_audio_cnn.ipynb)
        * Script: [```scripts/finetuned-cross/video_to_features_cnn.py```](https://github.com/ksanu1998/multimodal_course_project/blob/aashi/scripts/finetuned-cross/video_to_features_audio_cnn.py)
        <!-- * Saved Model: [vgg16_video_50_32_0.001](https://drive.google.com/file/d/1aZ4IMVIlKW8Qq-EvaVwd-7YKSm8obUXa/view?usp=drive_link) -->

* Experiment: Check cross performance of Vgg16 finetuned with faces on Mel spectrograms
    <!-- * Model: model.load_state_dict(torch.load('/content/drive/MyDrive/csci535/models/ResNet18_video_50_32_0.001')) -->
    * Number of classes: ```3``` (ANG, SAD, HAP)
    <!-- * Model fine-tuned on: averaged one-second granular frames -->
    * Total number of samples: ```273```
    <!-- * Number of train samples: ```191``` -->
    * Number of test samples: ```82```
    * Batch size: ```32```
    <!-- * lr: ```0.0001``` -->
    * Loss: ```nn.CrossEntropyLoss()```
    <!-- * Train epochs: ```50``` -->
    * Results:
        <!-- * Train Loss: ```0.5809```  -->
        <!-- * Train Accuracy: ```0.9686``` -->
        * Test Loss: ```1.1726```
        * Test Accuracy: ```0.3415```
    * Reproduce:
        * Notebook: [```notebooks/finetuned-cross/melspec_to_features_video_cnn.ipynb```](https://github.com/ksanu1998/multimodal_course_project/blob/aashi/notebooks/finetuned-cross/melspec_to_features_video_cnn.ipynb)
        * Script: [```scripts/finetuned-cross/melspec_to_features_video_cnn.py```](https://github.com/ksanu1998/multimodal_course_project/blob/aashi/scripts/finetuned-cross/melspec_to_features_video_cnn.py)
        <!-- * Saved Model: [vgg16_video_50_32_0.001](https://drive.google.com/file/d/1aZ4IMVIlKW8Qq-EvaVwd-7YKSm8obUXa/view?usp=drive_link) -->

* Experiment: Check performance of pre-trained Vgg16 on faces cropped from middle frames extracted out of videos and Mel spectrograms concatenated, from a fullscale of CREMA-D
    * Model: models.vgg16(pretrained=True)
    * Number of classes: ```3``` (ANG, SAD, HAP)
    <!-- * Model fine-tuned on: faces cropped out of middle frames and Mel spectrograms concatenated -->
    * Total number of samples: ```7473```
    * Number of train samples: ```5209```
    * Number of test samples: ```2233```
    * Batch size: ```32```
    <!-- * lr: ```0.0001``` -->
    * Loss: ```nn.CrossEntropyLoss()```
    <!-- * Train epochs: ```50``` -->
    * Results:
        <!-- * Train Loss: ```1.6099```  -->
        <!-- * Train Accuracy: ```0.4329``` -->
        * Test Loss: ```1.5713```
        * Test Accuracy: ```0.4716```
    * Reproduce:
        * Notebook: [```notebooks/pretrained/audio_video_pretrained_cnn.ipynb```](https://github.com/ksanu1998/multimodal_course_project/blob/aashi/notebooks/pretrained/audio_video_pretrained_cnn.ipynb)
        * Script: [```scripts/pretrained/audio_video_cnn.py```](https://github.com/ksanu1998/multimodal_course_project/blob/aashi/scripts/pretrained/audio_video_pretrained_cnn.py)
        <!-- * Saved Model: [vgg16_audio_video_50_32_0.0001](https://drive.google.com/file/d/1kjqmT-UssMUMGVL8dcJymzE_iCCqKtQ2/view?usp=drive_link) -->

* Experiment: Fine-tune Vgg16 on faces cropped from middle frames extracted out of videos and Mel spectrograms concatenated, from a fullscale of CREMA-D
    * Model: models.vgg16(pretrained=True)
    * Number of classes: ```3``` (ANG, SAD, HAP)
    * Model fine-tuned on: faces cropped out of middle frames and Mel spectrograms concatenated
    * Total number of samples: ```7473```
    * Number of train samples: ```5209```
    * Number of test samples: ```2233```
    * Batch size: ```32```
    * lr: ```0.0001```
    * Loss: ```nn.CrossEntropyLoss()```
    * Train epochs: ```50```
    * Results:
        * Train Loss: ```1.6099``` 
        * Train Accuracy: ```0.4329```
        * Test Loss: ```1.5713```
        * Test Accuracy: ```0.4716```
    * Reproduce:
        * Notebook: [```notebooks/finetuned-combined/audio_video_cnn.ipynb```](https://github.com/ksanu1998/multimodal_course_project/blob/aashi/notebooks/finetuned-combined/audio_video_cnn.ipynb)
        * Script: [```scripts/finetuned-combined/audio_video_cnn.py```](https://github.com/ksanu1998/multimodal_course_project/blob/aashi/scripts/finetuned-combined/audio_video_cnn.py)
      <!-- * Saved Model: [vgg16_audio_video_50_32_0.0001](https://drive.google.com/file/d/1kjqmT-UssMUMGVL8dcJymzE_iCCqKtQ2/view?usp=drive_link)-->

#### Resources
<!-- Audio feature extraction via spectrograms - https://github.com/DeepSpectrum/DeepSpectrum <br> -->
[GDrive](https://drive.google.com/drive/folders/1BhpgUDgbYwoTaTO6Yo8M3uR0Clw0bkiC?usp=drive_link) <br>
[GDoc](https://docs.google.com/document/d/1jN6ZpCUjqboJQLSFR-Osqlm5kRHGYX2a47GRADVYUPU/edit?usp=sharing)

