import torch
import torch.nn as nn
import torchaudio
from torchaudio.datasets import LIBRISPEECH
from torch.utils.data import DataLoader
import torchaudio.transforms as T
import matplotlib.pyplot as plt

# Device config
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# 1. Load LibriSpeech Dataset
train_dataset = LIBRISPEECH(".", url="train-clean-100", download=True)

# 2. Vocabulary Creation
def extract_vocab(dataset):
    vocab_set = set()
    for i in range(100):  # Limit to 100 samples for demo
        _, _, _, _, transcript, _ = dataset[i]
        vocab_set.update(list(transcript.lower()))
    vocab = sorted(vocab_set)
    vocab_dict = {c: i + 1 for i, c in enumerate(vocab)}  # 0 = blank
    vocab_dict["<pad>"] = 0
    return vocab_dict

vocab = extract_vocab(train_dataset)
vocab_size = len(vocab)

# 3. Preprocessing
transform = T.MFCC(sample_rate=16000, n_mfcc=40)

def preprocess(batch):
    waveform, _, _, _, transcript, _ = batch
    mfcc = transform(waveform).squeeze(0).transpose(0, 1)
    transcript_ids = [vocab.get(c, 0) for c in transcript.lower()]
    return mfcc, torch.tensor(transcript_ids)

# 4. DataLoader
def collate_fn(batch):
    features, targets = zip(*[preprocess(b) for b in batch])
    features = nn.utils.rnn.pad_sequence(features, batch_first=True)
    targets = nn.utils.rnn.pad_sequence(targets, batch_first=True, padding_value=0)
    return features.to(device), targets.to(device)

train_loader = DataLoader(train_dataset, batch_size=4, shuffle=True, collate_fn=collate_fn)

# 5. RNN Model
class SpeechToTextRNN(nn.Module):
    def __init__(self, input_dim, hidden_dim, vocab_size):
        super(SpeechToTextRNN, self).__init__()
        self.lstm = nn.LSTM(input_dim, hidden_dim, batch_first=True, bidirectional=True)
        self.fc = nn.Linear(hidden_dim * 2, vocab_size)

    def forward(self, x):
        out, _ = self.lstm(x)
        out = self.fc(out)
        return out

model = SpeechToTextRNN(40, 128, vocab_size).to(device)

# 6. Training Setup
criterion = nn.CrossEntropyLoss(ignore_index=0)
optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)

# 7. Train Loop
for epoch in range(5):
    model.train()
    total_loss = 0
    for features, targets in train_loader:
        optimizer.zero_grad()
        outputs = model(features)  # [B, T, Vocab]
        outputs = outputs.view(-1, vocab_size)
        targets = targets.view(-1)
        loss = criterion(outputs, targets)
        loss.backward()
        optimizer.step()
        total_loss += loss.item()
    print(f"Epoch [{epoch + 1}/5], Loss: {total_loss:.4f}")


"test "
import torch
import torchaudio.transforms as T
import matplotlib.pyplot as plt

# Load a single sample from the dataset for testing
sample_idx = 100  # Pick any index you like
waveform, _, _, _, transcript, _ = train_dataset[sample_idx]

# 1. Preprocessing: Extract MFCC from the sample
transform = T.MFCC(sample_rate=16000, n_mfcc=40)
mfcc = transform(waveform).squeeze(0).transpose(0, 1).unsqueeze(0).to(device)  # Add batch dimension and move to device

# 2. Model Inference
model.eval()  # Set model to evaluation mode
with torch.no_grad():
    output = model(mfcc)  # [1, T, Vocab]
    output = output.squeeze(0)  # Remove batch dimension
    predicted_indices = output.argmax(dim=-1)  # Get the indices with max probability for each time step

# 3. Decode the predicted indices into text
def decode_prediction(indices, vocab_dict):
    reversed_vocab = {i: c for c, i in vocab_dict.items()}  # Reverse the vocab_dict to get char -> index
    decoded_text = ''.join([reversed_vocab.get(idx.item(), '') for idx in indices])
    return decoded_text

# Get the predicted text
predicted_text = decode_prediction(predicted_indices, vocab)
print("Predicted Transcript: ", predicted_text)

# 4. Show the original and predicted transcriptions
print("Original Transcript: ", transcript)

# 5. Plot the waveform (optional)
plt.figure(figsize=(10, 4))
plt.plot(waveform.t().numpy())
plt.title("Waveform of the Audio Sample")
plt.show()
