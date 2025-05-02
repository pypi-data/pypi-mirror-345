import unittest

from hu2.email2 import Email,get_email_head



class TestEmail(unittest.TestCase):
    def test_email_head(self):
        h = [get_email_head('46133_7831中@qq.com'),
             get_email_head(None),
             get_email_head('None'),
             get_email_head('None@2@4'),
             ]
        print(h)

        pass
    def test_email2(self):
        eml = Email('13733160671@139.com','e991cc37c634941d1c00',
                         ['13733160671@139.com','461337831@qq.com'],
                         subject='检测任务说明3',
                         content='第三个检测到目前输入的原文和译文目标语种均为英文，已自动为您转换为英文翻译成中文的服务根据输入的原文 "increase"'
                         )
        eml.send('smtp.139.com')

if __name__ == '__main__':
    unittest.main()