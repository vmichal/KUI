

def classifier_is_permissible(reference, classification, required_FPR, minimal_sensitivity):
	# 'reference' is the correct classification. A list of 100 elements reference[sample]
	# 'classification' is the output to test. Format ... classification[alpha][sample]
	# 'required_FPR' and 'minimal_sensitivity' are the classifier parameters to beat
	num_alphas = len(classification) # the number of possible values of alpha
	scores = [] # stores (alpha, TPR, FPR) for each alpha
	for alpha in range(num_alphas):
		#get the total number of positives and negatives identified by the reference implementation
		P = sum(reference) # values are either 0 or 1
		N = len(reference) - P

		# Compute the number of correctly classified samples by the tested alhorithm
		TP = sum(x == 1 and x==y for x, y in zip(reference, classification[alpha]))
		TN = sum(x == 0 and x==y for x, y in zip(reference, classification[alpha]))
		FP = N - TN

		TPR = TP / P
		FPR = FP / N

	#extract only those values of alpha that achieve better results than our classification
	usable_alphas = [(alpha, TPR, FPR) for alpha, TPR, FPR in scores
	                    if FPR <= required_FPR  and TPR > minimal_sensitivity]

	if len(usable_alphas) == 0:
		return False # there is no parameter alpha for which the given classifier would be safer and faster

	# Extract the parameter with best score
	best_alpha, best_TPR, best_FPR = max(usable_alphas, key = lambda data: data[1])
	return True



#decide whether the new classifier is better:
our_TPR = 0.46
our_FPR = 0
is_better = classifier_is_permissible(ground_truth, new_classifier, 1, 0.46)