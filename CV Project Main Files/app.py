# streamlit_app.py

import os
import cv2
import numpy as np
import streamlit as st
from PIL import Image
from commonfunctions import *
from pre_processing import *
from staff import calculate_thickness_spacing, remove_staff_lines, coordinator
from segmenter import Segmenter
from connected_componentes import *
from fit import predict
from scipy.ndimage import binary_fill_holes
from skimage.morphology import skeletonize, thin

# Function to estimate staff line index and pitch
def estim(c, idx):
    spacing = imgs_spacing[idx]
    rows = imgs_rows[idx]
    margin = 1 + (spacing / 4)
    for index, line in enumerate(rows):
        if c >= line - margin and c <= line + margin:
            return index + 1, 0
        elif c >= line + margin and c <= line + 3 * margin:
            return index + 1, 1
    return 0, 0

# Function to draw staff lines on an image
def draw_staff(img, row_positions):
    image = np.copy(img)
    for x in range(len(row_positions)):
        image[int(row_positions[x]), :] = 0
    return image

# Function to get note name based on duration
def get_note_name(prev, octave, duration):
    if duration in ['4', 'a_4']:
        return f'{octave[0]}{prev}{octave[1]}/4'
    elif duration in ['8', '8_b_n', '8_b_r', 'a_8']:
        return f'{octave[0]}{prev}{octave[1]}/8'
    elif duration in ['16', '16_b_n', '16_b_r', 'a_16']:
        return f'{octave[0]}{prev}{octave[1]}/16'
    elif duration in ['32', '32_b_n', '32_b_r', 'a_32']:
        return f'{octave[0]}{prev}{octave[1]}/32'
    elif duration in ['2', 'a_2']:
        return f'{octave[0]}{prev}{octave[1]}/2'
    elif duration in ['1', 'a_1']:
        return f'{octave[0]}{prev}{octave[1]}/1'

# Function to filter beams
def filter_beams(prims, prim_with_staff, bounds):
    n_bounds = []
    n_prims = []
    n_prim_with_staff = []
    for i, prim in enumerate(prims):
        if prim.shape[1] >= 2 * prim.shape[0]:
            print('filter: ', prim.shape)
            continue
        else:
            n_bounds.append(bounds[i])
            n_prims.append(prims[i])
            n_prim_with_staff.append(prim_with_staff[i])
    return n_prims, n_prim_with_staff, n_bounds

# Function to get chord notation
def get_chord_notation(chord_list):
    chord_res = "{"
    for chord_note in chord_list:
        chord_res += (str(chord_note) + ",")
    chord_res = chord_res[:-1]
    chord_res += "}"
    return chord_res

# Streamlit app title and description
st.title("Optical Music Note Recognition using OpenCV")
st.write("")

# Upload input and output folders
input_folder_path = st.sidebar.text_input("Input Folder Path")
output_folder_path = st.sidebar.text_input("Output Folder Path")

if input_folder_path and output_folder_path:
    images_input = []  # Store input images for later display
    images_output = []  # Store output images for later display

    st.subheader("Input Images:")
    for filename in os.listdir(input_folder_path):
        if filename.endswith((".png", ".jpg", ".jpeg")):
            img_path = os.path.join(input_folder_path, filename)
            img = io.imread(img_path)
            images_input.append(img)
            st.image(img, caption=f"Input Image: {filename}", use_column_width=True)

    st.subheader("Output Images:")
    for filename in os.listdir(output_folder_path):
        if filename.endswith((".png", ".jpg", ".jpeg")):
            img_path = os.path.join(output_folder_path, filename)
            img = io.imread(img_path)
            images_output.append(img)
            st.image(img, caption=f"Output Image: {filename}", use_column_width=True)

    # Show Results Button
    if st.button("Show Results"):
        # Display all stored input images
        st.subheader("Input Images:")
        for idx, img in enumerate(images_input):
            st.image(img, caption=f"Input Image {idx + 1}", use_column_width=True)

        # Display all stored output images
        st.subheader("Output Images:")
        for idx, img in enumerate(images_output):
            st.image(img, caption=f"Output Image {idx + 1}", use_column_width=True)
