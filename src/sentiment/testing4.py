from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

# Set the device to run on (e.g. "/gpu:0" for GPU)
device = "cpu"

# Initialize the model

tokenizer = AutoTokenizer.from_pretrained("cardiffnlp/twitter-roberta-base-emotion")
model = AutoModelForSequenceClassification.from_pretrained("cardiffnlp/twitter-roberta-base-emotion")

# # Set the model to run on the specified device
# model.to(device)

def sentiment_classifier(text: str) -> str:
  # Encode the input text
  input_ids = torch.tensor(tokenizer.encode(text)).unsqueeze(0)
  input_ids = input_ids.to(device)
  
  # try ecxeption block to handle the RuntimeError
  try:
      # Get the predicted sentiment
      with torch.no_grad():
          outputs = model(input_ids)
          sentiment = torch.argmax(outputs[0]).item()
      if sentiment==0:
          return "anger"
      elif sentiment==1:
          return "joy"
      elif sentiment==2:
          return "optimism"
      elif sentiment==3:
          return "sadness"
  except RuntimeError:
      return "Error"

# Get the predicted sentiment
print(sentiment_classifier("I am happy"))