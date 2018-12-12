''' This file contains unit tests for
wdcli project script  '''

'''Creater Shafay Haseeb'''


#importing the wdcli script and unit test package
import unittest
import wdcli

#masking subclass of testcase
class Test_wdcli(unittest.TestCase):

    #test 1 for select_mirrors function
    def test_select_mirrors(self):
        #mirrors = ['https://dumps.wikimedia.org','https://dumps.wikimedia.your.org','http://wikipedia.c3sl.ufpr.br']
        #asserts that required output is generated when user selects an option
        self.assertEqual(wdcli.select_mirrors(1),'https://dumps.wikimedia.org') #test passed
        self.assertEqual(wdcli.select_mirrors(2),'https://dumps.wikimedia.your.org') #test passed
        self.assertEqual(wdcli.select_mirrors(3),'http://wikipedia.c3sl.ufpr.br') #test passed
        self.assertEqual(wdcli.select_mirrors(''),'https://dumps.wikimedia.org') #test passed
        #assert a value error when special char is passed, these test are failed
        self.assertRaises(ValueError,wdcli.select_mirrors,'@') #test failed
        self.assertRaises(ValueError,wdcli.select_mirrors,'a') #test failed


    #test 2 for select_date function
    def test_select_date(self):
        #test if default is chosen it must return first day of month
        self.assertEqual(wdcli.select_dates(''),'20181201') #test passed
        '''following two test suggest that throw excep block should be used
            instead of using a forever loop for invalid input'''
        #test to check boundry value of a day
        self.assertRaises(ValueError,wdcli.select_dates,'20181132') #test failed
        #test to check boundary value for month
        self.assertRaises(ValueError,wdcli.select_dates,'20181332') #test failed

    #test 3 for select_projects function
    def test_select_projects(self):
        #passing a string should output the list of the project
        self.assertEqual(wdcli.select_projects('wiki'),['wiki']) #test passed
        #pasing 'ENTER KEY' to simulate default choice should select a list of project
        self.assertEqual(wdcli.select_projects(''),['wiki','wikibooks','wiktionary','wikiquote','wikimedia','wikisource','wikinews','wikiversity','wikivoyage']) #test passed
        #passing special char should raise an errorvalue
        self.assertRaises(ValueError,wdcli.select_projects,'@')# test failed

    #test 4 for select_locale function
    def test_select_locale(self):
        #passing a string should output the list of locale
        self.assertEqual(wdcli.select_locale('en'),['en'])# test passed
        #pasing 'ENTER KEY' to simulate default choice should select 'en'
        self.assertEqual(wdcli.select_locale(' '),['en'])# test passed
        #passing special char should raise an errorvalue
        self.assertRaises(ValueError,wdcli.select_locale,'@')# test failed
    #test 5 for checkProject function
    def test_checkProject(self):
    #the function validates the user input by using boolean data type
        # passing correct project should result in True value
        self.assertTrue(wdcli.checkProject,'wiki')# test passed
        self.assertFalse(wdcli.checkProject,'wiko')# test failed
    #test 5 for checkLocale function
    #the function validates the user input by using boolean data type for locales
        # passing correct locale should result in True value
        self.assertTrue(wdcli.checkLocale,'en')# test passed
        self.assertFalse(wdcli.checkLocale,'@')# test failed




if __name__ == '__main__':
    unittest.main()
