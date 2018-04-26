import sys
import svgwrite
import re
    
LASER_VALUES = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmno"

LASER_WIDTH = 7
BUTTON_WIDTH = 9
MEASURE_WIDTH = LASER_WIDTH * 2 + BUTTON_WIDTH * 4 + 5

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
                result += [[192 * (numerator / denominator), (192 * (numerator / denominator)) / len(datalines)]]
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

def	draw_measure_lines(svg, measures):
	height = measures_to_length(measures)
	x0 = MEASURE_WIDTH / 2.0
	x1 = x0 + MEASURE_WIDTH
	pos = 0
	for m in measures:
		y = height - pos
		svg.add(svg.line((x0, y), (x1,y), stroke=svgwrite.rgb(20,20,20, '%')))
		pos = pos + m[0]
	return svg

def main(filename, savePath):
	pos = 0
	measure_numbers = get_measure_numbers(filename)
	line_index = 0
	height = measures_to_length(measure_numbers)
	
	output = svgwrite.Drawing(savePath, profile='tiny')
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
	lane_x = lane_x + LASER_WIDTH

	
	
	output = draw_measure_lines(output, measure_numbers)
	
	
	with open(filename, 'r') as f:
		all_lines = f.read()
		all_datalines = re.findall("[0-2]{4}\\|.*", all_lines)
		for line in all_datalines:
			to_add = int(pos_to_measure(pos,measure_numbers)[1])
			
	output.save()
	
main(sys.argv[1], sys.argv[2])