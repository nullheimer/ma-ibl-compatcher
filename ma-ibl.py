from pathlib import Path
import os
import re
from shutil import copy

def main():
	# Paths
	output_dir = Path("G:/ck3/ma-ibl")
	ck3_dir = Path("G:/Steam/steamapps/common/Crusader Kings III/game/gfx/map/map_object_data")
	ma_dir = Path("G:/Steam/steamapps/workshop/content/1158310/2452585382/gfx/map/map_object_data")
	ibl_dir = Path("G:/Steam/steamapps/workshop/content/1158310/2416949291/gfx/map/map_object_data")

	# Locator files
	locator_files = ("building_locators.txt", "special_building_locators.txt")

	# Ask for version number and create working directory
	match = None
	while match == None:
		version_no = input("Version number (e.g. 1.18.3): ").strip()
		match = re.match(r"[\d.]", version_no)
	working_dir = create_folders(version_no, output_dir)

	# Copy IBL locator files to working directory
	for file in os.listdir(Path(ibl_dir)):
		if file in locator_files:
			copy(Path(ibl_dir, file), Path(working_dir))
	
	# Get vanilla and MA locators
	ck3_locators, ma_locators, ibl_locators = get_locators(ck3_dir, ma_dir, working_dir, locator_files)

	# Compare locators
	modded_locators = compare_locators(ck3_locators, ma_locators)

	# Inject modded MA locators in IBL file
	ibl_locators = inject_locators(modded_locators, ibl_locators, working_dir)

	# Write to file
	for i, j in enumerate(locator_files):
		with open(Path(working_dir, j), "w", encoding="utf-8-sig") as f:
			f.writelines(ibl_locators[i])

def create_folders(version_no, output_dir):
	output_contents = os.listdir(output_dir)
	new_version_no = version_no
	a = 0
	while new_version_no in output_contents:
		# Append
		a += 1
		new_version_no = version_no + "-" + str(a)

	# Create directories
	os.makedirs(Path(output_dir) / new_version_no)
	working_dir = Path(output_dir) / new_version_no

	if new_version_no == version_no:
		print(f"Created {new_version_no}.")
	else:
		print(f"{version_no} already exists, created {new_version_no} instead.")
	return working_dir

def get_locators(ck3_dir, ma_dir, working_dir, locator_files):
	# [building_locators], [special_building_locators]
	ck3_locators = [[], []]
	ma_locators = [[], []]
	ibl_locators = [[], []]

	for i, j in enumerate(locator_files):
		with open(Path(ck3_dir, j), "r", encoding="utf-8-sig") as f:
			lines = f.readlines()
		for line in lines:
			ck3_locators[i].append(line.strip())

		with open(Path(ma_dir, j), "r", encoding="utf-8-sig") as f:
			lines = f.readlines()
		for line in lines:
			ma_locators[i].append(line.strip())

		with open(Path(working_dir, j), "r", encoding="utf-8-sig") as f:
			lines = f.readlines()
		for line in lines:
			ibl_locators[i].append(line)

	return ck3_locators, ma_locators, ibl_locators

def compare_locators(ck3_locators, ma_locators):
	modded_locators = [[], []]

	print("Comparing locators...")
	for i in range(len(ck3_locators)):
		for x, line in enumerate(ck3_locators[i]):
			# Detect new ID block and grab it
			if re.match(r"^id=\d*$", line):
				ck3_id_values = ck3_locators[i][x:x+4]

				# Compare!
				for j, ma_line in enumerate(ma_locators[i]):
				# Found ID in MA
					if ma_line == ck3_id_values[0]:
						if (
							ma_locators[i][j+1] != ck3_id_values[1] or	# position
							ma_locators[i][j+2] != ck3_id_values[2] or	# rotation
							ma_locators[i][j+3] != ck3_id_values[3]		# scale
						):
							modded_locators[i].extend(ma_locators[i][j:j+4])
						break
	print("Finished comparing locators.")

	return modded_locators

def inject_locators(modded_locators, ibl_locators, working_dir):
	print("Injecting locators...")
	for i in range(len(modded_locators)):
		for x, line in enumerate(modded_locators[i]):
			if re.match(r"^id=\d*$", line):
				
				for j, ibl_line in enumerate(ibl_locators[i]):
					if ibl_line.strip() == line:
						# Add indentation
						for k in range(4):
							modded_locators[i][x+k] = "\t\t\t" + modded_locators[i][x+k] + "\n"
						ibl_locators[i][j:j+4] = modded_locators[i][x:x+4]
						break
	print("Finished injecting locators.")

	return ibl_locators


if __name__ == "__main__":
	try:
		main()
	finally:
		input("Press enter to exit...")