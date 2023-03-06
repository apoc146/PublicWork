def check_overlap(line1, line2):
    x1_start, x1_end = line1
    x2_start, x2_end = line2
    if x1_end < x2_start or x2_end < x1_start:
        return False
    return True

if __name__ == '__main__':
	l1=[7,10]
	l2=[10,13]
	print(check_overlap(l1,l2))
