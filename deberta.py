# -*- coding: utf-8 -*-
"""Deberta.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1-itLWP8UXTdyMmEr4Warsk6wV5utFLyW
"""

!pip install datasets
!pip install evaluate

from datasets import load_dataset

# Load the Stanford Sentiment Treebank (SST) dataset
dataset = load_dataset("sst", "default")

# Print dataset structure
print(dataset)

dataset['train'][0]

from transformers import AutoModelForSequenceClassification, AutoTokenizer

# Choose a DeBERTa model (Example: DeBERTa-v3-base)
model_name = "microsoft/deberta-v3-base"

# Load tokenizer
tokenizer = AutoTokenizer.from_pretrained(model_name)

# Load model (for sentiment classification, use `num_labels=2` for binary tasks)
model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=2)

def tokenize_function(examples):
    return tokenizer(examples["sentence"], padding="max_length", truncation=True)

# Apply tokenization
tokenized_datasets = dataset.map(tokenize_function, batched=True)

# Remove original text column & set format for PyTorch
tokenized_datasets = tokenized_datasets.remove_columns(["sentence","tokens","tree"])

tokenized_datasets.set_format("torch")

# Check a sample tokenized entry
print(tokenized_datasets["train"][0])

tokenized_datasets['train'][0]

from transformers import TrainingArguments

training_args = TrainingArguments(
    output_dir="./results",  # Save model here
    evaluation_strategy="epoch",
    save_strategy="epoch",
    learning_rate=2e-5,
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    num_train_epochs=1,
    weight_decay=0.01,
    logging_dir="./logs",
    logging_steps=10,
    report_to="none"
)

from transformers import Trainer, TrainingArguments
import numpy as np
import evaluate

# Load accuracy metric
accuracy = evaluate.load("accuracy")

# Compute accuracy
def compute_metrics(eval_pred):
    logits, labels = eval_pred
    predictions = np.argmax(logits, axis=-1)
    return accuracy.compute(predictions=predictions, references=labels)

# Define Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_datasets["train"],
    eval_dataset=tokenized_datasets["validation"],
    tokenizer=tokenizer,
    compute_metrics=compute_metrics
)

trainer.train()

results = trainer.evaluate(tokenized_datasets["test"])
print(results)