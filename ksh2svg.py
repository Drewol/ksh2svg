import pygame
import pygame.image
import sys
import svgwrite
    
laser_values = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmno"

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
						
def main(filename, savePath)
	pos = 0
	measure_numbers = get_measure_numbers(filename)
	line_index = 0
	
	with open(filename, 'r') as f:
		all_lines = f.read()
		all_datalines = re.findall("[0-2]{4}\\|.*", all_lines)
		for line in all_datalines:
			to_add = int(pos_to_measure(pos,measure_numbers)[1])