import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'))
from qfc.core import filter_files, get_weight

def _equals(marks_list1, marks_list2):
	l1 = sorted(marks_list1)
	l2 = sorted(marks_list2)
	if len(l1) != len(l2):
		return False
	for i,_ in enumerate(l1):
		if l1[i] != l2[i]:
			return False
	return True

def test_filter_files():
    files = [
            '/',
            '/a/',
            '/b/',
            '/a/b',
            '/a/b/c',
            '/b/a/',
            '/b/a/c',
            'd',
            'da'
            ]
    assert(_equals(filter_files(files,''), ['/','d','da']))
    assert(_equals(filter_files(files,'/'), ['/']))
    assert(_equals(filter_files(files,'a'), ['/a/', '/b/a/', 'da']))



def test_weight():
    assert(get_weight('a','') == 1001)
    assert(get_weight('a/','') == 1000)
    assert(get_weight('a/b/','') == 2000)
    assert(get_weight('a/b/c','') == 3001)
    assert(get_weight('a','a')  == 1001)
    assert(get_weight('ab','a')  == 1021)
    assert(get_weight('bab','a')  == 1111)
    assert(get_weight('a_b','a')  == 1011)
    assert(get_weight('root/a_b','a')  == 2011)
    assert(get_weight('root/a_b_c_d_e_f_g_h_i_j_k','k')  == 2091)
    assert(get_weight('a/b/c/d/e/f/g/h/i/j/k','k')  == 10001)
    assert(get_weight('a/B/','b') == 2000)


