#encoding:utf-8
import maths_add.perfect_numbers

find_factors=perfect_numbers.find_factors

def isA_numbers(n,m):
	resultN=find_factors(n)
	resultM=find_factors(m)
	resultN.remove(n)
	resultM.remove(m)
	if sum(resultN)==m and sum(resultM)==n:
		return True
	return False

def countA_numbers(n,m):
	result=0
	for i in range(n,m+1):
		for j in range(n,m+1):
			if (isA_numbers(i,j)):
				result+=1
	return result//2

def printA_numbers(n,m):
	result=[]
	result1=countA_numbers(n,m)
	for i in range(n,m+1):
		for j in range(n,m+1):
			if (isA_numbers(i,j)):
				result.append(i)
				result.append(j)
	return result[:result1*2]
