# USAGE
# python recognize_faces_video.py --encodings encodings.pickle

# import the necessary packages
from imutils.video import VideoStream
import face_recognition
import argparse, threading
import imutils
import pickle
import time, os, shutil
import cv2
from imutils import paths

def encode_faces(dataset, encodings_file = "encodings.pickle", detection_method = "cnn"):
	# grab the paths to the input images in our dataset
	print("[INFO] quantifying faces...")
	imagePaths = list(paths.list_images(dataset))

	# initialize the list of known encodings and known names
	knownEncodings = []
	knownNames = []

	# loop over the image paths
	for (i, imagePath) in enumerate(imagePaths):
		# extract the person name from the image path
		print("[INFO] processing image {}/{}".format(i + 1,
			len(imagePaths)))
		name = imagePath.split(os.path.sep)[-2]

		# load the input image and convert it from RGB (OpenCV ordering)
		# to dlib ordering (RGB)
		image = cv2.imread(imagePath)
		rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

		# detect the (x, y)-coordinates of the bounding boxes
		# corresponding to each face in the input image
		boxes = face_recognition.face_locations(rgb,
			model=detection_method)

		# compute the facial embedding for the face
		encodings = face_recognition.face_encodings(rgb, boxes)

		# loop over the encodings
		for encoding in encodings:
			# add each encoding + name to our set of known names and
			# encodings
			knownEncodings.append(encoding)
			knownNames.append(name)

	# dump the facial encodings + names to disk
	if os.path.exists(encodings_file):
		with open(encodings_file,'rb') as rfp: 
			faces = pickle.load(rfp)
			faces['encodings'].extend(knownEncodings)
			faces['names'].extend(knownNames)
			with open(encodings_file, "wb") as wfp:
				pickle.dump(faces, wfp)
	else:
		# dump the facial encodings + names to disk
		print("[INFO] serializing encodings...")
		data = {"encodings": knownEncodings, "names": knownNames}
		with open(encodings_file, "wb") as wfp:
			pickle.dump(data, wfp)


#construct the argument parser and parse the arguments

ap = argparse.ArgumentParser()
ap.add_argument("-e", "--encodings", required=True,
	help="path to serialized db of facial encodings")
ap.add_argument("-d", "--detection-method", type=str, default="cnn",
	help="face detection model to use: either `hog` or `cnn`")
args = vars(ap.parse_args())


if os.path.exists('encodings.pickle'):
	os.remove('encodings.pickle')
encode_faces('dataset')

# load the known faces and embeddings
print("[INFO] loading encodings...")
data = pickle.loads(open(args["encodings"], "rb").read())

def save_id(directory, encodings):
	global data
	encode_faces(directory)
	data = pickle.loads(open(encodings, "rb").read())

# initialize the video stream and pointer to output video file, then
# allow the camera sensor to warm up
print("[INFO] starting video stream...")
vs = VideoStream(src=0).start()
time.sleep(2.0)

st = time.time()
fps = 0
num_ids = 0
num_imagem = 0
count_names = {}
# loop over frames from the video file stream
while True:
	if time.time() - st >= 1:
		print('fps: ', fps)
		fps = 0
		st = time.time()
	# grab the frame from the threaded video stream
	frame = vs.read()
	fps += 1
	
	# convert the input frame from BGR to RGB then resize it to have
	# a width of 750px (to speedup processing)
	rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
	rgb = imutils.resize(frame, width=420)
	r = frame.shape[1] / float(rgb.shape[1])
	h, w, _ = rgb.shape
	# detect the (x, y)-coordinates of the bounding boxes
	# corresponding to each face in the input frame, then compute
	# the facial embeddings for each face
	boxes = face_recognition.face_locations(rgb,
		model="cnn")
	encodings = face_recognition.face_encodings(rgb, boxes)
	names = []

	directory = 'dataset/'+ 'id' + str(num_ids)
	th = threading.Thread(target = save_id, args=(directory, args['encodings'])) 
	if not os.path.exists(directory):
		os.mkdir(directory)
	num_unknows = 0
	# loop over the facial embeddings
	for j, encoding in enumerate(encodings):
		# attempt to match each face in the input image to our known encodings
		matches = face_recognition.compare_faces(data["encodings"],
			encoding)
		name = "Unknown"
	
		# check to see if we have found a match
		if True in matches:
			# find the indexes of all matched faces then initialize a dictionary 
			# to count the total number of times each face was matched
			matchedIdxs = [i for (i, b) in enumerate(matches) if b]
			counts = {}

			# loop over the matched indexes and maintain a count for each recognized face
			for i in matchedIdxs:
				name = data["names"][i]
				counts[name] = counts.get(name, 0) + 1
			counts["Unknown"] = 20

			# determine the recognized face with the largest number of votes
			name = max(counts, key=counts.get)
		
		if name == "Unknown":
			num_unknows += 1
			(top, right, bottom, left) = boxes[j]
			if top >= 30: top -= 30
			if left >= 30: left -= 30
			if bottom <= h - 30: bottom += 30
			if right <= w - 30: right += 30
			unknown_face = rgb[top:bottom, left:right, :]
			if num_imagem < 35:
				cv2.imwrite(directory +  '/' + 'face' + str(num_imagem) + '.jpg', unknown_face)
			elif num_imagem == 35:
				print(num_ids, ' chegou')
				count_names['id' + str(num_ids)] = 26
				th.start()
			num_imagem += 1

		# update the list of names
		names.append(name)

	# Save who got in
	for n in names:
		if n != 'Unknown':
			if n not in count_names:
				count_names[n] = 1
			else:
				count_names[n] += 1

			if count_names[n] == 25:
				print(n, ' chegou!')
	
	names_out = []
	for n in count_names.keys():
		if n not in names:
			names_out.append(n)
	for n in names_out:
		del(count_names[n])

	
	# Find next id to be added and prevent false unknows
	if not num_unknows:
		num_files = len([name for name in os.listdir(directory)])
		if num_files > 0:
			num_ids += 1
			if num_files < 35:
				shutil.rmtree(directory) 
				num_ids -= 1			
		num_imagem = 0
		

	# loop over the recognized faces
	for ((top, right, bottom, left), name) in zip(boxes, names):
		# rescale the face coordinates
		top = int(top * r)
		right = int(right * r)
		bottom = int(bottom * r)
		left = int(left * r)

		# draw the predicted face name on the image
		cv2.rectangle(frame, (left, top), (right, bottom),
			(0, 255, 0), 2)
		y = top - 15 if top - 15 > 15 else top + 15
		cv2.putText(frame, name, (left, y), cv2.FONT_HERSHEY_SIMPLEX,
			0.75, (0, 255, 0), 2)


	cv2.imshow("Frame", frame)
	key = cv2.waitKey(1) & 0xFF

	# if the `q` key was pressed, break from the loop
	if key == ord("q"):
		break

# do a bit of cleanup
cv2.destroyAllWindows()
vs.stop()
