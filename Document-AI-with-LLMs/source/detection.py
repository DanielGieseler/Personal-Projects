
from pdf2image import convert_from_path
import pandas as pd
from ultralyticsplus import YOLO
import time
import numpy as np
import cv2
import os
import pickle
import PyPDF2


class LayoutAnalyzer():

    def __init__(self):
        self.files = pd.DataFrame(columns=['pdf_name', 'pdf_path', 'list_of_images'])
        self.files.set_index('pdf_name', inplace=True)
        self.results = pd.DataFrame(columns=['pdf_name', 'model_name', 'relevant_pages', 'partitions_metadata', 'runtime', 'rendered_pages'])
        self.results.set_index('pdf_name', inplace=True)
        self.models = {
            'yolo': None
        }

    
    def analyze(self, pdf_path, model_name, render = False):
        # instantiate a row in 'files'
        pdf_name = pdf_path.split('/')[-1].split('.pdf')[0]
        self.files.loc[pdf_name] = {
            'pdf_path': pdf_path,
            'list_of_images': convert_from_path(pdf_path, dpi = 120)
        }

        # redirect to selected model and track runtime
        start_time = time.time()
        if model_name == 'yolo':
            partitions_metadata = self.analyze_yolo(pdf_name) 
        else:
            print(f'No model with name {model_name}.')
            return # is this how I leave the method?
        end_time = time.time()

        # add dataframe
        self.results.loc[pdf_name] = {
            'pdf_name': pdf_name,
            'model_name': model_name,
            'relevant_pages': list(set([entry['page_number'] for entry in partitions_metadata])),
            'partitions_metadata': partitions_metadata,
            'runtime': end_time - start_time,
            'rendered_pages': None
        }

        # for debug purposes
        if render:
            self.render(pdf_name)

        self.crop_pdf(pdf_name, self.results.at[pdf_name, 'relevant_pages'])


    def rescale_bounding_box(self, bounding_box, size_reference, size_reference_new):
        # Calculate scale factors
        scale_x = size_reference_new[0] / size_reference[0]
        scale_y = size_reference_new[1] / size_reference[1]

        # Apply scale factors to points
        top_left = (int(bounding_box['top_left'][0] * scale_x), int(bounding_box['top_left'][1] * scale_y))
        bottom_right = (int(bounding_box['bottom_right'][0] * scale_x), int(bounding_box['bottom_right'][1] * scale_y))

        # Return new bounding box
        return top_left, bottom_right

    def render(self, pdf_name):
        #rendered_pages = []
        for page in self.results.loc[pdf_name, 'relevant_pages']:
            image = np.array(self.files.loc[pdf_name, 'list_of_images'][page-1])
            for partition in self.results.loc[pdf_name, 'partitions_metadata']:
                if partition['page_number'] == page:
                    # Determine scale factors
                    scale_factor = image.shape[0] / 700  # scale factor based on image width
                    thickness = int(2 * scale_factor)
                    font_size = 0.5 * scale_factor
                    offset = int(20 * scale_factor)

                    # Draw a red rectangle, while rescaling the bounding box
                    (x1, y1), (x2, y2) = self.rescale_bounding_box(partition['bounding_box'], partition['reference_size'], image.shape)
                    cv2.rectangle(image, (x1, y1), (x2, y2), color=(0, 0, 255), thickness=thickness)

                    # Draw the text
                    label = f"{partition['confidence']:.2f}"
                    cv2.putText(image, label, (x1, y1 + offset), cv2.FONT_HERSHEY_SIMPLEX, font_size, (0, 0, 255), thickness)
            # save
            #rendered_pages.append(image)
            cv2.imwrite(f"render_main/{pdf_name}_{page}.png", image)  # Save the image to the file
        #self.results.at[pdf_name, 'rendered_pages'] = rendered_pages

    def crop_pdf(self, pdf_name, page_list):
        # Create a PDF reader object
        with open(f'1.pdf_raw/{pdf_name}.pdf', 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            # Create a PDF writer object
            writer = PyPDF2.PdfWriter()
            for page in page_list:
                writer.add_page(reader.pages[page-1])
            # Write the output PDF
            with open(f'azure_main/{pdf_name}.pdf', 'wb') as output_file:
                writer.write(output_file)

    def analyze_yolo(self, pdf_name):
        CONFIDENCE_THRESHOLD = 0.5
        # init model
        if self.models['yolo'] is None:
            model = YOLO('keremberke/yolov8s-table-extraction')
            # set model parameters
            model.overrides['conf'] = CONFIDENCE_THRESHOLD  # NMS confidence threshold
            model.overrides['iou'] = 0.01  # NMS IoU threshold
            model.overrides['agnostic_nms'] = False  # NMS class-agnostic
            model.overrides['max_det'] = 200  # maximum number of detections per image
            # save
            self.models['yolo'] = model
        else:
            model = self.models['yolo']

        # retrieve list of images using pdf_name
        images = self.files.loc[pdf_name]['list_of_images']
        # save metadata of every partition in every image
        partitions_metadata = []
        for i, img in enumerate(images):
            output = model.predict(img)[0].boxes
            if output.shape[0] != 0: # something was detected
                size = output.orig_shape.tolist()
                for bb, conf in zip(output.xyxy.tolist(), output.conf.tolist()):
                    if conf > CONFIDENCE_THRESHOLD:
                        bb = list(map(int, bb))
                        partitions_metadata.append({
                            'page_number': i + 1,
                            'reference_size': size,
                            'bounding_box': {'top_left': (bb[0], bb[1]), 'bottom_right': (bb[2], bb[3])},
                            'confidence': conf
                        })
        return partitions_metadata

if __name__ == '__main__':
    analyzer = LayoutAnalyzer()
    files_folder = '1.pdf_raw'
    for file_name in os.listdir(files_folder):
        if file_name.endswith('.pdf'):
            analyzer.analyze(f'{files_folder}/{file_name}', 'yolo', render = False)

    print(analyzer.results[['relevant_pages', 'runtime']])

    # Save the results DataFrame to a pickle file
    with open('results.pkl', 'wb') as f:
        pickle.dump(analyzer.results, f)

