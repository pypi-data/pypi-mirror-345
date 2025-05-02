import gc
import io
import json
import os
import pickle
import random
import pkg_resources
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from typing import List


class KhmerDatasetLoader:
    DEFAULT_PATHS = {
        "word": "data/wild_khmer_data.pkl",
        "sentence": "data/wild_khmer_sentences.pkl",
        "location": "data/khmer_location_combinations.pkl",
        "address": "data/address_kh_data.pkl",
        "khmer_english": "data/combined_khmer_english.pkl"
    }

    def __init__(self, dataset_type, filepath=None):
        self.dataset_type = dataset_type.lower()
        if self.dataset_type not in self.DEFAULT_PATHS:
            raise ValueError(f"Unsupported dataset type: {self.dataset_type}")

        self.filepath = filepath or pkg_resources.resource_filename(
            'rdlab_dataset', self.DEFAULT_PATHS[self.dataset_type]
        )
        self.data = self._load_data()

    def _load_data(self):
        if not os.path.exists(self.filepath):
            print(f"Data file not found: {self.filepath}")
            return ["No Data Here!"]
        with open(self.filepath, 'rb') as f:
            data = pickle.load(f)
        return data if data else ["No Data Here!"]

    def get_all(self):
        return self.data

    def __len__(self):
        return len(self.data)

    def get_first(self):
        return self.data[0] if self.data else None

    def get_n_first(self, n=5):
        return self.data[:n]

    def find(self, item):
        return item in self.data


class FontShiftTester:
    def __init__(self, fonts_json="fonts.json", output_dir="check_font",
                 font_size=48, text_color=(0, 0, 0), background_color=(255, 255, 255),
                 margin=20, test_texts=None):
        self.fonts_json = fonts_json
        self.output_dir = output_dir
        self.font_size = font_size
        self.text_color = text_color
        self.background_color = background_color
        self.margin = margin
        self.test_texts = test_texts or ["កម្ពុជា", "ជំនាន់ថ្មី", "សិល្បៈ"]  # Default Khmer test texts

        with open(fonts_json, "r", encoding="utf-8") as f:
            self.fonts_with_shift = json.load(f)

        os.makedirs(self.output_dir, exist_ok=True)

    def generate_test_images(self):
        for idx, font_entry in enumerate(self.fonts_with_shift):
            font_path = font_entry["font_path"]
            shift_y = font_entry.get("shift_y", 0)
            crop_y = font_entry.get("crop_y", 0)

            font_name = os.path.splitext(os.path.basename(font_path))[0]
            font_folder = os.path.join(self.output_dir, f"font_{idx + 1}_{font_name}")
            os.makedirs(font_folder, exist_ok=True)

            try:
                font = ImageFont.truetype(font_path, self.font_size)
            except Exception as e:
                print(f"[ERROR] Failed to load font {font_path}: {e}")
                continue

            for i, text in enumerate(self.test_texts, 1):
                dummy_img = Image.new("RGB", (1, 1))
                draw = ImageDraw.Draw(dummy_img)
                bbox = draw.textbbox((0, 0), text, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]

                img_w = text_width + 2 * self.margin
                img_h = 60 + 2 * self.margin

                image = Image.new("RGB", (img_w, img_h), self.background_color)
                draw = ImageDraw.Draw(image)
                draw.text((self.margin, self.margin + shift_y), text, font=font, fill=self.text_color)

                # Apply vertical crop equally from top and bottom
                top_crop = crop_y
                bottom_crop = image.height - crop_y
                cropped_image = image.crop((0, top_crop, image.width, bottom_crop))

                timestamp = datetime.now().strftime("%H%M%S_%f")[:-3]
                filename = f"image_of_text_{i}_{timestamp}.png"
                image_path = os.path.join(font_folder, filename)
                cropped_image.save(image_path)
                print(f"[OK] Saved: {image_path}")


class TextArrayListImageGenerator:
    def __init__(self, font_path="font", background_path="background", output_folder="generated_images",
                 font_size=48, background_color=(255, 255, 255), text_color=(0, 0, 0), margin=20,
                 customize_font=False, folder_limit=10, output_count=4, num_threads=2,
                 rotate_text=True, gray_scale=True, font_folder=True, fonts_json="fonts.json",
                 random_crop_y=(0, 3),
                 random_shift_y=(0, 3)):  # <-- added
        self.font_path = pkg_resources.resource_filename('rdlab_dataset', font_path)
        self.background_path = pkg_resources.resource_filename('rdlab_dataset', background_path)
        self.output_folder = output_folder
        self.font_size = font_size
        self.background_color = background_color
        self.text_color = text_color
        self.margin = margin
        self.customize_font = customize_font
        self.folder_limit = folder_limit
        self.output_count = output_count
        self.num_threads = num_threads
        self.rotate_text = rotate_text
        self.gray_scale = gray_scale
        self.font_folder = font_folder
        self.fonts_json = fonts_json
        self.random_shift_y = random_shift_y  # <-- added
        self.random_crop_y = random_crop_y  # <-- added

        if not self.font_folder:
            with open(self.fonts_json, "r", encoding='utf-8') as f:
                self.fonts_with_shift = json.load(f)
        else:
            self.fonts_with_shift = None

    def add_noise(self, image):
        noise_type = random.choice(['gaussian', 'salt_pepper', 'speckle', 'poisson', 'blur'])
        img_array = np.array(image)

        if noise_type == 'gaussian':
            mean = 0
            var = random.uniform(10, 30)
            sigma = var ** 0.5
            gaussian = np.random.normal(mean, sigma, img_array.shape)
            noisy_img = np.clip(img_array + gaussian, 0, 255)
        elif noise_type == 'salt_pepper':
            amount = random.uniform(0.01, 0.05)
            noisy_img = np.copy(img_array)
            num_salt = np.ceil(amount * img_array.size * 0.5).astype(int)
            coords = [np.random.randint(0, i - 1, num_salt) for i in img_array.shape]
            noisy_img[tuple(coords)] = 255
            num_pepper = np.ceil(amount * img_array.size * 0.5).astype(int)
            coords = [np.random.randint(0, i - 1, num_pepper) for i in img_array.shape]
            noisy_img[tuple(coords)] = 0
        elif noise_type == 'speckle':
            speckle = np.random.randn(*img_array.shape)
            noisy_img = np.clip(img_array + img_array * speckle * random.uniform(0.05, 0.15), 0, 255)
        elif noise_type == 'poisson':
            vals = len(np.unique(img_array))
            vals = 2 ** np.ceil(np.log2(vals))
            noisy_img = np.clip(np.random.poisson(img_array * vals) / float(vals), 0, 255)
        elif noise_type == 'blur':
            return image.filter(ImageFilter.GaussianBlur(radius=random.uniform(1, 2)))

        return Image.fromarray(noisy_img.astype(np.uint8))

    def _generate_batch(self, text_batch: List[str], batch_index: int,
                        font_files, background_files, font_folder, save_as_pickle):

        range_start = batch_index * self.folder_limit
        range_end = range_start + self.folder_limit
        data_range = f"{range_start}_{range_end}"
        data_folder = os.path.join(self.output_folder, f"data_{data_range}")
        os.makedirs(data_folder, exist_ok=True)

        annotations = []
        pickle_data = [] if save_as_pickle else None

        for text in text_batch:
            timestamp = datetime.now().strftime("image_folder_date_%d_%m_%y_time_%H_%M_%S_%f")[:-3]
            batch_folder = os.path.join(data_folder, timestamp)
            os.makedirs(batch_folder, exist_ok=True)

            for _ in range(self.output_count):
                if self.font_folder:
                    font_file = random.choice(font_files)
                    font_path = os.path.join(font_folder if self.customize_font and font_folder else self.font_path, font_file)
                    shift_y = random.randint(*self.random_shift_y)  # <-- modified
                    crop_y = random.randint(*self.random_crop_y)
                else:
                    font_entry = random.choice(self.fonts_with_shift)
                    font_path = font_entry["font_path"]
                    shift_y = font_entry.get("shift_y", 0) + random.randint(*self.random_shift_y)  # <-- modified
                    crop_y = font_entry.get("crop_y", 0) + random.randint(*self.random_crop_y)
                    font_file = os.path.basename(font_path)

                shift_x = random.randint(-5, 5)
                background_file = random.choice(background_files)

                temp_font_size = self.font_size
                while True:
                    try:
                        temp_font = ImageFont.truetype(font_path, temp_font_size)
                    except:
                        temp_font = ImageFont.load_default()
                        break
                    dummy_img = Image.new('RGB', (1, 1))
                    draw = ImageDraw.Draw(dummy_img)
                    bbox = draw.textbbox((0, 0), text, font=temp_font)
                    text_height = bbox[3] - bbox[1]
                    if text_height <= 60 or temp_font_size <= 10:
                        break
                    temp_font_size -= 1

                background_path = os.path.join(self.background_path, background_file)
                background_image = Image.open(background_path).convert('RGB')

                text_width = bbox[2] - bbox[0]
                img_w = text_width + 2 * self.margin
                img_h = 60 + 2 * self.margin
                text_layer = Image.new('RGBA', (img_w, img_h), (255, 255, 255, 0))
                draw = ImageDraw.Draw(text_layer)

                draw.text(
                    (self.margin + shift_x, self.margin + shift_y),
                    text,
                    font=temp_font,
                    fill=self.text_color + (255,)
                )

                rotated_text = text_layer.rotate(random.uniform(-3, 3), expand=True) if self.rotate_text else text_layer
                resized_bg = background_image.resize(rotated_text.size)
                final_image = Image.alpha_composite(resized_bg.convert('RGBA'), rotated_text)

                top_crop = crop_y
                bottom_crop = final_image.height - crop_y
                cropped_image = final_image.crop((0, top_crop, final_image.width, bottom_crop)).convert('RGB')

                noisy_image = self.add_noise(cropped_image)

                if self.gray_scale:
                    noisy_image = noisy_image.convert('L')

                ts = datetime.now().strftime("%d_%m_%y_%H_%M_%S_%f")[:-3]
                fname = f"{os.path.splitext(font_file)[0]}_{os.path.splitext(background_file)[0]}_{ts}_noisy.png"
                out_path = os.path.join(batch_folder, fname)
                noisy_image.save(out_path)
                print(f"[Batch {data_range}] Image saved to {out_path}")

                annotations.append({'image_path': out_path.replace("\\", "/"), 'label': text})
                b = io.BytesIO()
                noisy_image.save(b, format='PNG')
                if save_as_pickle and pickle_data is not None:
                    pickle_data.append({'image': b.getvalue(), 'label': text, 'path': out_path.replace("\\", "/")})

        self._save_annotations_range(range_start, range_end, annotations, pickle_data, save_as_pickle)

    def generate_images(self, text_list, font_folder=None, save_as_pickle=False):
        if self.font_folder:
            font_files = [f for f in os.listdir(font_folder if self.customize_font and font_folder else self.font_path)
                          if f.lower().endswith(".ttf")]
        else:
            font_files = []

        background_files = [f for f in os.listdir(self.background_path) if f.lower().endswith(".jpg")]

        batches = [
            text_list[i:i + self.folder_limit]
            for i in range(0, len(text_list), self.folder_limit)
        ]

        with ThreadPoolExecutor(max_workers=self.num_threads) as executor:
            futures = []
            for idx, batch in enumerate(batches):
                futures.append(executor.submit(
                    self._generate_batch,
                    batch,
                    idx,
                    font_files,
                    background_files,
                    font_folder,
                    save_as_pickle
                ))
            for f in futures:
                f.result()

    def _save_annotations_range(self, start, end, annotations, pickle_data, save_as_pickle):
        data_range = f"{start}_{end}"
        folder = os.path.join(self.output_folder, f"data_{data_range}")
        if save_as_pickle and pickle_data is not None:
            with open(os.path.join(folder, f"annotations_{data_range}.pkl"), 'wb') as f:
                pickle.dump(pickle_data, f)
        else:
            with open(os.path.join(folder, f"annotations_{data_range}.txt"), 'w', encoding='utf-8') as f:
                for a in annotations:
                    f.write(f"{a['image_path']}\t{a['label']}\n")
        print(f"[Batch {data_range}] Annotations saved.")



class TextArrayListImageGeneratorExhaustive:
    def __init__(self, font_path="font", background_path="background", output_folder="generated_images",
                 font_size=48, background_color=(255, 255, 255), text_color=(0, 0, 0), margin=20,
                 customize_font=False, folder_limit=10, output_count=4, num_threads=2,
                 rotate_text=True, gray_scale=True, font_folder=True, fonts_json="fonts.json"):
        self.font_path = pkg_resources.resource_filename('rdlab_dataset', font_path)
        self.background_path = pkg_resources.resource_filename('rdlab_dataset', background_path)
        self.output_folder = output_folder
        self.font_size = font_size
        self.background_color = background_color
        self.text_color = text_color
        self.margin = margin
        self.customize_font = customize_font
        self.folder_limit = folder_limit
        self.output_count = output_count
        self.num_threads = num_threads
        self.rotate_text = rotate_text
        self.gray_scale = gray_scale
        self.font_folder = font_folder
        self.fonts_json = fonts_json

        if not self.font_folder:
            with open(self.fonts_json, "r", encoding='utf-8') as f:
                self.fonts_with_shift = json.load(f)
        else:
            self.fonts_with_shift = None

    def add_noise(self, image):
        noise_type = random.choice(['gaussian', 'salt_pepper', 'speckle', 'poisson', 'blur'])
        img_array = np.array(image)

        if noise_type == 'gaussian':
            mean = 0
            var = random.uniform(10, 30)
            sigma = var ** 0.5
            gaussian = np.random.normal(mean, sigma, img_array.shape)
            noisy_img = np.clip(img_array + gaussian, 0, 255)
        elif noise_type == 'salt_pepper':
            amount = random.uniform(0.01, 0.05)
            noisy_img = np.copy(img_array)
            num_salt = np.ceil(amount * img_array.size * 0.5).astype(int)
            coords = [np.random.randint(0, i - 1, num_salt) for i in img_array.shape]
            noisy_img[tuple(coords)] = 255
            num_pepper = np.ceil(amount * img_array.size * 0.5).astype(int)
            coords = [np.random.randint(0, i - 1, num_pepper) for i in img_array.shape]
            noisy_img[tuple(coords)] = 0
        elif noise_type == 'speckle':
            speckle = np.random.randn(*img_array.shape)
            noisy_img = np.clip(img_array + img_array * speckle * random.uniform(0.05, 0.15), 0, 255)
        elif noise_type == 'poisson':
            vals = len(np.unique(img_array))
            vals = 2 ** np.ceil(np.log2(vals))
            noisy_img = np.clip(np.random.poisson(img_array * vals) / float(vals), 0, 255)
        elif noise_type == 'blur':
            return image.filter(ImageFilter.GaussianBlur(radius=random.uniform(1, 2)))

        return Image.fromarray(noisy_img.astype(np.uint8))

    def _generate_batch(self, text_batch: List[str], batch_index: int,
                        font_files, background_files, font_folder, save_as_pickle):

        range_start = batch_index * self.folder_limit
        range_end = range_start + self.folder_limit
        data_range = f"{range_start}_{range_end}"
        data_folder = os.path.join(self.output_folder, f"data_{data_range}")
        os.makedirs(data_folder, exist_ok=True)

        annotations = []
        pickle_data = [] if save_as_pickle else None

        # Apply every font to every text
        for font_file in font_files:
            if self.font_folder:
                font_path = os.path.join(font_folder if self.customize_font and font_folder else self.font_path, font_file)
                shift_y, crop_y = 0, 0
            else:
                font_entry = next((f for f in self.fonts_with_shift if os.path.basename(f["font_path"]) == font_file), None)
                if not font_entry:
                    print(f"[SKIP] Font {font_file} not in fonts.json.")
                    continue
                font_path = font_entry["font_path"]
                shift_y = font_entry.get("shift_y", 0)
                crop_y = font_entry.get("crop_y", 0)

            for text in text_batch:
                timestamp = datetime.now().strftime("image_folder_date_%d_%m_%y_time_%H_%M_%S_%f")[:-3]
                batch_folder = os.path.join(data_folder, timestamp)
                os.makedirs(batch_folder, exist_ok=True)

                for _ in range(self.output_count):
                    background_file = random.choice(background_files)

                    temp_font_size = self.font_size
                    while True:
                        try:
                            temp_font = ImageFont.truetype(font_path, temp_font_size)
                        except:
                            temp_font = ImageFont.load_default()
                            break
                        dummy_img = Image.new('RGB', (1, 1))
                        draw = ImageDraw.Draw(dummy_img)
                        bbox = draw.textbbox((0, 0), text, font=temp_font)
                        text_height = bbox[3] - bbox[1]
                        if text_height <= 60 or temp_font_size <= 10:
                            break
                        temp_font_size -= 1

                    background_path = os.path.join(self.background_path, background_file)
                    background_image = Image.open(background_path).convert('RGB')

                    text_width = bbox[2] - bbox[0]
                    img_w = text_width + 2 * self.margin
                    img_h = 60 + 2 * self.margin
                    text_layer = Image.new('RGBA', (img_w, img_h), (255, 255, 255, 0))
                    draw = ImageDraw.Draw(text_layer)

                    draw.text(
                        (self.margin + random.randint(0, 10), self.margin + shift_y),
                        text,
                        font=temp_font,
                        fill=self.text_color + (255,)
                    )

                    rotated_text = text_layer.rotate(random.uniform(-3, 3), expand=True) if self.rotate_text else text_layer
                    resized_bg = background_image.resize(rotated_text.size)
                    final_image = Image.alpha_composite(resized_bg.convert('RGBA'), rotated_text)

                    # Apply crop_y from top and bottom
                    top_crop = crop_y
                    bottom_crop = final_image.height - crop_y
                    cropped_image = final_image.crop((0, top_crop, final_image.width, bottom_crop)).convert('RGB')

                    noisy_image = self.add_noise(cropped_image)

                    if self.gray_scale:
                        noisy_image = noisy_image.convert('L')

                    ts = datetime.now().strftime("%d_%m_%y_%H_%M_%S_%f")[:-3]
                    clean_font_name = os.path.splitext(font_file)[0]
                    clean_bg_name = os.path.splitext(background_file)[0]
                    fname = f"{clean_font_name}_{clean_bg_name}_{ts}_noisy.png"
                    out_path = os.path.join(batch_folder, fname)
                    noisy_image.save(out_path)
                    print(f"[{data_range}] Saved: {out_path}")

                    annotations.append({'image_path': out_path.replace("\\", "/"), 'label': text})
                    b = io.BytesIO()
                    noisy_image.save(b, format='PNG')
                    if save_as_pickle and pickle_data is not None:
                        pickle_data.append({'image': b.getvalue(), 'label': text, 'path': out_path.replace("\\", "/")})

        self._save_annotations_range(range_start, range_end, annotations, pickle_data, save_as_pickle)

    def generate_images(self, text_list, font_folder=None, save_as_pickle=False):
        if self.font_folder:
            font_files = [f for f in os.listdir(font_folder if self.customize_font and font_folder else self.font_path)
                          if f.lower().endswith(".ttf")]
        else:
            font_files = [os.path.basename(f["font_path"]) for f in self.fonts_with_shift]

        background_files = [f for f in os.listdir(self.background_path) if f.lower().endswith(".jpg")]

        batches = [
            text_list[i:i + self.folder_limit]
            for i in range(0, len(text_list), self.folder_limit)
        ]

        with ThreadPoolExecutor(max_workers=self.num_threads) as executor:
            futures = []
            for idx, batch in enumerate(batches):
                futures.append(executor.submit(
                    self._generate_batch,
                    batch,
                    idx,
                    font_files,
                    background_files,
                    font_folder,
                    save_as_pickle
                ))
            for f in futures:
                f.result()

    def _save_annotations_range(self, start, end, annotations, pickle_data, save_as_pickle):
        data_range = f"{start}_{end}"
        folder = os.path.join(self.output_folder, f"data_{data_range}")
        if save_as_pickle and pickle_data is not None:
            with open(os.path.join(folder, f"annotations_{data_range}.pkl"), 'wb') as f:
                pickle.dump(pickle_data, f)
        else:
            with open(os.path.join(folder, f"annotations_{data_range}.txt"), 'w', encoding='utf-8') as f:
                for a in annotations:
                    f.write(f"{a['image_path']}\t{a['label']}\n")
        print(f"[Batch {data_range}] Annotations saved.")