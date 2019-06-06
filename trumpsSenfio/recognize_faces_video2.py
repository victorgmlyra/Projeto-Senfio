# USAGE
# python recognize_faces_video.py --encodings encodings.pickle
# python recognize_faces_video.py --encodings encodings.pickle --output output/jurassic_park_trailer_output.avi --display 0

# import the necessary packages
from imutils.video import VideoStream
import face_recognition
import argparse
import imutils
import pickle
import time, os, shutil
import cv2
from imutils import paths
import os

def encode_faces():
	# construct the argument parser and parse the arguments
	ap = argparse.ArgumentParser()
	ap.add_argument("-i", "--dataset", required=True,
		help="path to input directory of faces + images")
	ap.add_argument("-e", "--encodings", required=True,
		help="path to serialized db of facial encodings")
	ap.add_argument("-d", "--detection-method", type=str, default="cnn",
		help="face detection model to use: either `hog` or `cnn`")
	args = vars(ap.parse_args())

	# grab the paths to the input images in our dataset
	print("[INFO] quantifying faces...")
	imagePaths = list(paths.list_images(args["dataset"]))

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
		imageOri = cv2.imread(imagePath)
		image = cv2.resize(imageOri, (640,480))
		rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

		# detect the (x, y)-coordinates of the bounding boxes
		# corresponding to each face in the input image
		boxes = face_recognition.face_locations(rgb,
			model=args["detection_method"])

		# compute the facial embedding for the face
		encodings = face_recognition.face_encodings(rgb, boxes)

		# loop over the encodings
		for encoding in encodings:
			# add each encoding + name to our set of known names and
			# encodings
			knownEncodings.append(encoding)
			knownNames.append(name)

	# dump the facial encodings + names to disk
	print("[INFO] serializing encodings...")
	data = {"encodings": knownEncodings, "names": knownNames}
	f = open(args["encodings"], "wb")
	f.write(pickle.dumps(data))
	f.close()


encode_faces()
# construct the argument parser and parse the arguments
#ap = argparse.ArgumentParser()
#ap.add_argument("-e", "--encodings", required=True,
#	help="path to serialized db of facial encodings")
#ap.add_argument("-o", "--output", type=str,
#	help="path to output video")
#ap.add_argument("-y", "--display", type=int, default=1,
#	help="whether or not to display output frame to screen")
#ap.add_argument("-d", "--detection-method", type=str, default="cnn",
#	help="face detection model to use: either `hog` or `cnn`")
#args = vars(ap.parse_args())




# load the known faces and embeddings
print("[INFO] loading encodings...")
<<<<<<< HEAD:trumpsSenfio/recognize_faces_video2.py
data = pickle.loads(open("encodings.pickle", "rb").read())
=======
data = pickle.loads(open(args["encodings"], "rb").read())
>>>>>>> 2f03f3aeade87b527ec35d7e0285c613661b3772:trumpsSenfio/recognize_faces_video.py

# initialize the video stream and pointer to output video file, then
# allow the camera sensor to warm up
print("[INFO] starting video stream...")
vs = VideoStream(src=0).start()
writer = None
time.sleep(2.0)

num_ids = 0
num_imagem = 0
if os.path.exists('encodings.pickle'):
	os.remove('encodings.pickle')
# loop over frames from the video file stream
while True:
	# grab the frame from the threaded video stream
	frame = vs.read()
	
	# convert the input frame from BGR to RGB then resize it to have
	# a width of 750px (to speedup processing)
	rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
	rgb = imutils.resize(frame, width=750)
	r = frame.shape[1] / float(rgb.shape[1])

	# detect the (x, y)-coordinates of the bounding boxes
	# corresponding to each face in the input frame, then compute
	# the facial embeddings for each face
	boxes = face_recognition.face_locations(rgb,
		model="cnn")
	encodings = face_recognition.face_encodings(rgb, boxes)
	names = []

	directory = 'dataset/'+ 'id' + str(num_ids)
	if not os.path.exists(directory):
		os.mkdir(directory)
	num_unknows = 0
	# loop over the facial embeddings
	for j, encoding in enumerate(encodings):
		# attempt to match each face in the input image to our known
		# encodings
		matches = face_recognition.compare_faces(data["encodings"],
			encoding)
		name = "Unknown"
	
		# check to see if we have found a match
		if True in matches:
			# find the indexes of all matched faces then initialize a
			# dictionary to count the total number of times each face
			# was matched
			matchedIdxs = [i for (i, b) in enumerate(matches) if b]
			counts = {}

			# loop over the matched indexes and maintain a count for
			# each recognized face face
			for i in matchedIdxs:
				name = data["names"][i]
				counts[name] = counts.get(name, 0) + 1
			counts["Unknown"] = 20
			# determine the recognized face with the largest number
			# of votes (note: in the event of an unlikely tie Python
			# will select first entry in the dictionary)
			name = max(counts, key=counts.get)
		
		if name == "Unknown":
			num_unknows += 1
			(top, right, bottom, left) = boxes[j]
			unknown_face = rgb[top:bottom, left:right, :]
			if num_imagem < 35:
				cv2.imwrite(directory +  '/' + 'face' + str(num_imagem) + '.jpg', unknown_face)
			num_imagem += 1

		# update the list of names
		names.append(name)
	
	if not num_unknows:
		num_files = len([name for name in os.listdir(directory)])
		if num_files > 0:
			num_ids += 1
			if num_files < 20:
				shutil.rmtree(directory) 
				num_ids -= 1
			else:
				os.system('python3 encode_faces.py --dataset ' + directory + ' --encodings encodings.pickle')
				data = pickle.loads(open(args["encodings"], "rb").read())
			
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

	# if the video writer is None *AND* we are supposed to write
	# the output video to disk initialize the writer
	#if writer is None and args["output"] is not None:
	#	fourcc = cv2.VideoWriter_fourcc(*"MJPG")
	#	writer = cv2.VideoWriter(args["output"], fourcc, 20,
	#		(frame.shape[1], frame.shape[0]), True)

	# if the writer is not None, write the frame with recognized
	# faces t odisk
	if writer is not None:
		writer.write(frame)

	# check to see if we are supposed to display the output frame to
	# the screen
	#if args["display"] > 0:
	cv2.imshow("Frame", frame)
	key = cv2.waitKey(1) & 0xFF

	# if the `q` key was pressed, break from the loop
	if key == ord("q"):
		break

# do a bit of cleanup
cv2.destroyAllWindows()
vs.stop()

# check to see if the video writer point needs to be released
if writer is not None:
	writer.release()