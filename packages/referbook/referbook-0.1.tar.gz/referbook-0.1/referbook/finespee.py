# Install dependencies before running:
# pip install transformers datasets torchaudio soundfile jiwer

import torch
from datasets import load_dataset
from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC, TrainingArguments, Trainer
import torchaudio
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Union

# 1. Load Dataset
dataset = load_dataset("mozilla-foundation/common_voice_11_0", "en", split="train[:1%]")

# 2. Preprocessing
processor = Wav2Vec2Processor.from_pretrained("facebook/wav2vec2-base-960h")
chars_to_ignore_regex = '[\,\?\.\!\-\;\:"]'

def remove_special_characters(batch):
    batch["text"] = re.sub(chars_to_ignore_regex, '', batch["sentence"]).lower()
    return batch

def speech_file_to_array_fn(batch):
    speech_array, _ = torchaudio.load(batch["path"])
    batch["speech"] = speech_array[0].numpy()
    batch["sampling_rate"] = 16000
    batch["input_values"] = processor(batch["speech"], sampling_rate=16000).input_values[0]
    batch["labels"] = processor.tokenizer(batch["text"]).input_ids
    return batch

dataset = dataset.map(remove_special_characters)
dataset = dataset.map(speech_file_to_array_fn)

# 3. Custom Dataset Class
class CustomDataset(torch.utils.data.Dataset):
    def __init__(self, data):
        self.data = data

    def __getitem__(self, idx):
        return {
            "input_values": torch.tensor(self.data[idx]["input_values"], dtype=torch.float),
            "labels": torch.tensor(self.data[idx]["labels"], dtype=torch.long)
        }

    def __len__(self):
        return len(self.data)

train_dataset = CustomDataset(dataset)

# 4. Data Collator
@dataclass
class DataCollatorCTCWithPadding:
    processor: Wav2Vec2Processor
    padding: Union[bool, str] = True

    def __call__(self, features: List[Dict[str, Any]]) -> Dict[str, Any]:
        input_features = [{"input_values": f["input_values"]} for f in features]
        label_features = [{"input_ids": f["labels"]} for f in features]

        batch = self.processor.pad(input_features, padding=self.padding, return_tensors="pt")
        with self.processor.as_target_processor():
            labels_batch = self.processor.pad(label_features, padding=self.padding, return_tensors="pt")

        # Replace padding with -100 for CTC Loss
        labels = labels_batch["input_ids"].masked_fill(labels_batch.attention_mask.ne(1), -100)
        batch["labels"] = labels

        return batch

# 5. Load Pre-trained Wav2Vec2 Model
model = Wav2Vec2ForCTC.from_pretrained(
    "facebook/wav2vec2-base-960h",
    ctc_loss_reduction="mean",
    pad_token_id=processor.tokenizer.pad_token_id,
)

# 6. Training Arguments
training_args = TrainingArguments(
    output_dir="./wav2vec2-finetuned",
    group_by_length=True,
    per_device_train_batch_size=8,
    evaluation_strategy="no",
    num_train_epochs=3,
    save_steps=10,
    save_total_limit=2,
    logging_steps=2,
    learning_rate=1e-4,
    fp16=torch.cuda.is_available(),
)

# 7. Trainer
data_collator = DataCollatorCTCWithPadding(processor=processor)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    tokenizer=processor.feature_extractor,
    data_collator=data_collator,
)

# 8. Start Training
trainer.train()

# 9. Save Fine-tuned Model
model.save_pretrained("fine-tuned-wav2vec2")
processor.save_pretrained("fine-tuned-wav2vec2")


"test"


# Install required libraries if not already installed:
# pip install transformers torchaudio soundfile

import torch
import torchaudio
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor

# Load fine-tuned model and processor
model_path = "fine-tuned-wav2vec2"  # or replace with your saved path
processor = Wav2Vec2Processor.from_pretrained(model_path)
model = Wav2Vec2ForCTC.from_pretrained(model_path)
model.eval()

# Load your audio file
def transcribe(path):
    speech_array, sample_rate = torchaudio.load(path)
    if sample_rate != 16000:
        resampler = torchaudio.transforms.Resample(orig_freq=sample_rate, new_freq=16000)
        speech_array = resampler(speech_array)
    input_values = processor(speech_array.squeeze(), return_tensors="pt", sampling_rate=16000).input_values
    with torch.no_grad():
        logits = model(input_values).logits
    predicted_ids = torch.argmax(logits, dim=-1)
    transcription = processor.decode(predicted_ids[0])
    return transcription

# Example usage
audio_path = "example.wav"  # Replace with your audio file path
print("Transcription:", transcribe(audio_path))



"mfcc featues "


import librosa
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

# Sample MFCC to token conversion
def extract_mfcc_as_tokens(file_path, n_mfcc=13):
    y, sr = librosa.load(file_path, sr=None)
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=n_mfcc)
    # Quantize to simulate 'words'
    quantized = np.round(mfcc).astype(int)
    tokens = ["mfcc_" + str(val) for row in quantized for val in row]
    return " ".join(tokens)

# Sample inputs (use librosa's sample audio for example)
sample_audio1 = librosa.example('trumpet')  # trumpet audio
sample_audio2 = librosa.example('brahms')   # classical music

# Create example dataset
X_raw = [
    extract_mfcc_as_tokens(sample_audio1),
    extract_mfcc_as_tokens(sample_audio2)
]
y = ['trumpet', 'classical']

# Vectorize using TF-IDF
vectorizer = TfidfVectorizer(max_features=1000)
X = vectorizer.fit_transform(X_raw)

# Train KNN classifier
knn = KNeighborsClassifier(n_neighbors=1)
knn.fit(X, y)

# Test on a new audio input (use trumpet again for demo)
test_audio = sample_audio1
test_tokens = extract_mfcc_as_tokens(test_audio)
test_vector = vectorizer.transform([test_tokens])

# Predict
prediction = knn.predict(test_vector)
print("Predicted label:", prediction[0])
