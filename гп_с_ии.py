import tkinter as tk
from tkinter import messagebox, ttk, scrolledtext, simpledialog, filedialog
import time
import webbrowser
import json
import os
import queue
import random
from urllib.parse import quote
from datetime import datetime
import subprocess
import sys
import urllib.request
import urllib.error
import socket
import threading
import hashlib
from tkinter import font as tkfont
import math
import ctypes
import winsound

# ========== ИНФОРМАЦИЯ ДЛЯ ПОЛЬЗОВАТЕЛЯ ==========
print("=" * 60)
print("Атом v4.0 PRO - Голосовой помощник")
print("=" * 60)
print("\nДля полной функциональности голосового ввода установите:")
print("1. speech_recognition: pip install SpeechRecognition")
print("2. pyttsx3: pip install pyttsx3")
print("3. pyaudio: pip install pyaudio")
print("\nИЛИ настройте системное распознавание речи в Windows.")
print("=" * 60)
print("\nВ текущем режиме доступен упрощенный голосовой ввод.")
print("=" * 60)

# ========== ПРОВЕРКА ДОСТУПНЫХ МЕТОДОВ ГОЛОСОВОГО ВВОДА ==========

VOICE_INPUT_AVAILABLE = False
VOICE_INPUT_METHOD = None
VOICE_METHODS = []

def check_voice_input_methods():
    """Проверка доступных методов голосового ввода"""
    methods = []
    
    try:
        # 1. Проверяем Windows Speech API
        if os.name == 'nt':
            try:
                # Пытаемся создать COM объект для голоса
                try:
                    import win32com.client
                    speaker = win32com.client.Dispatch("SAPI.SpVoice")
                    methods.append(('windows_sapi', 'Windows Speech API (голосовой вывод)'))
                except ImportError:
                    pass
                
                # Проверяем реестр на наличие голосовых движков
                try:
                    import winreg
                    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                                       r"SOFTWARE\Microsoft\Speech\Voices\Tokens")
                    winreg.CloseKey(key)
                    methods.append(('windows_speech', 'Windows Speech Platform'))
                except:
                    pass
                    
            except Exception as e:
                print(f"Ошибка проверки Windows SAPI: {e}")
    except:
        pass
    
    # 2. Проверяем наличие speech_recognition (если установлен)
    try:
        import speech_recognition as sr
        methods.append(('speech_recognition', 'SpeechRecognition (рекомендуется)'))
    except ImportError:
        pass
    
    # 3. Проверяем наличие pyttsx3 (если установлен)
    try:
        import pyttsx3
        methods.append(('pyttsx3', 'PyTTSx3 (синтез речи)'))
    except ImportError:
        pass
    
    # 4. Добавляем простой fallback метод
    methods.append(('simple_dialog', 'Диалоговый ввод (работает всегда)'))
    
    return methods

# Проверяем доступные методы
VOICE_METHODS = check_voice_input_methods()
if VOICE_METHODS:
    VOICE_INPUT_AVAILABLE = True
    # Выбираем лучший доступный метод
    for method_id, method_name in VOICE_METHODS:
        if method_id in ['speech_recognition', 'windows_sapi', 'pyttsx3']:
            VOICE_INPUT_METHOD = method_id
            break
    else:
        VOICE_INPUT_METHOD = VOICE_METHODS[0][0]
    
    print(f"Доступные методы голосового ввода: {[m[1] for m in VOICE_METHODS]}")
    print(f"Используется метод: {VOICE_INPUT_METHOD}")

# Импортируем библиотеки для голосового помощника если доступны
try:
    import speech_recognition as sr
    import pyttsx3
    SPEECH_AVAILABLE = True
except ImportError:
    SPEECH_AVAILABLE = False
    print("\nБиблиотеки для голосового помощника не установлены.")
    print("Доступен упрощенный режим голосового ввода.")

# Для звука активации в Windows
try:
    import winsound
    WINSOUND_AVAILABLE = True
except ImportError:
    WINSOUND_AVAILABLE = False

# ========== КОД ИИ-АССИСТЕНТА ==========

import pickle
from collections import defaultdict, deque
from typing import List, Tuple, Dict, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum
import statistics
import itertools
import re
import csv
from pathlib import Path

class ActivationFunction(Enum):
    SIGMOID = "sigmoid"
    RELU = "relu"
    TANH = "tanh"
    LEAKY_RELU = "leaky_relu"
    SOFTMAX = "softmax"

@dataclass
class TrainingConfig:
    learning_rate: float = 0.01
    momentum: float = 0.9
    batch_size: int = 32
    epochs: int = 100
    l2_lambda: float = 0.001
    dropout_rate: float = 0.0
    early_stopping_patience: int = 10
    validation_split: float = 0.2

class EnhancedNeuralNetwork:
    def __init__(self, layers: List[int], 
                 activations: List[ActivationFunction] = None,
                 config: TrainingConfig = None):
        
        self.layers = layers
        self.num_layers = len(layers)
        self.config = config or TrainingConfig()
        
        if activations is None:
            activations = [ActivationFunction.RELU] * (len(layers) - 2)
            activations.append(ActivationFunction.SIGMOID)
        
        self.activations = activations
        self.weights = []
        self.biases = []
        
        for i in range(len(layers) - 1):
            if i < len(activations) and activations[i] == ActivationFunction.RELU:
                std = math.sqrt(2.0 / layers[i])
            else:
                std = math.sqrt(1.0 / layers[i])
            
            weight_matrix = [[random.gauss(0, std) for _ in range(layers[i + 1])] 
                            for _ in range(layers[i])]
            bias_vector = [0.0 for _ in range(layers[i + 1])]
            
            self.weights.append(weight_matrix)
            self.biases.append(bias_vector)
        
        self.history = {'loss': [], 'accuracy': [], 'val_loss': [], 'val_accuracy': []}
    
    def _activate(self, x: float, activation: ActivationFunction) -> float:
        if activation == ActivationFunction.SIGMOID:
            return 1.0 / (1.0 + math.exp(-x))
        elif activation == ActivationFunction.RELU:
            return max(0.0, x)
        elif activation == ActivationFunction.LEAKY_RELU:
            return x if x > 0 else 0.01 * x
        elif activation == ActivationFunction.TANH:
            return math.tanh(x)
        else:
            return x
    
    def _activate_derivative(self, x: float, activation: ActivationFunction) -> float:
        if activation == ActivationFunction.SIGMOID:
            return x * (1 - x)
        elif activation == ActivationFunction.RELU:
            return 1.0 if x > 0 else 0.0
        elif activation == ActivationFunction.LEAKY_RELU:
            return 1.0 if x > 0 else 0.01
        elif activation == ActivationFunction.TANH:
            return 1 - x ** 2
        else:
            return 1.0
    
    def _softmax(self, x: List[float]) -> List[float]:
        exp_values = [math.exp(val - max(x)) for val in x]
        sum_exp = sum(exp_values)
        return [val / sum_exp for val in exp_values]
    
    def feedforward(self, inputs: List[float], training: bool = False):
        activations = [inputs]
        z_values = []
        current_activation = inputs
        
        for i in range(self.num_layers - 1):
            z = []
            for j in range(self.layers[i + 1]):
                weighted_sum = self.biases[i][j]
                for k in range(self.layers[i]):
                    weighted_sum += current_activation[k] * self.weights[i][k][j]
                z.append(weighted_sum)
            
            z_values.append(z)
            
            if i == self.num_layers - 2 and self.activations[i] == ActivationFunction.SOFTMAX:
                next_activation = self._softmax(z)
            else:
                next_activation = [self._activate(val, self.activations[i]) for val in z]
            
            if training and self.config.dropout_rate > 0 and i < self.num_layers - 2:
                next_activation = [val if random.random() > self.config.dropout_rate else 0 
                                 for val in next_activation]
            
            activations.append(next_activation)
            current_activation = next_activation
        
        return activations, z_values
    
    def predict(self, inputs: List[float]) -> List[float]:
        activations, _ = self.feedforward(inputs, training=False)
        return activations[-1]
    
    def predict_batch(self, X: List[List[float]]) -> List[List[float]]:
        return [self.predict(x) for x in X]
    
    def compute_loss(self, predictions: List[float], targets: List[float]) -> float:
        epsilon = 1e-8
        loss = 0.0
        for pred, target in zip(predictions, targets):
            loss -= target * math.log(pred + epsilon)
        return loss
    
    def compute_accuracy(self, predictions: List[List[float]], targets: List[List[float]]) -> float:
        correct = 0
        for pred, target in zip(predictions, targets):
            pred_idx = pred.index(max(pred))
            target_idx = target.index(max(target))
            if pred_idx == target_idx:
                correct += 1
        return correct / len(predictions)
    
    def train_on_batch(self, X_batch: List[List[float]], y_batch: List[List[float]]) -> float:
        total_loss = 0.0
        for X, y in zip(X_batch, y_batch):
            activations, _ = self.feedforward(X, training=True)
            total_loss += self.compute_loss(activations[-1], y)
        return total_loss / len(X_batch)
    
    def fit(self, X: List[List[float]], y: List[List[float]], verbose: bool = True):
        split_idx = int(len(X) * (1 - self.config.validation_split))
        X_train, X_val = X[:split_idx], X[split_idx:]
        y_train, y_val = y[:split_idx], y[split_idx:]
        
        for epoch in range(self.config.epochs):
            indices = list(range(len(X_train)))
            random.shuffle(indices)
            X_shuffled = [X_train[i] for i in indices]
            y_shuffled = [y_train[i] for i in indices]
            
            epoch_loss = 0.0
            num_batches = 0
            
            for i in range(0, len(X_train), self.config.batch_size):
                X_batch = X_shuffled[i:i + self.config.batch_size]
                y_batch = y_shuffled[i:i + self.config.batch_size]
                batch_loss = self.train_on_batch(X_batch, y_batch)
                epoch_loss += batch_loss
                num_batches += 1
            
            avg_loss = epoch_loss / max(num_batches, 1)
            
            val_loss = 0.0
            val_accuracy = 0.0
            
            if X_val:
                val_predictions = self.predict_batch(X_val)
                val_loss = sum(self.compute_loss(pred, target) 
                             for pred, target in zip(val_predictions, y_val)) / len(X_val)
                val_accuracy = self.compute_accuracy(val_predictions, y_val)
            
            train_predictions = self.predict_batch(X_train[:100])
            train_accuracy = self.compute_accuracy(train_predictions, y_train[:100])
            
            self.history['loss'].append(avg_loss)
            self.history['accuracy'].append(train_accuracy)
            self.history['val_loss'].append(val_loss)
            self.history['val_accuracy'].append(val_accuracy)
            
            if verbose and epoch % 10 == 0:
                print(f"Epoch {epoch:3d}: loss={avg_loss:.4f}, acc={train_accuracy:.4f}, val_loss={val_loss:.4f}, val_acc={val_accuracy:.4f}")
        
        return self.history
    
    def save(self, filename: str):
        data = {
            'layers': self.layers,
            'weights': self.weights,
            'biases': self.biases,
            'activations': [a.value for a in self.activations],
            'config': self.config.__dict__,
            'history': self.history
        }
        with open(filename, 'wb') as f:
            pickle.dump(data, f)
    
    @classmethod
    def load(cls, filename: str):
        with open(filename, 'rb') as f:
            data = pickle.load(f)
        config = TrainingConfig(**data['config'])
        activations = [ActivationFunction(a) for a in data['activations']]
        model = cls(data['layers'], activations, config)
        model.weights = data['weights']
        model.biases = data['biases']
        model.history = data['history']
        return model

class AIAssistantCore:
    def __init__(self):
        self.models = {}
        self.data_storage = defaultdict(list)
        self.history = []
        self.context = {}
        
    def process_query(self, query: str) -> str:
        """Основной метод обработки запросов"""
        self.history.append((datetime.now(), query))
        
        # Очистка запроса
        query = query.lower().strip()
        
        # Определение типа запроса
        response = ""
        
        if any(word in query for word in ['обучи', 'тренируй', 'создай модель', 'создай нейросеть']):
            response = self.handle_training_request(query)
        elif any(word in query for word in ['предскажи', 'прогноз', 'классифицируй', 'распознай']):
            response = self.handle_prediction_request(query)
        elif any(word in query for word in ['сохрани', 'экспорт', 'запиши']):
            response = self.handle_save_request(query)
        elif any(word in query for word in ['загрузи', 'импорт', 'открой']):
            response = self.handle_load_request(query)
        elif any(word in query for word in ['помощь', 'help', 'команды']):
            response = self.show_help()
        elif any(word in query for word in ['пример', 'демо', 'тест']):
            response = self.run_demo()
        elif any(word in query for word in ['статус', 'информация', 'инфо']):
            response = self.show_status()
        elif any(word in query for word in ['очисти', 'удали', 'reset']):
            response = self.clear_data(query)
        elif any(word in query for word in ['анализ', 'проанализируй', 'статистика']):
            response = self.analyze_data(query)
        else:
            response = self.handle_general_query(query)
        
        return response
    
    def handle_training_request(self, query: str) -> str:
        """Обработка запросов на обучение"""
        try:
            if 'нейросеть' in query or 'нейронную сеть' in query:
                return self.train_neural_network(query)
            elif 'случайный лес' in query or 'random forest' in query:
                return self.train_random_forest(query)
            elif 'дерево' in query or 'decision tree' in query:
                return self.train_decision_tree(query)
            elif 'кластеризация' in query or 'k-means' in query:
                return self.train_kmeans(query)
            else:
                return "Какую модель вы хотите обучить? Укажите: нейросеть, случайный лес, дерево решений или кластеризацию."
        except Exception as e:
            return f"Ошибка при обучении: {str(e)}"
    
    def handle_prediction_request(self, query: str) -> str:
        """Обработка запросов на предсказание"""
        try:
            # Извлечение данных из запроса
            numbers = self.extract_numbers(query)
            if not numbers:
                return "Пожалуйста, предоставьте данные для предсказания в виде чисел."
            
            # Поиск модели
            model_name = self.find_model_in_query(query)
            if not model_name:
                return "Какая модель должна сделать предсказание? Укажите имя модели."
            
            if model_name not in self.models:
                return f"Модель '{model_name}' не найдена. Сначала обучите модель."
            
            model = self.models[model_name]
            
            if hasattr(model, 'predict'):
                prediction = model.predict([numbers])
                if isinstance(prediction[0], list):
                    # Для классификации с несколькими классами
                    pred_values = prediction[0]
                    max_idx = pred_values.index(max(pred_values))
                    return f"Предсказание: класс {max_idx} с вероятностями: {pred_values}"
                else:
                    # Для регрессии или бинарной классификации
                    return f"Предсказание: {prediction[0]}"
            else:
                return "Модель не поддерживает предсказания."
                
        except Exception as e:
            return f"Ошибка при предсказании: {str(e)}"
    
    def handle_save_request(self, query: str) -> str:
        """Сохранение моделей или данных"""
        try:
            if 'модель' in query:
                # Извлечение имени модели
                match = re.search(r'модель\s+(\w+)', query)
                if match:
                    model_name = match.group(1)
                    if model_name in self.models:
                        filename = f"{model_name}_model.pkl"
                        self.models[model_name].save(filename)
                        return f"Модель '{model_name}' сохранена в файл {filename}"
                return "Укажите имя модели для сохранения."
            else:
                # Сохранение данных
                filename = "data_export.json"
                with open(filename, 'w') as f:
                    json.dump(self.data_storage, f)
                return f"Данные сохранены в файл {filename}"
        except Exception as e:
            return f"Ошибка при сохранении: {str(e)}"
    
    def handle_load_request(self, query: str) -> str:
        """Загрузка моделей или данных"""
        try:
            if 'модель' in query:
                # Поиск файла модели
                files = [f for f in os.listdir() if f.endswith('_model.pkl')]
                if files:
                    filename = files[0]
                    model_name = filename.replace('_model.pkl', '')
                    self.models[model_name] = EnhancedNeuralNetwork.load(filename)
                    return f"Модель '{model_name}' загружена из файла {filename}"
                return "Файлы моделей не найдены."
            else:
                # Загрузка данных
                if os.path.exists("data_export.json"):
                    with open("data_export.json", 'r') as f:
                        self.data_storage = json.load(f)
                    return "Данные загружены из файла data_export.json"
                return "Файл данных не найден."
        except Exception as e:
            return f"Ошибка при загрузке: {str(e)}"
    
    def handle_general_query(self, query: str) -> str:
        """Обработка общих запросов"""
        responses = {
            'привет': "Привет! Я ваш ИИ ассистент. Чем могу помочь?",
            'как дела': "У меня всё хорошо! Готов помочь вам с задачами машинного обучения.",
            'спасибо': "Пожалуйста! Обращайтесь, если понадобится ещё помощь.",
            'пока': "До свидания! Буду рад помочь вам в будущем.",
            'что ты умеешь': "Я могу обучать модели, делать предсказания, анализировать данные и многое другое. Скажите 'помощь' для списка команд.",
            'время': f"Текущее время: {datetime.now().strftime('%H:%M:%S')}",
            'дата': f"Сегодня: {datetime.now().strftime('%d.%m.%Y')}",
        }
        
        for key, response in responses.items():
            if key in query:
                return response
        
        # Математические вычисления
        if any(op in query for op in ['+', '-', '*', '/', '^']):
            try:
                # Безопасное вычисление
                expr = query.replace('x', '*').replace('^', '**')
                # Удаляем всё кроме чисел и операторов
                expr = re.sub(r'[^\d\+\-\*\/\.\(\)\s]', '', expr)
                if expr:
                    result = eval(expr)
                    return f"Результат: {result}"
            except:
                pass
        
        # Генерация данных
        if 'сгенерируй данные' in query or 'создай данные' in query:
            return self.generate_sample_data()
        
        return "Извините, я не совсем понял запрос. Попробуйте перефразировать или скажите 'помощь' для списка команд."
    
    def extract_numbers(self, text: str) -> List[float]:
        """Извлечение чисел из текста"""
        numbers = re.findall(r'[-+]?\d*\.\d+|\d+', text)
        return [float(num) for num in numbers]
    
    def find_model_in_query(self, query: str) -> str:
        """Поиск имени модели в запросе"""
        for model_name in self.models.keys():
            if model_name.lower() in query.lower():
                return model_name
        
        # Если модель не указана, вернем первую доступную
        if self.models:
            return list(self.models.keys())[0]
        
        return ""
    
    def train_neural_network(self, query: str) -> str:
        """Обучение нейронной сети"""
        # Извлечение параметров из запроса
        if 'для классификации' in query:
            layers = [10, 16, 8, 3]  # Пример для 3 классов
        elif 'для регрессии' in query:
            layers = [10, 8, 4, 1]
        else:
            layers = [10, 8, 4, 2]  # По умолчанию
        
        # Создание и обучение модели
        model_name = f"nn_model_{len(self.models)}"
        config = TrainingConfig(epochs=50, learning_rate=0.01)
        
        # Создание синтетических данных
        n_samples = 100
        n_features = layers[0]
        n_classes = layers[-1] if layers[-1] > 1 else 2
        
        X, y = self.create_sample_data(n_samples, n_features, n_classes)
        
        model = EnhancedNeuralNetwork(
            layers=layers,
            activations=[
                ActivationFunction.RELU,
                ActivationFunction.RELU,
                ActivationFunction.SOFTMAX if n_classes > 1 else ActivationFunction.SIGMOID
            ],
            config=config
        )
        
        history = model.fit(X, y, verbose=False)
        
        # Сохранение модели
        self.models[model_name] = model
        self.data_storage[model_name] = {
            'X_sample': X[:5],  # Сохраняем несколько примеров
            'y_sample': y[:5],
            'history': history
        }
        
        accuracy = history['accuracy'][-1]
        return f"Модель '{model_name}' обучена! Точность: {accuracy:.2%}\nАрхитектура: {layers}"
    
    def train_random_forest(self, query: str) -> str:
        """Обучение случайного леса (упрощенная версия)"""
        model_name = f"rf_model_{len(self.models)}"
        
        # Создание упрощенного дерева
        class SimpleTree:
            def __init__(self):
                self.threshold = random.random()
                self.feature = random.randint(0, 9)
            
            def predict(self, X):
                return [1 if x[self.feature] > self.threshold else 0 for x in X]
        
        # Создание "случайного леса" из простых деревьев
        class SimpleRandomForest:
            def __init__(self, n_trees=10):
                self.trees = [SimpleTree() for _ in range(n_trees)]
            
            def predict(self, X):
                predictions = []
                for x in X:
                    votes = [tree.predict([x])[0] for tree in self.trees]
                    prediction = 1 if sum(votes) > len(votes) / 2 else 0
                    predictions.append(prediction)
                return predictions
        
        model = SimpleRandomForest(n_trees=10)
        self.models[model_name] = model
        
        return f"Случайный лес '{model_name}' создан! (10 деревьев)"
    
    def train_decision_tree(self, query: str) -> str:
        """Обучение дерева решений"""
        model_name = f"dt_model_{len(self.models)}"
        
        class SimpleDecisionTree:
            def __init__(self):
                self.threshold = 0.5
                self.feature = 0
            
            def fit(self, X, y):
                # Простая логика: находим лучший порог для первого признака
                if X:
                    self.feature = random.randint(0, len(X[0])-1)
                    values = [x[self.feature] for x in X]
                    if values:
                        self.threshold = sum(values) / len(values)
                return self
            
            def predict(self, X):
                return [1 if x[self.feature] > self.threshold else 0 for x in X]
        
        model = SimpleDecisionTree()
        self.models[model_name] = model
        
        return f"Дерево решений '{model_name}' создано!"
    
    def train_kmeans(self, query: str) -> str:
        """Обучение K-means"""
        model_name = f"kmeans_model_{len(self.models)}"
        
        class SimpleKMeans:
            def __init__(self, n_clusters=3):
                self.n_clusters = n_clusters
                self.centroids = []
            
            def fit(self, X):
                if X and len(X) >= self.n_clusters:
                    indices = random.sample(range(len(X)), self.n_clusters)
                    self.centroids = [X[i][:] for i in indices]
                return self
            
            def predict(self, X):
                predictions = []
                for x in X:
                    if self.centroids:
                        distances = [math.sqrt(sum((x[i]-c[i])**2 for i in range(min(len(x), len(c))))) 
                                   for c in self.centroids]
                        predictions.append(distances.index(min(distances)))
                    else:
                        predictions.append(0)
                return predictions
        
        model = SimpleKMeans(n_clusters=3)
        self.models[model_name] = model
        
        return f"K-means модель '{model_name}' создана! (3 кластера)"
    
    def create_sample_data(self, n_samples: int, n_features: int, n_classes: int):
        """Создание синтетических данных"""
        X = []
        y = []
        
        for _ in range(n_samples):
            sample = [random.uniform(-1, 1) for _ in range(n_features)]
            X.append(sample)
            
            if n_classes > 1:
                # Многоклассовая классификация
                if sum(sample[:3]) > 0.5:
                    class_idx = 0
                elif sum(sample[3:6]) < -0.5:
                    class_idx = 1
                else:
                    class_idx = 2 if n_classes > 2 else 1
                
                one_hot = [0] * n_classes
                one_hot[class_idx % n_classes] = 1
                y.append(one_hot)
            else:
                # Регрессия
                y.append([sum(sample) + random.gauss(0, 0.1)])
        
        return X, y
    
    def generate_sample_data(self) -> str:
        """Генерация примеров данных"""
        datasets = {
            'iris': "Ирисы Фишера: 4 признака, 3 класса (setosa, versicolor, virginica)",
            'mnist': "Цифры MNIST: 784 признака (28x28), 10 классов (0-9)",
            'titanic': "Данные Титаника: возраст, пол, класс билета...",
            'boston': "Бостонское жилье: 13 признаков, цена недвижимости",
            'xor': "XOR проблема: 2 входа, 1 выход (0 или 1)"
        }
        
        result = "Примеры данных для обучения:\n"
        for name, desc in datasets.items():
            result += f"• {name}: {desc}\n"
        
        result += "\nСкажите 'обучи модель на XOR' или 'создай нейросеть для классификации'"
        return result
    
    def show_help(self) -> str:
        """Показать справку по командам"""
        help_text = """
🎯 ДОСТУПНЫЕ КОМАНДЫ ИИ-АССИСТЕНТА:

🤖 ОБУЧЕНИЕ МОДЕЛЕЙ:
• "Обучи нейросеть для классификации"
• "Создай случайный лес"
• "Обучи дерево решений"
• "Сделай кластеризацию K-means"

📊 ПРЕДСКАЗАНИЯ:
• "Предскажи по модели [имя] данные: 1, 2, 3"
• "Классифицируй: 5.1, 3.5, 1.4, 0.2"
• "Сделай прогноз для [числа]"

💾 СОХРАНЕНИЕ/ЗАГРУЗКА:
• "Сохрани модель как model1"
• "Загрузи последнюю модель"
• "Экспортируй данные"

📈 АНАЛИЗ ДАННЫХ:
• "Проанализируй данные"
• "Покажи статистику"
• "Сгенерируй пример данных"

🛠 ДРУГИЕ КОМАНДЫ:
• "Помощь" - показать это сообщение
• "Статус" - информация о моделях
• "Пример" - запустить демо
• "Очисти всё" - удалить все данные

📝 ПРИМЕРЫ ЗАПРОСОВ:
• "Обучи нейросеть на 100 примеров"
• "Предскажи с помощью модели nn_model_0: 0.5, -0.2, 0.8"
• "Сохрани все модели"
• "Покажи что ты умеешь"
"""
        return help_text
    
    def run_demo(self) -> str:
        """Запуск демонстрации"""
        demo_steps = [
            "1. Создаю нейросеть для классификации...",
            "2. Обучаю на синтетических данных...",
            "3. Делаю предсказание...",
            "4. Сохраняю модель..."
        ]
        
        result = "🚀 ЗАПУСК ДЕМОНСТРАЦИИ:\n\n"
        for step in demo_steps:
            result += step + "\n"
            time.sleep(0.5)
        
        # Демо обучение
        model_name = f"demo_model_{len(self.models)}"
        config = TrainingConfig(epochs=20, learning_rate=0.05)
        
        X, y = self.create_sample_data(50, 5, 3)
        
        model = EnhancedNeuralNetwork(
            layers=[5, 8, 3],
            activations=[ActivationFunction.RELU, ActivationFunction.SOFTMAX],
            config=config
        )
        
        history = model.fit(X, y, verbose=False)
        self.models[model_name] = model
        
        # Демо предсказание
        test_sample = [random.uniform(-1, 1) for _ in range(5)]
        prediction = model.predict(test_sample)
        pred_class = prediction.index(max(prediction))
        
        result += f"\n✅ ДЕМО ЗАВЕРШЕНО!\n"
        result += f"Модель: {model_name}\n"
        result += f"Тестовый образец: {test_sample[:3]}...\n"
        result += f"Предсказание: класс {pred_class}\n"
        result += f"Вероятности: {[f'{p:.2f}' for p in prediction]}\n"
        
        return result
    
    def show_status(self) -> str:
        """Показать статус системы"""
        status = "📊 СТАТУС СИСТЕМЫ:\n\n"
        
        # Модели
        if self.models:
            status += f"🤖 Обучено моделей: {len(self.models)}\n"
            for name, model in self.models.items():
                status += f"  • {name}: {type(model).__name__}\n"
        else:
            status += "🤖 Моделей пока нет\n"
        
        # Данные
        if self.data_storage:
            status += f"\n📁 Хранимых наборов данных: {len(self.data_storage)}\n"
        
        # История
        if self.history:
            status += f"\n📝 Последние запросы: {min(3, len(self.history))}\n"
            for timestamp, query in self.history[-3:]:
                time_str = timestamp.strftime("%H:%M")
                status += f"  [{time_str}] {query[:30]}...\n"
        
        # Контекст
        if self.context:
            status += f"\n🎭 Контекст: {len(self.context)} переменных\n"
        
        status += f"\n⏰ Время работы: {len(self.history)} запросов обработано"
        
        return status
    
    def clear_data(self, query: str) -> str:
        """Очистка данных"""
        if 'всё' in query or 'all' in query:
            self.models.clear()
            self.data_storage.clear()
            self.context.clear()
            return "✅ Все данные очищены!"
        elif 'модели' in query:
            count = len(self.models)
            self.models.clear()
            return f"✅ Удалено {count} моделей"
        elif 'данные' in query:
            count = len(self.data_storage)
            self.data_storage.clear()
            return f"✅ Удалено {count} наборов данных"
        else:
            return "Что именно очистить? Укажите: 'модели', 'данные' или 'всё'"
    
    def analyze_data(self, query: str) -> str:
        """Анализ данных"""
        if not self.data_storage:
            return "Нет данных для анализа. Сначала создайте или загрузите данные."
        
        analysis = "📈 АНАЛИЗ ДАННЫХ:\n\n"
        
        for name, data in self.data_storage.items():
            analysis += f"📁 {name}:\n"
            
            if 'X_sample' in data and data['X_sample']:
                X = data['X_sample']
                n_samples = len(X)
                n_features = len(X[0]) if X else 0
                
                analysis += f"  • Образцов: {n_samples}\n"
                analysis += f"  • Признаков: {n_features}\n"
                
                if n_samples > 0 and n_features > 0:
                    # Средние значения
                    means = []
                    for i in range(min(3, n_features)):  # Первые 3 признака
                        col_vals = [x[i] for x in X if i < len(x)]
                        if col_vals:
                            means.append(f"{sum(col_vals)/len(col_vals):.2f}")
                    
                    if means:
                        analysis += f"  • Средние значения: {', '.join(means)}\n"
            
            if 'history' in data and data['history']:
                hist = data['history']
                if 'accuracy' in hist and hist['accuracy']:
                    last_acc = hist['accuracy'][-1]
                    analysis += f"  • Точность модели: {last_acc:.2%}\n"
            
            analysis += "\n"
        
        analysis += "💡 Совет: используйте 'обучи модель' для улучшения результатов"
        return analysis

# ========== УЛУЧШЕННЫЙ ИИ АССИСТЕНТ ==========

class EnhancedAIAssistant(AIAssistantCore):
    def __init__(self):
        super().__init__()
        self.sentiment_analyzer = self.SentimentAnalyzer()
        self.recommender = self.RecommenderSystem()
        self.translator = self.Translator()
        self.code_generator = self.CodeGenerator()
        
    class SentimentAnalyzer:
        """Анализатор настроения текста"""
        def __init__(self):
            self.positive_words = {"хорошо", "отлично", "прекрасно", "замечательно", "супер", "класс", "люблю", "нравится", "удобно", "легко", "понятно"}
            self.negative_words = {"плохо", "ужасно", "отвратительно", "ненавижу", "неудобно", "сложно", "непонятно", "раздражает", "ошибка", "сломалось"}
            
        def analyze(self, text):
            words = set(text.lower().split())
            positive_count = len(words & self.positive_words)
            negative_count = len(words & self.negative_words)
            
            if positive_count > negative_count:
                return "positive", positive_count/(positive_count+negative_count+0.001)
            elif negative_count > positive_count:
                return "negative", negative_count/(positive_count+negative_count+0.001)
            else:
                return "neutral", 0.5
                
    class RecommenderSystem:
        """Система рекомендаций"""
        def __init__(self):
            self.user_preferences = {}
            self.recommendation_history = []
            
        def get_recommendation(self, user_id, category="general"):
            recommendations = {
                "general": ["Попробуйте функцию голосового поиска", "Настройте внешний вид под себя", 
                           "Используйте быстрые команды для экономии времени"],
                "ai": ["Обучите нейросеть для анализа данных", "Попробуйте сделать прогноз", 
                      "Экспортируйте результаты в файл"],
                "media": ["Настройте радиостанции", "Создайте плейлист", "Используйте голосовой поиск видео"],
                "tools": ["Воспользуйтесь калькулятором", "Попробуйте блокнот", "Настройте автоматизацию"]
            }
            return random.choice(recommendations.get(category, recommendations["general"]))
            
    class Translator:
        """Простой переводчик"""
        def __init__(self):
            self.dictionary = {
                "hello": "привет",
                "thank you": "спасибо",
                "goodbye": "до свидания",
                "how are you": "как дела",
                "i need help": "мне нужна помощь",
                "search": "поиск",
                "weather": "погода",
                "time": "время"
            }
            
        def translate(self, text, target_lang="ru"):
            # Простой перевод для демонстрации
            text_lower = text.lower()
            for eng, rus in self.dictionary.items():
                if eng in text_lower:
                    return text_lower.replace(eng, rus)
            return text
            
    class CodeGenerator:
        """Генератор кода"""
        def __init__(self):
            self.templates = {
                "python_function": "def {function_name}({params}):\n    \"\"\"{docstring}\"\"\"\n    {body}\n    return {return_value}",
                "html_page": "<!DOCTYPE html>\n<html>\n<head>\n    <title>{title}</title>\n</head>\n<body>\n    <h1>{heading}</h1>\n    {content}\n</body>\n</html>",
                "sql_query": "SELECT {columns}\nFROM {table}\nWHERE {conditions};"
            }
            
        def generate(self, code_type, **kwargs):
            template = self.templates.get(code_type, "")
            return template.format(**kwargs)
    
    def enhanced_process_query(self, query: str) -> str:
        """Улучшенная обработка запросов"""
        # Анализ настроения
        sentiment, score = self.sentiment_analyzer.analyze(query)
        
        # Добавляем дополнительные возможности
        if any(word in query.lower() for word in ['анализ настроения', 'настроение', 'эмоции']):
            return f"Настроение текста: {sentiment} (уверенность: {score:.2%})"
        
        elif any(word in query.lower() for word in ['рекомендация', 'совет', 'посоветуй']):
            category = "general"
            if 'ии' in query.lower():
                category = "ai"
            elif 'медиа' in query.lower():
                category = "media"
            elif 'инструмент' in query.lower():
                category = "tools"
            return f"Рекомендация: {self.recommender.get_recommendation('user', category)}"
        
        elif any(word in query.lower() for word in ['переведи', 'translation', 'translat']):
            text = query.lower().replace('переведи', '').replace('translation', '').replace('translat', '').strip()
            if text:
                translated = self.translator.translate(text)
                return f"Перевод: {translated}"
        
        elif any(word in query.lower() for word in ['сгенерируй код', 'код', 'программу']):
            return self.generate_code_from_query(query)
        
        # Вызов родительской обработки
        response = super().process_query(query)
        
        # Добавляем эмоциональную окраску
        if sentiment == "positive":
            return f"😊 Спасибо за позитивный запрос! {response}"
        elif sentiment == "negative":
            return f"😔 Понимаю ваше разочарование. {response}"
        else:
            return response
    
    def generate_code_from_query(self, query):
        """Генерация кода на основе запроса"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['функция', 'function']):
            return self.code_generator.generate(
                "python_function",
                function_name="example_function",
                params="param1, param2",
                docstring="Пример функции",
                body="# Ваш код здесь",
                return_value="result"
            )
        
        elif any(word in query_lower for word in ['html', 'страница', 'веб']):
            return self.code_generator.generate(
                "html_page",
                title="Пример страницы",
                heading="Заголовок",
                content="<p>Содержимое страницы</p>"
            )
        
        elif any(word in query_lower for word in ['sql', 'запрос', 'база данных']):
            return self.code_generator.generate(
                "sql_query",
                columns="*",
                table="users",
                conditions="age > 18"
            )
        
        return "Пример кода Python:\n\ndef hello_world():\n    print('Hello, World!')\n\nhello_world()"

# ========== ГРАФИЧЕСКИЙ ИНТЕРФЕЙС ==========

class ModernButton(tk.Canvas):
    """Современная кнопка с градиентами и эффектами"""
    
    def __init__(self, parent, text="", command=None, width=120, height=40, 
                 bg_color="#3498db", hover_color="#2980b9", text_color="white",
                 radius=10, font_size=11, icon=None):
        super().__init__(parent, width=width, height=height, 
                        highlightthickness=0, bg=parent.cget("bg"))
        self.parent = parent
        self.text = text
        self.command = command
        self.width = width
        self.height = height
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.text_color = text_color
        self.radius = radius
        self.font_size = font_size
        self.icon = icon
        self.is_hovered = False
        self.is_pressed = False
        
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.bind("<Button-1>", self.on_press)
        self.bind("<ButtonRelease-1>", self.on_release)
        
        self.draw_button()
    
    def draw_button(self):
        self.delete("all")
        
        # Цвет фона
        color = self.hover_color if self.is_hovered else self.bg_color
        
        # Создаем градиентный фон
        for i in range(self.height):
            ratio = i / self.height
            r = int(int(color[1:3], 16) * (1 - ratio * 0.3))
            g = int(int(color[3:5], 16) * (1 - ratio * 0.3))
            b = int(int(color[5:7], 16) * (1 - ratio * 0.3))
            grad_color = f'#{r:02x}{g:02x}{b:02x}'
            
            if self.radius > 0:
                # Для закругленных углов
                if i < self.radius or i > self.height - self.radius:
                    continue
                self.create_line(0, i, self.width, i, fill=grad_color, width=1)
            else:
                self.create_line(0, i, self.width, i, fill=grad_color, width=1)
        
        # Основной прямоугольник
        if self.radius > 0:
            self.create_rounded_rect(0, 0, self.width-1, self.height-1, 
                                    self.radius, fill=color, outline="")
        else:
            self.create_rectangle(0, 0, self.width-1, self.height-1, 
                                 fill=color, outline="")
        
        # Добавляем иконку если есть
        text_x = self.width // 2
        if self.icon:
            icon_text = self.icon + " "
            self.create_text(text_x - 10, self.height//2, 
                           text=icon_text, fill=self.text_color,
                           font=("Segoe UI Emoji", self.font_size), anchor="e")
            text_x += 15
        
        # Текст кнопки
        self.create_text(text_x, self.height//2, 
                        text=self.text, fill=self.text_color,
                        font=("Segoe UI", self.font_size, "bold"),
                        anchor="center")
        
        # Эффект нажатия
        if self.is_pressed:
            press_effect = "#ffffff40"
            if self.radius > 0:
                self.create_rounded_rect(0, 0, self.width-1, self.height-1, 
                                        self.radius, fill=press_effect, outline="")
            else:
                self.create_rectangle(0, 0, self.width-1, self.height-1, 
                                     fill=press_effect, outline="")
    
    def create_rounded_rect(self, x1, y1, x2, y2, radius, **kwargs):
        """Создание прямоугольника с закругленными углами"""
        points = [
            x1 + radius, y1,
            x2 - radius, y1,
            x2, y1,
            x2, y1 + radius,
            x2, y2 - radius,
            x2, y2,
            x2 - radius, y2,
            x1 + radius, y2,
            x1, y2,
            x1, y2 - radius,
            x1, y1 + radius,
            x1, y1
        ]
        return self.create_polygon(points, smooth=True, **kwargs)
    
    def on_enter(self, event):
        self.is_hovered = True
        self.draw_button()
    
    def on_leave(self, event):
        self.is_hovered = False
        self.is_pressed = False
        self.draw_button()
    
    def on_press(self, event):
        self.is_pressed = True
        self.draw_button()
    
    def on_release(self, event):
        self.is_pressed = False
        self.draw_button()
        if self.command:
            self.command()

class TextAnimation:
    """Класс для показа анимированных текстовых переходов"""
    
    def __init__(self, root):
        self.root = root
        self.animation_window = None
        self.playing = False
        
    def show_transition(self, title="Переход", duration=3):
        """Показать текстовый переход с современной анимацией"""
        try:
            # Создаем окно для анимации
            self.animation_window = tk.Toplevel(self.root)
            self.animation_window.title(title)
            self.animation_window.geometry("800x600")
            self.animation_window.configure(bg="#0f172a")
            self.animation_window.overrideredirect(True)  # Без рамки
            
            # Центрируем окно
            self.center_window(self.animation_window)
            
            # Canvas для анимации
            self.canvas = tk.Canvas(self.animation_window, bg="#0f172a", highlightthickness=0)
            self.canvas.pack(fill=tk.BOTH, expand=True)
            
            # Частицы для фона
            self.particles = []
            for _ in range(50):
                x = random.randint(0, 800)
                y = random.randint(0, 600)
                size = random.randint(1, 3)
                speed = random.uniform(0.5, 2)
                color = random.choice(['#3b82f6', '#8b5cf6', '#10b981', '#f59e0b'])
                particle = self.canvas.create_oval(x, y, x+size, y+size, fill=color, outline="")
                self.particles.append((particle, speed))
            
            # Анимированный заголовок
            self.title_text = self.canvas.create_text(
                400, 200,
                text="⚛️",
                fill="#60a5fa",
                font=('Segoe UI', 120, 'bold'),
                state='hidden'
            )
            
            # Подзаголовок
            self.subtitle_text = self.canvas.create_text(
                400, 300,
                text=title,
                fill="#ffffff",
                font=('Segoe UI', 36, 'bold'),
                state='hidden'
            )
            
            # Прогресс бар
            self.progress_bg = self.canvas.create_rectangle(
                200, 450, 600, 470,
                fill="#1e293b",
                outline="",
                state='hidden'
            )
            
            self.progress_fill = self.canvas.create_rectangle(
                200, 450, 200, 470,
                fill="#3b82f6",
                outline="",
                state='hidden'
            )
            
            # Запускаем анимации
            self.animate_particles()
            self.animate_title()
            
            # Закрываем окно через указанное время
            self.animation_window.after(duration * 1000, self.close_transition)
            
            self.playing = True
            
        except Exception as e:
            print(f"Ошибка при показе анимации: {e}")
            self.close_transition()
    
    def center_window(self, window):
        """Центрирование окна на экране"""
        window.update_idletasks()
        width = window.winfo_width()
        height = window.winfo_height()
        x = (window.winfo_screenwidth() // 2) - (width // 2)
        y = (window.winfo_screenheight() // 2) - (height // 2)
        window.geometry(f'{width}x{height}+{x}+{y}')
    
    def animate_particles(self):
        """Анимация частиц на фоне"""
        if not self.playing or not self.animation_window:
            return
            
        for particle_id, speed in self.particles:
            try:
                coords = self.canvas.coords(particle_id)
                if coords[1] > 600:
                    self.canvas.move(particle_id, 0, -650)
                else:
                    self.canvas.move(particle_id, 0, speed)
            except:
                pass
        
        if self.playing:
            self.animation_window.after(30, self.animate_particles)
    
    def animate_title(self):
        """Анимация появления заголовка"""
        if not self.playing or not self.animation_window:
            return
            
        try:
            # Показываем элементы
            self.canvas.itemconfig(self.title_text, state='normal')
            self.animation_window.after(500, lambda: self.canvas.itemconfig(self.subtitle_text, state='normal'))
            self.animation_window.after(1000, lambda: self.canvas.itemconfig(self.progress_bg, state='normal'))
            self.animation_window.after(1000, lambda: self.canvas.itemconfig(self.progress_fill, state='normal'))
            
            # Анимация прогресс бара
            self.animate_progress(200, 0)
            
            # Анимация пульсации эмодзи
            self.pulse_emoji(0)
            
        except:
            pass
    
    def animate_progress(self, x, step):
        """Анимация прогресс бара"""
        if not self.playing or not self.animation_window:
            return
            
        if x < 600:
            self.canvas.coords(self.progress_fill, 200, 450, x, 470)
            self.animation_window.after(20, lambda: self.animate_progress(x + 8, step + 1))
    
    def pulse_emoji(self, step):
        """Пульсация эмодзи"""
        if not self.playing or not self.animation_window:
            return
            
        try:
            size = 120 + 10 * math.sin(step * 0.2)
            self.canvas.itemconfig(self.title_text, font=('Segoe UI', int(size), 'bold'))
            
            # Меняем цвет
            colors = ['#60a5fa', '#8b5cf6', '#10b981', '#f59e0b']
            color = colors[step % len(colors)]
            self.canvas.itemconfig(self.title_text, fill=color)
            
            if self.playing:
                self.animation_window.after(100, lambda: self.pulse_emoji(step + 1))
        except:
            pass
    
    def close_transition(self):
        """Закрыть анимацию"""
        self.playing = False
        if self.animation_window and self.animation_window.winfo_exists():
            try:
                self.animation_window.destroy()
            except:
                pass
        self.animation_window = None

class ParticleSystem:
    """Система частиц для фона"""
    def __init__(self, canvas, width, height, particle_count=100):
        self.canvas = canvas
        self.width = width
        self.height = height
        self.particles = []
        self.colors = ['#3b82f6', '#8b5cf6', '#10b981', '#f59e0b', '#ef4444']
        
        for _ in range(particle_count):
            self.create_particle()
    
    def create_particle(self):
        x = random.randint(0, self.width)
        y = random.randint(0, self.height)
        size = random.randint(1, 4)
        speed = random.uniform(0.2, 1.5)
        color = random.choice(self.colors)
        direction = random.choice([-1, 1])
        
        particle = self.canvas.create_oval(
            x, y, x + size, y + size,
            fill=color, outline="", tags="particle"
        )
        
        self.particles.append({
            'id': particle,
            'x': x, 'y': y,
            'size': size,
            'speed': speed,
            'direction': direction
        })
    
    def update(self):
        for particle in self.particles:
            # Движение
            particle['x'] += particle['speed'] * particle['direction']
            particle['y'] += particle['speed'] * 0.5
            
            # Отскок от границ
            if particle['x'] > self.width or particle['x'] < 0:
                particle['direction'] *= -1
            
            if particle['y'] > self.height:
                particle['y'] = -particle['size']
            
            # Обновление позиции
            self.canvas.coords(
                particle['id'],
                particle['x'], particle['y'],
                particle['x'] + particle['size'], 
                particle['y'] + particle['size']
            )

class TypewriterLabel:
    """Текст с эффектом печатной машинки"""
    def __init__(self, parent, text, **kwargs):
        self.parent = parent
        self.full_text = text
        self.current_text = ""
        self.index = 0
        self.speed = kwargs.pop('speed', 50)
        self.on_complete = kwargs.pop('on_complete', None)
        
        self.label = tk.Label(parent, **kwargs)
        self.label.pack()
        
    def start(self):
        self.type_next_char()
    
    def type_next_char(self):
        if self.index < len(self.full_text):
            self.current_text += self.full_text[self.index]
            self.label.config(text=self.current_text)
            self.index += 1
            self.parent.after(self.speed, self.type_next_char)
        elif self.on_complete:
            self.on_complete()

# ========== ОСНОВНОЙ КЛАСС ПРИЛОЖЕНИЯ ==========

class EnhancedVoiceAssistantGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Атом v4.0 PRO")
        self.root.geometry("1200x800")
        self.root.configure(bg="#0f172a")
        
        # Инициализация улучшенного ИИ-ассистента
        self.ai_assistant = EnhancedAIAssistant()
        
        # Инициализация методов голосового ввода
        self.voice_methods = VOICE_METHODS
        self.voice_input_method = VOICE_INPUT_METHOD
        
        # Устанавливаем иконку окна
        try:
            self.root.iconbitmap('atom_icon.ico')
        except:
            pass
        
        # Устанавливаем минимальный размер окна
        self.root.minsize(1000, 700)
        
        # Инициализация текстовой анимации
        self.text_anim = TextAnimation(root)
        
        # Флаг для контроля работы фоновых задач
        self.running = True
        self.after_ids = []  # Список ID задач after
        
        # Флаги для активации по фразе
        self.voice_wake_word = "атом"
        self.wake_word_detection = False  # Флаг обнаружения ключевого слова
        self.background_listening = False  # Фоновая активация
        self.last_wake_time = 0  # Время последней активации (для предотвращения двойных срабатываний)
        self.activation_phrases = ["атом", "ато", "том", "ата", "атоме", "атома", "адон", "атон"]  # Варианты ключевого слова
        
        # Инициализация голосового движка если доступен
        self.speech_engine = None
        self.recognizer = None
        self.speech_queue = queue.Queue()  # Очередь для синтеза речи
        self.speech_thread = None
        self.speech_processing = False
        
        # Инициализация голосовых движков в зависимости от доступности
        if SPEECH_AVAILABLE:
            try:
                self.speech_engine = pyttsx3.init()
                # Настройки голоса
                voices = self.speech_engine.getProperty('voices')
                # Пытаемся найти русский голос
                for voice in voices:
                    if 'russian' in voice.name.lower() or 'russian' in voice.id.lower():
                        self.speech_engine.setProperty('voice', voice.id)
                        break
                # Скорость речи
                self.speech_engine.setProperty('rate', 150)
                # Громкость
                self.speech_engine.setProperty('volume', 0.9)
                
                self.recognizer = sr.Recognizer()
                # Настройки для лучшего распознавания
                self.recognizer.energy_threshold = 200
                self.recognizer.dynamic_energy_threshold = True
                self.recognizer.dynamic_energy_adjustment_damping = 0.15
                self.recognizer.dynamic_energy_ratio = 1.5
                self.recognizer.pause_threshold = 0.8
                
                # Запускаем поток обработки речи
                self.start_speech_processor()
                
            except Exception as e:
                print(f"Ошибка инициализации голосового движка: {e}")
        elif self.voice_input_method == 'windows_sapi':
            # Пытаемся использовать Windows SAPI
            try:
                import win32com.client
                self.speech_engine_win = win32com.client.Dispatch("SAPI.SpVoice")
                print("Используется Windows SAPI для синтеза речи")
            except Exception as e:
                print(f"Не удалось инициализировать Windows SAPI: {e}")
        
        # Инициализация настроек ДО их использования
        self.settings = {}
        
        # Очередь для сообщений
        self.message_queue = queue.Queue()
        
        # Флаги
        self.demo_mode = None  # Будет определено при выборе
        self.listening = False
        self.video_playing = False
        self.logged_in = False  # Флаг авторизации
        self.current_user = None  # Текущий пользователь
        self.voice_assistant_active = False  # Флаг активности голосового помощника
        
        # Новые атрибуты для автоматизации
        self.automation_tasks = []
        self.screenshots = []
        self.clipboard_history = []
        self.gesture_recognition = False
        
        # Настройки
        self.settings_file = "atom_settings.json"
        self.users_file = "atom_users.json"
        self.default_settings = {
            "search_engine": "https://www.google.com/search?q=",
            "search_engines": {
                "Google": "https://www.google.com/search?q=",
                "Яндекс": "https://yandex.ru/search/?text=",
                "DuckDuckGo": "https://duckduckgo.com/?q=",
                "Bing": "https://www.bing.com/search?q=",
                "DeepSeek": "https://www.deepseek.com/"
            },
            "social_networks": {
                "ВКонтакте": "https://vk.com",
                "Одноклассники": "https://ok.ru",
                "Telegram": "https://web.telegram.org",
                "WhatsApp Web": "https://web.whatsapp.com",
                "Discord": "https://discord.com/app",
                "Twitter": "https://twitter.com",
                "Facebook": "https://facebook.com",
                "Instagram": "https://instagram.com",
                "YouTube": "https://youtube.com",
                "Twitch": "https://twitch.tv",
                "DeepSeek AI": "https://chat.deepseek.com/"
            },
            "theme": "dark",
            "theme_color": "#3b82f6",
            "auto_start": True,
            "notifications": True,
            "demo_mode": True,
            "history_limit": 100,
            "weather_city": "Москва",
            "video_player": "browser",
            "voice_enabled": True,  # Голосовой помощник включен
            "voice_feedback": True,  # Озвучка всех действий
            "voice_language": "ru-RU",  # Язык распознавания
            "voice_speed": 150,  # Скорость речи
            "voice_volume": 0.9,  # Громкость
            "default_browser": "default",  # Браузер по умолчанию
            "browsers": {
                "По умолчанию": "default",
                "Chrome": "chrome",
                "Firefox": "firefox",
                "Edge": "msedge",
                "Opera": "opera"
            },
            "font_size": "normal",
            "animations": True,
            "wake_word": "атом",  # Ключевое слово для активации
            "wake_word_sensitivity": 0.3,
            "wake_word_variants": ["атом", "ато", "том", "ата", "атоме", "атома", "адон", "атон"]
        }
        
        # Инициализируем настройки значениями по умолчанию
        self.settings = self.default_settings.copy()
        
        # Пользователи
        self.users = {}
        self.load_users()
        
        # Загружаем пользовательские настройки
        self.load_settings()
        
        # Обновляем ключевое слово из настроек
        self.voice_wake_word = self.settings.get("wake_word", "атом")
        self.wake_sensitivity = self.settings.get("wake_word_sensitivity", 0.3)
        self.activation_phrases = self.settings.get("wake_word_variants", ["атом", "ато", "том", "ата", "атоме", "атома", "адон", "атон"])
        
        # Сначала показываем окно авторизации
        self.show_auth_window()
    
    # ========== НОВЫЕ МЕТОДЫ ДЛЯ ГОЛОСОВОГО ВВОДА БЕЗ БИБЛИОТЕК ==========
    
    def listen_without_speech_recognition(self, timeout=5):
        """
        Альтернативный метод распознавания речи без speech_recognition
        Использует доступные системные возможности
        """
        if not VOICE_INPUT_AVAILABLE:
            return None, 0.0
        
        try:
            if self.voice_input_method == 'speech_recognition' and SPEECH_AVAILABLE:
                # Используем оригинальный метод если speech_recognition доступен
                return self.listen_with_speech_recognition(timeout)
            elif self.voice_input_method == 'windows_sapi':
                return self.listen_with_windows_sapi(timeout)
            else:
                return self.listen_with_simple_dialog(timeout)
        except Exception as e:
            print(f"Ошибка при распознавании речи: {e}")
            return None, 0.0
    
    def listen_with_speech_recognition(self, timeout):
        """Использование speech_recognition если доступен"""
        try:
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=4)
                
            text = self.recognizer.recognize_google(audio, language='ru-RU')
            return text, 0.8
        except sr.WaitTimeoutError:
            return None, 0.0
        except sr.UnknownValueError:
            return None, 0.0
        except Exception as e:
            print(f"Ошибка speech_recognition: {e}")
            return None, 0.0
    
    def listen_with_windows_sapi(self, timeout):
        """
        Распознавание речи с помощью Windows Speech API
        Требует настройки распознавания речи в Windows
        """
        try:
            # Для Windows SAPI нужна настройка системы
            # Возвращаем упрощенный диалог
            return self.listen_with_simple_dialog(timeout)
        except Exception as e:
            print(f"Ошибка Windows SAPI: {e}")
            return self.listen_with_simple_dialog(timeout)
    
    def listen_with_simple_dialog(self, timeout):
        """
        Простой fallback метод - показывает диалог для ручного ввода
        """
        try:
            dialog = tk.Toplevel(self.root)
            dialog.title("Голосовой ввод")
            dialog.geometry("400x250")
            dialog.configure(bg=self.colors['bg'])
            dialog.resizable(False, False)
            dialog.transient(self.root)
            dialog.grab_set()
            
            # Центрируем диалог
            dialog.update_idletasks()
            x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (400 // 2)
            y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (250 // 2)
            dialog.geometry(f"400x250+{x}+{y}")
            
            # Заголовок
            label = tk.Label(dialog, text="🗣️ Голосовой ввод", 
                           bg=self.colors['bg'], fg=self.colors['primary_light'],
                           font=('Segoe UI', 16, 'bold'))
            label.pack(pady=20)
            
            # Инструкция
            instruction = tk.Label(dialog, 
                                 text="Произнесите команду, затем введите её ниже:",
                                 bg=self.colors['bg'], fg=self.colors['text'],
                                 font=('Segoe UI', 11))
            instruction.pack(pady=10)
            
            # Поле ввода
            result_var = tk.StringVar()
            entry = tk.Entry(dialog, textvariable=result_var,
                           font=('Segoe UI', 12), width=40,
                           bg=self.colors['bg_lighter'], fg=self.colors['text'])
            entry.pack(pady=10, padx=20)
            entry.focus_set()
            
            result_text = None
            confidence = 0.7
            
            def on_ok():
                nonlocal result_text
                result_text = result_var.get().strip()
                dialog.destroy()
            
            def on_cancel():
                nonlocal result_text
                result_text = None
                dialog.destroy()
            
            # Кнопки
            button_frame = tk.Frame(dialog, bg=self.colors['bg'])
            button_frame.pack(pady=20)
            
            ok_btn = tk.Button(button_frame, text="✅ Принять", 
                             bg=self.colors['success'], fg='white',
                             font=('Segoe UI', 10, 'bold'), 
                             padx=20, pady=8, command=on_ok)
            ok_btn.pack(side=tk.LEFT, padx=10)
            
            cancel_btn = tk.Button(button_frame, text="❌ Отмена",
                                 bg=self.colors['danger'], fg='white',
                                 font=('Segoe UI', 10),
                                 padx=20, pady=8, command=on_cancel)
            cancel_btn.pack(side=tk.LEFT, padx=10)
            
            # Обработка Enter и Escape
            entry.bind('<Return>', lambda e: on_ok())
            dialog.bind('<Escape>', lambda e: on_cancel())
            
            # Устанавливаем таймаут
            def close_after_timeout():
                if dialog.winfo_exists():
                    on_cancel()
            
            dialog.after(timeout * 1000, close_after_timeout)
            
            # Ждем закрытия диалога
            self.root.wait_window(dialog)
            
            return result_text, confidence if result_text else 0.0
            
        except Exception as e:
            print(f"Ошибка simple_dialog метода: {e}")
            return None, 0.0
    
    def improved_background_listening_no_libs(self):
        """
        Улучшенное фоновое прослушивание без внешних библиотек
        """
        if not self.background_listening or not self.running:
            return
        
        def simple_listener():
            print("Фоновое прослушивание запущено (упрощенная версия)")
            
            while self.background_listening and self.running:
                try:
                    # Эмулируем прослушивание с случайными срабатываниями
                    time.sleep(3)  # Проверяем каждые 3 секунды
                    
                    # Для демонстрации - эмуляция срабатывания
                    # В реальном приложении здесь была бы работа с микрофоном
                    if random.random() < 0.05:  # 5% шанс срабатывания для демо
                        print("✓ Демо: Эмуляция обнаружения ключевого слова")
                        self.wake_word_detected()
                        
                except Exception as e:
                    print(f"Ошибка в фоновом прослушивании: {e}")
                    time.sleep(1)
        
        if not hasattr(self, 'background_listener_thread') or not self.background_listener_thread.is_alive():
            self.background_listener_thread = threading.Thread(target=simple_listener, daemon=True)
            self.background_listener_thread.start()
    
    def voice_search_simple(self):
        """Упрощенный голосовой поиск"""
        self.speak("Скажите ваш поисковый запрос")
        
        text, confidence = self.listen_without_speech_recognition(10)
        
        if text and confidence > 0.5:
            self.search_query.set(text)
            self.perform_search()
            self.message_queue.put(f"Голосовой поиск: {text}")
            return True
        else:
            self.speak("Не удалось распознать запрос")
            self.message_queue.put("Не удалось распознать голосовой запрос")
            return False
    
    def process_voice_command_simple(self, command):
        """
        Упрощенная обработка голосовых команд
        """
        command_lower = command.lower()
        
        # Проверяем новые команды для автоматизации
        if "добавь задачу" in command_lower:
            task = command_lower.replace("добавь задачу", "").strip()
            if task:
                self.automation_tasks.append(task)
                self.message_queue.put(f"Задача добавлена: {task}")
                self.speak(f"Задача '{task}' добавлена в список автоматизации")
                return True
        
        elif "покажи задачи" in command_lower or "список задач" in command_lower:
            if self.automation_tasks:
                tasks_text = ", ".join(self.automation_tasks[:5])
                self.speak(f"У вас {len(self.automation_tasks)} задач: {tasks_text}")
            else:
                self.speak("Список задач пуст")
            return True
        
        elif "выполни задачи" in command_lower or "запусти задачи" in command_lower:
            self.run_automation_tasks()
            return True
        
        # Проверяем команды для редактора кода
        elif "новый код" in command_lower or "чистый редактор" in command_lower:
            self.code_text.delete(1.0, tk.END)
            self.speak("Редактор кода очищен")
            return True
        
        elif "сохрани код" in command_lower:
            self.save_code()
            return True
        
        # Системные команды
        elif "скриншот" in command_lower:
            self.take_screenshot()
            return True
        
        # Стандартные команды
        command_mappings = [
            (["поиск", "найди", "найти", "ищи", "искать"], self.handle_search_command),
            (["открой", "открыть", "зайди", "зайти", "перейди", "перейти"], self.handle_open_command),
            (["погода", "погоду", "погоде", "температура", "температуру"], self.handle_weather_command),
            (["калькулятор", "посчитай", "вычисли", "считай"], self.handle_calculator_command),
            (["время", "час", "сколько времени", "который час"], self.handle_time_command),
            (["браузер", "интернет", "сеть"], self.handle_browser_command),
            (["блокнот", "заметка", "заметки", "текст"], self.handle_notepad_command),
            (["дипсик", "deepseek", "искусственный интеллект", "ии", "ай", "ai"], self.handle_deepseek_command),
            (["помощь", "справка", "что ты умеешь", "команды"], self.handle_help_command),
            (["настройки", "опции", "параметры"], self.handle_settings_command),
            (["режим", "демо", "рабочий"], self.handle_mode_command),
            (["стоп", "хватит", "выйти", "закончи", "отключись", "выключись"], self.handle_stop_command),
            (["спасибо", "благодарю", "спс", "thanks", "thank you"], self.handle_thanks_command),
            (["ии", "искусственный интеллект", "обучи", "тренируй", "создай модель", "предскажи", "прогноз", "классифицируй", "распознай"], self.handle_ai_command)
        ]
        
        for keywords, handler in command_mappings:
            for keyword in keywords:
                if keyword in command_lower:
                    print(f"✓ Найдено ключевое слово: '{keyword}'")
                    handler(command_lower, keyword)
                    return True
        
        # Если команда не распознана, делаем поиск
        question_words = ["что", "как", "где", "кто", "почему", "зачем", "когда", "сколько"]
        words = command_lower.split()
        if any(word in words[:2] for word in question_words) or len(words) <= 4:
            self.search_query.set(command)
            self.perform_search()
            return True
        
        # Открываем как сайт
        self.open_site_by_voice(command)
        return True
    
    # ========== ОБНОВЛЕННЫЕ МЕТОДЫ ДЛЯ РАБОТЫ С НОВЫМИ ФУНКЦИЯМИ ==========
    
    def start_speech_processor(self):
        """Запуск обработчика речи"""
        def speech_processor():
            while self.running:
                try:
                    text = self.speech_queue.get(timeout=0.5)
                    if text and self.speech_engine:
                        try:
                            # Останавливаем текущее воспроизведение
                            self.speech_engine.stop()
                            # Произносим текст
                            self.speech_engine.say(text)
                            self.speech_engine.runAndWait()
                        except Exception as e:
                            print(f"Ошибка синтеза речи: {e}")
                            # Пересоздаем движок при ошибке
                            try:
                                self.speech_engine = pyttsx3.init()
                                self.speech_engine.setProperty('rate', self.settings.get("voice_speed", 150))
                                self.speech_engine.setProperty('volume', self.settings.get("voice_volume", 0.9))
                            except:
                                pass
                except queue.Empty:
                    continue
                except Exception as e:
                    print(f"Ошибка в обработчике речи: {e}")
        
        if (SPEECH_AVAILABLE or self.voice_input_method == 'windows_sapi') and not self.speech_thread:
            self.speech_thread = threading.Thread(target=speech_processor, daemon=True)
            self.speech_thread.start()
    
    def speak(self, text, priority=False):
        """Произнесение текста"""
        if not self.running:
            return
        
        if not self.settings.get("voice_feedback", True) and not priority:
            return
        
        if not text or not text.strip():
            return
        
        try:
            # Если есть speech_engine (pyttsx3)
            if self.speech_engine:
                self.speech_queue.put(text.strip())
            # Иначе если есть Windows SAPI
            elif hasattr(self, 'speech_engine_win'):
                try:
                    self.speech_engine_win.Speak(text.strip(), 0)
                except:
                    print(f"Не удалось произнести текст: {text[:50]}...")
            else:
                # Выводим в консоль
                print(f"Голос: {text}")
        except Exception as e:
            print(f"Ошибка синтеза речи: {e}")
    
    def voice_search(self):
        """Голосовой поиск"""
        if SPEECH_AVAILABLE:
            # Используем оригинальный метод с speech_recognition
            self.original_voice_search()
        elif VOICE_INPUT_AVAILABLE:
            # Используем альтернативный метод
            self.voice_search_simple()
        else:
            self.speak("Голосовой поиск недоступен")
            self.message_queue.put("Голосовой поиск недоступен")
    
    def original_voice_search(self):
        """Оригинальный метод голосового поиска"""
        if not SPEECH_AVAILABLE:
            return
        
        self.speak("Скажите ваш поисковый запрос")
        
        try:
            with sr.Microphone() as source:
                self.status_label.config(text="Слушаю...", fg=self.colors['primary_light'])
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=5)
                
            query = self.recognizer.recognize_google(audio, language='ru-RU')
            self.search_query.set(query)
            self.perform_search()
            self.status_label.config(text="Поиск выполнен", fg=self.colors['success'])
            
        except sr.WaitTimeoutError:
            self.speak("Время ожидания истекло")
            self.message_queue.put("Время ожидания истекло")
            self.status_label.config(text="Готов", fg=self.colors['text_secondary'])
        except sr.UnknownValueError:
            self.speak("Не удалось распознать речь")
            self.message_queue.put("Не удалось распознать речь")
            self.status_label.config(text="Готов", fg=self.colors['text_secondary'])
        except Exception as e:
            self.speak(f"Произошла ошибка: {str(e)[:30]}")
            self.message_queue.put(f"Ошибка: {e}")
            self.status_label.config(text="Готов", fg=self.colors['text_secondary'])
    
    def start_voice_assistant(self):
        """Запуск голосового помощника"""
        if SPEECH_AVAILABLE and self.settings.get("voice_enabled", True) and not self.demo_mode:
            # Используем оригинальный метод
            self.voice_assistant_active = True
            self.root.after(1000, self.start_original_voice_assistant)
        elif VOICE_INPUT_AVAILABLE and self.settings.get("voice_enabled", True) and not self.demo_mode:
            # Используем упрощенный метод
            self.voice_assistant_active = True
            self.root.after(1000, self.start_simple_voice_assistant)
        else:
            print("Голосовой помощник недоступен")
    
    def start_original_voice_assistant(self):
        """Оригинальный запуск голосового помощника"""
        if not SPEECH_AVAILABLE:
            return
        
        self.background_listening = True
        self.speak(f"Голосовой помощник активирован. Скажите '{self.voice_wake_word}' для активации.")
        self.message_queue.put(f"Голосовой помощник активирован. Скажите '{self.voice_wake_word}' для активации.")
        self.status_label.config(text=f"🎤 Ожидание: '{self.voice_wake_word}'", fg=self.colors['primary_light'])
        
        self.start_improved_background_listening()
    
    def start_simple_voice_assistant(self):
        """Упрощенный запуск голосового помощника"""
        if not VOICE_INPUT_AVAILABLE:
            return
        
        self.background_listening = True
        self.speak(f"Упрощенный голосовой помощник активирован")
        self.message_queue.put("Упрощенный голосовой помощник активирован")
        self.status_label.config(text="🎤 Упрощенный режим", fg=self.colors['primary_light'])
        
        # Запускаем упрощенное прослушивание
        self.improved_background_listening_no_libs()
    
    def start_improved_background_listening(self):
        """Улучшенное фоновое прослушивание для активации по фразе"""
        if not self.background_listening or not self.running:
            return
        
        def background_listener():
            print(f"Фоновое прослушивание запущено. Ожидание: {self.activation_phrases}")
            
            microphone_errors = 0
            
            while self.background_listening and self.running:
                try:
                    with sr.Microphone() as source:
                        self.recognizer.energy_threshold = 200
                        self.recognizer.dynamic_energy_adjustment_damping = 0.15
                        self.recognizer.dynamic_energy_ratio = 1.5
                        self.recognizer.pause_threshold = 0.8
                        
                        if microphone_errors == 0:
                            print("Калибрую микрофон...")
                            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                            print("Микрофон откалиброван")
                        
                        print("Слушаю...")
                        audio = self.recognizer.listen(
                            source, 
                            timeout=2,
                            phrase_time_limit=1.5
                        )
                        
                        microphone_errors = 0
                        
                        try:
                            text = self.recognizer.recognize_google(
                                audio, 
                                language='ru-RU',
                                show_all=True
                            )
                            
                            print(f"Распознано: {text}")
                            
                            if text and 'alternative' in text:
                                for alternative in text['alternative']:
                                    recognized_text = alternative['transcript'].lower().strip()
                                    confidence = alternative.get('confidence', 0.2)
                                    
                                    print(f"Вариант: '{recognized_text}' (уверенность: {confidence:.2f})")
                                    
                                    for phrase in self.activation_phrases:
                                        if (phrase in recognized_text or 
                                            recognized_text in phrase or 
                                            self.is_similar(phrase, recognized_text)):
                                            
                                            if confidence >= self.wake_sensitivity:
                                                current_time = time.time()
                                                if current_time - self.last_wake_time > 2:
                                                    self.last_wake_time = current_time
                                                    print(f"✓ Распознано ключевое слово: '{phrase}' (уверенность: {confidence:.2f})")
                                                    self.wake_word_detected()
                                                    break
                                    
                        except sr.UnknownValueError:
                            pass
                        except Exception as e:
                            print(f"Ошибка при обработке распознавания: {e}")
                            
                except sr.WaitTimeoutError:
                    continue
                except Exception as e:
                    microphone_errors += 1
                    print(f"Ошибка микрофона (#{microphone_errors}): {e}")
                    
                    if microphone_errors > 3:
                        print("Много ошибок микрофона, делаю паузу...")
                        time.sleep(2)
                        microphone_errors = 0
        
        if not hasattr(self, 'background_listener_thread') or not self.background_listener_thread.is_alive():
            self.background_listener_thread = threading.Thread(target=background_listener, daemon=True)
            self.background_listener_thread.start()
    
    def wake_word_detected(self):
        """Обработка обнаружения ключевого слова"""
        if not self.running:
            return
        
        print("✓ Ключевое слово обнаружено!")
        
        self.root.after(0, self.update_status_for_wake_word)
        
        self.root.after(0, lambda: self.play_activation_sound())
        
        self.root.after(100, lambda: self.speak("Слушаю вас", priority=True))
        
        self.root.after(800, self.process_voice_command_after_wake_word)
    
    def process_voice_command_after_wake_word(self):
        """Обработка голосовой команды после активации"""
        if not self.running:
            return
        
        print("✓ Начинаю слушать команду...")
        
        if SPEECH_AVAILABLE:
            # Используем оригинальный метод
            self.process_voice_command_original()
        elif VOICE_INPUT_AVAILABLE:
            # Используем упрощенный метод
            self.process_voice_command_simple_mode()
        else:
            self.speak("Голосовой ввод недоступен")
            self.status_label.config(text="Голосовой ввод недоступен", fg=self.colors['danger'])
    
    def process_voice_command_original(self):
        """Оригинальная обработка голосовой команды"""
        try:
            with sr.Microphone() as source:
                self.status_label.config(text="🎤 Слушаю команду...", fg=self.colors['primary_light'])
                
                print("Калибрую микрофон для команды...")
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                print("Микрофон подготовлен для команды")
                
                print("Ожидаю команду...")
                
                try:
                    audio = self.recognizer.listen(
                        source, 
                        timeout=5,
                        phrase_time_limit=4
                    )
                    
                    print("Аудио записано, обрабатываю...")
                    
                    try:
                        result = self.recognizer.recognize_google(
                            audio, 
                            language='ru-RU',
                            show_all=True
                        )
                        
                        print(f"Результат распознавания: {result}")
                        
                        if result and 'alternative' in result and len(result['alternative']) > 0:
                            best_result = result['alternative'][0]
                            command = best_result['transcript'].lower()
                            confidence = best_result.get('confidence', 0)
                            
                            print(f"✓ Команда распознана: '{command}' (уверенность: {confidence:.2f})")
                            self.message_queue.put(f"Команда: {command} (уверенность: {confidence:.2f})")
                            
                            if confidence > 0.2:
                                self.speak(f"Вы сказали: {command[:40]}")
                                self.process_enhanced_command(command)
                            else:
                                if len(result['alternative']) > 1:
                                    second_result = result['alternative'][1]
                                    command2 = second_result['transcript'].lower()
                                    confidence2 = second_result.get('confidence', 0)
                                    
                                    if confidence2 > 0.2:
                                        print(f"✓ Использую второй вариант: '{command2}' (уверенность: {confidence2:.2f})")
                                        self.speak(f"Вы сказали: {command2[:40]}")
                                        self.process_enhanced_command(command2)
                                    else:
                                        print("✗ Уверенность слишком низкая для всех вариантов")
                                        self.speak("Не удалось четко распознать команду. Повторите, пожалуйста.")
                                        self.status_label.config(text=f"🎤 Ожидание: '{self.voice_wake_word}'", fg=self.colors['primary_light'])
                                else:
                                    print("✗ Уверенность слишком низкая")
                                    self.speak("Не удалось четко распознать команду. Повторите, пожалуйста.")
                                    self.status_label.config(text=f"🎤 Ожидание: '{self.voice_wake_word}'", fg=self.colors['primary_light'])
                        else:
                            print("✗ Нет альтернатив в результате")
                            self.speak("Не удалось распознать команду")
                            self.status_label.config(text=f"🎤 Ожидание: '{self.voice_wake_word}'", fg=self.colors['primary_light'])
                            
                    except sr.UnknownValueError:
                        print("✗ Не удалось распознать команду (UnknownValueError)")
                        self.speak("Не удалось распознать команду")
                        self.status_label.config(text=f"🎤 Ожидание: '{self.voice_wake_word}'", fg=self.colors['primary_light'])
                        
                    except Exception as e:
                        print(f"✗ Ошибка при распознавании команды: {e}")
                        self.speak(f"Произошла ошибка при распознавании: {str(e)[:30]}")
                        self.status_label.config(text=f"🎤 Ожидание: '{self.voice_wake_word}'", fg=self.colors['primary_light'])
                        
                except sr.WaitTimeoutError:
                    print("✗ Время ожидания команды истекло")
                    self.speak("Время ожидания команды истекло")
                    self.status_label.config(text=f"🎤 Ожидание: '{self.voice_wake_word}'", fg=self.colors['primary_light'])
                    
        except Exception as e:
            print(f"✗ Ошибка при настройке микрофона: {e}")
            self.speak("Ошибка при настройке микрофона")
            self.status_label.config(text=f"🎤 Ожидание: '{self.voice_wake_word}'", fg=self.colors['primary_light'])
    
    def process_voice_command_simple_mode(self):
        """Упрощенная обработка голосовой команды"""
        self.speak("Скажите команду")
        
        # Используем упрощенный метод распознавания
        command, confidence = self.listen_without_speech_recognition(10)
        
        if command and confidence > 0.5:
            self.speak(f"Вы сказали: {command[:40]}")
            self.process_voice_command_simple(command)
            self.status_label.config(text=f"🎤 Ожидание: '{self.voice_wake_word}'", fg=self.colors['primary_light'])
        else:
            self.speak("Не удалось распознать команду")
            self.status_label.config(text=f"🎤 Ожидание: '{self.voice_wake_word}'", fg=self.colors['primary_light'])
    
    # ========== СУЩЕСТВУЮЩИЕ МЕТОДЫ (БЕЗ ИЗМЕНЕНИЙ) ==========
    
    def safe_after(self, delay_ms, callback, *args):
        """Безопасное выполнение after с отслеживанием ID"""
        if not self.running:
            return None
        
        def safe_callback():
            if self.running and self.root.winfo_exists():
                try:
                    callback(*args)
                except (tk.TclError, AttributeError, RuntimeError):
                    pass  # Окно уже уничтожено или виджет не существует
        
        after_id = self.root.after(delay_ms, safe_callback)
        self.after_ids.append(after_id)
        return after_id
    
    def cancel_all_after(self):
        """Отмена всех запланированных задач"""
        self.running = False
        for after_id in self.after_ids:
            try:
                self.root.after_cancel(after_id)
            except:
                pass
        self.after_ids.clear()
    
    def load_users(self):
        """Загрузка пользователей из файла"""
        try:
            if os.path.exists(self.users_file):
                with open(self.users_file, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if content:  # Проверяем, что файл не пустой
                        self.users = json.loads(content)
                    else:
                        self.users = {}
            else:
                self.users = {}
        except json.JSONDecodeError as e:
            print(f"Ошибка декодирования JSON в файле пользователей: {e}")
            self.users = {}
        except Exception as e:
            print(f"Ошибка загрузки пользователей: {e}")
            self.users = {}
    
    def save_users(self):
        """Сохранение пользователей в файл"""
        try:
            with open(self.users_file, 'w', encoding='utf-8') as f:
                json.dump(self.users, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Ошибка сохранения пользователей: {e}")
    
    def hash_password(self, password):
        """Хеширование пароля"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def show_auth_window(self):
        """Окно авторизации/регистрации с современным дизайном"""
        # Показываем анимацию при запуске
        self.text_anim.show_transition("Атом v4.0 PRO", 2)
        
        self.auth_window = tk.Toplevel(self.root)
        self.auth_window.title("Атом v4.0 PRO - Авторизация")
        self.auth_window.geometry("500x650")
        self.auth_window.configure(bg="#0f172a")
        self.auth_window.resizable(False, False)
        self.auth_window.attributes('-topmost', True)
        
        # Центрируем окно
        self.center_window(self.auth_window)
        
        # Canvas для градиентного фона
        canvas = tk.Canvas(self.auth_window, bg="#0f172a", highlightthickness=0)
        canvas.pack(fill=tk.BOTH, expand=True)
        
        # Рисуем градиентный фон
        width, height = 500, 650
        for i in range(height):
            ratio = i / height
            r = int(15 + (30 * ratio))
            g = int(23 + (42 * ratio))
            b = int(42 + (58 * ratio))
            color = f'#{r:02x}{g:02x}{b:02x}'
            canvas.create_line(0, i, width, i, fill=color, width=1)
        
        # Заголовок с эффектом
        canvas.create_text(250, 80,
                          text="⚛️",
                          fill="#60a5fa",
                          font=('Segoe UI', 72, 'bold'))
        
        canvas.create_text(250, 150,
                          text="Атом v4.0 PRO",
                          fill="#ffffff",
                          font=('Segoe UI', 28, 'bold'))
        
        canvas.create_text(250, 180,
                          text="Умный голосовой помощник с ИИ",
                          fill="#94a3b8",
                          font=('Segoe UI', 12))
        
        # Фрейм для вкладок с темным фоном (без прозрачности)
        notebook_frame = tk.Frame(canvas, bg='#1e293b')
        canvas.create_window(250, 350, window=notebook_frame, width=400, height=350)
        
        # Вкладки
        notebook = ttk.Notebook(notebook_frame)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Настраиваем стиль вкладок
        style = ttk.Style()
        style.configure('Modern.TNotebook', background='#1e293b', borderwidth=0)
        style.configure('Modern.TNotebook.Tab', 
                       background='#334155', 
                       foreground='#cbd5e1',
                       padding=[20, 10],
                       font=('Segoe UI', 10))
        style.map('Modern.TNotebook.Tab', 
                 background=[('selected', '#3b82f6')],
                 foreground=[('selected', 'white')])
        
        notebook.configure(style='Modern.TNotebook')
        
        # Вкладка входа
        login_frame = tk.Frame(notebook, bg='#1e293b')
        notebook.add(login_frame, text="Вход")
        
        # Вкладка регистрации
        register_frame = tk.Frame(notebook, bg='#1e293b')
        notebook.add(register_frame, text="Регистрация")
        
        # ===== ВКЛАДКА ВХОДА =====
        tk.Label(login_frame,
                text="Имя пользователя:",
                bg='#1e293b',
                fg='#cbd5e1',
                font=('Segoe UI', 11)).place(x=30, y=30)
        
        self.login_username = tk.StringVar()
        login_user_entry = tk.Entry(
            login_frame,
            textvariable=self.login_username,
            font=("Segoe UI", 12),
            bg='#0f172a',
            fg='white',
            insertbackground='white',
            relief=tk.FLAT,
            width=25
        )
        login_user_entry.place(x=30, y=60)
        
        tk.Label(login_frame,
                text="Пароль:",
                bg='#1e293b',
                fg='#cbd5e1',
                font=('Segoe UI', 11)).place(x=30, y=100)
        
        self.login_password = tk.StringVar()
        login_pass_entry = tk.Entry(
            login_frame,
            textvariable=self.login_password,
            font=("Segoe UI", 12),
            bg='#0f172a',
            fg='white',
            insertbackground='white',
            relief=tk.FLAT,
            width=25,
            show="•"
        )
        login_pass_entry.place(x=30, y=130)
        
        # Чекбокс "Запомнить меня"
        self.login_remember = tk.BooleanVar(value=True)
        remember_check = tk.Checkbutton(
            login_frame,
            text="Запомнить меня",
            variable=self.login_remember,
            bg='#1e293b',
            fg='#cbd5e1',
            selectcolor='#3b82f6',
            activebackground='#1e293b',
            activeforeground='#cbd5e1',
            font=('Segoe UI', 10)
        )
        remember_check.place(x=30, y=170)
        
        # Кнопка входа
        def create_login_button():
            btn_canvas = tk.Canvas(login_frame, bg='#1e293b', highlightthickness=0, width=200, height=45)
            btn_canvas.place(x=100, y=220)
            
            # Градиентная кнопка
            for i in range(45):
                ratio = i / 45
                r = int(59 * (1 - ratio * 0.3))
                g = int(130 * (1 - ratio * 0.3))
                b = int(246 * (1 - ratio * 0.3))
                color = f'#{r:02x}{g:02x}{b:02x}'
                btn_canvas.create_line(0, i, 200, i, fill=color, width=1)
            
            btn_canvas.create_text(100, 22,
                                  text="🚪 Войти",
                                  fill="white",
                                  font=('Segoe UI', 12, 'bold'))
            
            btn_canvas.bind("<Button-1>", lambda e: self.login_user())
            btn_canvas.bind("<Enter>", lambda e: btn_canvas.config(cursor="hand2"))
            btn_canvas.bind("<Leave>", lambda e: btn_canvas.config(cursor=""))
        
        create_login_button()
        
        # Гостевой доступ
        guest_btn = tk.Label(login_frame,
                           text="👤 Гостевой доступ",
                           bg='#1e293b',
                           fg='#60a5fa',
                           font=('Segoe UI', 10),
                           cursor="hand2")
        guest_btn.place(x=140, y=280)
        guest_btn.bind("<Button-1>", lambda e: self.guest_login())
        
        # ===== ВКЛАДКА РЕГИСТРАЦИИ =====
        tk.Label(register_frame,
                text="Имя пользователя:",
                bg='#1e293b',
                fg='#cbd5e1',
                font=('Segoe UI', 11)).place(x=30, y=30)
        
        self.reg_username = tk.StringVar()
        reg_user_entry = tk.Entry(
            register_frame,
            textvariable=self.reg_username,
            font=("Segoe UI", 12),
            bg='#0f172a',
            fg='white',
            insertbackground='white',
            relief=tk.FLAT,
            width=25
        )
        reg_user_entry.place(x=30, y=60)
        
        tk.Label(register_frame,
                text="Пароль:",
                bg='#1e293b',
                fg='#cbd5e1',
                font=('Segoe UI', 11)).place(x=30, y=100)
        
        self.reg_password = tk.StringVar()
        reg_pass_entry = tk.Entry(
            register_frame,
            textvariable=self.reg_password,
            font=("Segoe UI", 12),
            bg='#0f172a',
            fg='white',
            insertbackground='white',
            relief=tk.FLAT,
            width=25,
            show="•"
        )
        reg_pass_entry.place(x=30, y=130)
        
        tk.Label(register_frame,
                text="Повторите пароль:",
                bg='#1e293b',
                fg='#cbd5e1',
                font=('Segoe UI', 11)).place(x=30, y=170)
        
        self.reg_password_confirm = tk.StringVar()
        reg_pass_confirm_entry = tk.Entry(
            register_frame,
            textvariable=self.reg_password_confirm,
            font=("Segoe UI", 12),
            bg='#0f172a',
            fg='white',
            insertbackground='white',
            relief=tk.FLAT,
            width=25,
            show="•"
        )
        reg_pass_confirm_entry.place(x=30, y=200)
        
        # Чекбокс согласия
        self.reg_terms = tk.BooleanVar(value=False)
        terms_check = tk.Checkbutton(
            register_frame,
            text="Я согласен с пользовательским соглашением",
            variable=self.reg_terms,
            bg='#1e293b',
            fg='#cbd5e1',
            selectcolor='#3b82f6',
            activebackground='#1e293b',
            activeforeground='#cbd5e1',
            font=('Segoe UI', 9)
        )
        terms_check.place(x=30, y=240)
        
        # Кнопка регистрации
        def create_register_button():
            btn_canvas = tk.Canvas(register_frame, bg='#1e293b', highlightthickness=0, width=200, height=45)
            btn_canvas.place(x=100, y=280)
            
            # Градиентная кнопка
            for i in range(45):
                ratio = i / 45
                r = int(139 * (1 - ratio * 0.3))
                g = int(92 * (1 - ratio * 0.3))
                b = int(246 * (1 - ratio * 0.3))
                color = f'#{r:02x}{g:02x}{b:02x}'
                btn_canvas.create_line(0, i, 200, i, fill=color, width=1)
            
            btn_canvas.create_text(100, 22,
                                  text="📝 Зарегистрироваться",
                                  fill="white",
                                  font=('Segoe UI', 12, 'bold'))
            
            btn_canvas.bind("<Button-1>", lambda e: self.register_user())
            btn_canvas.bind("<Enter>", lambda e: btn_canvas.config(cursor="hand2"))
            btn_canvas.bind("<Leave>", lambda e: btn_canvas.config(cursor=""))
        
        create_register_button()
        
        # Скрываем главное окно
        self.root.withdraw()
        self.auth_window.grab_set()
        self.auth_window.focus_set()
        
        # Устанавливаем фокус на первое поле
        login_user_entry.focus_set()
        
        # Обработка Enter
        login_pass_entry.bind('<Return>', lambda e: self.login_user())
        reg_pass_confirm_entry.bind('<Return>', lambda e: self.register_user())
        
        # Версия внизу
        version_label = tk.Label(canvas,
                                text="Версия 4.0 PRO | © 2024 | С расширенными функциями ИИ",
                                bg='#0f172a',
                                fg='#64748b',
                                font=('Segoe UI', 9))
        canvas.create_window(250, 620, window=version_label)
        
        # Обработка закрытия окна авторизации
        self.auth_window.protocol("WM_DELETE_WINDOW", self.on_auth_window_close)
    
    def on_auth_window_close(self):
        """Обработка закрытия окна авторизации"""
        if self.auth_window and self.auth_window.winfo_exists():
            self.auth_window.destroy()
        self.on_closing()
    
    def center_window(self, window):
        """Центрирование окна на экране"""
        window.update_idletasks()
        width = window.winfo_width()
        height = window.winfo_height()
        x = (window.winfo_screenwidth() // 2) - (width // 2)
        y = (window.winfo_screenheight() // 2) - (height // 2)
        window.geometry(f'{width}x{height}+{x}+{y}')
    
    def login_user(self):
        """Авторизация пользователя"""
        username = self.login_username.get().strip()
        password = self.login_password.get().strip()
        
        if not username or not password:
            self.speak("Заполните все поля", priority=True)
            messagebox.showerror("Ошибка", "Заполните все поля")
            return
        
        if username in self.users:
            hashed_password = self.hash_password(password)
            if self.users[username]["password"] == hashed_password:
                self.logged_in = True
                self.current_user = username
                
                # Обновляем время последнего входа
                self.users[username]["last_login"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.save_users()
                
                # Загружаем настройки пользователя
                self.load_settings()
                
                # Закрываем окно авторизации
                if hasattr(self, 'auth_window') and self.auth_window.winfo_exists():
                    self.auth_window.destroy()
                
                # Показываем анимацию после успешной авторизации
                self.text_anim.show_transition(f"Добро пожаловать, {username}!", 2)
                self.speak(f"Добро пожаловать, {username}!")
                
                # Небольшая задержка перед показом выбора режима
                self.root.after(2500, self.show_mode_selection)
                return
        
        self.speak("Неверное имя пользователя или пароль", priority=True)
        messagebox.showerror("Ошибка", "Неверное имя пользователя или пароль")
    
    def register_user(self):
        """Регистрация нового пользователя с проверкой соглашения"""
        username = self.reg_username.get().strip()
        password = self.reg_password.get().strip()
        password_confirm = self.reg_password_confirm.get().strip()
        
        # Проверка обязательных полей
        if not username or not password:
            self.speak("Заполните обязательные поля", priority=True)
            messagebox.showerror("Ошибка", "Заполните обязательные поля")
            return
        
        # Проверка длины имени пользователя
        if len(username) < 3:
            self.speak("Имя пользователя должно быть не менее 3 символов", priority=True)
            messagebox.showerror("Ошибка", "Имя пользователя должно быть не менее 3 символов")
            return
        
        # Проверка длины пароля
        if len(password) < 6:
            self.speak("Пароль должен быть не менее 6 символов", priority=True)
            messagebox.showerror("Ошибка", "Пароль должен быть не менее 6 символов")
            return
        
        # Проверка совпадения паролей
        if password != password_confirm:
            self.speak("Пароли не совпадают", priority=True)
            messagebox.showerror("Ошибка", "Пароли не совпадают")
            return
        
        # Проверка пользовательского соглашения
        if not self.reg_terms.get():
            self.speak("Вы должны принять пользовательское соглашение", priority=True)
            messagebox.showerror("Ошибка", "Вы должны принять пользовательское соглашение")
            self.safe_after(100, lambda: self.show_terms_of_service(self.auth_window))
            return
        
        # Проверка существования пользователя
        if username in self.users:
            self.speak("Пользователь с таким именем уже существует", priority=True)
            messagebox.showerror("Ошибка", "Пользователь с такого имени уже существует")
            return
        
        # Сохраняем пользователя
        self.users[username] = {
            "password": self.hash_password(password),
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "last_login": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "settings": self.settings.copy(),
            "terms_accepted": True,
            "terms_accepted_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        self.save_users()
        
        # Автоматический вход
        self.logged_in = True
        self.current_user = username
        
        # Закрываем окно авторизации
        if hasattr(self, 'auth_window') and self.auth_window.winfo_exists():
            try:
                self.auth_window.destroy()
            except:
                pass
        
        # Показываем анимацию
        self.text_anim.show_transition(f"Регистрация успешна!\nДобро пожаловать, {username}!", 3)
        self.speak(f"Регистрация прошла успешно! Добро пожаловать, {username}!")
        
        # Показываем сообщение об успехе
        self.root.after(3500, lambda: messagebox.showinfo(
            "Успешная регистрация", 
            f"Регистрация прошла успешно!\n\n"
            f"Добро пожаловать, {username}!\n"
            f"Теперь вы можете использовать все функции Атом v4.0 PRO.")
        )
        
        self.root.after(3500, self.show_mode_selection)
    
    def guest_login(self):
        """Гостевой доступ"""
        self.logged_in = False
        self.current_user = None
        
        if hasattr(self, 'auth_window') and self.auth_window.winfo_exists():
            self.auth_window.destroy()
        
        # Показываем анимацию для гостя
        self.text_anim.show_transition("Гостевой доступ", 2)
        self.speak("Добро пожаловать в гостевой режим!")
        self.root.after(2500, self.show_mode_selection)
    
    def show_terms_of_service(self, parent_window=None):
        """Показать пользовательское соглашение"""
        try:
            # Если окно уже открыто, просто поднимаем его
            if hasattr(self, '_terms_window') and self._terms_window and self._terms_window.winfo_exists():
                try:
                    self._terms_window.lift()
                    self._terms_window.focus_set()
                    return
                except:
                    pass
            
            if parent_window is None:
                parent_window = self.root
            
            self._terms_window = tk.Toplevel(parent_window)
            self._terms_window.title("Пользовательское соглашение - Атом v4.0 PRO")
            self._terms_window.geometry("700x550")
            self._terms_window.configure(bg=self.colors['bg'])
            
            # Центрируем окно
            self.center_window(self._terms_window)
            
            # Canvas для фона
            canvas = tk.Canvas(self._terms_window, bg=self.colors['bg'], highlightthickness=0)
            canvas.pack(fill=tk.BOTH, expand=True)
            
            # Заголовок
            canvas.create_text(350, 40,
                             text="📜 ПОЛЬЗОВАТЕЛЬСКОЕ СОГЛАШЕНИЕ",
                             fill=self.colors['primary_light'],
                             font=('Segoe UI', 18, 'bold'))
            
            # Текст соглашения
            terms_text = scrolledtext.ScrolledText(
                canvas,
                height=20,
                width=80,
                bg=self.colors['bg_lighter'],
                fg=self.colors['text'],
                font=("Segoe UI", 10),
                wrap=tk.WORD,
                relief=tk.FLAT,
                borderwidth=0,
                padx=15,
                pady=15
            )
            canvas.create_window(350, 280, window=terms_text, width=650, height=400)
            
            # Текст пользовательского соглашения
            terms_content = """ПОЛЬЗОВАТЕЛЬСКОЕ СОГЛАШЕНИЕ
для использования голосового помощника "Атом v4.0 PRO"

Дата вступления в силу: 1 января 2024 г.

1. ОБЩИЕ ПОЛОЖЕНИЯ

1.1. Настоящее Пользовательское соглашение (далее – "Соглашение") регулирует отношения между пользователем (далее – "Пользователь") и разработчиком голосового помощника "Атом v4.0 PRO" (далее – "Разработчик") по использованию программы.

1.2. Используя программу "Атом v4.0 PRO", Пользователь подтверждает, что прочитал, понял и согласен с условиями настоящего Соглашения.

2. РЕГИСТРАЦИЯ И УЧЕТНАЯ ЗАПИСЬ

2.1. Для использования всех функций программы требуется регистрация учетной записи.

2.2. Пользователь обязуется предоставлять достоверную информацию при регистрации.

2.3. Пользователь самостоятельно несет ответственность за сохранность своих учетных данных.

2.4. Разработчик не несет ответственность за несанкционированный доступ к учетной записи Пользователя.

3. ПРАВА И ОБЯЗАННОСТИ ПОЛЬЗОВАТЕЛЯ

3.1. Пользователь имеет право:
- Использовать программу в личных некоммерческих целях;
- Создавать резервные копии своих данных;
- Обращаться в поддержку по вопросам работы программы.

3.2. Пользователь обязуется:
- Не использовать программу для противоправной деятельности;
- Не распространять вредоносное программное обеспечение;
- Не пытаться взломать или обойти защиту программы;
- Не нарушать авторские права третьих лиц.

4. ОГРАНИЧЕНИЯ ИСПОЛЬЗОВАНИЯ

4.1. Программа предоставляется "как есть" (as is).

4.2. Разработчик не гарантирует бесперебойную работу программы.

4.3. Разработчик оставляет за собой право вносить изменения в программу без предварительного уведомления.

5. КОНФИДЕНЦИАЛЬНОСТЬ

5.1. Все данные Пользователя хранятся локально на его устройстве.

5.2. Разработчик не собирает и не передает персональные данные Пользователя третьим лицам.

5.3. Хешированные пароли хранятся в локальном файле для целей аутентификации.

6. АВТОРСКИЕ ПРАВА

6.1. Все права на программу "Атом v4.0 PRO" принадлежат Разработчику.

6.2. Пользователю предоставляется право на использование программы в соответствии с условиями настоящего Соглашения.

7. ОТВЕТСТВЕННОСТЬ

7.1. Разработчик не несет ответственности за:
- Убытки, возникшие в результате использования программы;
- Невозможность использовать программы;
- Действия третьих лиц.

7.2. Пользователь использует программу на свой собственный риск.

8. ЗАКЛЮЧИТЕЛЬНЫЕ ПОЛОЖЕНИЯ

8.1. Настоящее Соглашение может быть изменено Разработчиком без предварительного уведомления.

8.2. Продолжение использования программы после изменений означает согласие с новыми условиями.

8.3. В случае возникновения споров, стороны будут стремиться решить их путем переговоров.

Для связи с разработчиком: atom.support@example.com

Нажимая "Я согласен", Вы подтверждаете, что прочитали и принимаете условия данного Соглашения."""
            
            terms_text.insert(tk.END, terms_content)
            terms_text.config(state=tk.DISABLED)
            
            # Фрейм для кнопок
            buttons_frame = tk.Frame(canvas, bg=self.colors['bg'])
            canvas.create_window(350, 520, window=buttons_frame)
            
            def accept_terms():
                try:
                    if hasattr(self, 'reg_terms'):
                        self.reg_terms.set(True)
                    self.speak("Вы приняли пользовательское соглашение!")
                    messagebox.showinfo("Соглашение", "Вы приняли пользовательское соглашение!")
                    
                    # Закрываем окно в основном потоке
                    self.safe_after(0, lambda: self._terms_window.destroy() if hasattr(self, '_terms_window') and self._terms_window else None)
                except Exception as e:
                    print(f"Ошибка при принятии соглашения: {e}")
            
            def print_terms():
                try:
                    self.speak("Для печати используйте комбинацию Ctrl+P")
                    messagebox.showinfo("Печать", "Для печати используйте комбинацию Ctrl+P в окне соглашения")
                except Exception as e:
                    print(f"Ошибка при печати: {e}")
            
            def close_window():
                try:
                    if hasattr(self, '_terms_window') and self._terms_window and self._terms_window.winfo_exists():
                        self._terms_window.destroy()
                except:
                    pass
            
            # Кнопки с современным дизайном
            accept_btn = tk.Canvas(buttons_frame, bg=self.colors['bg'], highlightthickness=0, width=180, height=35)
            accept_btn.pack(side=tk.LEFT, padx=5)
            accept_btn.create_rectangle(0, 0, 179, 34, fill=self.colors['success'], outline='')
            accept_btn.create_text(90, 17, text="✅ Принять соглашение", fill="white", font=('Segoe UI', 10, 'bold'))
            accept_btn.bind("<Button-1>", lambda e: accept_terms())
            accept_btn.bind("<Enter>", lambda e: accept_btn.config(cursor="hand2"))
            
            close_btn = tk.Canvas(buttons_frame, bg=self.colors['bg'], highlightthickness=0, width=100, height=35)
            close_btn.pack(side=tk.LEFT, padx=5)
            close_btn.create_rectangle(0, 0, 99, 34, fill=self.colors['danger'], outline='')
            close_btn.create_text(50, 17, text="❌ Закрыть", fill="white", font=('Segoe UI', 10, 'bold'))
            close_btn.bind("<Button-1>", lambda e: close_window())
            close_btn.bind("<Enter>", lambda e: close_btn.config(cursor="hand2"))
            
            # Обработка закрытия окна
            def on_window_close():
                close_window()
                # Освобождаем ссылку
                if hasattr(self, '_terms_window'):
                    delattr(self, '_terms_window')
            
            self._terms_window.protocol("WM_DELETE_WINDOW", on_window_close)
            
        except Exception as e:
            print(f"Ошибка при показе пользовательского соглашения: {e}")
            # Пытаемся показать простое окно сообщения
            try:
                messagebox.showerror("Ошибка", f"Не удалось открыть пользовательское соглашение: {e}")
            except:
                pass
    
    def show_mode_selection(self):
        """Показ окна выбора режима при запуске"""
        # Создаем окно выбора режима
        self.selection_window = tk.Toplevel(self.root)
        title = "Атом v4.0 PRO - Выбор режима"
        self.selection_window.title(title)
        self.selection_window.geometry("600x700")
        self.selection_window.configure(bg="#0f172a")
        self.selection_window.attributes('-topmost', True)
        self.selection_window.resizable(False, False)
        
        # Центрируем окно
        self.center_window(self.selection_window)
        
        # Canvas для фона
        canvas = tk.Canvas(self.selection_window, bg="#0f172a", highlightthickness=0)
        canvas.pack(fill=tk.BOTH, expand=True)
        
        # Заголовок с именем пользователя
        if self.logged_in:
            title_text = f"⚛️ Атом v4.0 PRO - {self.current_user}"
        else:
            title_text = "⚛️ Атом v4.0 PRO - Гость"
        
        canvas.create_text(300, 100,
                          text=title_text,
                          fill="#ffffff",
                          font=('Segoe UI', 28, 'bold'))
        
        # Информация о пользователе
        if self.logged_in:
            user_info = tk.Label(canvas,
                                text=f"👤 Вы вошли как: {self.current_user}",
                                bg='#0f172a',
                                fg='#60a5fa',
                                font=('Segoe UI', 12))
            canvas.create_window(300, 140, window=user_info)
        
        canvas.create_text(300, 180,
                          text="Выберите режим работы:",
                          fill="#94a3b8",
                          font=('Segoe UI', 14))
        
        # Фрейм для карточек режимов
        cards_frame = tk.Frame(canvas, bg='#0f172a')
        canvas.create_window(300, 400, window=cards_frame)
        
        # Карточка демо-режима
        demo_card = tk.Canvas(cards_frame, bg='#0f172a', highlightthickness=0, width=500, height=180)
        demo_card.grid(row=0, column=0, pady=10)
        
        # Фон карточки
        demo_card.create_rectangle(0, 0, 499, 179, fill='#1e293b', outline='')
        
        # Иконка и заголовок
        demo_card.create_text(50, 45,
                             text="🎬",
                             fill="#f59e0b",
                             font=('Segoe UI Emoji', 24))
        
        demo_card.create_text(200, 45,
                             text="ДЕМОНСТРАЦИОННЫЙ РЕЖИМ",
                             fill="#ffffff",
                             font=('Segoe UI', 16, 'bold'),
                             anchor="w")
        
        # Описание
        demo_card.create_text(200, 85,
                             text="• Голосовая демонстрация\n• Автоматическая демонстрация\n• Демо-функции\n• Обучающие видео\n• Тестирование возможностей",
                             fill="#cbd5e1",
                             font=('Segoe UI', 11),
                             anchor="w")
        
        # Кнопка выбора
        demo_btn = tk.Canvas(demo_card, bg='#1e293b', highlightthickness=0, width=120, height=35)
        demo_card.create_window(400, 140, window=demo_btn)
        demo_btn.create_rectangle(0, 0, 119, 34, fill='#f59e0b', outline='')
        demo_btn.create_text(60, 17, text="Выбрать", fill="white", font=('Segoe UI', 10, 'bold'))
        demo_btn.bind("<Button-1>", lambda e: self.start_with_mode(True))
        demo_btn.bind("<Enter>", lambda e: demo_btn.config(cursor="hand2"))
        
        # Карточка рабочего режима
        work_card = tk.Canvas(cards_frame, bg='#0f172a', highlightthickness=0, width=500, height=180)
        work_card.grid(row=1, column=0, pady=10)
        
        # Фон карточки
        work_card.create_rectangle(0, 0, 499, 179, fill='#1e293b', outline='')
        
        # Иконка и заголовок
        work_card.create_text(50, 45,
                             text="⚡",
                             fill="#10b981",
                             font=('Segoe UI Emoji', 24))
        
        work_card.create_text(200, 45,
                             text="РАБОЧИЙ РЕЖИМ",
                             fill="#ffffff",
                             font=('Segoe UI', 16, 'bold'),
                             anchor="w")
        
        # Описание
        work_card.create_text(200, 85,
                             text="• Реальная погода\n• Поиск в интернете\n• Открытие сайтов\n• Видеоплеер\n• Калькулятор\n• Проверка сайтов\n• Настройки\n• ГОЛОСОВОЙ ПОМОЩНИК\n• ИИ-АССИСТЕНТ\n• 🤖 Автоматизация задач\n• 💻 Редактор кода",
                             fill="#cbd5e1",
                             font=('Segoe UI', 11),
                             anchor="w")
        
        # Кнопка выбора
        work_btn = tk.Canvas(work_card, bg='#1e293b', highlightthickness=0, width=120, height=35)
        work_card.create_window(400, 140, window=work_btn)
        work_btn.create_rectangle(0, 0, 119, 34, fill='#10b981', outline='')
        work_btn.create_text(60, 17, text="Выбрать", fill="white", font=('Segoe UI', 10, 'bold'))
        work_btn.bind("<Button-1>", lambda e: self.start_with_mode(False))
        work_btn.bind("<Enter>", lambda e: work_btn.config(cursor="hand2"))
        
        # Кнопка смены пользователя
        if self.logged_in:
            logout_btn = tk.Label(canvas,
                                text="🔄 Сменить пользователя",
                                bg='#0f172a',
                                fg='#ef4444',
                                font=('Segoe UI', 10),
                                cursor="hand2")
            canvas.create_window(300, 620, window=logout_btn)
            logout_btn.bind("<Button-1>", lambda e: self.logout_user())
        
        # Версия
        version_label = tk.Label(canvas,
                                text="Версия 4.0 PRO | © 2024 | С расширенными функциями ИИ",
                                bg='#0f172a',
                                fg='#64748b',
                                font=('Segoe UI', 9))
        canvas.create_window(300, 670, window=version_label)
        
        # Блокируем главное окно
        self.selection_window.grab_set()
        self.selection_window.focus_set()
        
        # Обработка закрытия окна выбора
        self.selection_window.protocol("WM_DELETE_WINDOW", self.on_selection_window_close)
    
    def on_selection_window_close(self):
        """Обработка закрытия окна выбора режима"""
        if self.selection_window and self.selection_window.winfo_exists():
            self.selection_window.destroy()
        self.on_closing()
    
    def logout_user(self):
        """Выход из аккаунта"""
        self.logged_in = False
        self.current_user = None
        
        if hasattr(self, 'selection_window') and self.selection_window.winfo_exists():
            self.selection_window.destroy()
        
        self.speak("Вы вышли из аккаунта")
        self.show_auth_window()
    
    def start_with_mode(self, demo_mode):
        """Запуск приложения с выбранным режимом"""
        self.demo_mode = demo_mode
        
        # Сохраняем выбор режима
        self.settings["demo_mode"] = demo_mode
        self.save_settings()
        
        # Закрываем окно выбора режима
        if hasattr(self, 'selection_window') and self.selection_window.winfo_exists():
            self.selection_window.destroy()
        
        # Показываем анимацию при смене режима
        mode_name = "Демонстрационный" if demo_mode else "Рабочий"
        self.text_anim.show_transition(f"{mode_name} режим", 2)
        self.speak(f"Запуск {mode_name.lower()} режима")
        
        # Загружаем пользовательские настройки если есть
        if self.logged_in and self.current_user in self.users:
            user_settings = self.users[self.current_user].get("settings", {})
            if user_settings:
                # Обновляем настройки, сохраняя значения по умолчанию для отсутствующих ключей
                for key, value in user_settings.items():
                    if key in self.settings:
                        self.settings[key] = value
        
        # Запускаем основной интерфейс после анимации
        self.root.after(2500, self.create_main_interface)
    
    def load_settings(self):
        """Загрузка настроек из файла"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)
                    
                    # Объединяем с дефолтными настройки
                    for key, value in loaded_settings.items():
                        if key in self.settings:
                            self.settings[key] = value
                    
                    # Обновляем голосовые настройки
                    if self.speech_engine:
                        self.speech_engine.setProperty('rate', self.settings.get("voice_speed", 150))
                        self.speech_engine.setProperty('volume', self.settings.get("voice_volume", 0.9))
                        
        except Exception as e:
            print(f"Ошибка загрузки настроек: {e}")
    
    def save_settings(self):
        """Сохранение настроек в файл"""
        try:
            # Сохраняем настройки для текущего пользователя если авторизован
            if self.logged_in and self.current_user in self.users:
                self.users[self.current_user]["settings"] = self.settings
                self.save_users()
            
            # Также сохраняем в общий файл настроек
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"Ошибка сохранения настроек: {e}")
    
    def create_main_interface(self):
        """Создание основного интерфейса программы"""
        # Очищаем главное окно
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Настройка цветовой схемы
        self.setup_colors()
        
        # Создаем верхнюю панель
        self.create_top_panel()
        
        # Создаем основное содержимое
        self.create_main_content()
        
        # Создаем статус бар
        self.create_status_bar()
        
        # Добавляем горячие клавиши
        self.setup_hotkeys()
        
        # Показываем главное окно
        self.root.deiconify()
        
        # Запускаем обработчик очереди сообщений
        self.process_queue()
        
        # Запускаем голосового помощника если включен
        if (SPEECH_AVAILABLE or VOICE_INPUT_AVAILABLE) and self.settings.get("voice_enabled", True) and not self.demo_mode:
            self.voice_assistant_active = True
            self.root.after(1000, self.start_voice_assistant)
        
        # Показываем приветственное сообщение
        welcome_msg = f"Атом v4.0 PRO запущен в {'демонстрационном' if self.demo_mode else 'рабочем'} режиме!"
        if self.logged_in:
            welcome_msg += f"\nДобро пожаловать, {self.current_user}!"
        self.message_queue.put(welcome_msg)
        self.speak(welcome_msg)
        
        # Если демо-режим, запускаем демонстрацию
        if self.demo_mode:
            self.root.after(2000, self.start_demo)
    
    def setup_colors(self):
        """Настройка цветовой схемы"""
        self.colors = {
            'bg': '#0f172a',
            'bg_light': '#1e293b',
            'bg_lighter': '#334155',
            'text': '#f1f5f9',
            'text_secondary': '#94a3b8',
            'primary': '#3b82f6',
            'primary_light': '#60a5fa',
            'success': '#10b981',
            'warning': '#f59e0b',
            'danger': '#ef4444',
            'accent': '#8b5cf6'
        }
    
    def setup_hotkeys(self):
        """Настройка горячих клавиш"""
        # Панель быстрого доступа
        self.root.bind('<Control-q>', lambda e: self.create_quick_access_panel())
        
        # Сохранение данных
        self.root.bind('<Control-s>', lambda e: self.save_all_data())
        
        # Обновление интерфейса
        self.root.bind('<Control-r>', lambda e: self.refresh_interface())
        
        # Справка
        self.root.bind('<F1>', lambda e: self.speak("Справка открыта"))
        
        # Скриншот
        self.root.bind('<F2>', lambda e: self.take_screenshot())
    
    def create_top_panel(self):
        """Создание верхней панели управления"""
        top_frame = tk.Frame(self.root, bg=self.colors['bg_light'], height=70)
        top_frame.pack(fill=tk.X)
        
        # Логотип и название
        logo_frame = tk.Frame(top_frame, bg=self.colors['bg_light'])
        logo_frame.pack(side=tk.LEFT, padx=25)
        
        tk.Label(logo_frame, 
                text="⚛️",
                bg=self.colors['bg_light'],
                fg=self.colors['primary_light'],
                font=('Segoe UI Emoji', 28)).pack(side=tk.LEFT, padx=5)
        
        title_text = "Атом v4.0 PRO"
        if self.logged_in:
            title_text += f" | {self.current_user}"
        if self.demo_mode:
            title_text += " | Демо-режим"
            
        tk.Label(logo_frame,
                text=title_text,
                bg=self.colors['bg_light'],
                fg=self.colors['text'],
                font=('Segoe UI', 18, 'bold')).pack(side=tk.LEFT)
        
        # Панель кнопок справа
        button_frame = tk.Frame(top_frame, bg=self.colors['bg_light'])
        button_frame.pack(side=tk.RIGHT, padx=20)
        
        # Создаем современные кнопки
        buttons = [
            ("⚡ Быстрый доступ", self.create_quick_access_panel, self.colors['accent']),
            ("🎤 Голос", self.toggle_voice_assistant, self.colors['accent']),
            ("🤖 ИИ", self.open_ai_assistant, self.colors['primary']),
            ("⚙️ Настройки", self.open_settings, self.colors['primary']),
            (f"🔄 {'В рабочий' if self.demo_mode else 'В демо'}", self.switch_mode, 
             self.colors['success'] if self.demo_mode else self.colors['warning']),
            ("🚪 Выход", self.logout_or_exit, self.colors['danger'])
        ]
        
        for text, command, color in buttons:
            btn = tk.Button(button_frame, text=text, bg=color, fg='white',
                          font=('Segoe UI', 10, 'bold'), bd=0, padx=15, pady=8,
                          cursor="hand2", command=command)
            btn.pack(side=tk.LEFT, padx=5)
    
    def create_main_content(self):
        """Создание основного содержимого"""
        # Фрейм для контента
        content_frame = tk.Frame(self.root, bg=self.colors['bg'])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Создаем Notebook с современным стилем
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Modern.TNotebook', background=self.colors['bg_light'], borderwidth=0)
        style.configure('Modern.TNotebook.Tab', 
                       background=self.colors['bg_lighter'],
                       foreground=self.colors['text_secondary'],
                       padding=[25, 10],
                       font=('Segoe UI', 11))
        style.map('Modern.TNotebook.Tab', 
                 background=[('selected', self.colors['primary'])],
                 foreground=[('selected', 'white')])
        
        self.notebook = ttk.Notebook(content_frame, style='Modern.TNotebook')
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Создаем вкладки
        self.create_search_tab()
        self.create_social_tab()
        self.create_media_tab()
        self.create_tools_tab()
        self.create_automation_tab()
        self.create_development_tab()
        self.create_ai_tab()
        self.create_help_tab()
        self.create_log_tab()
    
    def create_search_tab(self):
        """Вкладка поиска с современным дизайном"""
        search_frame = tk.Frame(self.notebook, bg=self.colors['bg'])
        self.notebook.add(search_frame, text='🔍 Поиск')
        
        # Заголовок
        title_label = tk.Label(search_frame, text="Поиск информации",
                              bg=self.colors['bg'], fg=self.colors['text'],
                              font=('Segoe UI', 24, 'bold'))
        title_label.pack(pady=(20, 30))
        
        # Карточка поиска
        search_card = tk.Frame(search_frame, bg=self.colors['bg_lighter'], 
                              relief=tk.FLAT, bd=0, padx=20, pady=20)
        search_card.pack(pady=10, padx=50, fill=tk.X)
        
        # Выбор поисковой системы
        tk.Label(search_card, text="Поисковая система:", 
                bg=self.colors['bg_lighter'], fg=self.colors['text_secondary'],
                font=('Segoe UI', 11)).pack(anchor='w', pady=(0, 10))
        
        self.search_engine_var = tk.StringVar(value=list(self.settings["search_engines"].keys())[0])
        search_combo = ttk.Combobox(search_card, textvariable=self.search_engine_var,
                                   values=list(self.settings["search_engines"].keys()),
                                   state='readonly', width=40, font=('Segoe UI', 10))
        search_combo.pack(anchor='w', pady=(0, 20))
        
        # Поле ввода
        tk.Label(search_card, text="Поисковый запрос:", 
                bg=self.colors['bg_lighter'], fg=self.colors['text_secondary'],
                font=('Segoe UI', 11)).pack(anchor='w', pady=(0, 10))
        
        self.search_query = tk.StringVar()
        search_entry = tk.Entry(search_card, textvariable=self.search_query,
                               font=('Segoe UI', 12), bg=self.colors['bg'],
                               fg=self.colors['text'], insertbackground=self.colors['text'],
                               relief=tk.FLAT, width=50)
        search_entry.pack(anchor='w', pady=(0, 20))
        
        # Кнопки поиска
        button_frame = tk.Frame(search_card, bg=self.colors['bg_lighter'])
        button_frame.pack()
        
        search_btn = tk.Button(button_frame, text="🔍 Найти в интернете", 
                              bg=self.colors['primary'], fg='white',
                              font=('Segoe UI', 10, 'bold'), bd=0, padx=20, pady=10,
                              cursor="hand2", command=self.perform_search)
        search_btn.pack(side=tk.LEFT, padx=10)
        
        voice_btn = tk.Button(button_frame, text="🎤 Голосовой поиск", 
                             bg=self.colors['accent'], fg='white',
                             font=('Segoe UI', 10, 'bold'), bd=0, padx=20, pady=10,
                             cursor="hand2", command=self.voice_search)
        voice_btn.pack(side=tk.LEFT, padx=10)
        
        # Быстрый поиск
        quick_frame = tk.Frame(search_frame, bg=self.colors['bg'])
        quick_frame.pack(pady=40)
        
        tk.Label(quick_frame, text="Быстрый поиск:", 
                bg=self.colors['bg'], fg=self.colors['text'],
                font=('Segoe UI', 16, 'bold')).pack(pady=(0, 20))
        
        # Кнопки быстрого поиска
        quick_buttons = [
            ("🌤️ Погода", self.open_weather),
            ("📰 Новости", lambda: self.search_query.set("новости")),
            ("🎬 Видео", lambda: self.search_query.set("видео")),
            ("🗺️ Карты", lambda: self.search_query.set("карты")),
            ("🤖 DeepSeek", self.open_deepseek),
            ("🧮 Калькулятор", self.open_calculator),
            ("🌐 Браузер", self.open_browser_window),
            ("📝 Блокнот", self.open_notepad)
        ]
        
        for i, (text, command) in enumerate(quick_buttons):
            row, col = divmod(i, 4)
            
            if col == 0:
                row_frame = tk.Frame(quick_frame, bg=self.colors['bg'])
                row_frame.pack(pady=5)
            
            btn = tk.Button(row_frame, text=text, bg=self.colors['bg_lighter'], 
                          fg=self.colors['primary'], font=('Segoe UI', 10),
                          bd=0, padx=15, pady=8, cursor="hand2", command=command)
            btn.pack(side=tk.LEFT, padx=5)
    
    def create_automation_tab(self):
        """Вкладка автоматизации"""
        auto_frame = tk.Frame(self.notebook, bg=self.colors['bg'])
        self.notebook.add(auto_frame, text='🤖 Автоматизация')
        
        # Заголовок
        title_label = tk.Label(auto_frame, text="Автоматизация задач",
                              bg=self.colors['bg'], fg=self.colors['text'],
                              font=('Segoe UI', 24, 'bold'))
        title_label.pack(pady=(20, 30))
        
        # Список задач
        tasks_frame = tk.Frame(auto_frame, bg=self.colors['bg_lighter'],
                              relief=tk.FLAT, bd=0, padx=20, pady=20)
        tasks_frame.pack(pady=10, padx=50, fill=tk.BOTH, expand=True)
        
        tk.Label(tasks_frame, text="📋 Задачи автоматизации",
                bg=self.colors['bg_lighter'], fg=self.colors['text'],
                font=('Segoe UI', 16, 'bold')).pack(anchor='w', pady=(0, 20))
        
        # Список задач
        self.tasks_listbox = tk.Listbox(tasks_frame,
                                       bg=self.colors['bg'],
                                       fg=self.colors['text'],
                                       font=('Segoe UI', 10),
                                       height=8,
                                       relief=tk.FLAT)
        self.tasks_listbox.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Поле для новой задачи
        input_frame = tk.Frame(tasks_frame, bg=self.colors['bg_lighter'])
        input_frame.pack(fill=tk.X)
        
        self.new_task_var = tk.StringVar()
        task_entry = tk.Entry(input_frame, textvariable=self.new_task_var,
                            font=('Segoe UI', 11), bg=self.colors['bg'],
                            fg=self.colors['text'], width=40)
        task_entry.pack(side=tk.LEFT, padx=(0, 10), fill=tk.X, expand=True)
        
        # Кнопки
        buttons_frame = tk.Frame(tasks_frame, bg=self.colors['bg_lighter'])
        buttons_frame.pack()
        
        add_btn = tk.Button(buttons_frame, text="➕ Добавить",
                          bg=self.colors['success'], fg='white',
                          font=('Segoe UI', 10), bd=0, padx=15, pady=8,
                          cursor="hand2", command=self.add_automation_task)
        add_btn.pack(side=tk.LEFT, padx=5)
        
        remove_btn = tk.Button(buttons_frame, text="🗑️ Удалить",
                             bg=self.colors['danger'], fg='white',
                             font=('Segoe UI', 10), bd=0, padx=15, pady=8,
                             cursor="hand2", command=self.remove_automation_task)
        remove_btn.pack(side=tk.LEFT, padx=5)
        
        run_btn = tk.Button(buttons_frame, text="▶️ Выполнить",
                          bg=self.colors['primary'], fg='white',
                          font=('Segoe UI', 10), bd=0, padx=15, pady=8,
                          cursor="hand2", command=self.run_automation_tasks)
        run_btn.pack(side=tk.LEFT, padx=5)
        
        # Шаблоны задач
        templates_frame = tk.Frame(auto_frame, bg=self.colors['bg_lighter'],
                                  relief=tk.FLAT, bd=0, padx=20, pady=20)
        templates_frame.pack(pady=20, padx=50, fill=tk.X)
        
        tk.Label(templates_frame, text="🎯 Шаблоны задач",
                bg=self.colors['bg_lighter'], fg=self.colors['text'],
                font=('Segoe UI', 16, 'bold')).pack(anchor='w', pady=(0, 20))
        
        templates = [
            "Открыть все социальные сети",
            "Проверить почту и новости",
            "Запустить рабочие приложения",
            "Сделать скриншот экрана",
            "Очистить историю браузера"
        ]
        
        for template in templates:
            btn = tk.Button(templates_frame, text=template,
                          bg=self.colors['bg'], fg=self.colors['primary'],
                          font=('Segoe UI', 10), bd=0, padx=15, pady=8,
                          cursor="hand2",
                          command=lambda t=template: self.add_template_task(t))
            btn.pack(side=tk.LEFT, padx=5)
    
    def create_development_tab(self):
        """Вкладка разработки"""
        dev_frame = tk.Frame(self.notebook, bg=self.colors['bg'])
        self.notebook.add(dev_frame, text='💻 Разработка')
        
        # Заголовок
        title_label = tk.Label(dev_frame, text="Инструменты разработчика",
                              bg=self.colors['bg'], fg=self.colors['text'],
                              font=('Segoe UI', 24, 'bold'))
        title_label.pack(pady=(20, 30))
        
        # Code Editor
        editor_frame = tk.Frame(dev_frame, bg=self.colors['bg_lighter'],
                               relief=tk.FLAT, bd=0, padx=20, pady=20)
        editor_frame.pack(pady=10, padx=50, fill=tk.BOTH, expand=True)
        
        tk.Label(editor_frame, text="📝 Редактор кода",
                bg=self.colors['bg_lighter'], fg=self.colors['text'],
                font=('Segoe UI', 16, 'bold')).pack(anchor='w', pady=(0, 20))
        
        # Простой редактор кода
        self.code_text = scrolledtext.ScrolledText(
            editor_frame,
            height=15,
            bg='#1e1e1e',
            fg='#ffffff',
            font=('Consolas', 10),
            wrap=tk.WORD,
            relief=tk.FLAT,
            borderwidth=0,
            padx=15,
            pady=15,
            insertbackground='white'
        )
        self.code_text.pack(fill=tk.BOTH, expand=True)
        
        # Пример кода
        example_code = '''# Пример кода Python
def fibonacci(n):
    """Возвращает n-ное число Фибоначчи"""
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

# Вывод первых 10 чисел
for i in range(10):
    print(f"Fibonacci({i}) = {fibonacci(i)}")'''
        
        self.code_text.insert(tk.END, example_code)
        
        # Кнопки редактора
        buttons_frame = tk.Frame(editor_frame, bg=self.colors['bg_lighter'])
        buttons_frame.pack(pady=10)
        
        run_btn = tk.Button(buttons_frame, text="▶️ Выполнить",
                          bg=self.colors['success'], fg='white',
                          font=('Segoe UI', 10), bd=0, padx=15, pady=8,
                          cursor="hand2", command=self.run_code)
        run_btn.pack(side=tk.LEFT, padx=5)
        
        clear_btn = tk.Button(buttons_frame, text="🗑️ Очистить",
                            bg=self.colors['danger'], fg='white',
                            font=('Segoe UI', 10), bd=0, padx=15, pady=8,
                            cursor="hand2", command=lambda: self.code_text.delete(1.0, tk.END))
        clear_btn.pack(side=tk.LEFT, padx=5)
        
        save_btn = tk.Button(buttons_frame, text="💾 Сохранить",
                           bg=self.colors['primary'], fg='white',
                           font=('Segoe UI', 10), bd=0, padx=15, pady=8,
                           cursor="hand2", command=self.save_code)
        save_btn.pack(side=tk.LEFT, padx=5)
        
        # Консоль вывода
        console_frame = tk.Frame(dev_frame, bg=self.colors['bg_lighter'],
                                relief=tk.FLAT, bd=0, padx=20, pady=20)
        console_frame.pack(pady=20, padx=50, fill=tk.BOTH, expand=True)
        
        tk.Label(console_frame, text="📊 Консоль вывода",
                bg=self.colors['bg_lighter'], fg=self.colors['text'],
                font=('Segoe UI', 16, 'bold')).pack(anchor='w', pady=(0, 20))
        
        self.console_output = scrolledtext.ScrolledText(
            console_frame,
            height=8,
            bg='#0f172a',
            fg='#ffffff',
            font=('Consolas', 9),
            wrap=tk.WORD,
            relief=tk.FLAT,
            borderwidth=0,
            padx=15,
            pady=15,
            state=tk.DISABLED
        )
        self.console_output.pack(fill=tk.BOTH, expand=True)
    
    def create_ai_tab(self):
        """Вкладка ИИ-ассистента"""
        ai_frame = tk.Frame(self.notebook, bg=self.colors['bg'])
        self.notebook.add(ai_frame, text='🤖 ИИ Ассистент')
        
        # Заголовок
        title_label = tk.Label(ai_frame, text="Искусственный интеллект",
                              bg=self.colors['bg'], fg=self.colors['text'],
                              font=('Segoe UI', 24, 'bold'))
        title_label.pack(pady=(20, 10))
        
        # Описание
        desc_label = tk.Label(ai_frame, 
                             text="Обучайте нейросети, делайте предсказания и анализируйте данные",
                             bg=self.colors['bg'], fg=self.colors['text_secondary'],
                             font=('Segoe UI', 12))
        desc_label.pack(pady=(0, 30))
        
        # Панель управления ИИ
        control_frame = tk.Frame(ai_frame, bg=self.colors['bg_lighter'],
                                relief=tk.FLAT, bd=0, padx=20, pady=20)
        control_frame.pack(pady=10, padx=50, fill=tk.X)
        
        tk.Label(control_frame, text="🤖 Управление ИИ-ассистентом",
                bg=self.colors['bg_lighter'], fg=self.colors['text'],
                font=('Segoe UI', 16, 'bold')).pack(anchor='w', pady=(0, 20))
        
        # Кнопки управления
        buttons_frame = tk.Frame(control_frame, bg=self.colors['bg_lighter'])
        buttons_frame.pack()
        
        ai_buttons = [
            ("🧠 Обучить нейросеть", self.train_neural_network_ui),
            ("🌲 Случайный лес", self.train_random_forest_ui),
            ("📊 Анализ данных", self.analyze_data_ui),
            ("💾 Сохранить модели", self.save_ai_models),
            ("📈 Статус", self.show_ai_status),
            ("❓ Помощь", self.show_ai_help)
        ]
        
        for i, (text, command) in enumerate(ai_buttons):
            row, col = divmod(i, 3)
            
            if col == 0:
                row_frame = tk.Frame(buttons_frame, bg=self.colors['bg_lighter'])
                row_frame.pack(pady=5)
            
            btn = tk.Button(row_frame, text=text, bg=self.colors['primary'], 
                          fg='white', font=('Segoe UI', 10),
                          bd=0, padx=15, pady=8, cursor="hand2", command=command)
            btn.pack(side=tk.LEFT, padx=5)
        
        # Область предсказаний
        predict_frame = tk.Frame(ai_frame, bg=self.colors['bg_lighter'],
                                relief=tk.FLAT, bd=0, padx=20, pady=20)
        predict_frame.pack(pady=20, padx=50, fill=tk.X)
        
        tk.Label(predict_frame, text="📊 Сделать предсказание",
                bg=self.colors['bg_lighter'], fg=self.colors['text'],
                font=('Segoe UI', 16, 'bold')).pack(anchor='w', pady=(0, 20))
        
        # Ввод данных
        input_frame = tk.Frame(predict_frame, bg=self.colors['bg_lighter'])
        input_frame.pack()
        
        tk.Label(input_frame, text="Входные данные (через запятую):",
                bg=self.colors['bg_lighter'], fg=self.colors['text_secondary'],
                font=('Segoe UI', 11)).pack(anchor='w', pady=(0, 5))
        
        self.ai_input_data = tk.StringVar(value="0.5, -0.2, 0.8, 0.1, 0.3")
        ai_input_entry = tk.Entry(input_frame, textvariable=self.ai_input_data,
                                 font=('Segoe UI', 11), bg=self.colors['bg'],
                                 fg=self.colors['text'], insertbackground=self.colors['text'],
                                 relief=tk.FLAT, width=50)
        ai_input_entry.pack(anchor='w', pady=(0, 15))
        
        # Выбор модели
        model_frame = tk.Frame(input_frame, bg=self.colors['bg_lighter'])
        model_frame.pack(anchor='w', pady=(0, 15))
        
        tk.Label(model_frame, text="Модель:",
                bg=self.colors['bg_lighter'], fg=self.colors['text_secondary'],
                font=('Segoe UI', 11)).pack(side=tk.LEFT, padx=(0, 10))
        
        self.ai_model_var = tk.StringVar()
        model_combo = ttk.Combobox(model_frame, textvariable=self.ai_model_var,
                                  values=list(self.ai_assistant.models.keys()),
                                  state='readonly', width=30, font=('Segoe UI', 10))
        model_combo.pack(side=tk.LEFT)
        
        # Кнопка предсказания
        predict_btn = tk.Button(input_frame, text="🔮 Сделать предсказание",
                              bg=self.colors['success'], fg='white',
                              font=('Segoe UI', 10, 'bold'), bd=0, padx=20, pady=10,
                              cursor="hand2", command=self.make_ai_prediction)
        predict_btn.pack(anchor='w')
        
        # Результат
        self.ai_result_text = tk.Text(ai_frame, height=6, width=80,
                                     bg=self.colors['bg_lighter'],
                                     fg=self.colors['text'],
                                     font=('Consolas', 10),
                                     wrap=tk.WORD,
                                     relief=tk.FLAT,
                                     borderwidth=0,
                                     padx=15,
                                     pady=15)
        self.ai_result_text.pack(pady=20, padx=50, fill=tk.X)
        self.ai_result_text.insert(tk.END, "Здесь будут отображаться результаты работы ИИ...")
        self.ai_result_text.config(state=tk.DISABLED)
    
    def train_neural_network_ui(self):
        """Интерфейс для обучения нейросети"""
        train_window = tk.Toplevel(self.root)
        train_window.title("Обучение нейросети")
        train_window.geometry("500x400")
        train_window.configure(bg=self.colors['bg'])
        
        self.center_window(train_window)
        
        tk.Label(train_window, text="🧠 Обучение нейронной сети",
                bg=self.colors['bg'], fg=self.colors['text'],
                font=('Segoe UI', 16, 'bold')).pack(pady=20)
        
        # Тип задачи
        tk.Label(train_window, text="Тип задачи:",
                bg=self.colors['bg'], fg=self.colors['text_secondary'],
                font=('Segoe UI', 11)).pack(anchor='w', padx=50, pady=(0, 5))
        
        task_var = tk.StringVar(value="classification")
        task_frame = tk.Frame(train_window, bg=self.colors['bg'])
        task_frame.pack(anchor='w', padx=50, pady=(0, 15))
        
        tk.Radiobutton(task_frame, text="Классификация", variable=task_var, 
                      value="classification", bg=self.colors['bg'],
                      fg=self.colors['text']).pack(side=tk.LEFT, padx=10)
        tk.Radiobutton(task_frame, text="Регрессия", variable=task_var,
                      value="regression", bg=self.colors['bg'],
                      fg=self.colors['text']).pack(side=tk.LEFT, padx=10)
        
        # Количество образцов
        tk.Label(train_window, text="Количество образцов:",
                bg=self.colors['bg'], fg=self.colors['text_secondary'],
                font=('Segoe UI', 11)).pack(anchor='w', padx=50, pady=(0, 5))
        
        samples_var = tk.IntVar(value=100)
        samples_spin = tk.Spinbox(train_window, from_=10, to=1000, 
                                 textvariable=samples_var,
                                 font=('Segoe UI', 11), bg=self.colors['bg_lighter'],
                                 fg=self.colors['text'], width=10)
        samples_spin.pack(anchor='w', padx=50, pady=(0, 15))
        
        # Кнопки
        button_frame = tk.Frame(train_window, bg=self.colors['bg'])
        button_frame.pack(pady=30)
        
        def start_training():
            task = task_var.get()
            samples = samples_var.get()
            
            if task == "classification":
                query = "обучи нейросеть для классификации"
            else:
                query = "обучи нейросеть для регрессии"
            
            result = self.ai_assistant.enhanced_process_query(query)
            
            # Обновляем список моделей
            self.update_ai_model_list()
            
            # Показываем результат
            self.ai_result_text.config(state=tk.NORMAL)
            self.ai_result_text.delete(1.0, tk.END)
            self.ai_result_text.insert(tk.END, result)
            self.ai_result_text.config(state=tk.DISABLED)
            
            self.speak("Нейросеть обучена!")
            train_window.destroy()
        
        train_btn = tk.Button(button_frame, text="🚀 Начать обучение",
                            bg=self.colors['success'], fg='white',
                            font=('Segoe UI', 10, 'bold'), bd=0, padx=20, pady=10,
                            cursor="hand2", command=start_training)
        train_btn.pack(side=tk.LEFT, padx=10)
        
        cancel_btn = tk.Button(button_frame, text="❌ Отмена",
                             bg=self.colors['danger'], fg='white',
                             font=('Segoe UI', 10, 'bold'), bd=0, padx=20, pady=10,
                             cursor="hand2", command=train_window.destroy)
        cancel_btn.pack(side=tk.LEFT, padx=10)
    
    def train_random_forest_ui(self):
        """Интерфейс для обучения случайного леса"""
        query = "создай случайный лес"
        result = self.ai_assistant.enhanced_process_query(query)
        
        self.ai_result_text.config(state=tk.NORMAL)
        self.ai_result_text.delete(1.0, tk.END)
        self.ai_result_text.insert(tk.END, result)
        self.ai_result_text.config(state=tk.DISABLED)
        
        self.update_ai_model_list()
        self.speak("Случайный лес создан!")
    
    def analyze_data_ui(self):
        """Анализ данных через ИИ"""
        result = self.ai_assistant.analyze_data("анализ")
        
        self.ai_result_text.config(state=tk.NORMAL)
        self.ai_result_text.delete(1.0, tk.END)
        self.ai_result_text.insert(tk.END, result)
        self.ai_result_text.config(state=tk.DISABLED)
        
        self.speak("Данные проанализированы!")
    
    def save_ai_models(self):
        """Сохранение моделей ИИ"""
        result = self.ai_assistant.process_query("сохрани все модели")
        
        self.ai_result_text.config(state=tk.NORMAL)
        self.ai_result_text.delete(1.0, tk.END)
        self.ai_result_text.insert(tk.END, result)
        self.ai_result_text.config(state=tk.DISABLED)
        
        self.speak("Модели сохранены!")
    
    def show_ai_status(self):
        """Показать статус ИИ"""
        result = self.ai_assistant.show_status()
        
        self.ai_result_text.config(state=tk.NORMAL)
        self.ai_result_text.delete(1.0, tk.END)
        self.ai_result_text.insert(tk.END, result)
        self.ai_result_text.config(state=tk.DISABLED)
        
        self.speak("Статус показан!")
    
    def show_ai_help(self):
        """Показать справку ИИ"""
        result = self.ai_assistant.show_help()
        
        self.ai_result_text.config(state=tk.NORMAL)
        self.ai_result_text.delete(1.0, tk.END)
        self.ai_result_text.insert(tk.END, result)
        self.ai_result_text.config(state=tk.DISABLED)
        
        self.speak("Справка показана!")
    
    def make_ai_prediction(self):
        """Сделать предсказание с помощью ИИ"""
        input_data = self.ai_input_data.get()
        model_name = self.ai_model_var.get()
        
        if not input_data:
            messagebox.showerror("Ошибка", "Введите данные для предсказания")
            return
        
        if not model_name:
            messagebox.showerror("Ошибка", "Выберите модель")
            return
        
        query = f"предскажи по модели {model_name} данные: {input_data}"
        result = self.ai_assistant.enhanced_process_query(query)
        
        self.ai_result_text.config(state=tk.NORMAL)
        self.ai_result_text.delete(1.0, tk.END)
        self.ai_result_text.insert(tk.END, f"Запрос: {query}\n\nРезультат:\n{result}")
        self.ai_result_text.config(state=tk.DISABLED)
        
        self.speak("Предсказание выполнено!")
    
    def update_ai_model_list(self):
        """Обновление списка моделей в комбобоксе"""
        model_names = list(self.ai_assistant.models.keys())
        if model_names:
            self.ai_model_var.set(model_names[0])
        
        # Получаем виджет комбобокса
        for widget in self.notebook.winfo_children():
            if isinstance(widget, tk.Frame):
                for child in widget.winfo_children():
                    if isinstance(child, ttk.Combobox):
                        if child.get() == "" and model_names:
                            child['values'] = model_names
                            child.set(model_names[0])
    
    def open_ai_assistant(self):
        """Открыть ИИ-ассистента"""
        # Переключаемся на вкладку ИИ
        self.notebook.select(6)
        
        # Показываем справку
        result = self.ai_assistant.show_help()
        
        self.ai_result_text.config(state=tk.NORMAL)
        self.ai_result_text.delete(1.0, tk.END)
        self.ai_result_text.insert(tk.END, result)
        self.ai_result_text.config(state=tk.DISABLED)
        
        self.speak("ИИ-ассистент открыт! Я готов помогать вам с задачами машинного обучения.")
    
    def create_social_tab(self):
        """Вкладка социальных сетей"""
        social_frame = tk.Frame(self.notebook, bg=self.colors['bg'])
        self.notebook.add(social_frame, text='👥 Соцсети')
        
        # Заголовок
        title_label = tk.Label(social_frame, text="Социальные сети и мессенджеры",
                              bg=self.colors['bg'], fg=self.colors['text'],
                              font=('Segoe UI', 24, 'bold'))
        title_label.pack(pady=(20, 30))
        
        # Сетка соцсетей
        socials_frame = tk.Frame(social_frame, bg=self.colors['bg'])
        socials_frame.pack(pady=20)
        
        social_buttons = list(self.settings["social_networks"].items())
        
        for i, (name, url) in enumerate(social_buttons):
            row, col = divmod(i, 4)
            
            if col == 0:
                row_frame = tk.Frame(socials_frame, bg=self.colors['bg'])
                row_frame.pack(pady=10)
            
            card = tk.Frame(row_frame, bg=self.colors['bg_lighter'], 
                           relief=tk.FLAT, bd=0, width=150, height=80)
            card.pack_propagate(False)
            card.pack(side=tk.LEFT, padx=10)
            
            # Иконка
            icon_label = tk.Label(card, text=self.get_social_icon(name),
                                 bg=self.colors['bg_lighter'], fg=self.colors['primary'],
                                 font=('Segoe UI Emoji', 20))
            icon_label.pack(pady=(10, 5))
            
            # Название
            name_label = tk.Label(card, text=name, bg=self.colors['bg_lighter'],
                                 fg=self.colors['text'], font=('Segoe UI', 9))
            name_label.pack()
            
            # Привязываем событие клика
            card.bind("<Button-1>", lambda e, u=url, n=name: self.open_url_with_voice(u, n))
            icon_label.bind("<Button-1>", lambda e, u=url, n=name: self.open_url_with_voice(u, n))
            name_label.bind("<Button-1>", lambda e, u=url, n=name: self.open_url_with_voice(u, n))
            
            # Меняем курсор
            for widget in [card, icon_label, name_label]:
                widget.bind("<Enter>", lambda e, w=widget: w.config(cursor="hand2"))
    
    def get_social_icon(self, social_name):
        """Получение иконки для соцсети"""
        icons = {
            'ВКонтакте': '👥',
            'Одноклассники': '👨‍👩‍👧‍👦',
            'Telegram': '📨',
            'WhatsApp Web': '💬',
            'Discord': '🎮',
            'Twitter': '🐦',
            'Facebook': '📘',
            'Instagram': '📷',
            'YouTube': '🎥',
            'Twitch': '🕹️',
            'DeepSeek AI': '🤖'
        }
        return icons.get(social_name, '🌐')
    
    def open_url_with_voice(self, url, name):
        """Открыть URL с озвучкой"""
        self.open_url(url)
        self.speak(f"Открываю {name}")
    
    def create_media_tab(self):
        """Вкладка медиа"""
        media_frame = tk.Frame(self.notebook, bg=self.colors['bg'])
        self.notebook.add(media_frame, text='🎵 Медиа')
        
        # Заголовок
        title_label = tk.Label(media_frame, text="Медиа и развлечения",
                              bg=self.colors['bg'], fg=self.colors['text'],
                              font=('Segoe UI', 24, 'bold'))
        title_label.pack(pady=(20, 30))
        
        # Видеопоиск
        video_frame = tk.Frame(media_frame, bg=self.colors['bg_lighter'],
                              relief=tk.FLAT, bd=0, padx=20, pady=20)
        video_frame.pack(pady=10, padx=50, fill=tk.X)
        
        tk.Label(video_frame, text="🎬 Поиск видео",
                bg=self.colors['bg_lighter'], fg=self.colors['text'],
                font=('Segoe UI', 16, 'bold')).pack(anchor='w', pady=(0, 20))
        
        search_frame = tk.Frame(video_frame, bg=self.colors['bg_lighter'])
        search_frame.pack()
        
        self.video_search_query = tk.StringVar()
        video_entry = tk.Entry(search_frame, textvariable=self.video_search_query,
                              font=('Segoe UI', 11), bg=self.colors['bg'],
                              fg=self.colors['text'], insertbackground=self.colors['text'],
                              relief=tk.FLAT, width=40)
        video_entry.pack(side=tk.LEFT, padx=(0, 10))
        
        video_btn = tk.Button(search_frame, text="🔍 Искать видео",
                             bg=self.colors['primary'], fg='white',
                             font=('Segoe UI', 10, 'bold'), bd=0, padx=15, pady=8,
                             cursor="hand2", command=self.search_and_play_video)
        video_btn.pack(side=tk.LEFT)
        
        # Радио
        radio_frame = tk.Frame(media_frame, bg=self.colors['bg_lighter'],
                              relief=tk.FLAT, bd=0, padx=20, pady=20)
        radio_frame.pack(pady=20, padx=50, fill=tk.X)
        
        tk.Label(radio_frame, text="📻 Интернет-радио",
                bg=self.colors['bg_lighter'], fg=self.colors['text'],
                font=('Segoe UI', 16, 'bold')).pack(anchor='w', pady=(0, 20))
        
        radio_stations = [
            ("Европа Плюс", "http://ep128.hostingradio.ru:8030/ep128"),
            ("Русское Радио", "http://rusradio.hostingradio.ru/rusradio96.aacp"),
            ("Ди-FM", "http://dfm.hostingradio.ru/dfm96.aacp"),
            ("Наше Радио", "http://nashe1.hostingradio.ru/nashe-256")
        ]
        
        stations_frame = tk.Frame(radio_frame, bg=self.colors['bg_lighter'])
        stations_frame.pack()
        
        for name, url in radio_stations:
            btn = tk.Button(stations_frame, text=name, bg=self.colors['primary'],
                          fg='white', font=('Segoe UI', 10, 'bold'), bd=0,
                          padx=15, pady=8, cursor="hand2",
                          command=lambda u=url, n=name: self.play_radio_with_voice(u, n))
            btn.pack(side=tk.LEFT, padx=10)
    
    def play_radio_with_voice(self, url, name):
        """Воспроизведение радио с озвучкой"""
        self.play_radio(url)
        self.speak(f"Запускаю радио {name}")
    
    def create_tools_tab(self):
        """Вкладка инструментов"""
        tools_frame = tk.Frame(self.notebook, bg=self.colors['bg'])
        self.notebook.add(tools_frame, text='🛠️ Инструменты')
        
        # Заголовок
        title_label = tk.Label(tools_frame, text="Инструменты и утилиты",
                              bg=self.colors['bg'], fg=self.colors['text'],
                              font=('Segoe UI', 24, 'bold'))
        title_label.pack(pady=(20, 30))
        
        # Калькулятор
        calc_frame = tk.Frame(tools_frame, bg=self.colors['bg_lighter'],
                             relief=tk.FLAT, bd=0, padx=20, pady=20)
        calc_frame.pack(pady=10, padx=50, fill=tk.X)
        
        tk.Label(calc_frame, text="🧮 Калькулятор",
                bg=self.colors['bg_lighter'], fg=self.colors['text'],
                font=('Segoe UI', 16, 'bold')).pack(anchor='w', pady=(0, 20))
        
        # Поле калькулятора
        self.calc_display = tk.StringVar(value="0")
        calc_entry = tk.Entry(calc_frame, textvariable=self.calc_display,
                             font=('Segoe UI', 14), bg=self.colors['bg'],
                             fg=self.colors['text'], insertbackground=self.colors['text'],
                             relief=tk.FLAT, justify=tk.RIGHT, width=30)
        calc_entry.pack(pady=(0, 20))
        
        # Кнопки калькулятора
        calc_buttons = [
            ('7', '8', '9', '/'),
            ('4', '5', '6', '*'),
            ('1', '2', '3', '-'),
            ('0', '.', '=', '+')
        ]
        
        for i, row in enumerate(calc_buttons):
            row_frame = tk.Frame(calc_frame, bg=self.colors['bg_lighter'])
            row_frame.pack()
            
            for btn_text in row:
                color = self.colors['primary'] if btn_text.isdigit() or btn_text == '.' else \
                       self.colors['success'] if btn_text == '=' else \
                       self.colors['warning']
                
                btn = tk.Button(row_frame, text=btn_text, bg=color, fg='white',
                              font=('Segoe UI', 12, 'bold'), bd=0, width=4, height=2,
                              cursor="hand2", command=lambda t=btn_text: self.calc_button_click(t))
                btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        # Другие инструменты
        tools_frame2 = tk.Frame(tools_frame, bg=self.colors['bg_lighter'],
                               relief=tk.FLAT, bd=0, padx=20, pady=20)
        tools_frame2.pack(pady=20, padx=50, fill=tk.X)
        
        tk.Label(tools_frame2, text="📊 Другие инструменты",
                bg=self.colors['bg_lighter'], fg=self.colors['text'],
                font=('Segoe UI', 16, 'bold')).pack(anchor='w', pady=(0, 20))
        
        # Кнопки инструментов
        tools_buttons = [
            ("📁 Проводник", self.open_file_explorer),
            ("🎨 Paint", self.open_paint),
            ("📝 Блокнот", self.open_notepad),
            ("🕐 Часы", self.show_clock),
            ("🌐 Браузер", self.open_browser_window),
            ("🌤️ Погода", self.open_weather),
            ("🤖 DeepSeek", self.open_deepseek),
            ("⚙️ Настройки", self.open_settings)
        ]
        
        for i, (text, command) in enumerate(tools_buttons):
            row, col = divmod(i, 4)
            
            if col == 0:
                row_frame = tk.Frame(tools_frame2, bg=self.colors['bg_lighter'])
                row_frame.pack(pady=5)
            
            btn = tk.Button(row_frame, text=text, bg=self.colors['bg'], 
                          fg=self.colors['primary'], font=('Segoe UI', 10),
                          bd=0, padx=15, pady=8, cursor="hand2", command=command)
            btn.pack(side=tk.LEFT, padx=5)
    
    def create_help_tab(self):
        """Вкладка помощи"""
        help_frame = tk.Frame(self.notebook, bg=self.colors['bg'])
        self.notebook.add(help_frame, text='❓ Помощь')
        
        # Информация о программе
        info_text = f"""⚛️ Атом v4.0 PRO

Версия: 4.0 PRO (с расширенными функциями ИИ)
Режим: {'Демонстрационный' if self.demo_mode else 'Рабочий'}
Пользователь: {self.current_user if self.logged_in else 'Гость'}
Голосовой помощник: {'Доступен' if SPEECH_AVAILABLE else 'Не доступен'}

Новые функции v4.0:
• Улучшенный ИИ-ассистент с анализатором настроения
• 🤖 Автоматизация повседневных задач
• 💻 Редактор кода с выполнением Python
• Система рекомендаций
• Простой переводчик
• Генератор кода
• Частицы на фоне
• Горячие клавиши (Ctrl+Q, Ctrl+S, Ctrl+R)
• Панель быстрого доступа

Горячие клавиши:
• Ctrl+Q - Быстрый доступ
• Ctrl+S - Сохранить всё
• Ctrl+R - Обновить интерфейс
• F1 - Справка
• F2 - Скриншот

© 2024 Разработано для демонстрации возможностей ИИ"""
        
        info_label = tk.Label(help_frame, text=info_text, bg=self.colors['bg'],
                             fg=self.colors['text'], font=('Segoe UI', 11),
                             justify=tk.LEFT)
        info_label.pack(pady=50, padx=50)
        
        # Голосовые команды
        if SPEECH_AVAILABLE or VOICE_INPUT_AVAILABLE:
            commands_frame = tk.Frame(help_frame, bg=self.colors['bg_lighter'],
                                     relief=tk.FLAT, bd=0, padx=20, pady=20)
            commands_frame.pack(pady=20, padx=50, fill=tk.X)
            
            tk.Label(commands_frame, text="🎤 Голосовые команды",
                    bg=self.colors['bg_lighter'], fg=self.colors['text'],
                    font=('Segoe UI', 16, 'bold')).pack(anchor='w', pady=(0, 20))
            
            commands_text = """Доступные голосовые команды:

• "Атом" - активация по ключевому слову
• "Поиск [запрос]" - поиск в интернете
• "Открой [сайт]" - открыть сайт
• "Погода" - показать погоду
• "Калькулятор" - открыть калькулятор
• "Время" - показать текущее время
• "Браузер" - открыть браузер
• "Блокнот" - открыть блокнот
• "Дипсик" или "DeepSeek" - открыть DeepSeek AI

НОВЫЕ КОМАНДЫ v4.0:
• "Добавь задачу [текст]" - добавить задачу автоматизации
• "Покажи задачи" - показать список задач
• "Выполни задачи" - запустить задачи автоматизации
• "Новый код" - очистить редактор кода
• "Сохрани код" - сохранить код из редактора
• "Скриншот" - сделать снимок экрана
• "Проанализируй текст [текст]" - анализ настроения текста
• "Что на экране" - прочитать содержимое экрана (демо)

ИИ-КОМАНДЫ:
• "Обучи нейросеть" - обучить нейросеть
• "Предскажи с помощью [модель]" - сделать предсказание
• "Анализ данных" - проанализировать данные
• "Рекомендация" - получить рекомендацию
• "Переведи [текст]" - перевести текст

СИСТЕМНЫЕ КОМАНДЫ:
• "Стоп" - остановить голосового помощника
• "Настройки" - открыть настройки
• "Помощь" - показать справку
• "Выйти" - выход из программы"""
            
            commands_label = tk.Label(commands_frame, text=commands_text,
                                     bg=self.colors['bg_lighter'], fg=self.colors['text_secondary'],
                                     font=('Segoe UI', 9), justify=tk.LEFT)
            commands_label.pack(anchor='w')
    
    def create_log_tab(self):
        """Вкладка лога сообщений"""
        log_frame = tk.Frame(self.notebook, bg=self.colors['bg'])
        self.notebook.add(log_frame, text='📝 Лог')
        
        # Заголовок
        title_label = tk.Label(log_frame, text="Журнал событий",
                              bg=self.colors['bg'], fg=self.colors['text'],
                              font=('Segoe UI', 24, 'bold'))
        title_label.pack(pady=20)
        
        # Текстовая область лога
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            bg=self.colors['bg_lighter'],
            fg=self.colors['text'],
            font=("Consolas", 10),
            wrap=tk.WORD,
            height=25,
            relief=tk.FLAT,
            borderwidth=0,
            padx=15,
            pady=15
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        self.log_text.config(state=tk.DISABLED)
    
    def create_status_bar(self):
        """Создание статус бара"""
        status_frame = tk.Frame(self.root, bg=self.colors['bg_light'], height=40)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Статус
        self.status_label = tk.Label(status_frame, text="Готов",
                                    bg=self.colors['bg_light'],
                                    fg=self.colors['text_secondary'],
                                    font=('Segoe UI', 10))
        self.status_label.pack(side=tk.LEFT, padx=20)
        
        # Режим
        mode_text = "Демо-режим" if self.demo_mode else "Рабочий режим"
        self.mode_label = tk.Label(status_frame,
                                  text=f"Режим: {mode_text}",
                                  bg=self.colors['bg_light'],
                                  fg=self.colors['warning'] if self.demo_mode else self.colors['success'],
                                  font=('Segoe UI', 10))
        self.mode_label.pack(side=tk.LEFT, padx=20)
        
        # Время
        self.time_label = tk.Label(status_frame,
                                  text=time.strftime("%H:%M:%S"),
                                  bg=self.colors['bg_light'],
                                  fg=self.colors['text'],
                                  font=('Segoe UI', 10))
        self.time_label.pack(side=tk.RIGHT, padx=20)
        
        # Обновление времени
        self.update_time()
    
    def update_time(self):
        """Обновление времени в статус баре"""
        if not self.running or not self.root.winfo_exists():
            return
            
        current_time = time.strftime("%H:%M:%S")
        try:
            self.time_label.config(text=current_time)
            self.root.after(1000, self.update_time)
        except tk.TclError:
            pass
    
    def add_automation_task(self):
        """Добавление задачи автоматизации"""
        task = self.new_task_var.get().strip()
        if task:
            self.automation_tasks.append(task)
            self.tasks_listbox.insert(tk.END, f"✓ {task}")
            self.new_task_var.set("")
            self.speak(f"Задача добавлена: {task}")
    
    def remove_automation_task(self):
        """Удаление задачи автоматизации"""
        selection = self.tasks_listbox.curselection()
        if selection:
            index = selection[0]
            task = self.automation_tasks.pop(index)
            self.tasks_listbox.delete(index)
            self.speak(f"Задача удалена: {task}")
    
    def add_template_task(self, template):
        """Добавление задачи из шаблона"""
        self.automation_tasks.append(template)
        self.tasks_listbox.insert(tk.END, f"✓ {template}")
        self.speak(f"Добавлен шаблон: {template}")
    
    def run_automation_tasks(self):
        """Выполнение задач автоматизации"""
        if not self.automation_tasks:
            self.speak("Нет задач для выполнения")
            return
        
        self.speak(f"Начинаю выполнение {len(self.automation_tasks)} задач")
        
        for i, task in enumerate(self.automation_tasks, 1):
            self.message_queue.put(f"Задача {i}/{len(self.automation_tasks)}: {task}")
            self.perform_automated_task(task)
            time.sleep(1)
        
        self.speak("Все задачи выполнены")
    
    def perform_automated_task(self, task):
        """Выполнение конкретной задачи"""
        task_lower = task.lower()
        
        if "социальные сети" in task_lower:
            self.open_all_social_networks()
        elif "почт" in task_lower or "новости" in task_lower:
            self.check_news_and_mail()
        elif "приложения" in task_lower:
            self.open_work_apps()
        elif "скриншот" in task_lower:
            self.take_screenshot()
        elif "истори" in task_lower:
            self.clear_browser_history()
        else:
            self.message_queue.put(f"Выполняю: {task}")
    
    def open_all_social_networks(self):
        """Открыть все социальные сети"""
        for name, url in self.settings["social_networks"].items():
            if name != "DeepSeek AI":  # Пропускаем DeepSeek
                self.open_url(url)
                time.sleep(0.5)
        self.speak("Все социальные сети открыты")
    
    def check_news_and_mail(self):
        """Проверить новости и почту"""
        sites = [
            ("Новости", "https://news.google.com"),
            ("Почта", "https://mail.google.com"),
            ("Яндекс.Новости", "https://news.yandex.ru")
        ]
        
        for name, url in sites:
            self.open_url(url)
            time.sleep(1)
        
        self.speak("Новости и почта проверены")
    
    def open_work_apps(self):
        """Открыть рабочие приложения"""
        self.open_notepad()
        self.open_calculator()
        self.open_browser_window()
        self.speak("Рабочие приложения запущены")
    
    def take_screenshot(self):
        """Сделать скриншот (демо-версия)"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"
            
            # В реальном приложении здесь был бы код для создания скриншота
            # Но для демонстрации просто создаем файл-заглушку
            with open(filename, 'w') as f:
                f.write("Демо-скриншот\n")
            
            self.screenshots.append(filename)
            self.message_queue.put(f"Скриншот сохранен: {filename}")
            self.speak("Скриншот сделан и сохранен")
        except Exception as e:
            self.message_queue.put(f"Ошибка скриншота: {e}")
    
    def clear_browser_history(self):
        """Очистить историю браузера (демо)"""
        self.message_queue.put("История браузера очищена (демо)")
        self.speak("История браузера очищена в демонстрационном режиме")
    
    def run_code(self):
        """Выполнение кода из редактора"""
        code = self.code_text.get(1.0, tk.END).strip()
        
        if not code:
            self.speak("Нет кода для выполнения")
            return
        
        # Безопасное выполнение кода
        try:
            # Создаем безопасное окружение
            safe_globals = {
                '__builtins__': __builtins__,
                'print': lambda *args: self.code_print(*args),
                'math': math,
                'random': random,
                'time': time
            }
            
            # Выполняем код
            self.console_output.config(state=tk.NORMAL)
            self.console_output.delete(1.0, tk.END)
            self.console_output.insert(tk.END, ">>> Выполнение кода...\n\n")
            
            # Перенаправляем вывод
            exec(code, safe_globals)
            
            self.console_output.insert(tk.END, "\n>>> Код выполнен успешно!\n")
            self.console_output.see(tk.END)
            self.console_output.config(state=tk.DISABLED)
            
            self.speak("Код выполнен успешно")
            
        except Exception as e:
            self.console_output.insert(tk.END, f"\n>>> Ошибка: {str(e)}\n")
            self.console_output.see(tk.END)
            self.console_output.config(state=tk.DISABLED)
            self.speak(f"Ошибка выполнения кода: {str(e)[:50]}")
    
    def code_print(self, *args, **kwargs):
        """Кастомная функция print для редактора кода"""
        text = " ".join(str(arg) for arg in args)
        self.console_output.config(state=tk.NORMAL)
        self.console_output.insert(tk.END, text + "\n")
        self.console_output.see(tk.END)
        self.console_output.config(state=tk.DISABLED)
    
    def save_code(self):
        """Сохранение кода в файл"""
        code = self.code_text.get(1.0, tk.END).strip()
        
        if not code:
            self.speak("Нет кода для сохранения")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".py",
            filetypes=[("Python files", "*.py"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(code)
                self.message_queue.put(f"Код сохранен: {file_path}")
                self.speak("Код сохранен успешно")
            except Exception as e:
                self.message_queue.put(f"Ошибка сохранения: {e}")
                self.speak("Не удалось сохранить код")
    
    def create_quick_access_panel(self):
        """Панель быстрого доступа"""
        quick_panel = tk.Toplevel(self.root)
        quick_panel.title("Быстрый доступ")
        quick_panel.geometry("300x500")
        quick_panel.configure(bg=self.colors['bg'])
        quick_panel.attributes('-topmost', True)
        quick_panel.overrideredirect(True)
        
        # Позиция в правом верхнем углу
        screen_width = self.root.winfo_screenwidth()
        quick_panel.geometry(f"300x500+{screen_width-320}+20")
        
        # Заголовок
        title_label = tk.Label(quick_panel, text="⚡ Быстрый доступ",
                              bg=self.colors['primary'], fg='white',
                              font=('Segoe UI', 12, 'bold'), pady=10)
        title_label.pack(fill=tk.X)
        
        # Кнопки быстрого доступа
        quick_actions = [
            ("🎤 Голосовая команда", self.voice_search),
            ("📸 Скриншот", self.take_screenshot),
            ("🧮 Калькулятор", self.open_calculator),
            ("📝 Блокнот", self.open_notepad),
            ("🌐 Браузер", self.open_browser_window),
            ("🤖 ИИ Ассистент", self.open_ai_assistant),
            ("⚙️ Настройки", self.open_settings),
            ("💾 Сохранить всё", self.save_all_data),
            ("🔄 Обновить", self.refresh_interface)
        ]
        
        for text, command in quick_actions:
            btn = tk.Button(quick_panel, text=text,
                          bg=self.colors['bg_lighter'], fg=self.colors['text'],
                          font=('Segoe UI', 10), bd=0, padx=10, pady=12,
                          cursor="hand2", command=command,
                          anchor='w', width=25)
            btn.pack(pady=2, padx=10)
        
        # Кнопка закрытия
        close_btn = tk.Button(quick_panel, text="✕",
                            bg=self.colors['danger'], fg='white',
                            font=('Segoe UI', 10, 'bold'), bd=0,
                            cursor="hand2", command=quick_panel.destroy)
        close_btn.place(x=270, y=5, width=25, height=25)
    
    def save_all_data(self):
        """Сохранение всех данных программы"""
        try:
            # Сохраняем задачи автоматизации
            with open("automation_tasks.json", "w", encoding="utf-8") as f:
                json.dump(self.automation_tasks, f, ensure_ascii=False, indent=2)
            
            # Сохраняем код из редактора
            code = self.code_text.get(1.0, tk.END).strip()
            if code:
                with open("saved_code.py", "w", encoding="utf-8") as f:
                    f.write(code)
            
            # Сохраняем настройки
            self.save_settings()
            
            self.speak("Все данные сохранены успешно")
            self.message_queue.put("Все данные программы сохранены")
            
        except Exception as e:
            self.speak(f"Ошибка при сохранении данных: {str(e)[:30]}")
    
    def refresh_interface(self):
        """Обновление интерфейса"""
        self.speak("Обновляю интерфейс")
        self.message_queue.put("Обновление интерфейса...")
        
        # Перезагружаем цвета
        self.setup_colors()
        
        # Обновляем статус
        self.status_label.config(bg=self.colors['bg_light'], fg=self.colors['text_secondary'])
        
        self.speak("Интерфейс обновлен")
    
    def perform_search(self):
        """Выполнение поиска"""
        query = self.search_query.get().strip()
        if not query:
            self.speak("Введите поисковый запрос")
            self.message_queue.put("Введите поисковый запрос")
            return
        
        engine_name = self.search_engine_var.get()
        if engine_name not in self.settings["search_engines"]:
            engine_name = list(self.settings["search_engines"].keys())[0]
        
        base_url = self.settings["search_engines"][engine_name]
        search_url = base_url + quote(query.encode('utf-8'))
        
        self.open_url(search_url)
        self.message_queue.put(f"Поиск '{query}' в {engine_name}")
        self.speak(f"Ищу {query} в {engine_name}")
    
    def search_and_play_video(self):
        """Поиск и воспроизведение видео по названию"""
        query = self.video_search_query.get().strip()
        if not query:
            self.speak("Введите запрос для поиска видео")
            self.message_queue.put("Введите запрос для поиска видео")
            return
        
        search_url = f"https://www.youtube.com/results?search_query={quote(query.encode('utf-8'))}"
        
        # Открываем поиск видео
        self.open_url(search_url)
        self.message_queue.put(f"Ищу видео '{query}' на YouTube")
        self.speak(f"Ищу видео {query} на YouTube")
    
    def play_radio(self, url):
        """Воспроизведение интернет-радио"""
        try:
            self.open_url(url)
            self.message_queue.put(f"Радио запущено: {url}")
            self.speak("Запускаю интернет радио")
        except Exception as e:
            self.message_queue.put(f"Ошибка воспроизведения радио: {e}")
            self.speak("Не удалось запустить радио")
    
    def calc_button_click(self, button_text):
        """Обработка нажатия кнопки калькулятора"""
        current = self.calc_display.get()
        
        if button_text == '=':
            try:
                # Заменяем символы для eval
                expression = current.replace('×', '*').replace('÷', '/')
                result = eval(expression)
                self.calc_display.set(str(result))
                self.speak(f"Результат: {result}")
            except Exception as e:
                self.calc_display.set("Ошибка")
                self.speak("Ошибка вычисления")
                self.root.after(2000, lambda: self.calc_display.set("0"))
        elif button_text == 'C':
            self.calc_display.set("0")
        elif current == "0" or current == "Ошибка":
            self.calc_display.set(button_text)
        else:
            self.calc_display.set(current + button_text)
    
    def open_file_explorer(self):
        """Открыть проводник файлов"""
        try:
            if os.name == 'nt':  # Windows
                os.system('explorer .')
            elif os.name == 'posix':  # Linux, macOS
                os.system('xdg-open .' if os.name != 'darwin' else 'open .')
            
            self.message_queue.put("Открыт проводник файлов")
            self.speak("Открываю проводник файлов")
        except Exception as e:
            self.message_queue.put(f"Ошибка открытия проводника: {e}")
            self.speak("Не удалось открыть проводник")
    
    def open_paint(self):
        """Открыть Paint"""
        try:
            if os.name == 'nt':  # Windows
                os.system('mspaint')
            elif os.name == 'posix':  # Linux
                os.system('pinta' if os.system('which pinta') == 0 else 'krita')
            elif os.name == 'darwin':  # macOS
                os.system('open -a Paintbrush')
            
            self.message_queue.put("Открыт Paint")
            self.speak("Открываю Paint")
        except Exception as e:
            self.message_queue.put(f"Ошибка открытия Paint: {e}")
            self.speak("Не удалось открыть Paint")
    
    def open_notepad(self):
        """Открыть блокнот"""
        try:
            notepad_window = tk.Toplevel(self.root)
            notepad_window.title("Блокнот - Атом v4.0 PRO")
            notepad_window.geometry("600x400")
            notepad_window.configure(bg=self.colors['bg'])
            
            self.center_window(notepad_window)
            
            text_area = scrolledtext.ScrolledText(
                notepad_window,
                bg='#ffffff',
                fg='#000000',
                font=('Consolas', 10),
                wrap=tk.WORD,
                relief=tk.FLAT,
                borderwidth=0,
                padx=15,
                pady=15
            )
            text_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Панель инструментов
            toolbar = tk.Frame(notepad_window, bg=self.colors['bg_light'])
            toolbar.pack(fill=tk.X, padx=10, pady=(10, 0))
            
            def save_file():
                file_path = filedialog.asksaveasfilename(
                    defaultextension=".txt",
                    filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
                )
                if file_path:
                    try:
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(text_area.get(1.0, tk.END))
                        self.message_queue.put(f"Файл сохранен: {file_path}")
                        self.speak("Файл сохранен")
                    except Exception as e:
                        self.message_queue.put(f"Ошибка сохранения: {e}")
            
            def open_file():
                file_path = filedialog.askopenfilename(
                    filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
                )
                if file_path:
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            text_area.delete(1.0, tk.END)
                            text_area.insert(1.0, f.read())
                        self.message_queue.put(f"Файл открыт: {file_path}")
                        self.speak("Файл открыт")
                    except Exception as e:
                        self.message_queue.put(f"Ошибка открытия: {e}")
            
            save_btn = tk.Button(toolbar, text="💾 Сохранить", bg=self.colors['primary'],
                               fg='white', font=('Segoe UI', 9), bd=0, padx=10,
                               cursor="hand2", command=save_file)
            save_btn.pack(side=tk.LEFT, padx=5)
            
            open_btn = tk.Button(toolbar, text="📂 Открыть", bg=self.colors['success'],
                               fg='white', font=('Segoe UI', 9), bd=0, padx=10,
                               cursor="hand2", command=open_file)
            open_btn.pack(side=tk.LEFT, padx=5)
            
            clear_btn = tk.Button(toolbar, text="🗑️ Очистить", bg=self.colors['danger'],
                                fg='white', font=('Segoe UI', 9), bd=0, padx=10,
                                cursor="hand2", command=lambda: text_area.delete(1.0, tk.END))
            clear_btn.pack(side=tk.LEFT, padx=5)
            
            self.message_queue.put("Открыт блокнот")
            self.speak("Открываю блокнот")
            
        except Exception as e:
            self.message_queue.put(f"Ошибка открытия блокнота: {e}")
            self.speak("Не удалось открыть блокнот")
    
    def open_browser_window(self):
        """Открыть окно браузера"""
        try:
            browser = self.settings.get("default_browser", "default")
            browser_name = "по умолчанию"
            
            for name, key in self.settings["browsers"].items():
                if key == browser:
                    browser_name = name
                    break
            
            url = "https://chat.deepseek.com/"
            self.open_url(url)
            
            self.message_queue.put(f"Открыт браузер ({browser_name}): {url}")
            self.speak(f"Открываю браузер. Перехожу на DeepSeek AI")
            
        except Exception as e:
            self.message_queue.put(f"Ошибка открытия браузера: {e}")
            self.speak("Не удалось открыть браузер")
    
    def open_deepseek(self):
        """Открыть DeepSeek AI"""
        deepseek_url = "https://chat.deepseek.com/"
        self.open_url(deepseek_url)
        self.message_queue.put("Открываю DeepSeek AI")
        self.speak("Открываю DeepSeek AI - современный искусственный интеллект")
    
    def open_weather(self):
        """Открыть информацию о погоде"""
        city = self.settings.get("weather_city", "Москва")
        
        if self.demo_mode:
            self.show_demo_weather(city)
        else:
            search_url = f"https://www.google.com/search?q=погода+{quote(city.encode('utf-8'))}"
            self.open_url(search_url)
            self.message_queue.put(f"Погода для {city}")
            self.speak(f"Показываю погоду в городе {city}")
    
    def show_demo_weather(self, city):
        """Показать демонстрационную погоду"""
        weather_window = tk.Toplevel(self.root)
        weather_window.title(f"Демо: Погода в {city}")
        weather_window.geometry("400x300")
        weather_window.configure(bg=self.colors['bg'])
        
        self.center_window(weather_window)
        
        canvas = tk.Canvas(weather_window, bg=self.colors['bg'], highlightthickness=0)
        canvas.pack(fill=tk.BOTH, expand=True)
        
        canvas.create_text(200, 50,
                          text=f"🌤️ Погода в {city}",
                          fill=self.colors['primary_light'],
                          font=('Segoe UI', 20, 'bold'))
        
        weather_data = [
            ("Температура", f"{random.randint(-10, 30)}°C"),
            ("Ощущается как", f"{random.randint(-15, 28)}°C"),
            ("Влажность", f"{random.randint(40, 95)}%"),
            ("Ветер", f"{random.randint(0, 15)} м/с"),
            ("Давление", f"{random.randint(720, 780)} мм рт. ст."),
            ("Видимость", f"{random.randint(5, 20)} км")
        ]
        
        y_pos = 120
        for name, value in weather_data:
            canvas.create_text(150, y_pos,
                              text=name,
                              fill=self.colors['text_secondary'],
                              font=('Segoe UI', 11),
                              anchor="e")
            
            canvas.create_text(250, y_pos,
                              text=value,
                              fill=self.colors['text'],
                              font=('Segoe UI', 11, 'bold'),
                              anchor="w")
            y_pos += 30
        
        canvas.create_text(200, 250,
                          text="☀️⛅🌧️❄️",
                          fill=self.colors['primary_light'],
                          font=('Segoe UI Emoji', 24))
        
        canvas.create_text(200, 280,
                          text="Солнечно, облачно, возможен дождь",
                          fill=self.colors['text_secondary'],
                          font=('Segoe UI', 9))
        
        self.message_queue.put(f"Демо-погода для {city}")
        self.speak(f"Показываю демонстрационную погоду в городе {city}")
    
    def show_clock(self):
        """Показать часы"""
        clock_window = tk.Toplevel(self.root)
        clock_window.title("Часы - Атом v4.0 PRO")
        clock_window.geometry("300x200")
        clock_window.configure(bg=self.colors['bg'])
        
        self.center_window(clock_window)
        
        canvas = tk.Canvas(clock_window, bg=self.colors['bg'], highlightthickness=0)
        canvas.pack(fill=tk.BOTH, expand=True)
        
        time_label = tk.Label(canvas,
                            text=time.strftime("%H:%M:%S"),
                            bg=self.colors['bg'],
                            fg=self.colors['primary_light'],
                            font=('Consolas', 36, 'bold'))
        canvas.create_window(150, 80, window=time_label)
        
        date_label = tk.Label(canvas,
                            text=time.strftime("%d.%m.%Y"),
                            bg=self.colors['bg'],
                            fg=self.colors['text'],
                            font=('Segoe UI', 16))
        canvas.create_window(150, 120, window=date_label)
        
        days = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
        day_label = tk.Label(canvas,
                           text=days[int(time.strftime("%w")) - 1],
                           bg=self.colors['bg'],
                           fg=self.colors['text_secondary'],
                           font=('Segoe UI', 12))
        canvas.create_window(150, 150, window=day_label)
        
        def update_clock():
            if clock_window.winfo_exists():
                current_time = time.strftime("%H:%M:%S")
                time_label.config(text=current_time)
                clock_window.after(1000, update_clock)
        
        update_clock()
        
        self.message_queue.put("Открыты часы")
        self.speak("Показываю текущее время")
    
    def open_url(self, url):
        """Открыть URL в браузере"""
        try:
            browser = self.settings.get("default_browser", "default")
            
            if browser == "default":
                webbrowser.open(url)
            else:
                webbrowser.get(browser).open(url)
                
            return True
        except Exception as e:
            try:
                webbrowser.open(url)
                return True
            except:
                self.message_queue.put(f"Ошибка открытия URL: {e}")
                return False
    
    def toggle_voice_assistant(self):
        """Включить/выключить голосового помощника"""
        if not SPEECH_AVAILABLE and not VOICE_INPUT_AVAILABLE:
            self.speak("Голосовой помощник недоступен")
            self.message_queue.put("Голосовой помощник недоступен")
            return
        
        self.voice_assistant_active = not self.voice_assistant_active
        self.background_listening = self.voice_assistant_active
        
        if self.voice_assistant_active:
            self.speak(f"Голосовой помощник активирован")
            self.message_queue.put(f"Голосовой помощник активирован")
            self.status_label.config(text=f"🎤 Ожидание: '{self.voice_wake_word}'", fg=self.colors['primary_light'])
            self.start_voice_assistant()
        else:
            self.background_listening = False
            self.speak("Голосовой помощник отключен")
            self.message_queue.put("Голосовой помощник отключен")
            self.status_label.config(text="Голосовой помощник отключен", fg=self.colors['danger'])
    
    def open_settings(self):
        """Открыть настройки"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Настройки - Атом v4.0 PRO")
        settings_window.geometry("800x700")
        settings_window.configure(bg=self.colors['bg'])
        
        self.center_window(settings_window)
        
        notebook = ttk.Notebook(settings_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        general_frame = tk.Frame(notebook, bg=self.colors['bg'])
        notebook.add(general_frame, text="Общие")
        
        voice_frame = tk.Frame(notebook, bg=self.colors['bg'])
        notebook.add(voice_frame, text="Голос")
        
        appearance_frame = tk.Frame(notebook, bg=self.colors['bg'])
        notebook.add(appearance_frame, text="Внешний вид")
        
        self.create_general_settings(general_frame)
        self.create_improved_voice_settings(voice_frame)
        self.create_appearance_settings(appearance_frame)
        
        buttons_frame = tk.Frame(settings_window, bg=self.colors['bg_light'])
        buttons_frame.pack(fill=tk.X, padx=10, pady=10)
        
        def save_settings():
            self.settings["wake_word"] = self.voice_wake_word
            self.settings["wake_word_sensitivity"] = self.wake_sensitivity
            
            variants_text = self.wake_variants_var.get()
            variants = [v.strip().lower() for v in variants_text.split(",") if v.strip()]
            if variants:
                self.settings["wake_word_variants"] = variants
                self.activation_phrases = variants
            
            self.save_settings()
            settings_window.destroy()
            self.speak("Настройки сохранены")
            self.message_queue.put("Настройки сохранены")
            
            if self.voice_assistant_active:
                self.background_listening = False
                time.sleep(0.5)
                self.background_listening = True
                self.start_voice_assistant()
        
        save_btn = tk.Button(buttons_frame, text="💾 Сохранить",
                           bg=self.colors['success'], fg='white',
                           font=('Segoe UI', 10, 'bold'), bd=0, padx=20, pady=10,
                           cursor="hand2", command=save_settings)
        save_btn.pack(side=tk.RIGHT, padx=5)
        
        cancel_btn = tk.Button(buttons_frame, text="❌ Отмена",
                             bg=self.colors['danger'], fg='white',
                             font=('Segoe UI', 10, 'bold'), bd=0, padx=20, pady=10,
                             cursor="hand2", command=settings_window.destroy)
        cancel_btn.pack(side=tk.RIGHT, padx=5)
    
    def create_general_settings(self, parent):
        """Создание общих настроек"""
        row = 0
        
        tk.Label(parent, text="Поисковая система по умолчанию:",
                bg=self.colors['bg'], fg=self.colors['text'],
                font=('Segoe UI', 11)).grid(row=row, column=0, sticky='w', padx=20, pady=10)
        
        search_engine_var = tk.StringVar(value=list(self.settings["search_engines"].keys())[0])
        search_combo = ttk.Combobox(parent, textvariable=search_engine_var,
                                   values=list(self.settings["search_engines"].keys()),
                                   state='readonly', width=30, font=('Segoe UI', 10))
        search_combo.grid(row=row, column=1, padx=20, pady=10, sticky='w')
        row += 1
        
        tk.Label(parent, text="Город для погоды:",
                bg=self.colors['bg'], fg=self.colors['text'],
                font=('Segoe UI', 11)).grid(row=row, column=0, sticky='w', padx=20, pady=10)
        
        weather_city_var = tk.StringVar(value=self.settings.get("weather_city", "Москва"))
        weather_entry = tk.Entry(parent, textvariable=weather_city_var,
                                font=('Segoe UI', 11), bg=self.colors['bg_lighter'],
                                fg=self.colors['text'], width=30)
        weather_entry.grid(row=row, column=1, padx=20, pady=10, sticky='w')
        row += 1
        
        tk.Label(parent, text="Браузер по умолчанию:",
                bg=self.colors['bg'], fg=self.colors['text'],
                font=('Segoe UI', 11)).grid(row=row, column=0, sticky='w', padx=20, pady=10)
        
        browser_var = tk.StringVar(value=self.settings.get("default_browser", "default"))
        browser_combo = ttk.Combobox(parent, textvariable=browser_var,
                                    values=list(self.settings["browsers"].keys()),
                                    state='readonly', width=30, font=('Segoe UI', 10))
        browser_combo.grid(row=row, column=1, padx=20, pady=10, sticky='w')
        row += 1
        
        auto_start_var = tk.BooleanVar(value=self.settings.get("auto_start", True))
        auto_start_check = tk.Checkbutton(parent, text="Автоматический запуск при старте системы",
                                         variable=auto_start_var,
                                         bg=self.colors['bg'], fg=self.colors['text'],
                                         font=('Segoe UI', 11))
        auto_start_check.grid(row=row, column=0, columnspan=2, sticky='w', padx=20, pady=10)
        row += 1
        
        notifications_var = tk.BooleanVar(value=self.settings.get("notifications", True))
        notifications_check = tk.Checkbutton(parent, text="Показывать уведомления",
                                           variable=notifications_var,
                                           bg=self.colors['bg'], fg=self.colors['text'],
                                           font=('Segoe UI', 11))
        notifications_check.grid(row=row, column=0, columnspan=2, sticky='w', padx=20, pady=10)
        row += 1
    
    def create_improved_voice_settings(self, parent):
        """Создание улучшенных голосовых настроек"""
        row = 0
        
        tk.Label(parent, text="Ключевое слово для активации:",
                bg=self.colors['bg'], fg=self.colors['text'],
                font=('Segoe UI', 11)).grid(row=row, column=0, sticky='w', padx=20, pady=10)
        
        self.wake_word_var = tk.StringVar(value=self.voice_wake_word)
        wake_word_entry = tk.Entry(parent, textvariable=self.wake_word_var,
                                  font=('Segoe UI', 11), bg=self.colors['bg_lighter'],
                                  fg=self.colors['text'], width=30)
        wake_word_entry.grid(row=row, column=1, padx=20, pady=10, sticky='w')
        row += 1
        
        tk.Label(parent, text="Варианты распознавания (через запятую):",
                bg=self.colors['bg'], fg=self.colors['text'],
                font=('Segoe UI', 11)).grid(row=row, column=0, sticky='w', padx=20, pady=10)
        
        variants_text = ", ".join(self.activation_phrases)
        self.wake_variants_var = tk.StringVar(value=variants_text)
        wake_variants_entry = tk.Entry(parent, textvariable=self.wake_variants_var,
                                      font=('Segoe UI', 11), bg=self.colors['bg_lighter'],
                                      fg=self.colors['text'], width=30)
        wake_variants_entry.grid(row=row, column=1, padx=20, pady=10, sticky='w')
        row += 1
        
        tk.Label(parent, text="Чувствительность распознавания:",
                bg=self.colors['bg'], fg=self.colors['text'],
                font=('Segoe UI', 11)).grid(row=row, column=0, sticky='w', padx=20, pady=10)
        
        sensitivity_frame = tk.Frame(parent, bg=self.colors['bg'])
        sensitivity_frame.grid(row=row, column=1, padx=20, pady=10, sticky='w')
        
        self.sensitivity_var = tk.DoubleVar(value=self.wake_sensitivity)
        sensitivity_scale = tk.Scale(sensitivity_frame, from_=0.1, to=1.0, 
                                    resolution=0.1, orient=tk.HORIZONTAL,
                                    variable=self.sensitivity_var,
                                    length=200, bg=self.colors['bg_lighter'],
                                    fg=self.colors['text'], highlightthickness=0)
        sensitivity_scale.pack()
        
        sensitivity_label = tk.Label(sensitivity_frame, 
                                    text=f"Текущая: {self.wake_sensitivity:.1f}",
                                    bg=self.colors['bg'], fg=self.colors['text_secondary'],
                                    font=('Segoe UI', 9))
        sensitivity_label.pack()
        
        def update_sensitivity_label(*args):
            sensitivity_label.config(text=f"Текущая: {self.sensitivity_var.get():.1f}")
        
        self.sensitivity_var.trace_add('write', update_sensitivity_label)
        row += 1
        
        voice_enabled_var = tk.BooleanVar(value=self.settings.get("voice_enabled", True))
        voice_enabled_check = tk.Checkbutton(parent, text="Включить голосового помощника",
                                           variable=voice_enabled_var,
                                           bg=self.colors['bg'], fg=self.colors['text'],
                                           font=('Segoe UI', 11))
        voice_enabled_check.grid(row=row, column=0, columnspan=2, sticky='w', padx=20, pady=10)
        row += 1
        
        voice_feedback_var = tk.BooleanVar(value=self.settings.get("voice_feedback", True))
        voice_feedback_check = tk.Checkbutton(parent, text="Озвучивать все действия",
                                             variable=voice_feedback_var,
                                             bg=self.colors['bg'], fg=self.colors['text'],
                                             font=('Segoe UI', 11))
        voice_feedback_check.grid(row=row, column=0, columnspan=2, sticky='w', padx=20, pady=10)
        row += 1
        
        tk.Label(parent, text="Скорость речи:",
                bg=self.colors['bg'], fg=self.colors['text'],
                font=('Segoe UI', 11)).grid(row=row, column=0, sticky='w', padx=20, pady=10)
        
        speed_var = tk.IntVar(value=self.settings.get("voice_speed", 150))
        speed_scale = tk.Scale(parent, from_=100, to=300, 
                              resolution=10, orient=tk.HORIZONTAL,
                              variable=speed_var,
                              length=200, bg=self.colors['bg_lighter'],
                              fg=self.colors['text'], highlightthickness=0)
        speed_scale.grid(row=row, column=1, padx=20, pady=10, sticky='w')
        row += 1
        
        tk.Label(parent, text="Громкость:",
                bg=self.colors['bg'], fg=self.colors['text'],
                font=('Segoe UI', 11)).grid(row=row, column=0, sticky='w', padx=20, pady=10)
        
        volume_var = tk.DoubleVar(value=self.settings.get("voice_volume", 0.9))
        volume_scale = tk.Scale(parent, from_=0.1, to=1.0, 
                               resolution=0.1, orient=tk.HORIZONTAL,
                               variable=volume_var,
                               length=200, bg=self.colors['bg_lighter'],
                              fg=self.colors['text'], highlightthickness=0)
        volume_scale.grid(row=row, column=1, padx=20, pady=10, sticky='w')
        row += 1
        
        test_frame = tk.Frame(parent, bg=self.colors['bg'])
        test_frame.grid(row=row, column=0, columnspan=2, pady=20, padx=20, sticky='w')
        
        def test_wake_word():
            self.speak(f"Тестирую распознавание ключевого слова...")
            messagebox.showinfo("Тест", 
                f"Произнесите одно из ключевых слов:\n{', '.join(self.activation_phrases)}\n\n"
                f"Чувствительность: {self.sensitivity_var.get():.1f}")
        
        test_btn = tk.Button(test_frame, text="🎤 Тест распознавания",
                           bg=self.colors['primary'], fg='white',
                           font=('Segoe UI', 10, 'bold'), bd=0, padx=20, pady=10,
                           cursor="hand2", command=test_wake_word)
        test_btn.pack(side=tk.LEFT, padx=5)
        
        def calibrate_microphone():
            self.speak("Калибровка микрофона. Пожалуйста, помолчите 3 секунды.")
            try:
                with sr.Microphone() as source:
                    self.recognizer.adjust_for_ambient_noise(source, duration=3)
                    self.speak("Калибровка завершена. Микрофон настроен.")
                    messagebox.showinfo("Калибровка", "Микрофон успешно откалиброван.")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось откалибровать микрофон: {e}")
        
        calibrate_btn = tk.Button(test_frame, text="🎚️ Калибровать микрофон",
                                bg=self.colors['warning'], fg='white',
                                font=('Segoe UI', 10, 'bold'), bd=0, padx=20, pady=10,
                                cursor="hand2", command=calibrate_microphone)
        calibrate_btn.pack(side=tk.LEFT, padx=5)
        
        def update_wake_word(*args):
            new_word = self.wake_word_var.get().strip().lower()
            if new_word:
                self.voice_wake_word = new_word
                if new_word not in self.activation_phrases:
                    self.activation_phrases.append(new_word)
                    variants_text = ", ".join(self.activation_phrases)
                    self.wake_variants_var.set(variants_text)
        
        def update_sensitivity(*args):
            self.wake_sensitivity = self.sensitivity_var.get()
        
        self.wake_word_var.trace_add('write', update_wake_word)
        self.sensitivity_var.trace_add('write', update_sensitivity)
        
        def save_voice_settings():
            self.settings["voice_enabled"] = voice_enabled_var.get()
            self.settings["voice_feedback"] = voice_feedback_var.get()
            self.settings["voice_speed"] = speed_var.get()
            self.settings["voice_volume"] = volume_var.get()
            
            if self.speech_engine:
                self.speech_engine.setProperty('rate', speed_var.get())
                self.speech_engine.setProperty('volume', volume_var.get())
        
        voice_enabled_var.trace_add('write', lambda *args: save_voice_settings())
        voice_feedback_var.trace_add('write', lambda *args: save_voice_settings())
        speed_var.trace_add('write', lambda *args: save_voice_settings())
        volume_var.trace_add('write', lambda *args: save_voice_settings())
    
    def create_appearance_settings(self, parent):
        """Создание настроек внешнего вида"""
        row = 0
        
        tk.Label(parent, text="Тема оформления:",
                bg=self.colors['bg'], fg=self.colors['text'],
                font=('Segoe UI', 11)).grid(row=row, column=0, sticky='w', padx=20, pady=10)
        
        theme_var = tk.StringVar(value=self.settings.get("theme", "dark"))
        theme_combo = ttk.Combobox(parent, textvariable=theme_var,
                                  values=["dark", "light", "blue", "green"],
                                  state='readonly', width=30, font=('Segoe UI', 10))
        theme_combo.grid(row=row, column=1, padx=20, pady=10, sticky='w')
        row += 1
        
        tk.Label(parent, text="Основной цвет:",
                bg=self.colors['bg'], fg=self.colors['text'],
                font=('Segoe UI', 11)).grid(row=row, column=0, sticky='w', padx=20, pady=10)
        
        color_var = tk.StringVar(value=self.settings.get("theme_color", "#3b82f6"))
        color_entry = tk.Entry(parent, textvariable=color_var,
                              font=('Segoe UI', 11), bg=self.colors['bg_lighter'],
                              fg=self.colors['text'], width=30)
        color_entry.grid(row=row, column=1, padx=20, pady=10, sticky='w')
        row += 1
        
        tk.Label(parent, text="Размер шрифта:",
                bg=self.colors['bg'], fg=self.colors['text'],
                font=('Segoe UI', 11)).grid(row=row, column=0, sticky='w', padx=20, pady=10)
        
        font_size_var = tk.StringVar(value=self.settings.get("font_size", "normal"))
        font_combo = ttk.Combobox(parent, textvariable=font_size_var,
                                 values=["small", "normal", "large", "x-large"],
                                 state='readonly', width=30, font=('Segoe UI', 10))
        font_combo.grid(row=row, column=1, padx=20, pady=10, sticky='w')
        row += 1
        
        animations_var = tk.BooleanVar(value=self.settings.get("animations", True))
        animations_check = tk.Checkbutton(parent, text="Включить анимации",
                                        variable=animations_var,
                                        bg=self.colors['bg'], fg=self.colors['text'],
                                        font=('Segoe UI', 11))
        animations_check.grid(row=row, column=0, columnspan=2, sticky='w', padx=20, pady=10)
        row += 1
    
    def switch_mode(self):
        """Переключение между демо и рабочим режимом"""
        self.demo_mode = not self.demo_mode
        self.settings["demo_mode"] = self.demo_mode
        self.save_settings()
        
        mode_name = "демонстрационный" if self.demo_mode else "рабочий"
        self.speak(f"Переключен в {mode_name} режим")
        self.text_anim.show_transition(f"{mode_name.capitalize()} режим", 2)
        
        self.root.after(2500, self.create_main_interface)
    
    def logout_or_exit(self):
        """Выход или смена пользователя"""
        if self.logged_in:
            choice_window = tk.Toplevel(self.root)
            choice_window.title("Выход")
            choice_window.geometry("300x200")
            choice_window.configure(bg=self.colors['bg'])
            choice_window.resizable(False, False)
            
            self.center_window(choice_window)
            
            tk.Label(choice_window, text="Выберите действие:",
                    bg=self.colors['bg'], fg=self.colors['text'],
                    font=('Segoe UI', 14)).pack(pady=30)
            
            logout_btn = tk.Button(choice_window, text="🔄 Сменить пользователя",
                                 bg=self.colors['primary'], fg='white',
                                 font=('Segoe UI', 10, 'bold'), bd=0, padx=20, pady=10,
                                 cursor="hand2", command=lambda: [choice_window.destroy(), self.logout_user()])
            logout_btn.pack(pady=10)
            
            exit_btn = tk.Button(choice_window, text="🚪 Выйти из программы",
                               bg=self.colors['danger'], fg='white',
                               font=('Segoe UI', 10, 'bold'), bd=0, padx=20, pady=10,
                               cursor="hand2", command=self.on_closing)
            exit_btn.pack(pady=10)
            
            cancel_btn = tk.Button(choice_window, text="❌ Отмена",
                                 bg=self.colors['bg_lighter'], fg=self.colors['text'],
                                 font=('Segoe UI', 10), bd=0, padx=20, pady=10,
                                 cursor="hand2", command=choice_window.destroy)
            cancel_btn.pack(pady=10)
        else:
            self.on_closing()
    
    def open_calculator(self):
        """Открыть калькулятор"""
        self.notebook.select(3)
        self.speak("Открываю калькулятор")
    
    def start_demo(self):
        """Запуск демонстрации в демо-режиме"""
        if not self.demo_mode:
            return
        
        self.message_queue.put("Запуск демонстрации...")
        self.speak("Запускаю демонстрацию возможностей Атом v4.0 PRO")
        
        demo_steps = [
            (2000, lambda: self.speak("Демонстрация голосового помощника")),
            (4000, lambda: self.speak("Сейчас покажу возможности поиска")),
            (6000, lambda: [self.search_query.set("пример поиска"), self.perform_search()]),
            (9000, lambda: self.speak("Открываю социальные сети")),
            (10000, lambda: self.notebook.select(1)),
            (12000, lambda: self.speak("Показываю медиа возможности")),
            (13000, lambda: self.notebook.select(2)),
            (14000, lambda: [self.video_search_query.set("музыка"), self.search_and_play_video()]),
            (17000, lambda: self.speak("Демонстрирую инструменты")),
            (18000, lambda: self.notebook.select(3)),
            (19000, lambda: self.open_calculator()),
            (22000, lambda: self.speak("Демонстрирую автоматизацию")),
            (23000, lambda: self.notebook.select(4)),
            (24000, lambda: self.add_template_task("Открыть все социальные сети")),
            (27000, lambda: self.speak("Демонстрирую редактор кода")),
            (28000, lambda: self.notebook.select(5)),
            (30000, lambda: self.speak("Демонстрирую ИИ-ассистента")),
            (31000, lambda: self.notebook.select(6)),
            (32000, lambda: self.train_neural_network_ui()),
            (35000, lambda: self.speak("Демонстрация завершена")),
            (36000, lambda: self.message_queue.put("Демонстрация завершена"))
        ]
        
        for delay, action in demo_steps:
            self.root.after(delay, action)
    
    def process_queue(self):
        """Обработка очереди сообщений"""
        try:
            while not self.message_queue.empty():
                message = self.message_queue.get_nowait()
                self.add_to_log(message)
        except queue.Empty:
            pass
        finally:
            if self.running:
                self.root.after(100, self.process_queue)
    
    def add_to_log(self, message):
        """Добавление сообщения в лог"""
        try:
            timestamp = time.strftime("%H:%M:%S")
            log_entry = f"[{timestamp}] {message}\n"
            
            self.log_text.config(state=tk.NORMAL)
            self.log_text.insert(tk.END, log_entry)
            self.log_text.see(tk.END)
            self.log_text.config(state=tk.DISABLED)
        except Exception as e:
            print(f"Ошибка добавления в лог: {e}")
    
    def play_activation_sound(self):
        """Воспроизведение звука активации"""
        try:
            if WINSOUND_AVAILABLE:
                winsound.Beep(1000, 200)
        except:
            pass
    
    def is_similar(self, phrase, text, threshold=0.7):
        """Проверяет схожесть фраз"""
        if phrase in text or text in phrase:
            return True
        
        if len(phrase) >= 3 and len(text) >= 3:
            if phrase[:3] == text[:3]:
                return True
            
            if phrase[-3:] == text[-3:]:
                return True
        
        return False
    
    def process_enhanced_command(self, command):
        """Обработка расширенных голосовых команд"""
        print(f"Обрабатываю команду: '{command}'")
        
        original_command = command
        
        for phrase in self.activation_phrases:
            if command.startswith(phrase):
                command = command[len(phrase):].strip()
                print(f"Очищенная команда: '{command}'")
        
        command = command.replace(",", "").replace(".", "").replace("!", "").replace("?", "").strip()
        
        if not command:
            command = original_command
            print(f"Использую оригинальную команду: '{command}'")
        
        words = command.split()
        
        if not words:
            print("✗ Пустая команда")
            self.speak("Не услышал команду")
            self.status_label.config(text=f"🎤 Ожидание: '{self.voice_wake_word}'", fg=self.colors['primary_light'])
            return
        
        command_lower = command.lower()
        
        print(f"Анализирую команду: '{command_lower}'")
        
        # Проверяем новые команды для автоматизации
        if "добавь задачу" in command_lower:
            task = command_lower.replace("добавь задачу", "").strip()
            if task:
                self.automation_tasks.append(task)
                self.message_queue.put(f"Задача добавлена: {task}")
                self.speak(f"Задача '{task}' добавлена в список автоматизации")
                self.status_label.config(text=f"🎤 Ожидание: '{self.voice_wake_word}'", fg=self.colors['primary_light'])
                return True
        
        elif "покажи задачи" in command_lower or "список задач" in command_lower:
            if self.automation_tasks:
                tasks_text = ", ".join(self.automation_tasks[:5])
                self.speak(f"У вас {len(self.automation_tasks)} задач: {tasks_text}")
            else:
                self.speak("Список задач пуст")
            self.status_label.config(text=f"🎤 Ожидание: '{self.voice_wake_word}'", fg=self.colors['primary_light'])
            return True
        
        elif "выполни задачи" in command_lower or "запусти задачи" in command_lower:
            self.run_automation_tasks()
            self.status_label.config(text=f"🎤 Ожидание: '{self.voice_wake_word}'", fg=self.colors['primary_light'])
            return True
        
        # Проверяем команды для редактора кода
        elif "новый код" in command_lower or "чистый редактор" in command_lower:
            self.code_text.delete(1.0, tk.END)
            self.speak("Редактор кода очищен")
            self.status_label.config(text=f"🎤 Ожидание: '{self.voice_wake_word}'", fg=self.colors['primary_light'])
            return True
        
        elif "сохрани код" in command_lower:
            self.save_code()
            self.status_label.config(text=f"🎤 Ожидание: '{self.voice_wake_word}'", fg=self.colors['primary_light'])
            return True
        
        # Системные команды
        elif "скриншот" in command_lower:
            self.take_screenshot()
            self.status_label.config(text=f"🎤 Ожидание: '{self.voice_wake_word}'", fg=self.colors['primary_light'])
            return True
        
        # ИИ команды
        elif any(word in command_lower for word in ['проанализируй текст', 'анализ текста', 'настроение текста']):
            text = command_lower.replace("проанализируй текст", "").replace("анализ текста", "").replace("настроение текста", "").strip()
            if text:
                sentiment, score = self.ai_assistant.sentiment_analyzer.analyze(text)
                response = f"Анализ текста: настроение - {sentiment}, уверенность - {score:.0%}"
                self.speak(response)
                self.status_label.config(text=f"🎤 Ожидание: '{self.voice_wake_word}'", fg=self.colors['primary_light'])
                return True
        
        # Стандартные команды
        command_mappings = [
            (["поиск", "найди", "найти", "ищи", "искать"], self.handle_search_command),
            (["открой", "открыть", "зайди", "зайти", "перейди", "перейти"], self.handle_open_command),
            (["погода", "погоду", "погоде", "температура", "температуру"], self.handle_weather_command),
            (["калькулятор", "посчитай", "вычисли", "считай"], self.handle_calculator_command),
            (["время", "час", "сколько времени", "который час"], self.handle_time_command),
            (["браузер", "интернет", "сеть"], self.handle_browser_command),
            (["блокнот", "заметка", "заметки", "текст"], self.handle_notepad_command),
            (["дипсик", "deepseek", "искусственный интеллект", "ии", "ай", "ai"], self.handle_deepseek_command),
            (["помощь", "справка", "что ты умеешь", "команды"], self.handle_help_command),
            (["настройки", "опции", "параметры"], self.handle_settings_command),
            (["режим", "демо", "рабочий"], self.handle_mode_command),
            (["стоп", "хватит", "выйти", "закончи", "отключись", "выключись"], self.handle_stop_command),
            (["спасибо", "благодарю", "спс", "thanks", "thank you"], self.handle_thanks_command),
            (["ии", "искусственный интеллект", "обучи", "тренируй", "создай модель", "предскажи", "прогноз", "классифицируй", "распознай"], self.handle_ai_command)
        ]
        
        for keywords, handler in command_mappings:
            for keyword in keywords:
                if keyword in command_lower:
                    print(f"✓ Найдено ключевое слово: '{keyword}'")
                    handler(command_lower, keyword)
                    return
        
        question_words = ["что", "как", "где", "кто", "почему", "зачем", "когда", "сколько"]
        if any(word in words[:2] for word in question_words):
            print(f"✓ Определен как поисковый запрос: '{command}'")
            self.search_query.set(command)
            self.perform_search()
            self.status_label.config(text=f"🎤 Ожидание: '{self.voice_wake_word}'", fg=self.colors['primary_light'])
            return
        
        print(f"✗ Непонятная команда, открываю как сайт: '{command}'")
        self.open_site_by_voice(command)
        self.status_label.config(text=f"🎤 Ожидание: '{self.voice_wake_word}'", fg=self.colors['primary_light'])
    
    def handle_search_command(self, command, keyword):
        """Обработка команд поиска"""
        query = command.replace(keyword, "").strip()
        if not query:
            self.speak("Что искать?")
            return
        
        self.search_query.set(query)
        self.perform_search()
        self.status_label.config(text=f"🎤 Ожидание: '{self.voice_wake_word}'", fg=self.colors['primary_light'])
    
    def handle_open_command(self, command, keyword):
        """Обработка команд открытия"""
        site_name = command.replace(keyword, "").strip()
        if not site_name:
            self.speak("Что открыть?")
            return
        
        self.open_site_by_voice(site_name)
        self.status_label.config(text=f"🎤 Ожидание: '{self.voice_wake_word}'", fg=self.colors['primary_light'])
    
    def handle_weather_command(self, command, keyword):
        """Обработка команд погоды"""
        city = command.replace(keyword, "").strip()
        if city:
            self.settings["weather_city"] = city
            self.save_settings()
        
        self.open_weather()
        self.status_label.config(text=f"🎤 Ожидание: '{self.voice_wake_word}'", fg=self.colors['primary_light'])
    
    def handle_calculator_command(self, command, keyword):
        """Обработка команд калькулятора"""
        self.open_calculator()
        self.status_label.config(text=f"🎤 Ожидание: '{self.voice_wake_word}'", fg=self.colors['primary_light'])
    
    def handle_time_command(self, command, keyword):
        """Обработка команд времени"""
        current_time = time.strftime("%H:%M:%S")
        current_date = time.strftime("%d.%m.%Y")
        
        response = f"Сейчас {current_time}, сегодня {current_date}"
        self.speak(response)
        self.message_queue.put(f"Время: {response}")
        self.status_label.config(text=f"🎤 Ожидание: '{self.voice_wake_word}'", fg=self.colors['primary_light'])
    
    def handle_browser_command(self, command, keyword):
        """Обработка команд браузера"""
        self.open_browser_window()
        self.status_label.config(text=f"🎤 Ожидание: '{self.voice_wake_word}'", fg=self.colors['primary_light'])
    
    def handle_notepad_command(self, command, keyword):
        """Обработка команд блокнота"""
        self.open_notepad()
        self.status_label.config(text=f"🎤 Ожидание: '{self.voice_wake_word}'", fg=self.colors['primary_light'])
    
    def handle_deepseek_command(self, command, keyword):
        """Обработка команд DeepSeek"""
        self.open_deepseek()
        self.status_label.config(text=f"🎤 Ожидание: '{self.voice_wake_word}'", fg=self.colors['primary_light'])
    
    def handle_help_command(self, command, keyword):
        """Обработка команд помощи"""
        self.speak("Открываю справку")
        self.notebook.select(7)
        self.status_label.config(text=f"🎤 Ожидание: '{self.voice_wake_word}'", fg=self.colors['primary_light'])
    
    def handle_settings_command(self, command, keyword):
        """Обработка команд настроек"""
        self.open_settings()
        self.status_label.config(text=f"🎤 Ожидание: '{self.voice_wake_word}'", fg=self.colors['primary_light'])
    
    def handle_mode_command(self, command, keyword):
        """Обработка команд смены режима"""
        self.switch_mode()
        self.status_label.config(text=f"🎤 Ожидание: '{self.voice_wake_word}'", fg=self.colors['primary_light'])
    
    def handle_stop_command(self, command, keyword):
        """Обработка команд остановки"""
        self.voice_assistant_active = False
        self.background_listening = False
        self.speak("Голосовой помощник отключен")
        self.status_label.config(text="Голосовой помощник отключен", fg=self.colors['danger'])
    
    def handle_thanks_command(self, command, keyword):
        """Обработка команд благодарности"""
        responses = [
            "Всегда пожалуйста!",
            "Рад был помочь!",
            "Обращайтесь!",
            "Пожалуйста! Буду рад помочь снова."
        ]
        response = random.choice(responses)
        self.speak(response)
        self.status_label.config(text=f"🎤 Ожидание: '{self.voice_wake_word}'", fg=self.colors['primary_light'])
    
    def handle_ai_command(self, command, keyword):
        """Обработка команд ИИ-ассистента"""
        self.open_ai_assistant()
        
        if any(word in command for word in ["обучи", "тренируй", "создай"]):
            self.speak("Обрабатываю запрос на обучение ИИ...")
            result = self.ai_assistant.enhanced_process_query(command)
            self.message_queue.put(f"ИИ: {result[:100]}...")
        
        self.status_label.config(text=f"🎤 Ожидание: '{self.voice_wake_word}'", fg=self.colors['primary_light'])
    
    def open_site_by_voice(self, site_name):
        """Открытие сайта по голосовой команде"""
        site_name_lower = site_name.lower()
        
        site_mapping = {
            "вконтакте": ("ВКонтакте", self.settings["social_networks"]["ВКонтакте"]),
            "vk": ("ВКонтакте", self.settings["social_networks"]["ВКонтакте"]),
            "одноклассники": ("Одноклассники", self.settings["social_networks"]["Одноклассники"]),
            "ок": ("Одноклассники", self.settings["social_networks"]["Одноклассники"]),
            "телеграм": ("Telegram", self.settings["social_networks"]["Telegram"]),
            "telegram": ("Telegram", self.settings["social_networks"]["Telegram"]),
            "ватсап": ("WhatsApp Web", self.settings["social_networks"]["WhatsApp Web"]),
            "whatsapp": ("WhatsApp Web", self.settings["social_networks"]["WhatsApp Web"]),
            "дискорд": ("Discord", self.settings["social_networks"]["Discord"]),
            "discord": ("Discord", self.settings["social_networks"]["Discord"]),
            "твиттер": ("Twitter", self.settings["social_networks"]["Twitter"]),
            "twitter": ("Twitter", self.settings["social_networks"]["Twitter"]),
            "фейсбук": ("Facebook", self.settings["social_networks"]["Facebook"]),
            "facebook": ("Facebook", self.settings["social_networks"]["Facebook"]),
            "инстаграм": ("Instagram", self.settings["social_networks"]["Instagram"]),
            "instagram": ("Instagram", self.settings["social_networks"]["Instagram"]),
            "ютуб": ("YouTube", self.settings["social_networks"]["YouTube"]),
            "youtube": ("YouTube", self.settings["social_networks"]["YouTube"]),
            "твич": ("Twitch", self.settings["social_networks"]["Twitch"]),
            "twitch": ("Twitch", self.settings["social_networks"]["Twitch"]),
            "дипсик": ("DeepSeek AI", self.settings["social_networks"]["DeepSeek AI"]),
            "deepseek": ("DeepSeek AI", self.settings["social_networks"]["DeepSeek AI"]),
            "гугл": ("Google", self.settings["search_engines"]["Google"]),
            "google": ("Google", self.settings["search_engines"]["Google"]),
            "яндекс": ("Яндекс", self.settings["search_engines"]["Яндекс"]),
            "yandex": ("Яндекс", self.settings["search_engines"]["Яндекс"]),
            "бинг": ("Bing", self.settings["search_engines"]["Bing"]),
            "bing": ("Bing", self.settings["search_engines"]["Bing"]),
            "почта": ("Почта", "https://mail.google.com"),
            "gmail": ("Gmail", "https://mail.google.com"),
            "новости": ("Новости", "https://news.google.com"),
            "карты": ("Карты", "https://www.google.com/maps"),
            "google maps": ("Карты", "https://www.google.com/maps"),
            "переводчик": ("Переводчик", "https://translate.google.com"),
            "google translate": ("Переводчик", "https://translate.google.com")
        }
        
        # Поиск по точному совпадению
        if site_name_lower in site_mapping:
            name, url = site_mapping[site_name_lower]
            self.open_url(url)
            self.speak(f"Открываю {name}")
            return True
        
        # Поиск по частичному совпадению
        for key, (name, url) in site_mapping.items():
            if key in site_name_lower or site_name_lower in key:
                self.open_url(url)
                self.speak(f"Открываю {name}")
                return True
        
        # Если не нашли - делаем поиск
        self.search_query.set(site_name)
        self.perform_search()
        self.speak(f"Ищу информацию о {site_name}")
        return False
    
    def update_status_for_wake_word(self):
        """Обновление статуса при обнаружении ключевого слова"""
        try:
            if hasattr(self, 'status_label'):
                self.status_label.config(text="🎤 Ключевое слово обнаружено!", fg=self.colors['success'])
        except:
            pass
    
    def on_closing(self):
        """Обработка закрытия приложения"""
        if messagebox.askyesno("Выход", "Вы уверены, что хотите выйти?"):
            # Останавливаем все фоновые процессы
            self.running = False
            self.background_listening = False
            self.voice_assistant_active = False
            
            # Отменяем все запланированные задачи
            self.cancel_all_after()
            
            # Сохраняем настройки
            self.save_settings()
            
            # Останавливаем голосовой движок
            if self.speech_engine:
                try:
                    self.speech_engine.stop()
                except:
                    pass
            
            # Закрываем все окна
            try:
                if hasattr(self, 'selection_window') and self.selection_window.winfo_exists():
                    self.selection_window.destroy()
                
                if hasattr(self, 'auth_window') and self.auth_window.winfo_exists():
                    self.auth_window.destroy()
            except:
                pass
            
            # Закрываем главное окно
            self.root.destroy()

# ========== ТОЧКА ВХОДА ==========

def main():
    """Главная функция приложения"""
    try:
        # Инициализация главного окна
        root = tk.Tk()
        
        # Создание экземпляра приложения
        app = EnhancedVoiceAssistantGUI(root)
        
        # Обработка закрытия окна
        root.protocol("WM_DELETE_WINDOW", app.on_closing)
        
        # Запуск главного цикла
        root.mainloop()
        
    except Exception as e:
        print(f"Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
        
        # Пытаемся сохранить настройки при аварийном завершении
        try:
            if 'app' in locals():
                app.save_settings()
        except:
            pass

if __name__ == "__main__":
    main()