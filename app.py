#!flask/bin/python
# The above line is to specify which program to run this file with. We have virtualenv installed, so use that version of python.

from flask import Flask, jsonify, make_response, request
import nltk
import pprint
import string
from nltk.corpus import cmudict
from collections import defaultdict, OrderedDict

app = Flask(__name__)

transcr = cmudict.dict()



# TODO: Mock out some analytics requests.

# Normalizes the string, takes out any punctuation.
# Returns: a list of words.
def normalize_and_split_string(s):
	# Deletes punctuation using string.translate tables, then lowers the case and splits it into a list.
	# Creates table mapping punctuation to None
	delete_punctuation_map = dict((ord(char), None) for char in string.punctuation)

	return s.translate(delete_punctuation_map).lower().split()

# Transcribes the string into tokens.
def transcribe_string(s):
	return [transcr[word][0] for word in normalize_and_split_string(s)]

# Wraps calling transcribe_string on every line in list l
def transcribe_list(l):
	return [transcribe_string(line) for line in l]

# Returns the syllables and count of a line of tokenized lyrics.
def syllables_line(l):
	syllables = []
	syllable_count = 0

	for word in l:
		# Temp represents one syllable.
		temp = []
		phoneme_count = 0

		for phoneme in word:
			phoneme_count += 1
			temp.append(phoneme)
			# If the last character in that phoneme is a digit, it's a syllable.
			if phoneme[-1].isdigit():
				# Add the syllable to the return list and clear temp.
				syllables.append(temp)
				temp = []
				# Increment the number of syllables.
				syllable_count += 1

		# Add last few syllables on.
		if len(word) == phoneme_count and not(len(temp) == 0):
			syllables[-1] += temp


	return {"syllables": syllables, "count": syllable_count}

# Returns list of objects of lists of syllables of that line without word boundaries and associated count.
def get_syllables_and_count(tokenized_lyrics):
	return [syllables_line(line) for line in tokenized_lyrics]

@app.errorhandler(404)
def not_found(error):
	return make_response(jsonify({ "error": "Not found."}), 404)

@app.route("/tomford/api", methods=["GET"])
def index():
    return jsonify({ "message": "Welcome to the Tom Ford rap analytics API!" })

# Params: list of strings in JSON.
# Returns: a transcribed list of the passed-in lyrics.
@app.route("/tomford/api/tokenize", methods=["POST"])
def tokenize():
	# Abort if there is no request or if the request doesn't contain the lyrics property.
	if not request.json or not "lyrics" in request.json:
		abort(400)

	lyrics = request.json["lyrics"]

	# Call transcribe_list on the lyrics and return the JSON result
	return jsonify({ "tokenized_lyrics": transcribe_list(lyrics) })

# Params: tokenized_lyrics property inside JSON
# Returns: object with syllables_by_line property containing an array of syllables with counts for each line
@app.route("/tomford/api/syllables/", methods=["POST"])
def syllables():
	if not request.json or not "tokenized_lyrics" in request.json:
		abort(400)

	tokenized_lyrics = request.json["tokenized_lyrics"]

	return jsonify({ "syllables_by_line": get_syllables_and_count(tokenized_lyrics) })

# Params:
# Returns:
@app.route("/tomford/api/detect/", methods=["GET"])
def detection():
	return jsonify({ "message": "Detecting all schemes. Welcome." })

@app.route("/tomford/api/detect/perfect/", methods=["GET", "POST"])
def detect_perfect():
	return jsonify({ "message": "Detecting perfect rhymes." })

@app.route("/tomford/api/detect/multi/", methods=["GET", "POST"])
def detect_multis():
	return jsonify({ "message": "Detecting multis." })

if __name__ == '__main__':
    app.run(debug=True)
