import sys
import svgwrite
import re
    
#TODO: Make func that fills in laser expand ranges by
#      looking for the laserrange line and then 
#      progressing line by line till it reaches a '-' for that laser
		
LASER_VALUES = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmno"

LASER_WIDTH = 7
BUTTON_WIDTH = 9
FX_WIDTH = BUTTON_WIDTH * 2 + 1
MEASURE_WIDTH = LASER_WIDTH * 2 + BUTTON_WIDTH * 4 + 5
CHIP_HEIGHT = 3
LASER_COLORS = (svgwrite.rgb(0, 75, 100, '%'), svgwrite.rgb(100, 0, 25, '%'))
LASER_OPACITY = '0.33'
BT_COLOR = svgwrite.rgb(100,100,100, '%')
FX_COLOR = svgwrite.rgb(100,50,0, '%')
FX_OPACITY = '0.75'
EXIT_HEIGHT = 5
ENTRY_HEIGHT = 5

def get_measure_numbers(filename):
    result = []
    with open(filename, 'r') as f:
        all_lines = f.read()
        data = all_lines.split("\n--")
        measures = data[1:]
        data = data[0]
        numerator = 4
        denominator = 4
        tempo = re.findall("beat\\=./.", data)
        if len(tempo) > 0:
            numerator = int(tempo[0].split('=')[1].split('/')[0])
            denominator = int(tempo[0].split('=')[1].split('/')[1])
        for measure in measures: 
            datalines = re.findall("[0-2]{4}\\|.*", measure)
            tempo = re.findall("beat\\=./.", measure)
            if len(tempo) > 0:
                numerator = int(tempo[0].split('=')[1].split('/')[0])
                denominator = int(tempo[0].split('=')[1].split('/')[1])
            if(len(datalines) > 0):
                result += [[192 * (numerator / denominator), (192 * (numerator / denominator)) / len(datalines), (numerator, denominator)]]
    return result
    
def pos_to_measure(pos, measures):
    now = pos
    for measure in measures:
        now -= measure[0]
        if now < 0:
            return measure

def measures_to_length(measures):
    result = 0
    for m in measures:
        result += m[0]
    return result

		
def map_laser(l):
	result = LASER_VALUES.index(l)
	result /= 50
	return result
		
def get_next_laser(pos, datalines, measure_numbers, laser):
	counter = 1
	for line in datalines:
		to_add = int(pos_to_measure(pos,measure_numbers)[1])
		l = line[8 + laser]
		if l in LASER_VALUES:
			return [map_laser(l), pos, counter]
		elif l == '-':
			return None
		pos += to_add
		counter += 1
	return None
		
def	draw_measure_lines(svg, measures):
	height = measures_to_length(measures)
	x0 = MEASURE_WIDTH / 2.0 + LASER_WIDTH + 1
	x1 = x0 + MEASURE_WIDTH - 2 * LASER_WIDTH - 2
	pos = 0
	index = 1
	for m in measures:
		y = height - pos
		svg.add(svg.line((x0, y), (x1,y), stroke=svgwrite.rgb(100,100,100, '%')))
		t = "%02d" % index
		svg.add(svg.text(t, insert = (x0 - 7 * len(t) - LASER_WIDTH - 1, y), font_size = '12px'))
		for i in range(1, m[2][0]):
			y_c = y + (i / m[2][1]) * m[0]
			svg.add(svg.line((x0, y_c), (x1,y_c), stroke=svgwrite.rgb(25,25,25, '%')))
		pos = pos + m[0]
		index += 1
	return svg

def draw_bpm_text(svg, filename, measure_numbers):
	pos = 0
	height = measures_to_length(measure_numbers)
	with open(filename, 'r') as f:
		all_lines = f.readlines()
		for line in all_lines:
			if re.match("[0-2]{4}\\|.*", line) != None:
				pos += int(pos_to_measure(pos,measure_numbers)[1])
			elif line.startswith("t=") and '-' not in line:
				svg.add(svg.text(line[2:], insert = (MEASURE_WIDTH * 1.5, height - pos), font_size = '12px'))
	return svg

def get_expand_ranges(filename, measures):
    pos = 0
    height = measures_to_length(measures)
    result = [[],[]]
    filling_range = [(False, 0),(False, 0)]
    with open(filename, 'r') as f:
        all_lines = f.readlines()
        for line in all_lines:
            if re.match("[0-2]{4}\\|.*", line) != None:
                pos += int(pos_to_measure(pos,measures)[1])
                for i in range(2):
                    if filling_range[i][0] and line[8+i] == '-':
                        result[i].append((filling_range[i][1], pos))
                        filling_range[i] = (False, 0)
            elif line.startswith("laserrange_"):
                i = 0 if line[11] == 'l' else 1
                filling_range[i] = (True, pos)   
    return result

def main(filename, savePath):
	pos = 0
	measure_numbers = get_measure_numbers(filename)
	expand_ranges = get_expand_ranges(filename, measure_numbers)
	line_index = 0
	height = measures_to_length(measure_numbers)
	
	output = svgwrite.Drawing(savePath, size=(u'%dpx' % (MEASURE_WIDTH * 2), u'%dpx' % height), profile='tiny')
	lane_x = MEASURE_WIDTH / 2.0
	lane_w = MEASURE_WIDTH
	lane_y = 0
	lane_h = height
	
	output.add(output.rect((lane_x,lane_y),(lane_w,lane_h), fill=svgwrite.rgb(5,5,5,'%')))

	#Left Laser lane
	output.add(output.rect((lane_x,lane_y), (LASER_WIDTH, lane_h), fill=svgwrite.rgb(5,10,25,'%')))
	lane_x = lane_x + LASER_WIDTH
	output.add(output.rect((lane_x,lane_y), (1, lane_h), fill=svgwrite.rgb(40,40,40,'%')))
	lane_x = lane_x + 1
	#Button lanes
	for i in range(4):
		lane_x = lane_x + BUTTON_WIDTH
		output.add(output.rect((lane_x,lane_y), (1, lane_h), fill=svgwrite.rgb(40,40,40,'%')))
		lane_x = lane_x + 1
	
	#Right Laser lane
	output.add(output.rect((lane_x,lane_y), (LASER_WIDTH, lane_h), fill=svgwrite.rgb(25,5,10,'%')))
	
	lane_x = MEASURE_WIDTH / 2.0	
	
	output = draw_measure_lines(output, measure_numbers)
	output = draw_bpm_text(output, filename, measure_numbers)
	
	lasers = []
	bt_holds = []
	bt_chips = []
	fx_holds = []
	fx_chips = []
	
	fx_hold_active = [(False, 0), (False, 0)]
	bt_hold_active = [(False, 0), (False, 0), (False, 0), (False, 0)]
	
	with open(filename, 'r') as f:
		all_lines = f.read()
		all_datalines = re.findall("[0-2]{4}\\|.*", all_lines)
		for line in all_datalines:
			to_add = pos_to_measure(pos,measure_numbers)[1]
			
			#BTs
			for i in range(4):
				l = line[i]
				bt_x = lane_x + LASER_WIDTH + 1 + (BUTTON_WIDTH + 1) * i

				if (l == '0') and bt_hold_active[i][0]: # End Hold
					bt_h = pos - bt_hold_active[i][1]
					bt_y = height - pos
					bt_holds.append(output.rect((bt_x,bt_y),(BUTTON_WIDTH, bt_h), fill=BT_COLOR))
					bt_hold_active[i] = (False, 0)
				elif (l == '2') and bt_hold_active[i][0] == False: # Start Hold
					bt_hold_active[i] = (True, pos)
								
				if l == '1': # BT Chip
					bt_y = height - pos - CHIP_HEIGHT
					bt_chips.append(output.rect((bt_x,bt_y),(BUTTON_WIDTH, CHIP_HEIGHT), fill=BT_COLOR))			
				
			#FXs
			for i in range(2):
				l = line[5 + i]
				fx_x = lane_x + LASER_WIDTH + 1 + (2 * BUTTON_WIDTH + 2) * i

				if (l == '2' or l == '0') and fx_hold_active[i][0]: # End Hold
					fx_h = pos - fx_hold_active[i][1]
					fx_y = height - pos
					fx_holds.append(output.rect((fx_x,fx_y),(FX_WIDTH, fx_h), fill=FX_COLOR, fill_opacity=FX_OPACITY))
					fx_hold_active[i] = (False, 0)

				elif (l != '0' and l != '2') and fx_hold_active[i][0] == False: # Start Hold
					fx_hold_active[i] = (True, pos)
				
				if l == '2': # FX Chip
					fx_y = height - pos - CHIP_HEIGHT
					fx_chips.append(output.rect((fx_x,fx_y),(FX_WIDTH, CHIP_HEIGHT), fill=FX_COLOR))			

			
			#Lasers
			for i in range(2):
				l = line[8 + i]
				if l == '-':
					continue
				if l in LASER_VALUES:
					curr_laser = [map_laser(l), pos]
					next_laser = get_next_laser(pos + to_add, all_datalines[line_index + 1:], measure_numbers, i)
					if next_laser != None:
						is_expanded = False
						for r in expand_ranges[i]:
							if curr_laser[1] > r[1]:
								continue
							elif curr_laser[1] >= r[0]:
								is_expanded = True
								break
						
						duration = next_laser[1] - curr_laser[1]
						if is_expanded:
							l_x0 = next_laser[0] * (2 * MEASURE_WIDTH) - (next_laser[0] * LASER_WIDTH) + (LASER_WIDTH * (1 - next_laser[0]))
							l_x1 = curr_laser[0] * (2 * MEASURE_WIDTH) - (curr_laser[0] * LASER_WIDTH) + (LASER_WIDTH * (1 - curr_laser[0]))
						else:
							l_x0 = next_laser[0] * (MEASURE_WIDTH - LASER_WIDTH) + lane_x + LASER_WIDTH * 0.5
							l_x1 = curr_laser[0] * (MEASURE_WIDTH - LASER_WIDTH) + lane_x + LASER_WIDTH * 0.5
						if duration > 6:
							l_y0 = height - next_laser[1]
							l_y1 = height - pos
							l_points = [(l_x0 - LASER_WIDTH * 0.5, l_y0), 
													(l_x0 + LASER_WIDTH * 0.5, l_y0),
													(l_x1 + LASER_WIDTH * 0.5, l_y1), 
													(l_x1 - LASER_WIDTH * 0.5, l_y1)]
							lasers.append(output.polygon(l_points, fill=LASER_COLORS[i], fill_opacity=LASER_OPACITY))
						else: # Slam
							l_y = height - next_laser[1]
							l_h = duration
							l_x = min(l_x0, l_x1) - (LASER_WIDTH * 0.5)
							l_w = abs(l_x0 - l_x1) + LASER_WIDTH

							lasers.append(output.rect((l_x,l_y),(l_w, l_h), fill=LASER_COLORS[i], fill_opacity=LASER_OPACITY))
							#print("a: %s" % all_datalines[line_index + next_laser[2]])
							#print("b: %s" % all_datalines[line_index + next_laser[2] + 1])
							if all_datalines[line_index + next_laser[2] + 1][8+i] == '-': # add end segmento
								e_x = l_x0 - (LASER_WIDTH * 0.5);
								lasers.append(output.rect((e_x, l_y - EXIT_HEIGHT), (LASER_WIDTH, EXIT_HEIGHT), fill=LASER_COLORS[i], fill_opacity=LASER_OPACITY))
							if all_datalines[line_index - 1][8+i] == '-': # add start segment
								e_x = l_x1 - (LASER_WIDTH * 0.5);
								lasers.append(output.rect((e_x, l_y + duration), (LASER_WIDTH, ENTRY_HEIGHT), fill=LASER_COLORS[i], fill_opacity=LASER_OPACITY))
								
							
			pos = pos + to_add
			line_index += 1
					
	# add everything to separate lists and then
	# add them to output here for proper layering
	for hold in fx_holds:
		output.add(hold)
	for hold in bt_holds:
		output.add(hold)
	for laser in lasers:
		output.add(laser)
	for chip in fx_chips:
		output.add(chip)
	for chip in bt_chips:
		output.add(chip)
	
	output.save()
	
main(sys.argv[1], sys.argv[2])
print("Finished!")
