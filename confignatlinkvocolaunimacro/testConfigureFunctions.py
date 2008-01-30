import sys, unittest, win32api, os


file1 = os.path.join("C:\\", "testinifile.ini")

class TestProfileFunctions(unittest.TestCase):
    """test ini file functions from win32api"""
    def setUp(self):
        f1 = open(file1, 'w')
        f1.close()



    def tearDown(self):
        if os.path.isfile(file1):
            os.remove(file1)
        



    def test_setting_values(self):
        f1 = open(file1, 'w')
        f1.close()
        win32api.WriteProfileVal('s1', 'k1','v1', file1)
        win32api.WriteProfileVal('s1', 'k2','v2', file1)
        win32api.WriteProfileVal('s2', 'kk1','vv1', file1)
        section = win32api.GetProfileSection('s1', file1)
        expected = ['k1=v1', 'k2=v2']
        self.assert_(expected == section, "section |%s| not as expected: |%s|"% (section, expected))

        # this call deletes a key:::::    
        win32api.WriteProfileVal('s1', 'k2',None, file1)
        section = win32api.GetProfileSection('s1', file1)
        expected = ['k1=v1']
        self.assert_(expected == section, "section |%s| after deleted keys is not as expected: |%s|"% (section, expected))
                
        



def _run():
    unittest.main()
    

if __name__ == "__main__":
    _run()
