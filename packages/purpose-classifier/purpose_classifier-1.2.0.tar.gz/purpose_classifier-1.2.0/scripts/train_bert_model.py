#!/usr/bin/env python
"""
Train a BERT-based purpose code classifier.

This script trains a BERT model for purpose code classification using CSV files 
in the data directory, then replaces the existing combined_model.pkl with the new model.
"""

import os
import sys
import json
import glob
import time
import shutil
import argparse
import logging
import datetime
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from tqdm import tqdm

import torch
from torch.utils.data import Dataset, DataLoader
from torch.optim import AdamW
from transformers import BertTokenizer, BertForSequenceClassification
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

# Add the parent directory to the path so we can import the purpose_classifier package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from purpose_classifier.utils.preprocessor import TextPreprocessor
from purpose_classifier.config.settings import PURPOSE_CODES_PATH
from purpose_classifier.bert_adapter import BertModelAdapter, BertVectorizerAdapter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/bert_training_{}.log'.format(
            datetime.datetime.now().strftime('%Y%m%d_%H%M%S')))
    ]
)
logger = logging.getLogger(__name__)

# Constants
BERT_MODEL = 'bert-base-uncased'

class PurposeCodeDataset(Dataset):
    """Dataset for purpose code classification with BERT."""
    
    def __init__(self, texts, labels, tokenizer, max_length=128):
        """
        Initialize the dataset.
        
        Args:
            texts: List of text samples
            labels: List of corresponding labels
            tokenizer: BERT tokenizer
            max_length: Maximum sequence length
        """
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length
    
    def __len__(self):
        return len(self.texts)
    
    def __getitem__(self, idx):
        text = self.texts[idx]
        label = self.labels[idx]
        
        encoding = self.tokenizer(
            text,
            add_special_tokens=True,
            max_length=self.max_length,
            padding='max_length',
            truncation=True,
            return_tensors='pt'
        )
        
        # Convert labels to torch.long (int64) type
        return {
            'input_ids': encoding['input_ids'].squeeze(),
            'attention_mask': encoding['attention_mask'].squeeze(),
            'label': torch.tensor(label, dtype=torch.long)
        }

def load_purpose_codes(filepath):
    """Load purpose codes from JSON file"""
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.error(f"Failed to load purpose codes from {filepath}: {str(e)}")
        return {}

def load_csv_files(data_dir='data'):
    """Load all CSV files in the data directory."""
    csv_files = glob.glob(os.path.join(data_dir, '*.csv'))
    if not csv_files:
        logger.error(f"No CSV files found in {data_dir}")
        return None
    
    logger.info(f"Found {len(csv_files)} CSV files in {data_dir}")
    
    # Load and combine all CSV files
    dfs = []
    for csv_file in csv_files:
        try:
            logger.info(f"Loading {csv_file}")
            df = pd.read_csv(csv_file)
            if 'narration' not in df.columns or 'purpose_code' not in df.columns:
                logger.warning(f"File {csv_file} does not have required columns. Skipping.")
                continue
            dfs.append(df)
            logger.info(f"Loaded {len(df)} rows from {csv_file}")
        except Exception as e:
            logger.error(f"Failed to load {csv_file}: {str(e)}")
    
    if not dfs:
        logger.error("No valid CSV files could be loaded")
        return None
    
    # Combine all dataframes
    combined_df = pd.concat(dfs, ignore_index=True)
    logger.info(f"Combined dataset has {len(combined_df)} rows")
    
    # Drop duplicates
    combined_df.drop_duplicates(subset=['narration', 'purpose_code'], inplace=True)
    logger.info(f"After removing duplicates, dataset has {len(combined_df)} rows")
    
    return combined_df

def train_bert_model(df, output_model_path, test_size=0.2, batch_size=16, epochs=5, learning_rate=2e-5):
    """Train a BERT model for purpose code classification."""
    preprocessor = TextPreprocessor()
    
    # Preprocess text
    logger.info("Preprocessing text...")
    df['processed_text'] = df['narration'].apply(preprocessor.preprocess)
    
    # Encode labels
    label_encoder = LabelEncoder()
    df['label'] = label_encoder.fit_transform(df['purpose_code'])
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        df['processed_text'].values, 
        df['label'].values,
        test_size=test_size, 
        stratify=df['purpose_code'], 
        random_state=42
    )
    
    logger.info(f"Training set: {len(X_train)} samples")
    logger.info(f"Test set: {len(X_test)} samples")
    
    # Initialize tokenizer and model
    logger.info(f"Initializing BERT model {BERT_MODEL}...")
    tokenizer = BertTokenizer.from_pretrained(BERT_MODEL)
    model = BertForSequenceClassification.from_pretrained(
        BERT_MODEL, 
        num_labels=len(label_encoder.classes_)
    )
    
    # Create datasets and dataloaders
    train_dataset = PurposeCodeDataset(X_train, y_train, tokenizer)
    test_dataset = PurposeCodeDataset(X_test, y_test, tokenizer)
    
    train_dataloader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    test_dataloader = DataLoader(test_dataset, batch_size=batch_size)
    
    # Set up optimizer
    optimizer = AdamW(model.parameters(), lr=learning_rate)
    
    # Check for GPU
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    logger.info(f"Using device: {device}")
    model.to(device)
    
    # Training loop
    logger.info("Starting training...")
    model.train()
    for epoch in range(epochs):
        logger.info(f"Epoch {epoch+1}/{epochs}")
        epoch_loss = 0
        
        progress_bar = tqdm(train_dataloader, desc=f"Epoch {epoch+1}")
        for batch in progress_bar:
            # Move tensors to device
            input_ids = batch['input_ids'].to(device)
            attention_mask = batch['attention_mask'].to(device)
            labels = batch['label'].to(device)
            
            # Forward pass
            optimizer.zero_grad()
            outputs = model(
                input_ids=input_ids,
                attention_mask=attention_mask,
                labels=labels
            )
            
            loss = outputs.loss
            epoch_loss += loss.item()
            
            # Backward pass
            loss.backward()
            optimizer.step()
            
            progress_bar.set_postfix({'loss': loss.item()})
        
        avg_epoch_loss = epoch_loss / len(train_dataloader)
        logger.info(f"Average loss for epoch {epoch+1}: {avg_epoch_loss:.4f}")
        
        # Evaluate on test set
        model.eval()
        test_preds = []
        test_labels = []
        
        with torch.no_grad():
            for batch in tqdm(test_dataloader, desc="Evaluating"):
                input_ids = batch['input_ids'].to(device)
                attention_mask = batch['attention_mask'].to(device)
                labels = batch['label'].to(device)
                
                outputs = model(
                    input_ids=input_ids,
                    attention_mask=attention_mask
                )
                
                preds = torch.argmax(outputs.logits, dim=1)
                test_preds.extend(preds.cpu().numpy())
                test_labels.extend(labels.cpu().numpy())
        
        accuracy = accuracy_score(test_labels, test_preds)
        logger.info(f"Test accuracy: {accuracy:.4f}")
        
        # Switch back to training mode
        model.train()
    
    # Final evaluation
    model.eval()
    logger.info("Final evaluation on test set...")
    
    test_preds = []
    test_labels = []
    
    with torch.no_grad():
        for batch in tqdm(test_dataloader, desc="Final evaluation"):
            input_ids = batch['input_ids'].to(device)
            attention_mask = batch['attention_mask'].to(device)
            labels = batch['label'].to(device)
            
            outputs = model(
                input_ids=input_ids,
                attention_mask=attention_mask
            )
            
            preds = torch.argmax(outputs.logits, dim=1)
            test_preds.extend(preds.cpu().numpy())
            test_labels.extend(labels.cpu().numpy())
    
    accuracy = accuracy_score(test_labels, test_preds)
    logger.info(f"Final test accuracy: {accuracy:.4f}")
    
    # Get classification report
    class_names = [label_encoder.inverse_transform([i])[0] for i in range(len(label_encoder.classes_))]
    report = classification_report(test_labels, test_preds, target_names=class_names)
    logger.info(f"Classification report:\n{report}")
    
    # Create adapters for compatibility with LightGBMPurposeClassifier
    model_adapter = BertModelAdapter(model, tokenizer, device)
    vectorizer_adapter = BertVectorizerAdapter(tokenizer)
    
    # Create model package compatible with the original LightGBM model structure
    logger.info("Creating model package...")
    model_package = {
        'model': model_adapter,
        'vectorizer': vectorizer_adapter,
        'label_encoder': label_encoder,
        'created_at': datetime.datetime.now().isoformat(),
        'model_type': 'bert',
        'bert_model_name': BERT_MODEL,
        'preprocessing': preprocessor,
        # Add other necessary components
        'tokenizer': tokenizer,
        'bert_model': model,
        'params': {
            'model_type': 'bert',
            'learning_rate': learning_rate,
            'batch_size': batch_size,
            'epochs': epochs,
            'max_length': 128
        }
    }
    
    # Create a directory for the model if it doesn't exist
    os.makedirs(os.path.dirname(output_model_path), exist_ok=True)
    
    # Save the model
    logger.info(f"Saving model to {output_model_path}")
    torch.save(model.state_dict(), f"{output_model_path}.pt")
    joblib.dump(model_package, output_model_path)
    
    return model_package

def backup_existing_model(model_path):
    """Backup the existing model before replacing it."""
    if not os.path.exists(model_path):
        logger.warning(f"No existing model found at {model_path}. No backup needed.")
        return
    
    # Create backup directory if it doesn't exist
    backup_dir = os.path.join(os.path.dirname(model_path), 'backup')
    os.makedirs(backup_dir, exist_ok=True)
    
    # Create backup filename with timestamp
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = os.path.join(backup_dir, f"combined_model_pre_bert.pkl")
    
    # Backup the model
    logger.info(f"Backing up existing model from {model_path} to {backup_path}")
    shutil.copy2(model_path, backup_path)
    
    # Also make a timestamped copy
    timestamped_backup = os.path.join(backup_dir, f"combined_model_{timestamp}.pkl")
    shutil.copy2(model_path, timestamped_backup)
    
    logger.info(f"Backup completed successfully")

def main():
    """Main function to train the BERT model."""
    parser = argparse.ArgumentParser(description='Train a BERT model for purpose code classification')
    parser.add_argument('--data-dir', type=str, default='data',
                       help='Directory containing the CSV files')
    parser.add_argument('--output-model', type=str, default='models/combined_model.pkl',
                       help='Path to save the trained model')
    parser.add_argument('--test-size', type=float, default=0.2,
                       help='Proportion of data to use for testing')
    parser.add_argument('--batch-size', type=int, default=16,
                       help='Batch size for training')
    parser.add_argument('--epochs', type=int, default=5,
                       help='Number of training epochs')
    parser.add_argument('--learning-rate', type=float, default=2e-5,
                       help='Learning rate for optimizer')
    parser.add_argument('--skip-backup', action='store_true',
                       help='Skip backing up the existing model')
    
    args = parser.parse_args()
    
    # Load all CSV files
    df = load_csv_files(args.data_dir)
    if df is None:
        logger.error("Failed to load data. Exiting.")
        return 1
    
    # Backup existing model
    if not args.skip_backup:
        backup_existing_model(args.output_model)
    
    # Train the model
    try:
        train_bert_model(
            df,
            args.output_model,
            test_size=args.test_size,
            batch_size=args.batch_size,
            epochs=args.epochs,
            learning_rate=args.learning_rate
        )
        logger.info("Model training completed successfully!")
        return 0
    except Exception as e:
        logger.error(f"Error during model training: {str(e)}")
        return 1

if __name__ == '__main__':
    sys.exit(main()) 