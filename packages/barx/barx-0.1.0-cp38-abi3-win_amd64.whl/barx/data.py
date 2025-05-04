"""
Data loading and preprocessing utilities for BARX.

This module provides tools for loading and preprocessing data
for machine learning tasks.
"""

import csv
import json
import numpy as np
from typing import List, Dict, Tuple, Any, Optional, Union, Iterator
from .tensor import Tensor, T

class Dataset:
    """
    Base dataset class.
    
    Abstract class for all datasets in BARX.
    """
    
    def __init__(self):
        """Initialize dataset."""
        pass
        
    def __getitem__(self, index: int) -> Tuple[Tensor, Tensor]:
        """
        Get a single data item and its label.
        
        Args:
            index: Index of the data item
            
        Returns:
            Tuple of (data, label) tensors
        """
        raise NotImplementedError("Subclasses must implement __getitem__")
        
    def __len__(self) -> int:
        """
        Get number of items in dataset.
        
        Returns:
            Number of items
        """
        raise NotImplementedError("Subclasses must implement __len__")


class DataLoader:
    """
    Data loader for providing batched data.
    
    Wraps a dataset and provides batched iteration over its items.
    """
    
    def __init__(self, 
                 dataset: Dataset, 
                 batch_size: int = 32, 
                 shuffle: bool = True):
        """
        Initialize data loader.
        
        Args:
            dataset: Dataset to load data from
            batch_size: Size of each batch (default: 32)
            shuffle: Whether to shuffle the data (default: True)
        """
        self.dataset = dataset
        self.batch_size = batch_size
        self.shuffle = shuffle
        self._indices = list(range(len(dataset)))
        
    def __iter__(self) -> Iterator[Tuple[Tensor, Tensor]]:
        """
        Get iterator over batches.
        
        Returns:
            Iterator yielding (data_batch, label_batch) tuples
        """
        if self.shuffle:
            np.random.shuffle(self._indices)
            
        for i in range(0, len(self._indices), self.batch_size):
            batch_indices = self._indices[i:i+self.batch_size]
            batch_data = []
            batch_labels = []
            
            for idx in batch_indices:
                data, label = self.dataset[idx]
                batch_data.append(data.data)
                batch_labels.append(label.data)
                
            # Stack the batch
            data_tensor = T.tensor(np.stack(batch_data))
            label_tensor = T.tensor(np.stack(batch_labels))
            
            yield data_tensor, label_tensor
            
    def __len__(self) -> int:
        """
        Get number of batches.
        
        Returns:
            Number of batches
        """
        return (len(self.dataset) + self.batch_size - 1) // self.batch_size


class CSVDataset(Dataset):
    """
    Dataset for loading data from CSV files.
    
    Provides functionality to load and preprocess CSV data.
    """
    
    def __init__(self, 
                 filepath: str, 
                 x_cols: List[str], 
                 y_cols: List[str], 
                 delimiter: str = ',',
                 skip_header: bool = True,
                 x_transform: Optional[callable] = None,
                 y_transform: Optional[callable] = None):
        """
        Initialize CSV dataset.
        
        Args:
            filepath: Path to CSV file
            x_cols: List of column names for input features
            y_cols: List of column names for output labels
            delimiter: CSV delimiter character (default: ',')
            skip_header: Whether to skip the header row (default: True)
            x_transform: Optional function to transform input features
            y_transform: Optional function to transform output labels
        """
        super().__init__()
        self.filepath = filepath
        self.x_cols = x_cols
        self.y_cols = y_cols
        self.delimiter = delimiter
        self.skip_header = skip_header
        self.x_transform = x_transform
        self.y_transform = y_transform
        
        # Load data
        self._load_data()
        
    def _load_data(self):
        """Load data from CSV file."""
        self.data = []
        self.labels = []
        
        with open(self.filepath, 'r', newline='') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=self.delimiter)
            
            for row in reader:
                # Extract features
                x = [float(row[col]) for col in self.x_cols]
                
                # Extract labels
                y = [float(row[col]) for col in self.y_cols]
                
                # Apply transformations if needed
                if self.x_transform:
                    x = self.x_transform(x)
                
                if self.y_transform:
                    y = self.y_transform(y)
                
                self.data.append(np.array(x, dtype=np.float32))
                self.labels.append(np.array(y, dtype=np.float32))
                
    def __getitem__(self, index: int) -> Tuple[Tensor, Tensor]:
        """
        Get a single data item and its label.
        
        Args:
            index: Index of the data item
            
        Returns:
            Tuple of (data, label) tensors
        """
        x = T.tensor(self.data[index])
        y = T.tensor(self.labels[index])
        return x, y
        
    def __len__(self) -> int:
        """
        Get number of items in dataset.
        
        Returns:
            Number of items
        """
        return len(self.data)


class JSONDataset(Dataset):
    """
    Dataset for loading data from JSON files.
    
    Provides functionality to load and preprocess JSON data.
    """
    
    def __init__(self, 
                 filepath: str,
                 x_keys: List[str],
                 y_keys: List[str],
                 root_path: str = None,
                 x_transform: Optional[callable] = None,
                 y_transform: Optional[callable] = None):
        """
        Initialize JSON dataset.
        
        Args:
            filepath: Path to JSON file
            x_keys: List of keys for input features
            y_keys: List of keys for output labels
            root_path: JSON path to data array (default: None, assumes root is array)
            x_transform: Optional function to transform input features
            y_transform: Optional function to transform output labels
        """
        super().__init__()
        self.filepath = filepath
        self.x_keys = x_keys
        self.y_keys = y_keys
        self.root_path = root_path
        self.x_transform = x_transform
        self.y_transform = y_transform
        
        # Load data
        self._load_data()
        
    def _load_data(self):
        """Load data from JSON file."""
        self.data = []
        self.labels = []
        
        with open(self.filepath, 'r') as jsonfile:
            json_data = json.load(jsonfile)
            
            # Navigate to root path if provided
            if self.root_path:
                for key in self.root_path.split('.'):
                    json_data = json_data[key]
                    
            # Process each item
            for item in json_data:
                # Extract features
                x = self._extract_values(item, self.x_keys)
                
                # Extract labels
                y = self._extract_values(item, self.y_keys)
                
                # Apply transformations if needed
                if self.x_transform:
                    x = self.x_transform(x)
                
                if self.y_transform:
                    y = self.y_transform(y)
                
                self.data.append(np.array(x, dtype=np.float32))
                self.labels.append(np.array(y, dtype=np.float32))
                
    def _extract_values(self, item: Dict, keys: List[str]) -> List[float]:
        """
        Extract values from item using keys.
        
        Args:
            item: Dictionary to extract values from
            keys: List of keys to extract
            
        Returns:
            List of extracted values
        """
        values = []
        
        for key in keys:
            # Handle nested keys with dot notation
            if '.' in key:
                value = item
                for k in key.split('.'):
                    if isinstance(value, dict) and k in value:
                        value = value[k]
                    else:
                        value = 0.0  # Default for missing keys
                        break
            else:
                value = item.get(key, 0.0)
                
            # Convert to float
            try:
                values.append(float(value))
            except (ValueError, TypeError):
                values.append(0.0)  # Default for non-numeric values
                
        return values
        
    def __getitem__(self, index: int) -> Tuple[Tensor, Tensor]:
        """
        Get a single data item and its label.
        
        Args:
            index: Index of the data item
            
        Returns:
            Tuple of (data, label) tensors
        """
        x = T.tensor(self.data[index])
        y = T.tensor(self.labels[index])
        return x, y
        
    def __len__(self) -> int:
        """
        Get number of items in dataset.
        
        Returns:
            Number of items
        """
        return len(self.data)


class InMemoryDataset(Dataset):
    """
    Dataset for in-memory data.
    
    Provides a simple way to wrap NumPy arrays or lists as a dataset.
    """
    
    def __init__(self, 
                 features: Union[List, np.ndarray], 
                 labels: Union[List, np.ndarray],
                 x_transform: Optional[callable] = None,
                 y_transform: Optional[callable] = None):
        """
        Initialize in-memory dataset.
        
        Args:
            features: Input features array
            labels: Output labels array
            x_transform: Optional function to transform input features
            y_transform: Optional function to transform output labels
        """
        super().__init__()
        
        if isinstance(features, list):
            features = np.array(features, dtype=np.float32)
        if isinstance(labels, list):
            labels = np.array(labels, dtype=np.float32)
            
        self.features = features
        self.labels = labels
        self.x_transform = x_transform
        self.y_transform = y_transform
        
        assert len(self.features) == len(self.labels), "Features and labels must have the same length"
        
    def __getitem__(self, index: int) -> Tuple[Tensor, Tensor]:
        """
        Get a single data item and its label.
        
        Args:
            index: Index of the data item
            
        Returns:
            Tuple of (data, label) tensors
        """
        x = self.features[index]
        y = self.labels[index]
        
        # Apply transformations if needed
        if self.x_transform:
            x = self.x_transform(x)
        
        if self.y_transform:
            y = self.y_transform(y)
            
        return T.tensor(x), T.tensor(y)
        
    def __len__(self) -> int:
        """
        Get number of items in dataset.
        
        Returns:
            Number of items
        """
        return len(self.features)
