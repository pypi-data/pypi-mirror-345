# import statements
import os
import csv

# # input statements to obtain path to data + name of output csv
# home_dir = os.path.expanduser("~")
# file_path = input("Please input path to folder containing data: ")
# output_csv = input("Please input the name of the resulting csv file (.csv is NOT required): ") + ".csv"
# output_csv = os.path.join(os.getcwd(), output_csv)
# root_dir = file_path

# #  ----- working ----- #

# # test path: /scr/data/skala_redox_data/241004_New_2DG+A549/A549_Cyanide

# # keep track # of '_'
# num_underscore = 0

# # stores list of list of data extracted from each file name
# list_extracted_features = []

# # stores list of all sub-folder names
# file_names = []

# # list that stores all rows of csv file
# write_rows = []

# # stores full path of each sub-folder
# paths = []

# # stores list of headers prior to update
# first_headers = ["file_name", "file_path"]

# # stores list of updated header names
# updated_col_names = ["file_name", "file_path"]



# # extracts features from name
# for entry in os.listdir(root_dir):
# 	full_path = os.path.join(root_dir, entry)
# 	file_names.append(entry)
# 	paths.append(full_path)
	
# 	if os.path.isdir(full_path):
# 		parts = entry.split("_")
# 		num_underscore = len(parts)
# 		list_extracted_features.append(parts)



# # adds features obtained to new row in csv file        
# def add_features():
# 	for i in range(len(list_extracted_features)):
# 		list = []
# 		list.append(file_names[i])
# 		list.append(paths[i])

# 		for j in range(len(list_extracted_features[0])):
# 			list.append(list_extracted_features[i][j])

# 		write_rows.append(list)



# # creates the csv file and outputs first 3 rows of csv file
# def create_csv():
# 	with open(output_csv, mode='w', newline='') as csv_file:
# 		writer = csv.writer(csv_file)
# 		for i in range(num_underscore):
# 			first_headers.append("column_" + str(i))
			
		
# 		writer.writerow(first_headers)

# 		print("\n---------- CSV Preview (header + first 2 rows): ----------\n")
# 		print(", ".join(first_headers))
# 		for row in write_rows[:2]:
# 			print(", ".join(row))
# 		print("\n")

# 		writer.writerows(write_rows)



# # asks user to input column names
# def update_col_names():
# 	# updated list of headers
# 	print("Please input the following names for columns:\n  -cell_line\n  -condition\n  -dish\n  -channel_type\n  -cell_type\n")
# 	possible_inputs = ["cell_line", "condition", "dish", "channel_type", "cell_type"]
# 	for i in range(num_underscore):
# 		new_col_name = input(first_headers[i+2] + ": ")
# 		if new_col_name not in possible_inputs:
# 			raise Exception("INVALID INPUT")
# 		updated_col_names.append(str(new_col_name))
	


# # updates each row
# def update_row():
# 	# index of dish
# 	index_dish = updated_col_names.index("dish") - 2

# 	# index of channel type
# 	index_ct = updated_col_names.index("channel_type") - 2

# 	# changes Dish# -> # in each row
# 	for i in range(len(list_extracted_features)):
# 		change_dish = list_extracted_features[i][index_dish].upper()		
# 		if "DISH" in change_dish:
# 			dish_num = change_dish.replace("DISH", "")
# 			list_extracted_features[i][index_dish] = dish_num

# 		else:
# 			raise Exception("WRONG COLUMN NAME")

# 	# changes #n or #f -> n or f
# 	for i in range(len(list_extracted_features)):
# 		change_ct_list = list(list_extracted_features[i][index_ct])

# 		if 'f' in change_ct_list:
# 			list_extracted_features[i][index_ct] = 'f'

# 		elif 'n' in change_ct_list:
# 			list_extracted_features[i][index_ct] = 'n'
		
# 		else:
# 			raise Exception("INVALID CHANNEL TYPE")

# 	for i in range(len(file_names)):
# 		list_extracted_features[i].insert(0, file_names[i])
# 		list_extracted_features[i].insert(1, paths[i])




# # updates the csv files with newly inputted headers
# def update_csv():
# 	with open(output_csv, mode='w', newline='') as csv_file:
# 		writer = csv.writer(csv_file)
# 		writer.writerow(updated_col_names)
# 		writer.writerows(list_extracted_features)
	



# add_features()
# create_csv()
# update_col_names()
# update_row()
# update_csv()


def generate_csv_with_column_prompt(input_folder, output_csv_name):
	"""
	Wrapper to call the original csv generator with column name prompt.
	Still requires manual input for columns (as originally designed).
	"""
	global file_names, paths, list_extracted_features, updated_col_names
	file_names, paths, list_extracted_features = [], [], []
	updated_col_names = ["file_name", "file_path"]

	# Re-run logic manually within this function as per original flow
	root_dir = input_folder
	output_csv = output_csv_name if output_csv_name.endswith(".csv") else output_csv_name + ".csv"
	output_csv = os.path.join(os.getcwd(), output_csv)

	# Extract
	for entry in os.listdir(root_dir):
			full_path = os.path.join(root_dir, entry)
			file_names.append(entry)
			paths.append(full_path)
			if os.path.isdir(full_path):
					parts = entry.split("_")
					list_extracted_features.append(parts)

	num_underscore = len(list_extracted_features[0])

	# Prompt user for column names
	print("Please input the following names for columns:\n  -cell_line\n  -condition\n  -dish\n  -channel_type\n  -cell_type\n")
	possible_inputs = ["cell_line", "condition", "dish", "channel_type", "cell_type"]
	for i in range(num_underscore):
			new_col_name = input("column_" + str(i) + ": ")
			if new_col_name not in possible_inputs:
					raise Exception("INVALID INPUT")
			updated_col_names.append(str(new_col_name))

	# Fix and insert metadata
	index_dish = updated_col_names.index("dish") - 2
	index_ct = updated_col_names.index("channel_type") - 2

	for i in range(len(list_extracted_features)):
			dish_val = list_extracted_features[i][index_dish].upper()
			if "DISH" in dish_val:
					list_extracted_features[i][index_dish] = dish_val.replace("DISH", "")
			else:
					raise Exception("Expected 'DISH#' format in 'dish' column")

			ct_val = list_extracted_features[i][index_ct]
			if 'f' in ct_val:
					list_extracted_features[i][index_ct] = 'f'
			elif 'n' in ct_val:
					list_extracted_features[i][index_ct] = 'n'
			else:
					raise Exception("Expected channel type to include 'f' or 'n'")
			
			list_extracted_features[i].insert(0, file_names[i])
			list_extracted_features[i].insert(1, paths[i])

	# Write CSV
	with open(output_csv, mode='w', newline='') as csv_file:
			writer = csv.writer(csv_file)
			writer.writerow(updated_col_names)
			writer.writerows(list_extracted_features)
