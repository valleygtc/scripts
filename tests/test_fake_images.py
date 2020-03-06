import unittest


from fake_images import fake_img, fake_img2


class TestFakeImages(unittest.TestCase):
    def test_fake_img(self):
        content = fake_img(600, 400)

    def test_fake_img2(self):
        content = fake_img2(600, 400)

