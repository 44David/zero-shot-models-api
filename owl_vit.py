import requests
import torch
from PIL import Image
from transformers import OwlViTProcessor, OwlViTForObjectDetection

def owl_vit_predict(req_url, req_text):
	processor = OwlViTProcessor.from_pretrained("google/owlvit-base-patch32")
	model = OwlViTForObjectDetection.from_pretrained("google/owlvit-base-patch32")

	image = Image.open(requests.get(req_url, stream=True).raw)
	text_labels = [[ req_text ]]

	inputs = processor(text=text_labels, images=image, return_tensors="pt")
	outputs = model(**inputs)

	# Target image sizes (height, width) to rescale box predictions [batch_size, 2]
	target_sizes = torch.tensor([(image.height, image.width)])

	# Convert outputs (bounding boxes and class logits) to Pascal VOC format (xmin, ymin, xmax, ymax)
	results = processor.post_process_grounded_object_detection(
		outputs=outputs, target_sizes=target_sizes, threshold=0.1, text_labels=text_labels
	)

	# Retrieve predictions for the first image for the corresponding text queries
	result = results[0]

	boxes, scores, text_labels = result["boxes"], result["scores"], result["text_labels"]

    # TODO Change this so it returns the values
	for box, score, text_label in zip(boxes, scores, text_labels):
		box = [round(i, 2) for i in box.tolist()]
		print(f"Detected {text_label} with confidence {round(score.item(), 3)} at location {box}")